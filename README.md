# resolve-issue

Try to resolve a GitHub issue for you. From the issue, modify the local codebase to resolve the issue passed as
parameter.

## Requirements

It uses [Amazon Bedrock](https://aws.amazon.com/bedrock/) to generate the description.
You must have an AWS account and have permissions to invoke models in Amazon Bedrock.
This script uses the model `anthropic.claude-3-sonnet-20240229-v1:0` so you need to have access to this model in your account.

## Getting started
- Download the code: `git clone git@github.com:vincbeck/resolve-issue.git`
- Create virtual environment: `pyenv virtualenv 3.10 resolve-issue`
- Activate the environment: `pyenv activate resolve-issue`
- Install all dependencies: `pip install -r requirements.txt`
- Go the directory containing the local codebase you want to modify
- Run the script from the local codebase: `<path_to_resolve_issue_dir>/resolve-issue.py https://github.com/<respository>/issues/<issue_number>`. 
Example: `../resolve-issue/resolve-issue.py https://github.com/apache/airflow/issues/40307`
