import os
from unittest import TestCase
from mock import MagicMock
from cloudseed.providers.ec2 import EC2Provider
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig


class TestEC2Provider(TestCase):

    def setUp(self):
        base_path = '{0}/tests/resources'.format(os.getcwd())
        self.config_ec2 = '{0}/config_ec2.yaml'.format(base_path)

    def test_get_all_instances(self):
<<<<<<< HEAD
        resource = FilesystemConfig(local_config=self.config_ec2)
        config = Config(resource, provider=MagicMock())
        config.data['aws.key'] = 'asdf'
        config.data['aws.secret'] = 'asdf'
=======
        config = Config(local_config=self.config_ec2, provider=MagicMock())
        try:
            config.data['aws.key'] = os.environ['AWS_ACCESS_KEY_ID']
            config.data['aws.secret'] = os.environ['AWS_SECRET_ACCESS_KEY']
        except:
            #self.log.warning('need to set both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env vars')
            return

>>>>>>> 83606c37c62fb939ca664cfa5ee4dea5e100bdee
        ec2 = EC2Provider(config)



