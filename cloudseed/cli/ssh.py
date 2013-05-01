'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
import sys
import logging
from cloudseed.modules import ssh


log = logging.getLogger(__name__)


def run(config, argv):

    current_env = config.environment

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return
    else:
        sys.stdout.write('Connecting to environment \'{0}\'\n'\
            .format(current_env))

    ssh.connect_master(config)
