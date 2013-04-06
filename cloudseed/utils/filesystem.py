from __future__ import absolute_import
import os
import logging
import yaml


log = logging.getLogger(__name__)


def write_key_for_config(key, config):
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


class YAMLReader(object):
    log = logging.getLogger(__name__)

    @staticmethod
    def load_file(*args):
        data = {}

        for path in args:
            try:
                log.debug('Loading file %s', path)

                with open(path) as f:
                    try:
                        data.update(yaml.load(f))
                    except Exception as e:
                        log.warning(
                            'Unable to merge data from file %s: %s',
                            path, e.message)
            except IOError:
                log.warning('Failed to load file %s', path)

        return data


class YAMLWriter(object):
    log = logging.getLogger(__name__)

    @staticmethod
    def write_file(path, data):
        log.debug('Writing file to %s with %s', path, data)

        try:
            with open(path, 'w') as f:
                f.write(yaml.dump(data, default_flow_style=False))
        except IOError:
            log.error('Failed writing file %s with %s', path, data)
            raise


class Filesystem(YAMLReader, YAMLWriter):

    @staticmethod
    def user_path():
        return os.path.join(os.path.expanduser('~'), '.cloudseed')

    @staticmethod
    def local_path():
        return os.path.join(os.getcwd(), '.cloudseed')

    @staticmethod
    def local_env_path(env):
        return os.path.join(Filesystem.local_path(), env)

    @staticmethod
    def project_path(project):
        return os.path.join(
            Filesystem.user_path(),
            project)

    @staticmethod
    def project_env_path(project, env):
        return os.path.join(
            Filesystem.project_path(project),
            env)
