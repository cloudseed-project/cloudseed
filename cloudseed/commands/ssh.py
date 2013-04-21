'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
import sys
import logging
from subprocess import call
from cloudseed.exceptions import ProviderError
from cloudseed.exceptions import UnknownConfigProvider
from cloudseed.utils.exceptions import (
    profile_key_error, config_key_error
)


log = logging.getLogger(__name__)


def run(config, argv):

    profile = config.profile['master']

    try:
        provider = config.provider_for_profile(profile)
    except UnknownConfigProvider as e:
        sys.stdout.write(
            'Unknown config provider \'{0}\', unable to continue.\n'\
            .format(e.message))
        return

    with profile_key_error():
        username = profile['ssh_username']

    with config_key_error():
        hostname = config.data['master']

    identity = provider.ssh_identity()

    if not identity:
        log.error('Unable to ssh. Provider {0} failed to provide ssh identity'\
            .format(config.data['provider']))
        raise ProviderError

    log.debug('Opening SSH to %s@%s using identity %s',
        username, hostname, identity)

    call('ssh {0}@{1} -i {2} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes' \
        .format(
            username,
            hostname,
            identity), shell=True)

