import os
import boto
from boto.ec2.connection import EC2Connection
from cloudseed.security import add_key_for_config
from cloudseed.utils.exceptions import config_key_error


class EC2Provider(object):

    def __init__(self, config):
        self.pem_file = None
        self.config = config
        #self._connect()
        #self._create_key_pair()

    def _connect(self):
        with config_key_error():
            self.conn = EC2Connection(
                    self.config.data['aws.key'],
                    self.config.data['aws.secret']
                )

    def _create_key_pair(self):
        name = '{0}_{1}_{2}'.format(
                self.config.data.get('project'),
                self.config.data.get('session'),
                'ec2'
            )

        # \/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/ #
        ####################################################
        # filename = add_key_for_config(key, self.config)  #
        ####################################################
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #


        # location = self.config.data.get(
        #     'ec2.key_path',
        #     '{0}/.cloudseed/{1}'.format(
        #             os.path.expanduser('~'),
        #             self.config.data.get('project')
        #         )
        #     )
        # self.pem_file = '{0}{1}.pem'.format(location,name)

        # if not os.path.exists(location):
        #     os.makedirs(location)
        try:
            key_pair = self.conn.create_key_pair(name)
            #key_pair.material
            #key_pair.save(location)
        except:
            pass
            # keys = self.conn.get_all_key_pairs()
            # for key in keys:
            #     if key.name == name:
            #         key.delete()




    def get_all_instances(self):
        return self.conn.get_all_instances()

    # def kill_all_instances(self):
    #     for r in ec2.get_all_instances():
    #         ec2.terminate_instances(r.instances[0].id)

    # def run_instances(image_id=None, key_name='ec2-key'):
    #     reservation = self.conn.run_instances( **WEB)
    #     #reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name=key_name)



