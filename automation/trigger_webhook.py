import os
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load env variables from root directory .env
BASE_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

PAYLOAD_PATH = Path(__file__).parent / "sample_rfq_payload.json"

def trigger_webhook():
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        print("Error: WEBHOOK_URL not found in environment variables or .env file.")
        return

    if not PAYLOAD_PATH.exists():
        print(f"Error: Sample payload file not found at {PAYLOAD_PATH}")
        return

    # Read JSON payload
    with open(PAYLOAD_PATH, "r", encoding="utf-8") as f:
        try:
            payload = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Failed to parse JSON payload. {e}")
            return

    print(f"Sending RFQ payload to webhook: {webhook_url} ...")
    
    # Send POST request
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        # Check HTTP status (Make.com normally returns 200, or "Accepted" text)
        if 200 <= response.status_code < 300:
            print("Success! Webhook triggered successfully.")
            print(f"HTTP Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
        else:
            print(f"Error: Webhook responded with status code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to webhook. {e}")

if __name__ == "__main__":
    trigger_webhook()
