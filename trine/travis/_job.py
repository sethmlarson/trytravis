from ._travis import Resource


class Job(Resource):
    """Representation of a Travis Job"""

    @property
    def number(self):
        """Incremental number for a Repository's Builds.

        :rtype: str
        """
        return self._get_property('number')

    @property
    def state(self):
        """Current state of the job.

        :rtype: str
        """
        return self._get_property('state')

    @property
    def started_at(self):
        """When the Job started.

        :rtype: datetime.datetime
        """
        started_at = self._get_property('started_at')
        if started_at:
            return self._convert_dt(started_at)
        else:
            return None

    @property
    def finished_at(self):
        """When the Job finished.

        :rtype: datetime.datetime
        """
        finished_at = self._get_property('finished_at')
        if finished_at:
            return self._convert_dt(finished_at)
        else:
            return None

    @property
    def build(self):
        """The Build the Job is associated with.

        :rtype: trine.travis.Build
        """
        build = self._get_property('build')
        from ._build import Build
        return Build(self._travis, build['id'])

    @property
    def queue(self):
        """The worker queue this Job was scheduled on.

        :rtype: str
        """
        return self._get_property('queue')

    @property
    def repository(self):
        """The Repository this Job is associated with.

        :rtype: trine.travis.Repository
        """
        repo = self._get_property('repository')
        from ._repo import Repository
        return Repository(self._travis, repo['id'])

    @property
    def owner(self):
        """The User or Organization this Job belongs to.

        :rtype: trine.travis.Owner
        """
        owner = self._get_property('owner')
        if owner['@type'] == 'user':
            from ._owner import User
            return User(self._travis, owner['id'])
        else:
            from ._owner import Organization
            return Organization(self._travis, owner['id'])

    @property
    def stage(self):
        """The Stage that this Job has.

        :rtype: trine.travis.Stage
        """
        stage = self._get_property('stage')
        if stage:
            from ._stage import Stage
            return Stage(self._travis, stage['id'])
        else:
            return None

    def cancel(self):
        """This cancels a currently running job."""
        self._travis.request('POST', '/job/%d/cancel' % self.id)

    def restart(self):
        """This restarts a job that has completed or been canceled."""
        self._travis.request('POST', '/job/%d/restart' % self.id)

    def debug(self):
        """This restarts a job in debug mode, enabling the logged-in user
        to SSH into the build VM. This feature is only available on the
        travis-ci.com domain.
        """
        self._travis.request('POST', '/job/%d/debug' % self.id)

    def _get_standard_rep(self):
        with self._travis.request('GET', '/job/%d' % self.id) as r:
            self._data = r.json()

