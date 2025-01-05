# %%
from google.cloud import bigquery
import pandas as pd
from google.oauth2 import service_account
from typing import List, Optional


def get_bigquery_client(credentials_path: str) -> bigquery.Client:
    """Initialize BigQuery client with service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )
    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def create_dataset(
    client: bigquery.Client, project_id: str, dataset_id: str, location: str
) -> str:
    """Create a BigQuery dataset if it doesn't exist."""
    dataset_ref = f"{project_id}.{dataset_id}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    dataset = client.create_dataset(dataset, exists_ok=True)
    print(f"Created dataset {dataset_ref}")
    return dataset_ref


def get_ground_truth_schema() -> List[bigquery.SchemaField]:
    """Define schema for ground truth table."""
    return [
        bigquery.SchemaField("index", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("document", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("summary", "STRING", mode="REQUIRED"),
    ]


def get_generated_summaries_schema() -> List[bigquery.SchemaField]:
    """Define schema for generated summaries table."""
    return [
        bigquery.SchemaField("index", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("id", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("generated_summary", "STRING", mode="REQUIRED"),
    ]


def setup_ground_truth_table(client: bigquery.Client, dataset_ref: str) -> str:
    """Create ground truth table."""
    table_id = f"{dataset_ref}.ground_truth"
    table = bigquery.Table(table_id, schema=get_ground_truth_schema())
    table = client.create_table(table, exists_ok=True)
    print(f"Created ground truth table: {table_id}")
    return table_id


def setup_generated_summaries_table(client: bigquery.Client, dataset_ref: str) -> str:
    """Create generated summaries table."""
    table_id = f"{dataset_ref}.generated_summaries"
    table = bigquery.Table(table_id, schema=get_generated_summaries_schema())
    table = client.create_table(table, exists_ok=True)
    print(f"Created generated summaries table: {table_id}")
    return table_id


def load_ground_truth_data(file_path: str) -> pd.DataFrame:
    """Load and prepare ground truth data."""
    df = pd.read_json(file_path)
    df["index"] = range(len(df))
    return df


def populate_ground_truth_table(
    client: bigquery.Client, df: pd.DataFrame, table_id: str
) -> None:
    """Populate the ground truth table with data."""
    job_config = bigquery.LoadJobConfig(
        schema=get_ground_truth_schema(),
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(
        f"Populated ground truth table with {client.get_table(table_id).num_rows} rows"
    )


def setup_and_populate_ground_truth(
    client: bigquery.Client, dataset_ref: str, data_file_path: str
) -> str:
    """Setup ground truth table and populate it with data."""
    # Setup table
    table_id = setup_ground_truth_table(client, dataset_ref)

    # Load and populate data
    df = load_ground_truth_data(data_file_path)
    populate_ground_truth_table(client, df, table_id)

    return table_id


def main(
    credentials_path: str,
    project_id: str,
    dataset_id: str,
    location: str,
    data_file_path: str,
) -> None:
    """Main function to setup tables and populate ground truth data."""
    # Initialize client
    client = get_bigquery_client(credentials_path)

    # Create dataset
    dataset_ref = create_dataset(client, project_id, dataset_id, location)

    # Setup and populate ground truth table
    ground_truth_table_id = setup_and_populate_ground_truth(
        client, dataset_ref, data_file_path
    )

    # Only setup generated summaries table (no data population)
    generated_summaries_table_id = setup_generated_summaries_table(client, dataset_ref)

    print("\nSetup complete!")
    print(f"Ground truth table populated: {ground_truth_table_id}")
    print(
        f"Generated summaries table ready for future use: {generated_summaries_table_id}"
    )


if __name__ == "__main__":
    # Configuration
    CREDENTIALS_PATH = "../secrets/vertex-ai.json"
    PROJECT_ID = "dag-task"
    DATASET_ID = "text_summarization"
    LOCATION = "us-central1"
    DATA_FILE_PATH = "../data/xsum_sampled.json"

    main(
        credentials_path=CREDENTIALS_PATH,
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        location=LOCATION,
        data_file_path=DATA_FILE_PATH,
    )

# %%
