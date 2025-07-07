import os
import sys
import openai
from github import Github

# Get environment variables
api_key = os.environ.get("OPENROUTER_API_KEY")
pat = os.environ.get("PAT_REPO_B")
repo_name = os.environ.get("TARGET_REPO")
pr_number = int(os.environ.get("TARGET_PR_NUMBER", 0))

# Configure OpenRouter (OpenAI-compatible)
openai.api_key = api_key
openai.base_url = "https://openrouter.ai/api/v1"

# Initialize GitHub client
gh = Github(pat)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
files = pr.get_files()

# Collect diff from PR
diff_text = ""
for f in files:
    if hasattr(f, "patch") and f.patch:
        diff_text += f"### {f.filename}:\n{f.patch}\n\n"

# Prepare messages for review
messages = [
    {"role": "system", "content": "You are a senior software engineer reviewing a pull request. Provide clear, concise code review feedback."},
    {"role": "user", "content": f"Please review this pull request diff:\n\n{diff_text}"}
]

# Try AI review
try:
    response = openai.ChatCompletion.create(
        model="openai/gpt-3.5-turbo",  # You can use other OpenRouter models like mistralai/mixtral-8x7b
        messages=messages,
    )
       review_comment = response.choices[0].message.content
    pr.create_issue_comment(f"🤖 **AI Review Summary** (via OpenRouter):\n\n{review_comment}")
