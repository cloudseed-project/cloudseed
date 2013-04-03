import os
import boto
from boto.ec2.connection import EC2Connection

class EC2Provider(object):

    def __init__(self, config):
        self.config = config
        self._connect()
        self._create_key_pair()
        
    def _connect(self):
        self.conn = EC2Connection(self.config['aws_key'], self.config['aws_secret'])

    def _create_key_pair(self):
        name = self.config.get('name', 'ec2-key')
        location = self.config.get('location', '~/.ssh')
        import pdb; pdb.set_trace()
        try:
            key_pair = self.conn.create_key_pair(name)
            key_pair.save(location)
        except:
            #already exists
            pass


    # def get_all_instances(self):
    #     return self.conn.get_all_instances()

    # def kill_all_instances(self):
    #     for r in ec2.get_all_instances():
    #         ec2.terminate_instances(r.instances[0].id)
    
    # def run_instances(image_id=None, key_name='ec2-key'):
    #     reservation = self.conn.run_instances( **WEB)
    #     #reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name=key_name)



