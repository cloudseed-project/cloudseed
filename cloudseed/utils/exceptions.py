from __future__ import absolute_import
import logging
from contextlib import contextmanager
from cloudseed.exceptions import MissingConfigKey

log = logging.getLogger(__name__)


@contextmanager
def config_key_error():
    try:
        yield
    except KeyError as e:
        log.error('{0}: {1}',
            MissingConfigKey.__doc__,
            e.message)
        raise MissingConfigKey(*e.args)
    finally:
        pass
