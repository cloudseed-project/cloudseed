import logging
import yaml
from cloudseed.utils import ssh

log = logging.getLogger(__name__)


def create_master(config):

    profile = config.profile['master']

    # raises UnknownConfigProvider
    provider = config.provider_for_profile(profile)

    provider_name = profile['provider']
    provider_config = config.providers[provider_name]

    before_identity = hash(tuple(provider_config.itervalues()))
    result = provider.bootstrap(profile, config)
    after_identity = hash(tuple(provider_config.itervalues()))

    if before_identity != after_identity:
        config.update_providers({provider_name: provider_config})

    config.update_config({'master': result})


def next_id_for_state(state, config):

    try:
        ssh_client = ssh.master_client_with_config(config)
    except:
        return 0

    cmd_current_items = 'sudo sh -c "salt --out=yaml -G \'roles:{0}\' grains.item id"'\
        .format(state)

    log.debug('Executing: %s', cmd_current_items)

    data = ssh.run(
        ssh_client,
        cmd_current_items)

    # https://github.com/saltstack/salt/issues/4696
    if not data.lower().startswith('no minions matched'):
        obj = yaml.load(data)
        return len(list(obj.iterkeys()))

    return 0


def instance_name_for_state(state, config):
    instance_id = next_id_for_state(state, config)
    return 'cloudseed-{0}-{1}'.format(
        config.data['project'].lower(),
        instance_id)

