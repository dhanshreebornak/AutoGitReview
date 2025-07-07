import os
import sys
from openai import OpenAI, APIError, RateLimitError, AuthenticationError, NotFoundError
from github import Github

# Log: Starting script
print("🚀 Starting AI PR Review Script...")

# Get environment variables
api_key = os.environ.get("OPENROUTER_API_KEY")
pat = os.environ.get("PAT_REPO_B")
repo_name = os.environ.get("TARGET_REPO")
pr_number = int(os.environ.get("TARGET_PR_NUMBER", 0))

print(f"🔐 Environment loaded:")
print(f"  - TARGET_REPO: {repo_name}")
print(f"  - TARGET_PR_NUMBER: {pr_number}")
print(f"  - API key present: {'✅' if api_key else '❌'}")
print(f"  - PAT_REPO_B present: {'✅' if pat else '❌'}")

# Initialize OpenRouter (OpenAI-compatible) client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",  # OpenRouter endpoint
)

# Initialize GitHub client
print("🔧 Connecting to GitHub...")
gh = Github(pat)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
files = pr.get_files()
print(f"📦 Fetched PR #{pr_number} files...")

# Collect diff from PR
diff_text = ""
for f in files:
    if hasattr(f, "patch") and f.patch:
        diff_text += f"### {f.filename}:\n{f.patch}\n\n"

print(f"🧠 Total diff characters: {len(diff_text)}")

MAX_CHARS = 6000
if len(diff_text) > MAX_CHARS:
    print(f"⚠️ Diff text too long ({len(diff_text)} chars). Truncating to {MAX_CHARS} chars.")
    diff_text = diff_text[:MAX_CHARS]
else:
    print(f"✅ Diff text within limit: {len(diff_text)} chars.")
    

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
    print("🤖 Calling OpenRouter ChatCompletion...")
    response = client.chat.completions.create(
    model="mistralai/mixtral-8x7b-32768",
    messages=messages,
    max_tokens=1000,
        )
    review_comment = response.choices[0].message.content
    print("✅ Received AI response. Posting comment to PR...")
    pr.create_issue_comment(f"🤖 **AI Review Summary** (via OpenRouter):\n\n{review_comment}")
    print("✅ Review comment posted successfully.")

except AuthenticationError as e:
    print(f"[AUTH ERROR] {e}")
    pr.create_issue_comment("❌ OpenRouter API authentication failed. Please check your API key.")
    sys.exit(1)

except RateLimitError as e:
    print(f"[RATE LIMIT ERROR] {e}")
    pr.create_issue_comment("⚠️ OpenRouter API rate limit reached. Try again later.")
    sys.exit(1)

except APIError as e:
    print(f"[API ERROR] {e}")
    pr.create_issue_comment(f"❌ OpenRouter API error: {str(e)}")
    sys.exit(1)

except Exception as e:
    print(f"[UNHANDLED ERROR] {e}")
    pr.create_issue_comment(f"❌ Unexpected error during AI Review: {str(e)}")
    sys.exit(1)
