import sys
import os
import paramiko
from cloudseed.exceptions import (
    UnknownConfigProvider, MissingIdentity
)

from cloudseed.utils.exceptions import (
    profile_key_error, config_key_error
)



def run(client, command):
    client.exec_command(command)


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

    # raises KeyError aka MissingConifgKey
    with config_key_error():
        hostname = config.data['master']

    identity = profile.get('ssh_password', provider.ssh_identity())

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


def client(hostname, identity=None, username=None, password=None, port=22):

    if identity:
        return _client_with_identity(hostname, port, username, identity)
    elif username and password:
        return _client_with_password(hostname, port, username, password)


def _client_with_identity(hostname, port, username, identity):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        key_filename=identity)
    return client


def _client_with_password(hostname, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password)

    return client
