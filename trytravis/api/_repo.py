from ._travis import Resource


class Repository(Resource):
    @property
    def name(self):
        """The name of the Repository on GitHub.
        
        :rtype: str
        """
        return self._get_property('name')

    @property
    def slug(self):
        """The slug (author/name) of the Repository on GitHub.
        
        :rtype: str
        """
        return self._get_property('slug')

    @property
    def description(self):
        """The description of the Repository on GitHub
        
        :rtype: str
        """
        return self._get_property('description')

    @property
    def github_language(self):
        """The language that the Repository is primarily
        written in on GitHub.
        
        :rtype: str
        """
        return self._get_property('github_language')

    @property
    def active(self):
        """If `true` the Repository is currently enabled with Travis CI.
        
        :rtype: bool
        """
        return self._get_property('active')

    @property
    def private(self):
        """If `true` the Repository is private.
        
        :rtype: bool
        """
        return self._get_property('private')

    @property
    def starred(self):
        """If `true` the Repository is starred on Travis CI.
        
        :rtype: bool
        """
        return self._get_property('starred')

    @property
    def owner(self):
        """The Owner of the Repository.
        
        :rtype: trytravis.api.Owner
        """
        from ._owner import User, Organization
        owner_json = self._get_property('owner')
        if owner_json['@type'] == 'user':
            return User(self._travis, owner_json['id'])
        else:
            return Organization(self._travis, owner_json['id'])

    @property
    def current_build(self):
        """The current build for the Repository.
        
        :rtype: trytravis.api.Build
        """
        from ._build import Build
        build_id = self._get_property('current_build', cache_time=5)
        return Build(self._travis, build_id)

    @property
    def default_branch(self):
        """The default branch for the Repository on GitHub.
        
        :rtype: trytravis.api.Branch
        """
        from ._branch import Branch
        branch_id = self._get_property('default_branch')
        return Branch(self._travis, branch_id)

    def activate(self):
        """Activate the Repository on Travis."""
        with self._travis.request('POST', '/repo/%d/activate' % self.id) as r:
            pass  # TODO: Handle errors and invalidate the `active` prop.
            
    def deactivate(self):
        """Deactivate the Repository on Travis."""
        with self._travis.request('POST', '/repo/%d/deactivate' % self.id) as r:
            pass  # TODO: Handle errors and invalidate the `active` prop.

    def star(self):
        """Star the Repository on Travis."""
        with self._travis.request('POST', '/repo/%d/star' % self.id) as r:
            pass  # TODO: Handle errors and invalidate the `starred` prop.
            
    def unstar(self):
        """Unstar the Repository on Travis."""
        with self._travis.request('POST', '/repo/%d/unstar' % self.id) as r:
            pass  # TODO: Handle errors and invalidate the `starred` prop.
