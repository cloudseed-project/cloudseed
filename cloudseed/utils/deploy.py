'''
These utility functions borrow VERY heavily from salt-cloud:
https://github.com/saltstack/salt-cloud/blob/develop/saltcloud/utils/__init__.py
Credit where credit is due to those guys, nice work.
'''
from __future__ import absolute_import
import os
import logging
from jinja2 import Template
from cloudseed.utils.filesystem import Filesystem

log = logging.getLogger(__name__)


def __render_script(path, **kwargs):
    '''
    Return the rendered script
    '''
    log.debug('Rendering deploy script: {0}'.format(path))

    try:
        with open(path, 'r') as fp_:
            template = Template(fp_.read())
            return str(template.render(**kwargs))
    except AttributeError:
        # Specified renderer was not found
        with open(path, 'r') as fp_:
            return fp_.read()


def _transfer_keys_for_providers(providers):
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


def bootstrap_script(script, config, extras):

    project = config.data['project']
    profiles = config.profile

    providers = _providers_for_config(config)

    transfer_keys_data = _transfer_keys_for_providers(providers)
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
        'master': 'localhost'})

    if os.path.isabs(script):
        # The user provided an absolute path to the deploy script, let's use it
        return __render_script(
            script,
            profiles=profiles_data,
            provider=providers_data,
            transfer_keys=transfer_keys_data,
            extras=extras,
            master=master,
            minion=minion)

    if os.path.isabs('{0}.sh'.format(script)):
        # The user provided an absolute path to the deploy script, although no
        # extension was provided. Let's use it anyway.
        return __render_script(
            '{0}.sh'.format(script),
            profiles=profiles_data,
            provider=providers_data,
            transfer_keys=transfer_keys_data,
            extras=extras,
            master=master,
            minion=minion)

    for search_path in config.master_script_paths:
        if os.path.isfile(os.path.join(search_path, script)):
            return __render_script(
                os.path.join(search_path, script),
                profiles=profiles_data,
                provider=providers_data,
                transfer_keys=transfer_keys_data,
                extras=extras,
                master=master,
                minion=minion)

        if os.path.isfile(os.path.join(search_path, '{0}.sh'.format(script))):
            return __render_script(
                os.path.join(search_path, '{0}.sh'.format(script)),
                profiles=profiles_data,
                provider=providers_data,
                transfer_keys=transfer_keys_data,
                extras=extras,
                master=master,
                minion=minion)

    # No deploy script was found, return an empty string
    return ''
