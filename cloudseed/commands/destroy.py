'''
usage:
  cloudseed destroy <environment>


options:
  -h, --help            Show this screen.
  <environment>         Destroys a server environment (master and all boxes)

'''
import sys
import logging
from docopt import docopt

log = logging.getLogger(__name__)


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    env = args['<environment>']

    current_env = config.session.get('environment', None)

    if env:
        if env != current_env:
            config.activate_environment(env)
            current_env = env

        answer = raw_input(
            'Are you sure you want to destroy \'{0}\' [y/N] '\
            .format(current_env))

        if answer.lower() in ('y', 'yes', 'true', 't', '1'):
            sys.stdout.write('Destroying environment \'{0}\'\n'.format(current_env))
            config.provider.kill_all_instances()



