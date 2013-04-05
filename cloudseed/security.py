import os
import logging

log = logging.getLogger(__name__)


def add_key_for_config(key, config):
    log.debug('Saving key for config')
    data = config.data

    filename = '{0}_{1}_{2}'.format(
        data['project'],
        data['session'],
        data['provider'])

    log.debug('Key filename: %s', filename)

    path = '{0}/.cloudseed/{1}/{2}'.format(
        os.path.expanduser('~'),
        data['project'],
        filename)

    log.debug('Key path: %s', path)

    with open(path, 'w') as target:
        target.write(key)

    os.chmod(path, 0600)

    return path
