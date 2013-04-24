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


def bootstrap_script(script, data, config):

    project = config.data['project']

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
            profiles=data.get('profiles'),
            provider=data.get('provider'),
            extras=data.get('extras'),
            master=master,
            minion=minion)

    if os.path.isabs('{0}.sh'.format(script)):
        # The user provided an absolute path to the deploy script, although no
        # extension was provided. Let's use it anyway.
        return __render_script(
            '{0}.sh'.format(script),
            profiles=data.get('profiles'),
            provider=data.get('provider'),
            extras=data.get('extras'),
            master=master,
            minion=minion)

    for search_path in config.master_script_paths:
        if os.path.isfile(os.path.join(search_path, script)):
            return __render_script(
                os.path.join(search_path, script),
                profiles=data.get('profiles'),
                provider=data.get('provider'),
                extras=data.get('extras'),
                master=master,
                minion=minion)

        if os.path.isfile(os.path.join(search_path, '{0}.sh'.format(script))):
            return __render_script(
                os.path.join(search_path, '{0}.sh'.format(script)),
                profiles=data.get('profiles'),
                provider=data.get('provider'),
                extras=data.get('extras'),
                master=master,
                minion=minion)

    # No deploy script was found, return an empty string
    return ''
