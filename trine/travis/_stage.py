from ._travis import Resource


class Stage(Resource):
    """Representation of a Stage"""

    @property
    def number(self):
        """Incremental number for a Stage

        :rtype: int
        """
        return self._get_property('stage')

    @property
    def name(self):
        """Name of the Stage.

        :rtype: str
        """
        return self._get_property('name')

    @property
    def state(self):
        """Current state of the Stage.

        :rtype: str
        """
        return self._get_property('stage')

    @property
    def started_at(self):
        """When the Stage started.

        :rtype: datetime.datetime
        """
        started_at = self._get_property('started_at')
        if started_at:
            return self._convert_dt(started_at)
        else:
            return None

    @property
    def finished_at(self):
        """When the Stage finished.

        :rtype: datetime.datetime
        """
        finished_at = self._get_property('finished_at')
        if finished_at:
            return self._convert_dt(finished_at)
        else:
            return None

    @property
    def jobs(self):
        """The Jobs of a Stage"""
        
