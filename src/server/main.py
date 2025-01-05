from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from google.cloud import bigquery
from google.oauth2 import service_account
import os
import json
from typing import Optional
from functools import lru_cache

# from dotenv import load_dotenv
# load_dotenv()

app = FastAPI()


# Configuration from environment variables
class Settings:
    PROJECT_ID: str = os.getenv("PROJECT_ID", "dag-task")
    DATASET_ID: str = os.getenv("DATASET_ID", "text_summarization")
    LOCATION: str = os.getenv("LOCATION", "us-central1")

    @classmethod
    @lru_cache()
    def get_credentials(cls):
        """Get credentials with fallback options."""
        try:
            # First try: Get from environment variable
            if json_creds := os.getenv("GCP_SERVICE_ACCOUNT_CREDENTIALS"):
                return service_account.Credentials.from_service_account_info(
                    json.loads(json_creds)
                )

            # Second try: Use default credentials (works in Cloud Run/GKE)
            return service_account.Credentials.get_default()

        except Exception as e:
            # Fallback: Use local file (for development only)
            return service_account.Credentials.from_service_account_file(
                "./secrets/vertex-ai.json"
            )


settings = Settings()


# Response Model
class SummaryResponse(BaseModel):
    document: str
    generated_summary: str
    ground_truth_summary: Optional[str] = None
    summary_source: str  # Will be either "cache" or "generated"


@lru_cache()
def get_bigquery_client():
    """Initialize BigQuery client with credentials."""
    credentials = settings.get_credentials()
    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def setup_genai():
    """Initialize Google GenerativeAI with credentials."""
    credentials = settings.get_credentials()
    genai.configure(credentials=credentials)


def get_document_by_index(client: bigquery.Client, index: int):
    """Fetch document and summary from ground truth table by index."""
    query = f"""
    SELECT document, summary
    FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.ground_truth`
    WHERE index = {index}
    LIMIT 1
    """
    results = client.query(query).result()
    for row in results:
        return row.document, row.summary
    return None, None


def generate_summary(document: str) -> str:
    """Generate summary using GenerativeAI."""
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""Generate a 1 line summary which captures relevant details of the following dense text:
---
Text:

{document}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        },
    )

    return response.text


def get_stored_summary(client: bigquery.Client, index: int) -> Optional[str]:
    """Fetch previously generated summary from BigQuery."""
    query = f"""
    SELECT generated_summary
    FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.generated_summaries`
    WHERE index = {index}
    LIMIT 1
    """
    results = client.query(query).result()
    for row in results:
        return row.generated_summary
    return None


def store_generated_summary(client: bigquery.Client, index: int, summary: str):
    """Store generated summary in BigQuery."""
    table_id = f"{settings.PROJECT_ID}.{settings.DATASET_ID}.generated_summaries"
    rows_to_insert = [
        {
            "index": index,
            "id": index,  # Using index as id for simplicity
            "generated_summary": summary,
        }
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        raise Exception(f"Error inserting rows: {errors}")


# Initialize clients at startup
@app.on_event("startup")
async def startup_event():
    setup_genai()


@app.get("/")
async def hello() -> str:
    """Endpoint to return a greeting message."""
    return "Hello, this API is to showcase Vertex AI based summarization!"


@app.get("/summarize/{index}", response_model=SummaryResponse)
async def summarize_document(index: int):
    """Endpoint to fetch document and generate/retrieve summary."""
    try:
        client = get_bigquery_client()

        # Fetch document from BigQuery
        document, ground_truth_summary = get_document_by_index(client, index)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Check if summary already exists
        if stored_summary := get_stored_summary(client, index):
            generated_summary = stored_summary
            summary_source = "cache"
        else:
            # Generate new summary and store it
            generated_summary = generate_summary(document)
            store_generated_summary(client, index, generated_summary)
            summary_source = "generated"

        return SummaryResponse(
            document=document,
            generated_summary=generated_summary,
            ground_truth_summary=ground_truth_summary,
            summary_source=summary_source,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
