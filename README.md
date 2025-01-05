# Setup GCP

1. enable the vertex ai and other google cloud services

```bash
gcloud services enable \
    bigquery.googleapis.com \
    aiplatform.googleapis.com \
    dataflow.googleapis.com \
    notebooks.googleapis.com \
    storage.googleapis.com \
    storage-component.googleapis.com \
    storage-api.googleapis.com \
    storage-transfer.googleapis.com \
    compute.googleapis.com \
    dataform.googleapis.com \
    datacatalog.googleapis.com \
    visionai.googleapis.com \
    dataplex.googleapis.com \
    artifactregistry.googleapis.com
```

2. Get json key for corresponding service account
3. Test the vertex ai api using the hello.py file
