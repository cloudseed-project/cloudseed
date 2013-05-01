'''
usage:
  cloudseed instance --profile-name=<profile_name> --salt-config=<salt-config>

options:
  -h, --help               show this screen.
  <environment>            set the current environment

'''

import sys
import os
import yaml
from docopt import docopt
from cloudseed.utils.filesystem import YAMLReader

def run(config, argv):
    args = docopt(__doc__, argv=argv)
    print(args)
    current_env = config.environment
    profile_name = args['--profile-name']
    salt_config_path = args['--salt-config']

    if not os.path.isfile(salt_config_path):
        sys.stdout.write('No config found at {0}.\n'.format(salt_config_path))
        return

    salt_config = YAMLReader.load_file(salt_config_path)

    import pdb; pdb.set_trace()


    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return
