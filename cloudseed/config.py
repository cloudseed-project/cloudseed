import os
import yaml
from stevedore import driver
from cloudseed.exceptions import (
    NoProviderInConfig, ConfigNotFound, UnknownConfigProvider,
    NoProjectInConfig
)


class Config(object):
    def __init__(self, resource, provider=None):

        if not provider:
            try:
                provider_name = resource.data['provider']
            except KeyError:
                raise NoProviderInConfig

            try:
                em = driver.DriverManager(
                    'com.cloudseed.providers',
                    provider_name,
                    invoke_on_load=True,
                    invoke_kwds={'config': self})
                provider = em.driver
            except RuntimeError:
                raise UnknownConfigProvider

        self.__provider = provider
        self.__resource = resource

    @property
    def data(self):
        return self.__resource.data

    @property
    def session(self):
        return self.__resource.session

    @property
    def provider(self):
        return self.__provider


class DictConfig(object):
    def __init__(self, data, session=None):

        if 'project' not in data:
            raise NoProjectInConfig

        self.data = data
        self.session = {} if session is None else session


class FilesystemConfig(object):

    def __init__(self,
        local_config,
        project_config=None,
        global_config=None,
        session_config=None):

        self.data = self.config_for(
            local_config,
            project_config,
            global_config)

        if session_config:
            self.session = self.session_for(session_config)
        else:
            try:
                path = self.session_path(self.data)
                self.session = self.session_for(path)
            except KeyError:
                self.session = {}

    def session_path(self, config):

        session_id = config['session']

        path = '{0}/{1}/session_{2}'.format(
            os.path.expanduser('~'),
            config['project'],
            session_id)

        return path

    def session_for(self, path):
        try:
            with open(path) as f:
                return yaml.load(f)
        except IOError:
            return {}

    def config_for(self, local_config, project_config=None, global_config=None):
        global_data = {}
        project_data = {}
        local_data = {}

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))

        if not global_config:
            global_config = '{0}/config'.format(user_dir)

        try:
            with open(local_config) as cfg:
                local_data = yaml.load(cfg)
        except IOError:
            raise ConfigNotFound

        try:
            project = local_data['project']
        except KeyError:
            raise NoProjectInConfig

        if not project_config:
            project_config = '{0}/{1}/config'.format(user_dir, project)

        try:
            with open(global_config) as cfg:
                global_data = yaml.load(cfg)
        except IOError:
            pass

        try:
            with open(project_config) as cfg:
                project_data = yaml.load(cfg)
        except IOError:
            pass

        data = {}
        data.update(global_data)
        data.update(project_data)
        data.update(local_data)

        return data
