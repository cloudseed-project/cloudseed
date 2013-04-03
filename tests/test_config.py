import os
from unittest import TestCase
from mock import MagicMock
from cloudseed.config import Config

from cloudseed.exceptions import (
    NoProviderInConfig, ConfigNotFound, UnknownConfigProvider,
    NoProjectInConfig
)


class TestConfig(TestCase):

    def setUp(self):
        base_path = '{0}/tests/resources'.format(os.getcwd())
        self.config_local = '{0}/config_local.yaml'.format(base_path)
        self.config_project = '{0}/config_project.yaml'.format(base_path)
        self.config_global = '{0}/config_global.yaml'.format(base_path)

        self.config_local_no_provider = '{0}/config_local_no_provider.yaml'\
        .format(base_path)

        self.config_local_no_project = '{0}/config_local_no_project.yaml'\
        .format(base_path)

        self.config_local_min = '{0}/config_local_min.yaml'\
        .format(base_path)

    def test_config_local_config(self):
        config = Config(local_config=self.config_local, provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec23')
        self.assertTrue(config.data['ec2.key'] == 'aaaaaa')

    def test_config_not_found(self):
        self.assertRaises(
            ConfigNotFound,
            Config,
            local_config='/foo/bar/baz.yaml')

    def test_config_no_provider(self):
        self.assertRaises(
            NoProviderInConfig,
            Config,
            local_config=self.config_local_no_provider)

    def test_config_no_project(self):
        self.assertRaises(
            NoProjectInConfig,
            Config,
            local_config=self.config_local_no_project)

    def test_config_unknown_provider(self):
        self.assertRaises(
            UnknownConfigProvider,
            Config,
            local_config=self.config_local)

    def test_config_project_config(self):
        config = Config(
            local_config=self.config_local_min,
            project_config=self.config_project,
            provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec22')
        self.assertTrue(config.data['ec2.key'] == 'ffff00')

    def test_config_global_config(self):
        config = Config(
            local_config=self.config_local_min,
            global_config=self.config_global,
            provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec21')
        self.assertTrue(config.data['ec2.key'] == 'ff0000')

    def test_config_overrides(self):
        config = Config(
            local_config=self.config_local,
            project_config=self.config_project,
            global_config=self.config_global,
            provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec23')
        self.assertTrue(config.data['ec2.key'] == 'aaaaaa')
