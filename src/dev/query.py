# %%
from google.cloud import bigquery
from google.oauth2 import service_account
from typing import List, Dict, Any
import pandas as pd


def get_bigquery_client(credentials_path: str) -> bigquery.Client:
    """Initialize BigQuery client with service account credentials."""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path
    )
    return bigquery.Client(credentials=credentials, project=credentials.project_id)


def query_ground_truth(
    client: bigquery.Client, project_id: str, dataset_id: str, limit: int = 5
) -> pd.DataFrame:
    """Query the ground truth table and return sample rows."""
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.ground_truth`
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


def query_generated_summaries(
    client: bigquery.Client, project_id: str, dataset_id: str, limit: int = 5
) -> pd.DataFrame:
    """Query the generated summaries table and return sample rows."""
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.generated_summaries`
    LIMIT {limit}
    """
    return client.query(query).to_dataframe()


def get_table_stats(
    client: bigquery.Client, project_id: str, dataset_id: str
) -> Dict[str, Any]:
    """Get basic statistics about both tables."""
    stats_query = f"""
    SELECT
        'ground_truth' as table_name,
        COUNT(*) as row_count,
        COUNT(DISTINCT id) as unique_ids
    FROM `{project_id}.{dataset_id}.ground_truth`
    UNION ALL
    SELECT
        'generated_summaries' as table_name,
        COUNT(*) as row_count,
        COUNT(DISTINCT id) as unique_ids
    FROM `{project_id}.{dataset_id}.generated_summaries`
    """
    return client.query(stats_query).to_dataframe()


def compare_table_contents(
    client: bigquery.Client, project_id: str, dataset_id: str
) -> pd.DataFrame:
    """Compare IDs between ground truth and generated summaries tables."""
    comparison_query = f"""
    SELECT
        'only_in_ground_truth' as location,
        COUNT(*) as count
    FROM `{project_id}.{dataset_id}.ground_truth` g
    WHERE NOT EXISTS (
        SELECT 1
        FROM `{project_id}.{dataset_id}.generated_summaries` s
        WHERE g.id = s.id
    )
    UNION ALL
    SELECT
        'only_in_generated_summaries' as location,
        COUNT(*) as count
    FROM `{project_id}.{dataset_id}.generated_summaries` s
    WHERE NOT EXISTS (
        SELECT 1
        FROM `{project_id}.{dataset_id}.ground_truth` g
        WHERE s.id = g.id
    )
    UNION ALL
    SELECT
        'in_both_tables' as location,
        COUNT(*) as count
    FROM `{project_id}.{dataset_id}.ground_truth` g
    INNER JOIN `{project_id}.{dataset_id}.generated_summaries` s
    ON g.id = s.id
    """
    return client.query(comparison_query).to_dataframe()


def run_test_queries():
    """Run all test queries and display results."""
    # Configuration
    CREDENTIALS_PATH = "../secrets/vertex-ai.json"
    PROJECT_ID = "dag-task"
    DATASET_ID = "text_summarization"

    # Initialize client
    client = get_bigquery_client(CREDENTIALS_PATH)

    print("\n=== Testing Ground Truth Table ===")
    try:
        df_ground_truth = query_ground_truth(client, PROJECT_ID, DATASET_ID)
        print("\nSample rows from ground truth table:")
        print(df_ground_truth)
    except Exception as e:
        print(f"Error querying ground truth table: {str(e)}")

    print("\n=== Testing Generated Summaries Table ===")
    try:
        df_generated = query_generated_summaries(client, PROJECT_ID, DATASET_ID)
        print("\nSample rows from generated summaries table:")
        print(df_generated)
    except Exception as e:
        print(f"Error querying generated summaries table: {str(e)}")

    print("\n=== Table Statistics ===")
    try:
        stats = get_table_stats(client, PROJECT_ID, DATASET_ID)
        print("\nTable statistics:")
        print(stats)
    except Exception as e:
        print(f"Error getting table statistics: {str(e)}")

    """
    print("\n=== Table Comparison ===")
    try:
        comparison = compare_table_contents(client, PROJECT_ID, DATASET_ID)
        print("\nComparison between tables:")
        print(comparison)
    except Exception as e:
        print(f"Error comparing tables: {str(e)}")
    """


if __name__ == "__main__":
    run_test_queries()


# %%
