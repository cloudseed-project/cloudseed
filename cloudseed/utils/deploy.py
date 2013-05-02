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


def script(script, config, data):

    if os.path.isabs(script):
        # The user provided an absolute path to the deploy script, let's use it
        return __render_script(
            script,
            data=data)

    if os.path.isabs('{0}.sh'.format(script)):
        # The user provided an absolute path to the deploy script, although no
        # extension was provided. Let's use it anyway.
        return __render_script(
            '{0}.sh'.format(script),
            data=data)

    for search_path in config.script_paths:
        if os.path.isfile(os.path.join(search_path, script)):
            return __render_script(
                os.path.join(search_path, script),
                data=data)

        if os.path.isfile(os.path.join(search_path, '{0}.sh'.format(script))):
            return __render_script(
                os.path.join(search_path, '{0}.sh'.format(script)),
                data=data)

    # No deploy script was found, return an empty string
    return ''
