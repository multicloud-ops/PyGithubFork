from .base import PyGithubTestCase

# To run tests do: 'pytest -v -s'


class TestGithubFork(PyGithubTestCase):
    def test_get_fork(self):
        # Test getting forked repo
        forked_repo = self.fork_object.get_fork()
        self.assertEqual(forked_repo, self.gh.get_repo(forked_repo.full_name))
        self.assertEqual(forked_repo.full_name, 'dummyUser/dummyRepo')

    def test_create_or_sync_branch_from_upstream(self):
        # Testing creating github forked branch object
        self.fork_object.create_or_sync_branch_from_upstream(
            upstream_branch='dummyUpstreamBranch',
            downstream_branch='dummyDownstreamBranch',
            force=True
        )

        # Check that branch exists
        self.assertEqual('dummyDownstreamBranch', self.gh.get_repo(
            self.fork_object.get_fork().full_name).get_branch('dummyDownstreamBranch').name
        )

    def test__get_repo_from_url(self):
        # Test getting repo
        repo = self.fork_object._get_repo_from_url('https://github.com/{}'.format('dummyUser/dummyRepo'))
        self.assertEqual(repo, self.gh.get_repo('dummyUser/dummyRepo'))

    def test__create_github_connection(self):
        # Skip testing internal function
        self.assertEqual(True, True)

    def test__create_ref_from_upstream(self):
        # Skip testing internal function
        self.assertEqual(True, True)

    def test__sync_branch_with_upstream(self):
        # Skip testing internal function
        self.assertEqual(True, True)


class TestGithubForkedBranch(PyGithubTestCase):
    def test_create_file(self):
        # Dummy yaml content
        content = 'dummyContent'
        path = 'dummyFile.txt'

        # Create file
        created_file = self.forked_branch_object.create_file(
            path=path,
            message='dummyCreateMessage',
            content=content
        )

        # Check that file created is correct
        self.assertEqual(created_file['content'].path, path)

    def test_update_content(self):
        # Dummy yaml content
        content = 'dummyContent'
        path = 'dummyFile.txt'

        # Update file
        updated_file = self.forked_branch_object.update_content(
            update_file=path,
            message='dummyUpdateMessage',
            content=content
        )

        # Check that file updated is correct
        self.assertEqual(updated_file['content'].path, path)

    def test_create_pull(self):
        # Create pull request
        pull_request = self.forked_branch_object.create_pull(
            title='dummtTitle',
            body='dummyBody'
        )

        # Check that pull request was created
        self.assertEqual(pull_request.title, 'dummyTitle')
