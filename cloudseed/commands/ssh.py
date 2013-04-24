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

    current_env = config.environment

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return
    else:
        sys.stdout.write('Connecting to environment \'{0}\'\n'\
            .format(current_env))

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

    sys.stdout.write('Hostname is \'{0}\'\n'\
            .format(hostname))

    call('ssh {0}@{1} -i {2} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o IdentitiesOnly=yes' \
        .format(
            username,
            hostname,
            identity), shell=True)

