import os
import sys
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, NotFoundError
from github import Github

# Get environment variables
api_key = os.environ.get("OPENROUTER_API_KEY")
pat = os.environ.get("PAT_REPO_B")
repo_name = os.environ.get("TARGET_REPO")
pr_number = int(os.environ.get("TARGET_PR_NUMBER", 0))

# Initialize OpenRouter (OpenAI-compatible) client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",  # OpenRouter endpoint
)
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
    {
        "role": "system",
        "content": "You are a senior software engineer reviewing a pull request. Provide clear, concise code review feedback."
    },
    {
        "role": "user",
        "content": f"Please review this pull request diff:\n\n{diff_text}"
    }
]

# Try AI review
try:
    response = openai.ChatCompletion.create(  # or client.chat.completions.create() if using client
        model="openai/gpt-3.5-turbo",
        messages=messages,
    )
    review_comment = response.choices[0].message.content
    pr.create_issue_comment(f"🤖 **AI Review Summary** (via OpenRouter):\n\n{review_comment}")

except AuthenticationError:
    pr.create_issue_comment("❌ OpenRouter API authentication failed. Please check your API key.")
    sys.exit(1)

except RateLimitError:
    pr.create_issue_comment("⚠️ OpenRouter API rate limit reached. Try again later.")
    sys.exit(1)

except APIError as e:
    pr.create_issue_comment(f"❌ OpenRouter API error: {str(e)}")
    sys.exit(1)

except Exception as e:
    pr.create_issue_comment(f"❌ Unexpected error during AI Review: {str(e)}")
    sys.exit(1)
