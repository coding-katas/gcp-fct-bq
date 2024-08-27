from google.cloud import bigquery
from google.cloud import storage
from cloudevents.http import CloudEvent
import functions_framework

@functions_framework.cloud_event
def hello_gcs(cloud_event: CloudEvent) -> tuple:
    """This function is triggered by a change in a storage bucket.

    Args:
        cloud_event: The CloudEvent that triggered this function.
    Returns:
        The event ID, event type, bucket, name, metageneration, and timeCreated.
    """
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket_name = data["bucket"]
    file_name = data["name"]
    metageneration = data["metageneration"]
    time_created = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket_name}")
    print(f"File: {file_name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {time_created}")
    print(f"Updated: {updated}")


    # Initialize clients
    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    # Download the file from GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    file_path = f"/tmp/{file_name}"
    blob.download_to_filename(file_path)

    # Define the BigQuery table schema
    table_id = "porject-formation-1.customer_test_anis.rep_sales"
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("rep_id", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("rep_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("segment", "STRING", mode="REQUIRED")
        ],
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )

    # Load data into BigQuery
    with open(file_path, "rb") as source_file:
        load_job = bigquery_client.load_table_from_file(
            source_file, table_id, job_config=job_config
        )

    load_job.result()  # Wait for the job to complete

    return event_id, event_type, bucket_name, file_name, metageneration, time_created, updated
