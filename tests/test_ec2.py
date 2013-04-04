from unittest import TestCase
from cloudseed.providers.ec2 import EC2Provider
from mock import MagicMock
from cloudseed.config import Config
import os

class TestEC2Provider(TestCase):

    def setUp(self):
        base_path = '{0}/tests/resources'.format(os.getcwd())
        self.config_ec2 = '{0}/config_ec2.yaml'.format(base_path)

    def test_get_all_instances(self):
        
        config = Config(local_config=self.config_ec2, provider=MagicMock())
        config.data['aws.key'] = 'asdf'
        config.data['aws.secret'] = 'asdf'
        ec2 = EC2Provider(config)
        

        
