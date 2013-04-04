import os
from unittest import TestCase
from mock import MagicMock
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig
from cloudseed.config import DictConfig
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

        self.config_global_empty = '{0}/config_global_empty.yaml'\
        .format(base_path)

        self.config_project_empty = '{0}/config_project_empty.yaml'\
        .format(base_path)

    def test_fs_config_local_config(self):
        resource = FilesystemConfig(local_config=self.config_local)
        config = Config(resource, provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec23')
        self.assertTrue(config.data['ec2.key'] == 'aaaaaa')

    def test_fs_config_not_found(self):
        self.assertRaises(
            ConfigNotFound,
            FilesystemConfig,
            local_config='/foo/bar/baz.yaml')

    def test_fs_config_no_project(self):
        self.assertRaises(
            NoProjectInConfig,
            FilesystemConfig,
            local_config=self.config_local_no_project)

    def test_dict_config_no_project(self):
        self.assertRaises(
            NoProjectInConfig,
            DictConfig,
            {})

    def test_fs_config_no_provider(self):
        self.assertRaises(
            NoProviderInConfig,
            Config,
            FilesystemConfig(local_config=self.config_local_no_provider,
                            project_config=self.config_project_empty,
                            global_config=self.config_global_empty))

    def test_fs_config_unknown_provider(self):
        self.assertRaises(
            UnknownConfigProvider,
            Config,
            FilesystemConfig(local_config=self.config_local))

    def test_dict_config_no_provider(self):
        self.assertRaises(
            NoProviderInConfig,
            Config,
            DictConfig({'project': 'foo'}))

    def test_dict_config_unknown_provider(self):
        self.assertRaises(
            UnknownConfigProvider,
            Config,
            DictConfig({'project': 'foo', 'provider': 'foo'}))

    def test_fs_project_config(self):
        resource = FilesystemConfig(
            local_config=self.config_local_min,
            project_config=self.config_project)

        config = Config(resource, provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec22')
        self.assertTrue(config.data['ec2.key'] == 'ffff00')

    def test_fs_config_global(self):
        resource = FilesystemConfig(
            local_config=self.config_local_min,
            global_config=self.config_global)

        config = Config(resource, provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec21')
        self.assertTrue(config.data['ec2.key'] == 'ff0000')

    def test_fs_config_overrides(self):
        resource = FilesystemConfig(
            local_config=self.config_local,
            project_config=self.config_project,
            global_config=self.config_global)

        config = Config(resource, provider=MagicMock())

        self.assertTrue(config.data['project'] == 'test')
        self.assertTrue(config.data['session'] == 'ffffff')
        self.assertTrue(config.data['provider'] == 'ec23')
        self.assertTrue(config.data['ec2.key'] == 'aaaaaa')
