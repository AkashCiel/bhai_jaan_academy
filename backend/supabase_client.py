import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_BUCKET = "daily-topic-reports"
SUPABASE_PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF")

# Validate environment variables
if not SUPABASE_PROJECT_REF:
    raise ValueError("SUPABASE_PROJECT_REF environment variable is not set")
if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY environment variable is not set")


def upload_html_to_supabase(filename: str, html_content: str) -> str:
    """
    Uploads an HTML file to Supabase Storage using the REST API and returns the public URL.
    Adds robust error logging for debugging.
    """
    url = f"https://{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "text/html; charset=utf-8",
        "x-upsert": "true",
        "Cache-Control": "public, max-age=3600"
    }
    

    try:
        print(f"[Supabase Upload] Uploading to: {url}")
        print(f"[Supabase Upload] Headers: {headers}")
        response = requests.post(url, headers=headers, data=html_content.encode("utf-8"))
        print(f"[Supabase Upload] Response status: {response.status_code}")
        print(f"[Supabase Upload] Response text: {response.text}")
        if not response.ok:
            raise Exception(f"Failed to upload file: {response.text}")
        # Construct the public URL
        public_url = f"https://{SUPABASE_PROJECT_REF}.supabase.co/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"
        print(f"[Supabase Upload] Public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"[Supabase Upload] Exception: {e}")
        raise 