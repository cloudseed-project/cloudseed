import os
import yaml
from stevedore import driver
from cloudseed.exceptions import (
    NoProviderInConfig, ConfigNotFound, UnknownConfigProvider
)


class Config(object):
    def __init__(self, path):

        try:
            with open('{}/.cloudseed'\
                .format(os.path.expanduser('~'))) as cfg:
                self.data = yaml.load(cfg)
        except IOError:
            self.data = {}

        import pdb; pdb.set_trace()

        try:
            with open(path) as cfg:
                self.data.update(yaml.load(cfg))
        except IOError:
            raise ConfigNotFound

        try:
            provider = self.data['provider']
        except KeyError:
            raise NoProviderInConfig

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


