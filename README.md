# PyGithubFork

Wraps [PyGithub](https://github.com/PyGithub/PyGithub) to simplify workflows dealing with forks.


## Example usage

```python
from github import Github
from githubfork.githubfork import GithubFork

ghtoken='your token'
GITHUB_BASE_URL='base_url_for_your_github (i.e. https://github.com/api/v3)'

# Create a normal Github object to store auth info and handle communication
g = Github(base_url=GITHUB_BASE_URL, login_or_token=ghtoken, retry=5)


# Create a fork repo from a given repository
forked_repo = GithubFork(github=g, fork_from='multicloud-ops/somerepo')

# Create a feature branch off a upstream bramch
forked_branch = forked_repo.create_branch_from_upstream(
    upstream_branch='master'
    downstream_branch='myrandomfix'
)

# Update some content on the forks feature branch
forked_branch.update_content(
    update_file='some/file',
    message='Automatically updated this file yall',
    content='some random content'
)

# Create a pull request against the upstream branch
forked_branch.create_pull(
    title='Some automated PR',
    body='This is automated. Just approve'
)
```
