import os
import openai
from github import Github
from github.PullRequest import PullRequest

openai.api_key = os.getenv("OPENAI_API_KEY")
gh = Github(os.getenv("GITHUB_TOKEN"))

repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("GITHUB_REF").split("/")[-1]
repo = gh.get_repo(repo_name)
pr: PullRequest = repo.get_pull(int(pr_number))

diff = pr.diff_url
files = pr.get_files()
summary = ""

for file in files:
    patch = file.patch or ""
    summary += f"File: {file.filename}\nPatch:\n{patch}\n\n"

# Send to OpenAI
prompt = f"Review the following code diff and provide suggestions:\n\n{summary}"

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a senior software engineer reviewing pull requests."},
        {"role": "user", "content": prompt}
    ]
)

review = response.choices[0].message['content']

# Post comment on PR
pr.create_issue_comment(f"### 🤖 AI Review Summary:\n{review}")
