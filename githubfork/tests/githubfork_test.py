import unittest, os, sys
import yaml
from github import Github
sys.path.append('..')
from githubfork import GithubFork, GithubForkedBranch

# Set GITHUB_TOKEN in env before running tests
# To run tests do: 'pytest -v -s'

# DELETE testing-fork branch created and close pull request after running tests

github_repo = 'eveliososa/testing' # Change github_repo to the upstream repo you want to fork from
github_repo_branch = 'main'
github_fork_repo_branch = 'testing-fork'

class TestGithubFork(unittest.TestCase):
    def setUp(self):
        # Create github connect, change format if using github.ibm
        self.gh = Github(os.getenv('GITHUB_TOKEN'))
        
        # Create fork
        self.fork_object = GithubFork(github=self.gh, fork_from=github_repo)

        # Get two repos
        self.repo = self.gh.get_repo(github_repo)
        self.forked_repo = self.fork_object.get_fork()

        self.forked_branch_object = GithubForkedBranch(
            repo=self.forked_repo,
            branch=github_fork_repo_branch,
            upstream_repo=self.repo,
            upstream_branch=github_repo_branch
        )

    def test_get_fork(self):
        # Test getting forked repo
        forked_repo = self.fork_object.get_fork()
        self.assertEqual(forked_repo, self.gh.get_repo(self.forked_repo.full_name))

    def test_create_branch_from_upstream(self):
        # Testing creating github forked branch object
        forked_branch_object = self.fork_object.create_branch_from_upstream(
            upstream_branch=github_repo_branch,
            downstream_branch=github_fork_repo_branch
        )

        # Check that branch exists
        self.assertEqual(github_fork_repo_branch, self.gh.get_repo(self.forked_repo.full_name).get_branch(github_fork_repo_branch).name)

    def test__get_repo_from_url(self):
        # Test getting repo
        repo = self.fork_object._get_repo_from_url('https://github.com/{}'.format(github_repo))
        self.assertEqual(repo, self.gh.get_repo(github_repo))

    def test__create_github_connection(self):
        self.assertEqual(True, True)

    def test_create_file(self):
        # Dummy yaml content
        parsed_yaml = {'content':'testing'}
        path = 'githubfork_testing.yaml'

        # Create file
        created_file = self.forked_branch_object.create_file(
            path=path,
            message='Testing creating a file.',
            content=yaml.dump(parsed_yaml, sort_keys=False)
        )

        # Get file content
        created_file_github = self.forked_repo.get_contents(path=path, ref=github_fork_repo_branch)
        parsed_yaml_github = yaml.load(created_file_github.decoded_content, Loader=yaml.SafeLoader)

        # Compare they are equal
        self.assertDictEqual(parsed_yaml, parsed_yaml_github)
        self.assertEqual(created_file['content'], created_file_github)

    def test_update_content(self):
        # Dummy yaml content
        parsed_yaml = {'new-content':'new-testing'}
        path = 'githubfork_testing.yaml'

        # Update file
        updated_file = self.forked_branch_object.update_content(
            update_file=path, 
            message='Update testing yaml file', 
            content=yaml.dump(parsed_yaml, sort_keys=False)
        )

        # Get file content
        updated_file_github = self.forked_repo.get_contents(path=path, ref=github_fork_repo_branch)
        parsed_yaml_github = yaml.load(updated_file_github.decoded_content, Loader=yaml.SafeLoader)

        # Compare they are equal
        self.assertDictEqual(parsed_yaml, parsed_yaml_github)
        self.assertEqual(updated_file['content'], updated_file_github)

    def test_create_pull(self):
        # Create pull request
        pull_request = self.forked_branch_object.create_pull(
            title='Testing pull request',
            body='message for testing pull request'
        )

        # Check for pull request
        pull_request_github = self.repo.get_pulls(state='open', sort='created', base=github_repo_branch)[0]

        # Compare that pull request exists
        self.assertEqual(pull_request, pull_request_github)
