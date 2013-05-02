from __future__ import absolute_import
import os
import logging
import paramiko
from cloudseed.exceptions import (
    UnknownConfigProvider, MissingIdentity
)

from cloudseed.utils.exceptions import (
    profile_key_error, config_key_error
)


log = logging.getLogger(__name__)


def run(client, command):
    # to get the exit code of the command:
    # chan = client.get_transport().open_session()
    # chan.exec_command(command)
    # print('exit status: %s' % chan.recv_exit_status())

    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read()


def master_client_with_config(config):
    profile = config.profile['master']
    identity = None
    hostname = None
    username = None

    # raises UnknownConfigProvider
    provider = config.provider_for_profile(profile)

    # raises KeyError aka MissingProfileKey
    with profile_key_error():
        username = profile['ssh_username']
        log.debug('SSH Client Username: %s', username)

    # raises KeyError aka MissingConifgKey
    with config_key_error():
        hostname = config.data['master']
        log.debug('SSH Client Hostname: %s', hostname)

    identity = profile.get('ssh_password', provider.ssh_identity())
    log.debug('SSH Client Identity: %s', identity)

    if not identity:
        raise MissingIdentity
#         log.error('No identity specificed.\n\
# Please set ssh_password on the master profile or provide a private_key \
# in your provider for this master')
#         return

    return connect(
        hostname=hostname,
        username=username,
        identity=identity)


def connect(hostname, username, identity):

    if os.path.isabs(identity):
        return client(
            hostname=hostname,
            username=username,
            identity=identity)
    else:
        return client(
            hostname=hostname,
            username=username,
            password=identity)


def client(hostname, identity=None, username=None, password=None, port=22):

    if identity:
        return _client_with_identity(hostname, port, username, identity)
    elif username and password:
        return _client_with_password(hostname, port, username, password)


def _client_with_identity(hostname, port, username, identity):
    log.debug(
        'Initializing SSH Client: ssh -p %s-i %s %s@%s',
        port, identity, username, hostname)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        key_filename=identity,
        timeout=5)
    return client


def _client_with_password(hostname, port, username, password):
    log.debug(
        'Initializing SSH Client\nhostname: %s\nport: %s\nusername: %s\npassword: %s\n',
        hostname, port, username, password)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password,
        timeout=5)

    return client
