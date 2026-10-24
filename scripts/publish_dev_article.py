"""Publishes CalmQueue submission article to DEV.to using the official Forem API."""

import os
import sys
import json
import re
import urllib.request
import urllib.error

ARTICLE_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "dev_article_submission.md")

def parse_markdown_submission(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter if present
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        raise ValueError("Could not parse YAML frontmatter from article")

    frontmatter = match.group(1)
    body = match.group(2).strip()

    title = "CalmQueue: The Sloth-Speed AI That Turns 28 Daily Notifications Into 3 Quiet Actions"
    title_match = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()

    tags = ["devchallenge", "hf26challenge", "opensource", "ai"]
    tags_match = re.search(r"^tags:\s*(.+)$", frontmatter, re.MULTILINE)
    if tags_match:
        raw_tags = tags_match.group(1).split(",")
        tags = [t.strip().lstrip("#") for t in raw_tags if t.strip()]

    return title, body, tags

def publish_to_dev(api_key: str):
    if not api_key or not api_key.strip():
        print("ERROR: DEV API key is missing or empty.", file=sys.stderr)
        sys.exit(1)

    api_key = api_key.strip()
    title, body, tags = parse_markdown_submission(ARTICLE_PATH)

    # First, verify user authentication and check existing articles to avoid duplicates
    user_req = urllib.request.Request(
        "https://dev.to/api/users/me",
        headers={
            "api-key": api_key,
            "User-Agent": "CalmQueue-Submitter/1.0"
        }
    )
    try:
        with urllib.request.urlopen(user_req, timeout=10) as resp:
            user_data = json.loads(resp.read().decode())
            username = user_data.get("username", "Unknown")
            name = user_data.get("name", "Unknown")
            print(f"Authenticated as DEV user: @{username} ({name})")
    except urllib.error.HTTPError as e:
        print(f"ERROR: DEV API authentication failed (HTTP {e.code}): {e.reason}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Check user's articles to see if already published
    articles_req = urllib.request.Request(
        "https://dev.to/api/articles/me/all",
        headers={
            "api-key": api_key,
            "User-Agent": "CalmQueue-Submitter/1.0"
        }
    )
    try:
        with urllib.request.urlopen(articles_req, timeout=10) as resp:
            existing = json.loads(resp.read().decode())
            for art in existing:
                if "CalmQueue" in art.get("title", ""):
                    print(f"Article already exists! URL: {art.get('url')}")
                    print(f"Status: Published = {art.get('published')}")
                    print(f"ID: {art.get('id')}")

                    status_file = os.path.join(os.path.dirname(__file__), "..", "docs", "dev_submission_status.json")
                    with open(status_file, "w", encoding="utf-8") as sf:
                        json.dump({
                            "published": art.get("published", True),
                            "url": art.get("url"),
                            "id": art.get("id"),
                            "title": art.get("title"),
                            "created_at": art.get("published_at")
                        }, sf, indent=2)

                    return art.get("url")
    except Exception as e:
        print(f"Warning: Could not fetch existing articles: {e}")

    # Prepare publication payload
    payload = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": body,
            "tags": tags[:4],  # DEV allows maximum 4 tags
            "series": None
        }
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    publish_req = urllib.request.Request(
        "https://dev.to/api/articles",
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
            "User-Agent": "CalmQueue-Submitter/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(publish_req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            article_url = result.get("url")
            print(f"SUCCESS: Article published successfully!")
            print(f"PUBLIC ARTICLE URL: {article_url}")
            print(f"ARTICLE ID: {result.get('id')}")

            # Save public status metadata locally for verification (no secrets saved)
            status_file = os.path.join(os.path.dirname(__file__), "..", "docs", "dev_submission_status.json")
            with open(status_file, "w", encoding="utf-8") as sf:
                json.dump({
                    "published": True,
                    "url": article_url,
                    "id": result.get("id"),
                    "title": result.get("title", title),
                    "created_at": result.get("created_at")
                }, sf, indent=2)

            return article_url
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode()
        print(f"ERROR: Failed to publish article (HTTP {e.code}): {err_msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error during publication: {e}", file=sys.stderr)
        sys.exit(1)

def get_secure_api_key() -> str:
    """Retrieves DEV API key securely using environment variable or getpass.
    Never accepts credentials via command-line arguments to prevent process-table leaks.
    """
    # 0. Check secure environment variable
    env_key = os.environ.get("DEVTO_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 1. Attempt getpass.getpass() in terminal (input is hidden, no echo)
    try:
        import getpass
        print("=" * 60)
        print("CALMQUEUE - DEV.TO COMPETITION SUBMISSION PUBLISHER")
        print("=" * 60)
        print("Please enter your fresh DEV.to API Key below (input is hidden):")
        key = getpass.getpass(prompt="DEV API Key: ")
        if key and key.strip():
            return key.strip()
    except Exception as e:
        pass

    # 4. Fallback to native Tkinter masked dialog if terminal input is non-interactive
    try:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        key = simpledialog.askstring(
            title="DEV.to API Key",
            prompt="Enter your DEV.to API Key for Hacktoberfest Week 3 submission:\n(Input is hidden and never logged)",
            show="*"
        )
        root.destroy()
        if key and key.strip():
            return key.strip()
    except Exception as e:
        pass

    print("ERROR: No DEV API key was entered.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    key = get_secure_api_key()
    publish_to_dev(key)
