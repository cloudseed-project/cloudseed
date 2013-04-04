import os
import boto
from boto import ec2
from boto.exception import EC2ResponseError
from cloudseed.security import add_key_for_config
from cloudseed.utils.exceptions import config_key_error
from cloudseed.exceptions import (
    CloudseedError, KeyAndPairAlreadyExist, KeyNotFound
)
from cloudseed.utils.logging import Loggable


class NeedsEc2Key(CloudseedError):
    ''' Needs Ec2 Keys'''


class EC2Provider(Loggable):

    def __init__(self, config):
        self.pem_file = None
        self.config = config
        self._connect()

    def _connect(self):

        cfg_region = self.config.data.get('ec2.region', 'us-east-1')

        with config_key_error():
            region = ec2.get_region(cfg_region,
                aws_access_key_id=self.config.data['ec2.key'],
                aws_secret_access_key=self.config.data['ec2.secret'])

            self.conn = boto.connect_ec2(
                aws_access_key_id=self.config.data['ec2.key'],
                aws_secret_access_key=self.config.data['ec2.secret'],
                region=region)

    def bootstrap(self):

        try:
            self.verify_keys()
        except NeedsEc2Key:
            self.create_key_pair()

    def verify_keys(self):

        data = self.config.data

        if 'ec2.key_name' not in data \
        and 'ec2.key_path' not in data:
            self.log.debug('ec2 key settings not present')
            raise NeedsEc2Key

        with config_key_error():
            ec2_key_name = self.config.data['ec2.key_name']
            ec2_key_path = self.config.data['ec2.key_path']

        if not os.path.isfile(ec2_key_path):
            self.log.error('Unable to locate key at %s', ec2_key_path)
            raise KeyNotFound

        if not self._ec2_key_exists(ec2_key_name):
            self.log.error('Invalid EC2 key name %s', ec2_key_name)
            raise KeyNotFound

    def create_key_pair(self):
        name = '{0}_{1}_{2}'.format(
                self.config.data.get('project'),
                self.config.data.get('session'),
                'ec2'
            )

        # self._delete_key_with_name(name)

        # ec2_key_exists = self._ec2_key_exists(name)
        # location = '{0}/.cloudseed/{1}'.format(
        #             os.path.expanduser('~'),
        #             self.config.data.get('project')
        #         )
        # pem_file = '{0}/{1}'.format(location, name)

        # if os.path.exists(pem_file) and ec2_key_exists:
        #     self.log.debug('[EC2] already created a key, all is well')
        #     raise KeyAndPairAlreadyExist()
        #     return
        # elif not os.path.exists(pem_file) and ec2_key_exists:
        #     self.log.debug('[EC2] key is created, but no pem file...get it from someone who made it')
        #     self.log.debug('[EC2] Alternatively, you can delete the key, and remake it')
        #     #self._delete_key_with_name(name)
        #     raise KeyNotFound()
        #     return

        self.log.debug('[EC2] created key_pair with name: %s', name)
        key_pair = self.conn.create_key_pair(name)

        filename = add_key_for_config(key_pair.material, self.config)
        self.config.update_config({'ec2.key_name': name,
                                   'ec2.key_path': filename})

    def _ec2_key_exists(self, name):
        try:
            self.conn.get_all_key_pairs([name])
            return True
        except EC2ResponseError:
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



