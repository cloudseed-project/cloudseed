'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
import logging
from subprocess import call
from cloudseed.utils.exceptions import (
    profile_key_error, config_key_error
)


log = logging.getLogger(__name__)


def connect_master(config):

    profile = config.profile['master']

    # raises UnknownConfigProvider
    provider = config.provider_for_profile(profile)

    with profile_key_error():
        username = profile['ssh_username']

    with config_key_error():
        hostname = config.data['master']

    identity = provider.ssh_identity()

    log.debug('Opening SSH to %s@%s using identity %s',
        username, hostname, identity)

    call('ssh {0}@{1} -i {2} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes' \
        .format(
            username,
            hostname,
            identity), shell=True)
