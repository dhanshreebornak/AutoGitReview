import os
from github import Github
from openai import OpenAI

# Get environment variables
openai_api_key = os.environ["OPENAI_API_KEY"]
pat = os.environ["PAT_REPO_B"]
repo_name = os.environ["TARGET_REPO"]
pr_number = int(os.environ["TARGET_PR_NUMBER"])

# Init OpenAI client
client = OpenAI(api_key=openai_api_key)

# Init GitHub client
gh = Github(pat)
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)
files = pr.get_files()

# Collect diff
diff_text = ""
for f in files:
    if hasattr(f, "patch"):
        diff_text += f"### {f.filename}:\n{f.patch}\n\n"

# OpenAI Chat Completion (new format)
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a code reviewer. Analyze the following code changes and provide feedback."
        },
        {
            "role": "user",
            "content": f"Please review the following PR diff:\n\n{diff_text}"
        }
    ]
)

# Get response content
review_comment = response.choices[0].message.content

# Post review as PR comment
pr.create_issue_comment(f"🤖 **AI Review Summary**:\n\n{review_comment}")
