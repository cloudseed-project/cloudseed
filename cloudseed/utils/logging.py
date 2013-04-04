from __future__ import absolute_import
import logging


class Loggable(object):
    def __init__(self, *args, **kwargs):
        name = '%s.%s' % (self.__module__, self.__class__.__name__)
        self.log = logging.getLogger(name)

        super(Loggable, self).__init__(*args, **kwargs)

