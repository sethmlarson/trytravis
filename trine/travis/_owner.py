import datetime
from ._travis import Resource


class Owner(Resource):
    @property
    def login(self):
        """Login name for the User or Organization.
        
        :rtype: str
        """
        return self._get_property('login')

    @property
    def name(self):
        """Display name for the User or Organization.
        
        :rtype: str
        """
        return self._get_property('name')

    @property
    def avatar_url(self):
        """URL for the avatar of the User or Organization.
        
        :rtype: str
        """
        return self._get_property('avatar_url')

    @property
    def github_id(self):
        """GitHub ID for the User or Organization
        
        :rtype: int
        """
        return self._get_property('github_id')

    @property
    def repositories(self):
        """A list of trent.models.Repository objects
        belonging to the Owner."""
        repos = []
        if 'repo_ids' in self._data:
            repo_ids = self._data['repo_ids']
        else:
            repo_ids = []

            def convert_func(data):
                return [repo['id'] for repo in data['repositories']]

            for repo_id in self._travis.request_paginated('/owner/%s/repos' % self.login, convert_func):
                repo_ids.append(repo_id)
        self._data['repo_ids'] = repo_ids

        from ._repo import Repository
        for repo_id in repo_ids:
            repos.append(Repository(self._travis, repo_id))
        return repos


class User(Owner):
    @property
    def is_syncing(self):
        """Boolean value for if the User is currently
        syncing their GitHub information.
        
        :rtype: bool
        """
        return self._get_property('is_syncing', cache_time=2)
    
    @property
    def synced_at(self):
        """Last time that the User synced their account.
        
        :rtype: datetime.datetime
        """
        timestamp = self._get_property('synced_at')
        return datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
    
    def sync(self):
        """Syncs the user with the latest information from GitHub."""
        with self._travis.request('POST', '/user/%d/sync' % self.id) as r:
            pass  # TODO: Error handling here.

    def _get_standard_rep(self):
        with self._travis.request('GET', '/user/%d' % self.id) as r:
            self._data = r.json()


class Organization(Owner):
    def _get_standard_rep(self):
        with self._travis.request('GET', '/orgs/%d' % self.id) as r:
            self._data = r.json()
