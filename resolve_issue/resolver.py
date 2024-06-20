import json
import re
import subprocess
from tempfile import NamedTemporaryFile

import boto3
from github import Github
from github.Issue import Issue


def get_issue(issue_url: str) -> (str, str, Issue):
    """
    Return the issue information.

    :param issue_url: The Github issue URL
    """
    match = re.match(r"https://github\.com/(.+?)/(.+?)/issues/([0-9]+)", issue_url, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"The URL specified {issue_url!r} is not valid. The URL must be a Github issue URL.")

    owner = match.group(1)
    repo = match.group(2)
    issue_number = match.group(3)

    print(f"Fetching data from issue #{issue_number} from {owner}/{repo}")

    gh_client = Github()
    repository = gh_client.get_repo(f"{owner}/{repo}")
    return owner, repo, repository.get_issue(int(issue_number))


def get_code_diff(issue: Issue, owner: str, repo: str):
    """
    Ask Bedrock to generate a code diff to resolve a particular issue
    :param issue: The issue object
    :param owner: Owner
    :param repo: Repository name
    """
    print("Asking Bedrock to resolve the issue")
    print(_generate_prompt(issue, owner, repo))
    client = boto3.client('bedrock-runtime')
    body = {
        "messages": [
            {
                "role": "user",
                "content": _generate_prompt(issue, owner, repo),
            }
        ],
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
    }
    response = client.invoke_model(
        body=str.encode(json.dumps(body)),
        modelId="anthropic.claude-3-sonnet-20240229-v1:0"
    )
    body_json = json.loads(response['body'].read().decode('utf-8'))
    response = body_json["content"][0]["text"]

    match = re.search(r"<code_diff>(.*?)</code_diff>", response, flags=re.S)
    if not match:
        raise RuntimeError(f"Impossible to generate a code diff for this issue. response={response}")

    return match.group(1)


def apply_code_diff(code_diff: str):
    with NamedTemporaryFile() as local_tmp_file:
        print(code_diff)
        local_tmp_file.write(bytes(code_diff, "utf-8"))

        command = ["git", "apply", local_tmp_file.name]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()

        if process.returncode != 0:
            print(process.returncode)
            raise RuntimeError("Failed to apply the code diff locally")

        print("Code has been modified to address the issue. Please check it!")


def _generate_prompt(issue: Issue, owner: str, repo: str) -> str:
    """
    Generate the prompt to be given to the LLM agent in order to generate the code change
    :param issue: Issue object
    :param owner: The owner of the repo
    :param repo: The repository name
    """
    title = issue.title
    body = issue.body

    return (f"Generate a code diff to resolve the issue below related to the project {owner} {repo}. "
            f"This code diff should be applicable on current Airflow codebase through the command `git apply`. "
            f"The current Airflow codebase is available here https://github.com/apache/airflow. "
            f"Do not generate a code diff on an outdated codebase! "
            f"Add also comments in the code to explain the changes. "
            f"Return the code diff in <code_diff></code_diff> XML tags.\n\n"
            f"Title of the issue: {title}\n"
            f"Description of the issue: {body}")
