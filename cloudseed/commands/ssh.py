'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
import logging
from subprocess import call
from cloudseed.exceptions import MissingSessionKey, ProviderError
from cloudseed.utils.exceptions import profile_key_error


log = logging.getLogger(__name__)


def run(config, argv):

    with profile_key_error():
        username = config.profile['bootstrap']['ssh_username']

    try:
        hostname = config.session['bootstrap']
    except KeyError:
        log.error('You must bootstrap a profile before you can ssh')
        raise MissingSessionKey('bootstrap')

    identity = config.provider.ssh_identity()

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

