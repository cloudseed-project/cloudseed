'''
usage:
  cloudseed env <environment>

options:
  -h, --help               show this screen.
  <environment>            set the current environment

'''
import os
import sys
from docopt import docopt
from cloudseed.utils.filesystem import Filesystem


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = args['<environment>']
    current_env = config.session.get('environment', None)
    env_path = Filesystem.local_env_path(env)

    if env == current_env:
        sys.stdout.write('Already on \'{0}\'\n'.format(env))
    elif os.path.isdir(env_path):
        config.update_session({'environment': env})
        sys.stdout.write('Switched to environment \'{0}\'\n'.format(env))
    else:
        sys.stdout.write('Environment \'{0}\' does not exist\n'.format(env))

