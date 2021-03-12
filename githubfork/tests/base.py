import os
import httpretty
from github import Github
from unittest import TestCase
from ..githubfork import GithubFork, GithubForkedBranch


class JsonContent:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return owner

        path = os.getcwd()

        with open(f'{path}/githubfork/tests/github_objects/{self.name}.json') as file:
            setattr(instance, self.name, file.read())

        return getattr(instance, self.name)


class MockGithubResponse:
    org = JsonContent('organization')
    user = JsonContent('user')
    repo = JsonContent('repo')
    repo_ref = JsonContent('repo_ref')
    repo_branch = JsonContent('repo_branch')
    repo_pull = JsonContent('repo_pull')
    forks = JsonContent('forks')
    forked_repo = JsonContent('forked_repo')
    forked_repo_ref = JsonContent('forked_repo_ref')
    forked_repo_branch = JsonContent('forked_repo_branch')
    forked_repo_file = JsonContent('forked_repo_file')
    forked_repo_file_content = JsonContent('forked_repo_file_content')


class PyGithubTestCase(TestCase):
    def setUp(self):
        httpretty.enable()
        httpretty.reset()

        base_url = 'https://api.github.com'

        headers = {
            'content-type': 'application/json',
            'X-OAuth-Scopes': 'admin:org, admin:repo_hook, repo, user',
            'X-Accepted-OAuth-Scopes': 'repo'
        }

        fake = MockGithubResponse()

        # Mock GET request to GitHub
        response_mapping = {
            base_url + '/users/dummyUser': fake.user,
            base_url + '/repos/dummyOrg/dummyRepo': fake.repo,
            base_url + '/repos/dummyOrg/dummyRepo/branches/dummyUpstreamBranch': fake.repo_branch,
            base_url + '/repos/dummyOrg/dummyRepo/git/refs/heads/dummyUpstreamBranch': fake.repo_ref,
            base_url + '/repos/dummyOrg/dummyRepo/forks': fake.forks,
            base_url + '/repos/dummyUser/dummyRepo': fake.forked_repo,
            base_url + '/repos/dummyUser/dummyRepo/branches/dummyDownstreamBranch': fake.forked_repo_branch,
            base_url + '/repos/dummyUser/dummyRepo/contents/dummyFile.txt': fake.forked_repo_file_content
        }
        for url, response in response_mapping.items():
            httpretty.register_uri(
                method=httpretty.GET,
                uri=url,
                body=response,
                adding_headers=headers
            )

        # Mock POST requests to GitHub
        request_mapping = {
            base_url + '/repos/dummyOrg/dummyRepo/forks': fake.forked_repo,
            base_url + '/repos/dummyUser/dummyRepo/git/refs': fake.forked_repo_ref,
            base_url + '/repos/dummyOrg/dummyRepo/pulls': fake.repo_pull
        }
        for url, request in request_mapping.items():
            httpretty.register_uri(
                method=httpretty.POST,
                uri=url,
                body=request,
                status=202
            )

        # Mock PUT requests to GitHub
        sent_mapping = {
            base_url + '/repos/dummyUser/dummyRepo/contents/dummyFile.txt': fake.forked_repo_file
        }
        for url, sent in sent_mapping.items():
            httpretty.register_uri(
                method=httpretty.PUT,
                uri=url,
                body=sent,
                status=202
            )

        # Create github connect
        self.gh = Github('dummyToken')

        # Upstream repo
        self.repo = self.gh.get_repo('dummyOrg/dummyRepo')

        # Create fork object
        self.fork_object = GithubFork(github=self.gh, upstream_repo=self.repo)

        # Downstream repo
        self.forked_repo = self.fork_object.get_fork()

        # Create forked branch object
        self.forked_branch_object = GithubForkedBranch(
            repo=self.forked_repo,
            branch='dummyDownstreamRepo',
            upstream_repo=self.repo,
            upstream_branch='dummyUpstreamRepo'
        )

    def tearDown(self):
        httpretty.disable()
