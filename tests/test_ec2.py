import os
import unittest
from mock import MagicMock
from cloudseed.providers.ec2 import EC2Provider
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig

LIVE_EC2 = 'AWS_ACCESS_KEY_ID' in os.environ and \
'AWS_SECRET_ACCESS_KEY' in os.environ


class TestEC2Provider(unittest.TestCase):

    def setUp(self):
        base_path = '{0}/tests/resources'.format(os.getcwd())
        self.config_ec2 = '{0}/config_ec2.yaml'.format(base_path)

    @unittest.skipUnless(LIVE_EC2, 'AWS Environment not set')
    def test_get_all_instances(self):
        resource = FilesystemConfig(local_config=self.config_ec2)
        resource.data['aws.key'] = 'asdf'
        resource.data['aws.secret'] = 'asdf'

        config = Config(resource, provider=MagicMock())

        try:
            config.data['aws.key'] = os.environ['AWS_ACCESS_KEY_ID']
            config.data['aws.secret'] = os.environ['AWS_SECRET_ACCESS_KEY']
        except:
            #self.log.wargning('need to set both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars')
            return

        ec2 = EC2Provider(config)



