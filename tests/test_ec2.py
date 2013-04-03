from unittest import TestCase
from cloudseed.providers.ec2 import EC2Provider


class TestEC2Provider(TestCase):

    def test_get_all_instances(self):
        config = {'aws_key':'AKIAJADTWQVKNWOJUFIQ',
                  'aws_secret':'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'}
        ec2 = EC2Provider(config)
        

        
