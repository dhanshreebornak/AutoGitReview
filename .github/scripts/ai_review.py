import os
from github import Github
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
token = os.environ["PAT_REPO_B"]
target_repo = os.environ["TARGET_REPO"]
pr_number = int(os.environ["TARGET_PR_NUMBER"])

gh = Github(token)
repo = gh.get_repo(target_repo)
pr = repo.get_pull(pr_number)
files = pr.get_files()

diff_text = "\n".join([f.patch for f in files if hasattr(f, "patch")])

# Call OpenAI to analyze diff_text
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You're a code reviewer AI."},
        {"role": "user", "content": f"Review this diff:\n{diff_text}"}
    ]
)

# Post comment to the PR
pr.create_issue_comment(f"🤖 AI Review Summary:\n{response['choices'][0]['message']['content']}")
