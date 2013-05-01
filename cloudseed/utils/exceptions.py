from __future__ import absolute_import
import logging
import paramiko
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
        log.error('%s: %s',
            MissingConfigKey.__doc__,
            e.message)
        raise
    except MissingProfileKey as e:
        log.error('%s: %s',
            MissingProfileKey.__doc__,
            e.message)
        raise
    except MissingIdentity as e:
        log.error('%s: %s',
            MissingIdentity.__doc__,
            e.message)
        raise
    except UnknownConfigProvider as e:
        log.error('%s: %s',
            UnknownConfigProvider.__doc__,
            e.message)
        raise
    except paramiko.AuthenticationException:
        raise

