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

    master = config.master_config_data(files=['/etc/salt/master'])

    instance_name = instances.instance_name_for_state(state, config)
    instance_id = instance_name.rsplit('-')[-1]
    minion_id = '{0}{1}'.format(state, instance_id)

    pem, pub = salt.gen_keys()

    data['salt']['minion_pub'] = pub
    data['salt']['minion_pem'] = pem
    data['salt']['minion'] = config.minion_config_data({})

    salt.accept_key(master['pki_dir'], pub, minion_id)

    return
    instances.create_instance(
        config=config,
        profile_name=profile_name,
        state=state,
        data=data)
