import os
import unittest
from mock import MagicMock
from cloudseed.providers.ec2 import EC2Provider
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig
from cloudseed.config import MemoryConfig
from cloudseed.providers.ec2 import NeedsEc2Key
from cloudseed.exceptions import (
    KeyNotFound, MissingConfigKey
)


LIVE_EC2 = 'AWS_ACCESS_KEY_ID' in os.environ and \
'AWS_SECRET_ACCESS_KEY' in os.environ


class TestEC2Provider(unittest.TestCase):

    def setUp(self):
        base_path = '{0}/tests/resources'.format(os.getcwd())
        self.config_ec2_with_key = '{0}/config_ec2_with_key.yaml'.format(base_path)
        self.config_ec2_no_key = '{0}/config_ec2_no_key.yaml'.format(base_path)

    # @unittest.skipUnless(LIVE_EC2, 'AWS Environment not set')
    # def test_ec2provider_create_key_pair_with_key(self):
    #     resource = FilesystemConfig(local_config=self.config_ec2_with_key)
    #     resource.data['aws.key'] = os.environ['AWS_ACCESS_KEY_ID']
    #     resource.data['aws.secret'] = os.environ['AWS_SECRET_ACCESS_KEY']
    #     config = Config(resource, provider=MagicMock())

    #     ec2 = EC2Provider(config)
    #     if config.data.get('ec2.key_name', False) and \
    #     config.data.get('ec2.key_path', False):
    #         self.assertEqual(True,True)
    #     else:
    #         self.assertEqual(True,False)

    def test_no_aws_key(self):
        self.assertRaises(
            MissingConfigKey,
            EC2Provider,
            Config(MemoryConfig({
                'project': 'foo',
                'provider': 'ec2',
                'aws.secret': 'foo'}), provider=MagicMock))

    def test_no_aws_secret(self):
        self.assertRaises(
            MissingConfigKey,
            EC2Provider,
            Config(MemoryConfig({
                'project': 'foo',
                'provider': 'ec2',
                'aws.key': 'foo'}), provider=MagicMock))

    def test_no_ec2_keys(self):
        resource = MemoryConfig({
                'project': 'foo',
                'provider': 'ec2',
                'aws.key': 'foo',
                'aws.secret': 'foo'})

        config = Config(resource, EC2Provider)
        ec2 = config.provider

        self.assertRaises(
            NeedsEc2Key,
            ec2.verify_keys)

    # @unittest.skipUnless(LIVE_EC2, 'AWS Environment not set')
    # def test_ec2provider_create_key_pair_with_key(self):
    #     resource = FilesystemConfig(local_config=self.config_ec2_no_key)
    #     resource.data['aws.key'] = os.environ['AWS_ACCESS_KEY_ID']
    #     resource.data['aws.secret'] = os.environ['AWS_SECRET_ACCESS_KEY']

    #     config = Config(resource, provider=EC2Provider)
    #     ec2 = config.provider

    #     if not config.data.get('ec2.key_name', False) and not config.data.get('ec2.key_path', False):
    #         try:
    #             ec2.create_key_pair()
    #         except KeyAndPairAlreadyExist:
    #             pass
    #         except MissingPemAtSpecifiedPath:
    #             pass
    #         except:
    #             raise

