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


class User(Owner):
    @property
    def is_syncing(self):
        """Boolean value for if the User is currently
        syncing their GitHub information.
        
        :rtype: bool
        """
        return self._get_property('is_syncing')
    
    @property
    def synced_at(self):
        """Last time that the User synced their account.
        
        :rtype: datetime.datetime
        """
        timestamp = self._get_property('synced_at')
        return datetime.datetime.strptime('%Y-%m-%dT%H:%M:%SZ')
    
    def sync(self):
        """Syncs the user with the latest information from GitHub."""
        with self._travis.request('POST', '/user/%d/sync' % self.id) as r:
            pass  # TODO: Error handling here.


class Organization(Owner):
    pass
