'''
usage:
  cloudseed sync

options:
  -h, --help         Show this screen.

'''
import sys
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    current_env = config.session.get('environment', None)

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')

    sys.stdout.write('Syncing states for \'{0}\'\n'.format(current_env))


