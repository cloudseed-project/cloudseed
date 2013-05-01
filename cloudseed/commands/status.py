'''
usage: cloudseed status
'''
import sys
import os
from docopt import docopt


def write(value):
    sys.stdout.write('{0}\n'.format(value))


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = config.environment

    write('environment: {0}'.format(env))
    write('master: {0}'\
        .format(config.data.get('master', 'Not Bootstrapped')))




