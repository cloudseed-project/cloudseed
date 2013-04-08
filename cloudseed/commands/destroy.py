'''
usage:
  cloudseed destroy <environment>
  

options:
  -h, --help            Show this screen.
  <environment>         Destroys a server environment (master and all boxes)

'''
import os
import logging
import sys
from subprocess import call
from docopt import docopt
from cloudseed.utils.filesystem import (Filesystem)

log = logging.getLogger(__name__)


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    env = args['<environment>']

    current_env = config.session.get('environment', None)

    if env:
        if env != current_env:
            config.activate_environment(env)
            current_env = env
        config.provider.kill_all_instances()
    
        
    