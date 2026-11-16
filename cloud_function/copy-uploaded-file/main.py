
import logging
import functions_framework
from google.cloud import storage

SOURCE_BUCKET_NAME = "ravi-gcp-lab-transactions-001"
DESTINATION_BUCKET_NAME = "ravi-gcp-lab-transactions-001"

SOURCE_FILE_PREFIX = "incoming/"
DESTINATION_FILE_PREFIX = "uploading/"

storage_client = storage.Client()


@functions_framework.cloud_event
def move_file(cloud_event):

    data = cloud_event.data
    print("here")

    source_bucket_name = data["bucket"]
    source_file_name = data["name"]

    generation = int(data["generation"])

    # Process only files inside incoming/
    if (
        source_bucket_name != SOURCE_BUCKET_NAME
        or not source_file_name.startswith(SOURCE_FILE_PREFIX)
        or source_file_name.endswith("/")
    ):
        logging.info("File does not match source criteria. Skipping.")
        return

    # Construct destination object name
    relative_file_name = source_file_name[len(SOURCE_FILE_PREFIX):]

    destination_file_name = (
        f"{DESTINATION_FILE_PREFIX}{relative_file_name}"
    )

    source_bucket = storage_client.bucket(SOURCE_BUCKET_NAME)
    destination_bucket = storage_client.bucket(DESTINATION_BUCKET_NAME)

    source_blob = source_bucket.blob(
        source_file_name,
        generation=generation
    )

    destination_blob = destination_bucket.blob(destination_file_name)

    # Copy the object using rewrite
    token = None

    while True:
        token, bytes_rewritten, total_bytes = destination_blob.rewrite(
            source_blob,
            token=token
        )

        if token is None:
            break

    # Delete the original object only after successful copy
    source_blob.delete(if_generation_match=generation)

    logging.info(
        "Moved gs://%s/%s to gs://%s/%s",
        SOURCE_BUCKET_NAME,
        source_file_name,
        DESTINATION_BUCKET_NAME,
        destination_file_name
    )
