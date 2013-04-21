import os
import logging

log = logging.getLogger(__name__)


def write_key_for_config(key, provider, config):
    log.debug('Saving key for config')
    data = config.data
    session = config.session

    filename = '{0}_{1}_{2}'.format(
        data['project'],
        session['environment'],
        provider['provider'])

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
