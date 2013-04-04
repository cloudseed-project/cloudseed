import os
import boto
from boto.ec2.connection import EC2Connection

class EC2Provider(object):

    def __init__(self, config):
        self.pem_file = None
        self.config = config.data
        self._connect()
        self._create_key_pair()
        
    def _connect(self):
        self.conn = EC2Connection(
                self.config['aws.key'], 
                self.config['aws.secret']
            )

    def _create_key_pair(self):
        name = '{0}_{1}_{2}'.format(
                self.config.get('project'),
                self.config.get('session'),
                'ec2'
            )
        
        location = self.config.get(
            'ec2.key_path', 
            '~/.cloudseed/{0}'.format(self.config.get('project')))
        self.pem_file = '{0}{1}.pem'.format(location,name)
        if not os.path.exists(location):
            os.makedirs(location)
        import pdb; pdb.set_trace()
        # try:
        #     key_pair = self.conn.create_key_pair(name)
        #     key_pair.save(location)
        # except:
        #     #already exists
        #     #self.log.warning('[ec2provider] pem file already created')
        #     keys = self.conn.get_all_key_pairs()
        #     for key in keys:
        #         if key.name == name:
        #             import pdb; pdb.set_trace()
        #             #key.save(location)
            


    # def get_all_instances(self):
    #     return self.conn.get_all_instances()

    # def kill_all_instances(self):
    #     for r in ec2.get_all_instances():
    #         ec2.terminate_instances(r.instances[0].id)
    
    # def run_instances(image_id=None, key_name='ec2-key'):
    #     reservation = self.conn.run_instances( **WEB)
    #     #reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name=key_name)



