import os
import logging

LOG = logging.getLogger(__name__)


def add_key_for_config(key, config):
    LOG.debug('Saving key for config')
    data = config.data

    filename = '{0}_{1}_{2}'.format(
        data['project'],
        data['session'],
        data['provider'])

    LOG.debug('Key filename: %s', filename)

    path = '{0}/.cloudseed/{1}/{2}'.format(
        os.path.expanduser('~'),
        data['project'],
        filename)

    LOG.debug('Key path: %s', path)

    with open(path, 'w') as target:
        target.write(key)

    os.chmod(path, 0600)

    return path
