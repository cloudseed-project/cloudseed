'''
usage:
  cloudseed bootstrap [<environment>]

options:
  -h, --help               Show this screen.
  <environment>            The profile name in your .cloudseed/ folder to load

'''
import sys
from docopt import docopt
from cloudseed.exceptions import UnknownConfigProvider
from cloudseed.modules import instances


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = args['<environment>']
    current_env = config.environment

    if env:
        if env != current_env:
            config.activate_environment(env)
            current_env = env

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return

    sys.stdout.write('Bootstrapping \'{0}\'\n'.format(current_env))
    sys.stdout.write('This may take a minute, please wait...\n')

    instances.create_master(config)
