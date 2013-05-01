'''
usage:
  cloudseed deploy <state>... [<machine>]

options:
  -h, --help         Show this screen.
  <state>            The state you would like to deploy
  <machine>          Optional machine to deploy the state too

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

    state = args['<state>'][0]
    machine = args['<machine>']
    minion_id = 0

    # TODO ensure we have a bootstrapped master
    # bail if we don't

    with ssh_client_error():
        ssh_client = ssh.master_client_with_config(config)

    current_env = config.environment

    if current_env:
        sys.stdout.write('Deploying states \'{0}\'\n'.format(state))

        cmd_current_items = 'sudo sh -c "salt --out=yaml -G \'roles:{0}\' grains.item id"'\
        .format(state)


        log.debug('Executing: %s', cmd_current_items)

        data = ssh.run(
            ssh_client,
            cmd_current_items)

        # https://github.com/saltstack/salt/issues/4696
        if not data.lower().startswith('no minions matched'):
            obj = yaml.load(data)
            minion_id = len(list(obj.iterkeys()))

        ssh.run(
            ssh_client,
            'sudo sh -c "salt-key --gen-keys-dir=/tmp --gen-keys={0}{1}"'.format(state, minion_id))

        #salt-key --gen-keys=master
        profile_path = '/etc/salt/cloudseed/profile'
        provider_path = '/etc/salt/cloudseed/providers'

        ssh.run(
            ssh_client,
            'cloudseed --profile={0} --provider={1} deploy {2}' \
            .format(profile_path, provider_path, state))

        config.provider.deploy(states, machine)
    else:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')


