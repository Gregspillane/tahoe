#!/usr/bin/env python3
"""
Script to create a Google Cloud service account for Speech API access.
This is a development utility to set up proper authentication.
"""

import json
import subprocess
import os
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {cmd}")
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Exception running command: {cmd}")
        print(f"Exception: {e}")
        return None

def main():
    project_id = "tahoe-469019"
    service_account_name = "transcription-service"
    service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
    key_file_path = Path(__file__).parent / "credentials" / "service-account-key.json"
    
    print(f"Creating service account for project: {project_id}")
    
    # Ensure credentials directory exists
    key_file_path.parent.mkdir(exist_ok=True)
    
    # Create service account
    print(f"Creating service account: {service_account_name}")
    cmd = f"gcloud iam service-accounts create {service_account_name} --display-name='Transcription Service' --project={project_id}"
    result = run_command(cmd)
    if result is None:
        print("Failed to create service account")
        return False
    
    # Grant necessary permissions
    print("Granting Cloud Speech permissions...")
    roles = [
        "roles/speech.admin",
        "roles/speech.client", 
        "roles/storage.objectViewer"  # For S3-like access if needed
    ]
    
    for role in roles:
        cmd = f"gcloud projects add-iam-policy-binding {project_id} --member='serviceAccount:{service_account_email}' --role='{role}'"
        result = run_command(cmd)
        if result is None:
            print(f"Failed to grant role: {role}")
            return False
        print(f"Granted role: {role}")
    
    # Create and download key file
    print(f"Creating key file: {key_file_path}")
    cmd = f"gcloud iam service-accounts keys create {key_file_path} --iam-account={service_account_email} --project={project_id}"
    result = run_command(cmd)
    if result is None:
        print("Failed to create key file")
        return False
    
    print(f"Service account key created successfully: {key_file_path}")
    
    # Update .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("Updating .env file...")
        
        # Read current .env
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Update or add GOOGLE_APPLICATION_CREDENTIALS
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                lines[i] = f'GOOGLE_APPLICATION_CREDENTIALS={key_file_path}\n'
                updated = True
                break
        
        if not updated:
            lines.append(f'GOOGLE_APPLICATION_CREDENTIALS={key_file_path}\n')
        
        # Write updated .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print("Updated .env file with service account credentials path")
    
    print("\n✅ Service account setup complete!")
    print(f"📁 Key file: {key_file_path}")
    print(f"📧 Service account: {service_account_email}")
    print("\nNext steps:")
    print("1. Restart your application to use the new credentials")
    print("2. The application will now use service account authentication")
    
    return True

if __name__ == "__main__":
    main()