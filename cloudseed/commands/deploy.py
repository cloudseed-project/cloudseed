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


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    # TODO ensure we have a bootstrapped master
    # bail if we don't

    states = args['<state>']
    machine = args['<machine>']

    current_env = config.session.get('environment', None)

    if current_env:
        sys.stdout.write('Deploying states \'{0}\'\n'.format(', '.join(states)))
        config.provider.deploy(states, machine)
    else:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
