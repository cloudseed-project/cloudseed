'''
usage: cloudseed status
'''
import sys
from docopt import docopt


def write(value):
    sys.stdout.write('{0}\n'.format(value))


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = config.session['environment']

    write('Current Environment: {0}'.format(env))
    write('Master available at: {0}'\
        .format(config.data.get('master', 'Not Bootstrapped')))




