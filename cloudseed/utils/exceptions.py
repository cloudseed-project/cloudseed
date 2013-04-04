from __future__ import absolute_import
import logging
from contextlib import contextmanager
from cloudseed.exceptions import MissingConfigKey

log = logging.getLogger(__name__)


@contextmanager
def config_key_error(send=None):
    try:
        yield
    except KeyError as e:
        log.error('%s: %s',
            MissingConfigKey.__doc__,
            e.message)

        if send:
            raise send(*e.args)

        raise MissingConfigKey(*e.args)