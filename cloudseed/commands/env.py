'''
usage:
  cloudseed env [<environment>]

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

    active_env = config.environment
    env = args['<environment>']
    if not env:
        local_path = os.path.join(Filesystem.local_path())
        dirs = (x for x in next(os.walk(local_path))[1] if x != 'current')
        for d in dirs:
            if active_env == d:
                sys.stdout.write('* {0}\n'.format(d))
            else:
                sys.stdout.write('  {0}\n'.format(d))
        return


    env_path = Filesystem.local_env_path(env)

    if env == active_env:
        sys.stdout.write('Already on \'{0}\'\n'.format(env))
    elif os.path.isdir(env_path):
        config.activate_environment(env)
        sys.stdout.write('Switched to environment \'{0}\'\n'.format(env))
    else:
        sys.stdout.write('Environment \'{0}\' does not exist\n'.format(env))

