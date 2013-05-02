'''
usage:
  cloudseed deploy <state>...

options:
  -h, --help         Show this screen.
  <state>            The state you would like to deploy
'''
import sys
import logging
import yaml
from docopt import docopt
from cloudseed.utils import ssh
from cloudseed.utils.exceptions import ssh_client_error


log = logging.getLogger(__name__)


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    states = args['<state>']

    # TODO ensure we have a bootstrapped master
    # bail if we don't

    with ssh_client_error():
        ssh_client = ssh.master_client_with_config(config)

    current_env = config.environment

    if current_env:

        sys.stdout.write('Deploying states \'{0}\'\n'.format(','.join(states)))
        config_path = '/etc/salt/cloudseed/config'
        profile_path = '/etc/salt/cloudseed/profile'
        providers_path = '/etc/salt/cloudseed/providers'

        for state in states:
            if config.profile_for_key(state):
                cmd = 'cloudseed --config={0} --profile={1} --provider={2} instance --profile-name={3} --state={3} &'\
                .format(
                    config_path,
                    profile_path,
                    providers_path,
                    state)

                wrap_cmd = 'sudo sh -c "{0}"'.format(cmd)
                log.debug('Executing: %s', wrap_cmd)

                ssh.run(ssh_client, wrap_cmd)

    else:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')


