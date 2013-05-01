'''
usage:
  cloudseed instance --profile-name=<profile_name> --state=<state>

options:
  -h, --help               show this screen.
  <environment>            set the current environment

'''

import sys
import os
import yaml
from docopt import docopt
from cloudseed.modules import instances
from cloudseed.utils.filesystem import YAMLReader
from cloudseed.utils.filesystem import Filesystem


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    current_env = config.environment
    profile_name = args['--profile-name']
    state = args['--state']

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return

    data = {}

    instances.create_instance(
        config=config,
        profile_name=profile_name,
        state=state,
        data=data)
