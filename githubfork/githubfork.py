from github import GithubException, UnknownObjectException


class GithubForkSyncError(Exception):
    pass


class GithubFork:
    def __init__(self, github, upstream_repo=None, fork_from=None, fork_from_url=None):
        """Create a fork of a given github repo in the authenticated users account.

        Args:
            github (github.Github): Authenticated PyGithub object to use for Github connections.
            upstream_repo (github.Repository.Repository, optional): PyGithub Repository Object. Defaults to None.
            fork_from (string, optional): Github repository to fork in PyGithub "repo_full" format. Defaults to None.
            fork_from_url (string, optional): [description]. Defaults to None.

        Raises:
            AssertionError: When neither upstream_repo, fork_from or fork_from_url is specified
        """

        if github:
            self.gh = github
        else:
            self.gh = self._create_github_connection()

        if upstream_repo:
            self.upstream_repo = upstream_repo
        elif fork_from:
            self.upstream_repo = self.gh.get_repo(fork_from)
        elif fork_from_url:
            self.upstream_repo = self._get_repo_from_url(fork_from_url)
        else:
            raise AssertionError('Must specify either upstream_repo, fork_from or fork_from_url')

        self.fork = self.upstream_repo.create_fork()

        self.fork_owner = self.fork.owner

    def _create_github_connection(self):
        raise NotImplementedError('You must supply a github connection object')

    def _get_repo_from_url(self, url):
        return self.gh.get_repo('/'.join(url.split('/')[-2:]))

    def get_fork(self):
        """Get the fork that has been created

        Returns:
            github.Repository.Repository: PyGithub object for interacting with the forked repository
        """
        return self.fork

    def _create_ref_from_upstream(self, upstream_ref, downstream_ref):
        # Get sha of upstream ref and create downstream ref
        ur = self.upstream_repo.get_git_ref(ref=upstream_ref)
        self.fork.create_git_ref(ref=downstream_ref, sha=ur.object.sha)

    def create_or_sync_branch_from_upstream(self, upstream_branch, downstream_branch, force=False):
        """Create a branch in fork from upstream branch or sync branch if already exists

        Args:
            upstream_branch (string): The branch in the upstream repository to use as base
            downstream_branch (string): The feature branch to create in the fork
            force (bool): Force sync the branch if it cannot be fast-forwarded

        Returns:
            GithubForkedBranch: A GithubForkedBranch object which can be used to interact with the content on the forked branch

        Raises:
            UnknownObjectException: When ref of upstream could not be found
            GithubForkSyncError: When forked branch could not be created or synced from upstream branch
        """
        try:
            self._create_ref_from_upstream(
                upstream_ref='heads/{}'.format(upstream_branch),
                downstream_ref='refs/heads/{}'.format(downstream_branch)
            )
        except UnknownObjectException as e:
            raise UnknownObjectException(status=e.status, data=e.data)

        except GithubException as e:
            if e.status == 422:
                # The branch already exists. Make sure it's in sync
                if self._sync_branch_with_upstream(
                    upstream_branch=upstream_branch,
                    downstream_branch=downstream_branch,
                    force=force
                ):
                    return GithubForkedBranch(
                        repo=self.fork,
                        branch=downstream_branch,
                        upstream_repo=self.upstream_repo,
                        upstream_branch=upstream_branch
                    )
            else:
                raise GithubForkSyncError(e)
        return GithubForkedBranch(
            repo=self.fork,
            branch=downstream_branch,
            upstream_repo=self.upstream_repo,
            upstream_branch=upstream_branch
        )

    def _sync_branch_with_upstream(self, upstream_branch, downstream_branch, force=False):
        forkbranch = self.fork.get_git_ref(ref='heads/{}'.format(downstream_branch))
        ur = self.upstream_repo.get_git_ref(ref='heads/{}'.format(upstream_branch))
        # Check if we're already synced
        if ur.object.sha == forkbranch.object.sha:
            return True
        try:
            # Try to fast forward or force
            forkbranch.edit(sha=ur.object.sha, force=force)
        except GithubException as e:
            raise GithubForkSyncError(e)
        return True


class GithubForkedBranch:
    def __init__(self, repo, branch, upstream_repo, upstream_branch):
        """Branch in fork from upstream branch

        Args:
            repo (github.Repository.Repository): Repository object of the forked repository
            branch (string): Feature branch in the forked repository to use as head
            upstream_repo (github.Repository.Repository): Repository object of the upstream repository
            upstream_branch (string): Branch in the upstream repository to use as base
        """
        self.repo = repo
        self.owner_login = repo.owner.login
        self.branch = branch
        self.base = upstream_branch
        self.upstream_repo = upstream_repo

    def create_file(self, path, message, content):
        """Creates file using github.Repository.Repository.create_file

        Args:
            path (string): path of file to create
            message (string): commit message
            content (string): content

        Returns:
            {‘content’: ContentFile:, ‘commit’: Commit}: PyGithub file and commit object
        """
        return self.repo.create_file(path=path, message=message, content=content, branch=self.branch)

    def update_content(self, update_file, message, content):
        """Gets the sha of a given file and update it using github.Repository.Repository.update_file

        Args:
            update_file (string): path of file to update content of
            message (string): commit message
            content (string): content

        Returns:
            {‘content’: ContentFile:, ‘commit’: Commit}: PyGithub file and commit object
        """
        # When we update a file we first need to get the sha of the existing file
        sha = self.repo.get_contents(path=update_file, ref=self.branch).sha
        return self.repo.update_file(
            path=update_file,
            message=message,
            content=content,
            sha=sha,
            branch=self.branch
        )

    def create_pull(self, title, body):
        """Create a pull request against the upstream base branch

        Args:
            title (string): Title of pull request
            body (string): Body of pull request

        Returns:
            github.IssuePullRequest.IssuePullRequest: PyGithub pull request object
        """
        return self.upstream_repo.create_pull(
            title=title,
            body=body,
            base=self.base,
            head='{}:{}'.format(self.owner_login, self.branch)
        )
