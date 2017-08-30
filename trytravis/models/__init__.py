__all__ = ['Travis', 'Resource', 'Paginator',
           'Owner', 'Organization', 'User',
           'ResourceNotFound', 'APIError']


class ResourceNotFound(LookupError):
    pass


class APIError(Exception):
    pass


from ._travis import Travis, Resource, Paginator
from ._owner import Owner, Organization, User
