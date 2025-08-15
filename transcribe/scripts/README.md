# Development Scripts

This directory contains utility scripts for development and debugging.

## Scripts

### `create_service_account.py`
**Purpose**: Creates a Google Cloud service account for Speech API access during development.

**Usage**:
```bash
cd scripts
python create_service_account.py
```

**What it does**:
- Creates a new service account named `transcription-service`
- Grants necessary permissions (`roles/speech.admin`, `roles/speech.client`, `roles/storage.objectViewer`)
- Downloads service account key to `credentials/service-account-key.json`
- Updates `.env` file with `GOOGLE_APPLICATION_CREDENTIALS` path

**Requirements**: 
- `gcloud` CLI installed and authenticated
- Project ID: `tahoe-469019`

## Notes

These scripts are for development/debugging only and should not be used in production environments.