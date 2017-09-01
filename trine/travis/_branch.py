from ._travis import Resource


class Branch(Resource):
    """Representation of a GitHub branch that is detected by Travis."""

    @property
    def name(self):
        """The name of the branch

        :rtype: str
        """
        return self._get_property('name')

    @property
    def default_branch(self):
        """If true this branch is the default branch for
        the Repository on GitHub.

        :rtype: bool
        """
        return self._get_property('default_branch')

    @property
    def exists_on_github(self):
        """If true this branch still exists on GitHub.

        :rtype: bool
        """
        return self._get_property('exists_on_github')

    @property
    def repository(self):
        """Returns the Repository that the branch belongs to.

        :rtype: trine.travis.Repository
        """
        repo = self._get_property('repository')
        from ._repo import Repository
        return Repository(repo['id'])

    @property
    def last_build(self):
        """Returns the last Build for the branch if one exists.
        If one doesn't exist return None.

        :rtype: trine.travis.Build
        """
        last_build = self._get_property('last_build')
        if last_build is None:
            return None
        else:
            from ._build import Build
            return Build(last_build['id'])

