import os
import yaml
from stevedore import driver
from cloudseed.exceptions import (
    NoProviderInConfig, ConfigNotFound, UnknownConfigProvider,
    NoProjectInConfig
)


class Config(object):
    def __init__(self,
        local_config,
        project_config=None,
        global_config=None):

        local_data = {}
        project_data = {}
        global_data = {}

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))

        if not global_config:
            global_config = '{0}/config'.format(user_dir)

        try:
            with open(local_config) as cfg:
                local_data = yaml.load(cfg)
        except IOError:
            raise ConfigNotFound

        try:
            provider = local_data['provider']
        except KeyError:
            raise NoProviderInConfig

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

        self.data = {}
        self.data.update(global_data)
        self.data.update(project_data)
        self.data.update(local_data)

        try:
            em = driver.DriverManager(
                'com.cloudseed.providers',
                provider,
                invoke_on_load=True,
                invoke_kwds={'config': self})
        except RuntimeError:
            raise UnknownConfigProvider

        self.__provider = em.driver

    @property
    def provider(self):
        return self.__provider

    @property
    def profile(self):
        return self.__provider


