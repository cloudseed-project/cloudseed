'''
usage:
  cloudseed bootstrap [<environment>]

options:
  -h, --help               Show this screen.
  <environment>            The profile name in your .cloudseed/ folder to load

'''
import sys
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = args['<environment>']
    current_env = config.session.get('environment', None)

    if env:
        if env != current_env:
            config.activate_environment(env)
            current_env = env

    if current_env:
        sys.stdout.write('Bootstrapping \'{0}\'\n'.format(current_env))
        sys.stdout.write('This may take a minute, please wait...\n')
        config.provider.bootstrap()
    else:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
