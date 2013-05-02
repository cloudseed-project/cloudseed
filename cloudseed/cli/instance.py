'''
usage:
  cloudseed instance --profile-name=<profile_name> --state=<state>

options:
  -h, --help               show this screen.
  <environment>            set the current environment

'''

import sys
from docopt import docopt
from salt.client import LocalClient
from cloudseed.modules import instances
from cloudseed.modules import salt
from cloudseed.utils.filesystem import Filesystem


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    profile_name = args['--profile-name']
    state = args['--state']

    data = {'salt': {}}

    master = config.master_config_data(files=['/etc/salt/master'])

    instance_name = instances.instance_name_for_state(state, config)
    instance_id = instance_name.rsplit('-')[-1]
    minion_id = '{0}{1}'.format(state, instance_id)

    pem, pub = salt.gen_keys()

    client = LocalClient()
    grains = client.cmd('master', 'grains.item', ['fqdn'])

    try:
        master_fqdn = grains['master']['fqdn']
    except KeyError:
        return

    minion_data = {'master': master_fqdn}
    profile = config.profile_for_key(profile_name)
    minion_data.update(profile.get('minion', {}))

    data['salt']['minion_pub'] = pub
    data['salt']['minion_pem'] = pem
    data['salt']['minion'] = Filesystem.encode(
        config.minion_config_data(minion_data))

    salt.accept_key(master['pki_dir'], pub, minion_id)

    instances.create_instance(
        config=config,
        profile_name=profile_name,
        state=state,
        data=data)
