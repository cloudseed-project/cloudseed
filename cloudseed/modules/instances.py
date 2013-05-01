import os
import logging
import yaml
from cloudseed.utils import ssh
from cloudseed.utils.filesystem import Filesystem


log = logging.getLogger(__name__)


def _ssh_keys_for_providers(providers):
    transfer_keys = []
    for key, value in providers.iteritems():
        if 'private_key' in value:

            key_path = os.path.expanduser(value['private_key'])

            with open(key_path) as f:
                key_data = f.read()

            target_key = '/etc/salt/cloudseed/{0}'\
            .format(os.path.basename(value['private_key']))

            transfer_keys.append('echo "{0}" > {1}; chmod 600 {1}'\
                .format(
                    key_data,
                    target_key))

            value['private_key'] = target_key

    return transfer_keys


def _providers_for_config(config):
    provider_keys = set()
    providers = config.providers
    result = {}

    for key, value in config.profile.iteritems():
        try:
            provider_keys.add(value['provider'])
        except KeyError:
            pass

    for key in provider_keys:
        try:
            data = providers[key].copy()
        except KeyError:
            continue

        result[key] = data

    return result


def _master_data(config):

    project = config.data['project']
    profiles = config.profile
    providers = _providers_for_config(config)

    ssh_keys_data = _ssh_keys_for_providers(providers)
    profiles_data = Filesystem.encode(profiles)
    providers_data = Filesystem.encode(providers)

    master_project_path = os.path.join(
        Filesystem.project_path(project),
        'master')

    master_env_path = os.path.join(
        Filesystem.current_env(),
        'master'
        )

    merged_master = Filesystem.load_file(master_project_path, master_env_path)

    master = Filesystem.encode(merged_master)
    minion = Filesystem.encode(
        {'id': 'master',
        'master': 'localhost',
        'grains': {'roles': ['master']}})

    salt_data = {
    'master': master,
    'minion': minion}

    cloudseed_data = {
    'profiles': profiles_data,
    'providers': providers_data,
    'ssh_keys': ssh_keys_data}

    return {
    'salt': salt_data,
    'cloudseed': cloudseed_data
    }


def create_master(config, data=None):

    if not data:
        data = _master_data(config)

    result = create_instance(
        config=config,
        profile_name='master',
        state='master',
        data=data)

    config.update_config({'master': result})


# def create_master(config):

#     profile = config.profile['master']

#     # raises UnknownConfigProvider
#     provider = config.provider_for_profile(profile)

#     provider_name = profile['provider']
#     provider_config = config.providers[provider_name]

#     before_identity = hash(tuple(provider_config.itervalues()))
#     result = provider.bootstrap(profile, config)
#     after_identity = hash(tuple(provider_config.itervalues()))

#     if before_identity != after_identity:
#         config.update_providers({provider_name: provider_config})

#     config.update_config({'master': result})


def create_instance(config, profile_name, state, data):
    profile = config.profile[profile_name]

    # raises UnknownConfigProvider
    provider = config.provider_for_profile(profile)
    instance_name = instance_name_for_state(state, config)

    return provider.create_instance(
        profile,
        config,
        instance_name,
        data)


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

