#!/usr/bin/env python3
"""
Fetch knowledge files from a private GitHub repository.

All personal documents (about, experience, skills, projects, stories, etc.)
are stored in a PRIVATE GitHub repo to keep them out of the public portfolio.

This script is executed:
  - During the build process on Render (before ingestion)
  - Locally after cloning (one-time setup)

Usage:
  python scripts/fetch_private_knowledge.py

Required environment variables:
  GITHUB_TOKEN            - GitHub personal access token with 'repo' scope
  PRIVATE_KNOWLEDGE_REPO  - Repo in "owner/repo" format (e.g. "swalihkolakkadan/swalih-private-knowledge")
"""
import os
import sys
import base64
import urllib.request
import urllib.error
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# Where knowledge files are stored in this project
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"


def fetch_repo_tree(repo: str, token: str) -> list:
    """Fetch the full file tree from the private GitHub repository."""
    api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "swalih-bot-api",
    }

    request = urllib.request.Request(api_url, headers=headers)
    with urllib.request.urlopen(request) as response:
        tree_data = json.loads(response.read().decode())

    return tree_data.get("tree", [])


def fetch_file_content(repo: str, token: str, file_path: str) -> str:
    """Fetch and decode a single file's content from GitHub."""
    content_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "swalih-bot-api",
    }

    request = urllib.request.Request(content_url, headers=headers)
    with urllib.request.urlopen(request) as response:
        content_data = json.loads(response.read().decode())

    return base64.b64decode(content_data["content"]).decode("utf-8")


def clean_knowledge_dir():
    """
    Remove all existing knowledge files/dirs EXCEPT .gitkeep.
    This ensures a fresh fetch every time (no stale files).
    """
    if not KNOWLEDGE_DIR.exists():
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        return

    for item in KNOWLEDGE_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def fetch_private_knowledge() -> int:
    """
    Fetch all markdown files from the private GitHub repo
    and save them into the knowledge/ directory, preserving structure.

    The private repo structure should mirror what knowledge/ expects:
        personal/
            about.md
        portfolio/
            experience.md
            projects.md
            skills.md
        stories/
            ...

    Returns the number of files fetched.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("PRIVATE_KNOWLEDGE_REPO")

    if not github_token or not repo:
        print("⚠️  GITHUB_TOKEN or PRIVATE_KNOWLEDGE_REPO not set.")
        print("   Skipping private knowledge fetch.")
        print("   Set these env vars to fetch your knowledge base.")
        return 0

    print(f"📥 Fetching knowledge base from private repo: {repo}")

    try:
        # Get full repository tree
        tree = fetch_repo_tree(repo, github_token)

        # Filter for markdown and text files (the knowledge we care about)
        knowledge_files = [
            item
            for item in tree
            if item["type"] == "blob"
            and (item["path"].endswith(".md") or item["path"].endswith(".txt"))
            and not item["path"].startswith(".")  # Skip dotfiles like .gitignore
            and item["path"] != "README.md"  # Skip repo-level README
        ]

        if not knowledge_files:
            print("⚠️  No knowledge files found in private repo.")
            return 0

        # Clean existing knowledge files before fetching fresh
        clean_knowledge_dir()

        files_fetched = 0

        for file_info in knowledge_files:
            file_path = file_info["path"]

            try:
                content = fetch_file_content(repo, github_token, file_path)

                # Write to knowledge directory, preserving repo structure
                target_path = KNOWLEDGE_DIR / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content, encoding="utf-8")

                print(f"  ✅ {file_path}")
                files_fetched += 1

            except urllib.error.HTTPError as e:
                print(f"  ❌ Failed to fetch {file_path}: {e.code} {e.reason}")
            except Exception as e:
                print(f"  ❌ Error fetching {file_path}: {e}")

        print(f"\n📦 Fetched {files_fetched} knowledge file(s) into knowledge/")
        return files_fetched

    except urllib.error.HTTPError as e:
        print(f"❌ GitHub API error: {e.code} - {e.reason}")
        if e.code == 401:
            print("   Check that your GITHUB_TOKEN is valid and has 'repo' scope.")
        elif e.code == 404:
            print(f"   Repository '{repo}' not found or token lacks access.")
        return 0
    except Exception as e:
        print(f"❌ Error fetching private knowledge: {e}")
        return 0


if __name__ == "__main__":
    count = fetch_private_knowledge()
    if count == 0:
        print("\n💡 To set up, create a private GitHub repo with your knowledge files,")
        print("   then set GITHUB_TOKEN and PRIVATE_KNOWLEDGE_REPO in your .env file.")
    sys.exit(0)
