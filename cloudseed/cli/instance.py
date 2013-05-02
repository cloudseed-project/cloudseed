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
from cloudseed.modules import salt
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

    data = {'salt':{}}

    instance_name = instances.instance_name_for_state(state, config)
    instance_id = instance_name.rsplit('-')[-1]
    minion_id = '{0}{1}'.format(state, instance_id)

    pub, pem = salt.create_key_for_name(minion_id)

    with open(pub, 'r') as f:
        data['salt']['minion_pub'] = f.read()

    with open(pem, 'r') as f:
        data['salt']['minion_pem'] = f.read()

    # data needs to have the following:
    # data.salt.minion_pem <- private key data
    # data.salt.minion_pub <- public key data
    # data.salt.minion <- Minion Conf
    import pdb; pdb.set_trace()
    return
    instances.create_instance(
        config=config,
        profile_name=profile_name,
        state=state,
        data=data)
