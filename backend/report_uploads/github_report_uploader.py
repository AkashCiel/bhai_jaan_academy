import os
import requests
from urllib.parse import quote

GITHUB_API_URL = "https://api.github.com"
REPO_OWNER = "AkashCiel"
REPO_NAME = "bhai_jaan_academy_reports"
BRANCH = "main"
GITHUB_TOKEN = os.getenv("REPORTS_GITHUB_TOKEN")

assert GITHUB_TOKEN, "REPORTS_GITHUB_TOKEN environment variable must be set."

def slugify_topic(value: str) -> str:
    """
    Converts a string to a slug suitable for directory or file names (for topic).
    """
    import re
    value = value.strip()
    value = re.sub(r'[^a-zA-Z0-9\-_ ]', '', value)
    value = re.sub(r'\s+', '_', value)
    return value

def user_dir_from_email(email: str) -> str:
    """
    Extracts the username from the email (before @) and removes all special characters.
    """
    import re
    username = email.split('@')[0]
    username = re.sub(r'[^a-zA-Z0-9]', '', username)
    return username

def get_github_headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

def get_file_sha(path: str) -> str:
    """
    Returns the SHA of a file in the repo if it exists, else None.
    """
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{quote(path)}"
    r = requests.get(url, headers=get_github_headers())
    if r.status_code == 200:
        return r.json().get('sha')
    return None

def upload_report(email: str, topic: str, html_content: str, filename: str = None) -> str:
    """
    Uploads the HTML report to the GitHub repo in the correct directory structure and returns the public URL.
    If filename is provided, use it as the file name (with .html extension).
    """
    user_dir = user_dir_from_email(email)
    topic_slug = slugify_topic(topic)
    dir_path = f"reports/{user_dir}/{topic_slug}"
    if filename:
        file_slug = slugify_topic(filename)
        file_name = f"{file_slug}.html"
    else:
        file_name = f"{topic}.html"
    file_path = f"{dir_path}/{file_name}"
    # Check if file exists to get its SHA (for update vs create)
    sha = get_file_sha(file_path)
    # Prepare commit payload
    import base64
    content_b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
    commit_msg = f"Add report for {email} - {topic}"
    payload = {
        "message": commit_msg,
        "content": content_b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha
    url = f"{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}/contents/{quote(file_path)}"
    r = requests.put(url, headers=get_github_headers(), json=payload)
    if r.status_code not in (200, 201):
        raise Exception(f"Failed to upload report: {r.status_code} {r.text}")
    # Construct the public GitHub Pages URL
    public_url = f"https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}/{dir_path}/{quote(file_name)}"
    return public_url 