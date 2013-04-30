'''
usage:
  cloudseed deploy <state>... [<machine>]

options:
  -h, --help         Show this screen.
  <state>            The state you would like to deploy
  <machine>          Optional machine to deploy the state too

'''
import sys
from docopt import docopt
from cloudseed.utils import ssh
from cloudseed.utils.exceptions import ssh_client_error


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    states = args['<state>']
    machine = args['<machine>']

    # TODO ensure we have a bootstrapped master
    # bail if we don't

    with ssh_client_error():
        ssh_client = ssh.master_client_with_config(config)

    current_env = config.environment

    if current_env:
        sys.stdout.write('Deploying states \'{0}\'\n'.format(', '.join(states)))

        #salt-key --gen-keys=master
        ssh.run(ssh_client, 'cloudseed --profile=/etc/salt/cloudseed/profile --config= ')
        config.provider.deploy(states, machine)
    else:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')


