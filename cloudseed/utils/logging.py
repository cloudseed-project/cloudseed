from __future__ import absolute_import
import logging


class LogDescriptor(object):

    def __get__(self, instance, owner, *args):
        try:
            return getattr(instance, '_log')
        except AttributeError:
            name = '%s.%s' % (instance.__module__, instance.__class__.__name__)
            log = logging.getLogger(name)
            setattr(instance, '_log', log)
            return log


class Loggable(object):
    log = LogDescriptor()

