class Commit(object):
    """Representation of a Git commit object on GitHub"""

    def __init__(self, sha, ref, message, compare_url, committed_at,
                 committier, author):

        self.sha = sha  # type: str
        self.ref = ref  # type: str
        self.message = message  # type: str
        self.compare_url = compare_url  # type: str
        self.committed_at = committed_at  # type: datetime.datetime
        self.committer = committer  # type: Actor
        self.author = author  # type: Actor


class Actor(object):
    """Git actor helper object with name and avatar_url."""

    def __init__(self, name, avatar_url):
        self.name = name
        self.avatar_url = avatar_url
