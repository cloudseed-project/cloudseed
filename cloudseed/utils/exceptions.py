from __future__ import absolute_import
import logging
from contextlib import contextmanager
from cloudseed.exceptions import (
    MissingConfigKey, MissingProfileKey, MissingIdentity,
    UnknownConfigProvider
)

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


@contextmanager
def profile_key_error(send=None):
    try:
        yield
    except KeyError as e:
        log.error('%s: %s',
            MissingProfileKey.__doc__,
            e.message)

        if send:
            raise send(*e.args)

        raise MissingProfileKey(*e.args)

@contextmanager
def ssh_client_error():
    try:
        yield
    except MissingConfigKey as e:
        pass
    except MissingProfileKey as e:
        pass
    except MissingIdentity as e:
        pass
    except UnknownConfigProvider as e:
        pass

        log.error('%s: %s',
            MissingProfileKey.__doc__,
            e.message)

        raise RuntimeError
