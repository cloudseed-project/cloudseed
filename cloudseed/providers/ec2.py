import os
import boto
from boto.ec2.connection import EC2Connection
from cloudseed.security import add_key_for_config
from cloudseed.utils.exceptions import config_key_error
from cloudseed.exceptions import\
    (KeyAndPairAlreadyExist, MissingPemAtSpecifiedPath)
from cloudseed.utils.logging import Loggable

class EC2Provider(Loggable):

    def __init__(self, config):
        self.pem_file = None
        self.config = config
        self._connect()
        

    def _connect(self):
        with config_key_error():
            self.conn = EC2Connection(
                    self.config.data['aws.key'],
                    self.config.data['aws.secret']
                )

    

    def create_key_pair(self):
        name = '{0}_{1}_{2}'.format(
                self.config.data.get('project'),
                self.config.data.get('session'),
                'ec2'
            )

        self._delete_key_with_name(name)

        ec2_key_exists = self._key_exists(name)
        location = '{0}/.cloudseed/{1}'.format(
                    os.path.expanduser('~'),
                    self.config.data.get('project')
                )
        pem_file = '{0}/{1}'.format(location,name)



        if os.path.exists(pem_file) and ec2_key_exists:
            self.log.debug('[EC2] already created a key, all is well')
            raise KeyAndPairAlreadyExist()
            return
        elif not os.path.exists(pem_file) and ec2_key_exists:
            self.log.debug('[EC2] key is created, but no pem file...get it from someone who made it')
            self.log.debug('[EC2] Alternatively, you can delete the key, and remake it')
            #self._delete_key_with_name(name)
            raise MissingPemAtSpecifiedPath()
            return


        self.log.debug('[EC2] created key_pair with name: %s', name)
        key_pair = self.conn.create_key_pair(name)
        
        filename = add_key_for_config(key_pair.material, self.config)
        self.config.update_config({'ec2.key_name':name,
                                    'ec2.key_path':location})
        
        

              
       

    def _key_exists(self, name):
        keys = self.conn.get_all_key_pairs()
        for key in keys:
            if key.name == name:
                return True
        return False


    def _create_pair_by_name(self,name):
        return self.conn.create_key_pair(name)

    def get_all_instances(self):
        return self.conn.get_all_instances()

    def _delete_key_with_name(self,name):
        keys = self.conn.get_all_key_pairs()
        for key in keys:
            if key.name == name:
                key.delete()

    # def kill_all_instances(self):
    #     for r in ec2.get_all_instances():
    #         ec2.terminate_instances(r.instances[0].id)

    # def run_instances(image_id=None, key_name='ec2-key'):
    #     reservation = self.conn.run_instances( **WEB)
    #     #reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name=key_name)



