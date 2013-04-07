import os
import time
from itertools import starmap
import yaml
import boto
from boto import ec2
from boto.exception import EC2ResponseError
from cloudseed.utils.deploy import bootstrap_script
from cloudseed.security import add_key_for_config
from cloudseed.utils.exceptions import config_key_error, profile_key_error
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

    def ssh_identity(self):
        return os.path.expanduser(self.config.data['ec2.key_path'])

    def deploy_config(self, context=None):
        data = self.config.data.copy()
        data['ec2.key_path'] = '/etc/salt/cloudseed.pem'
        return yaml.dump(data, default_flow_style=False)

    def deploy_profile(self, context=None):
        return yaml.dump(self.config.profile, default_flow_style=False)

    def deploy_extras(self, context=None):
        key_path = os.path.expanduser(self.config.data['ec2.key_path'])
        with open(key_path) as f:
            key = f.read()

        return ['echo "{0}" > /etc/salt/cloudseed.pem'.format(key)]

    def bootstrap(self):
        self.log.info('Creating bootstrap node')
        try:
            self.verify_keys()
        except NeedsEc2Key:
            self.log.debug('Createing EC2 key')
            self.create_key_pair()

        groups = self._initialize_security_groups()
        self._build_master(security_groups=groups)

    def verify_keys(self):

        data = self.config.data

        if 'ec2.key_name' not in data \
        and 'ec2.key_path' not in data:
            self.log.debug('EC2 key settings not present')
            raise NeedsEc2Key

        with config_key_error():
            ec2_key_name = self.config.data['ec2.key_name']
            ec2_key_path = os.path.expanduser(self.config.data['ec2.key_path'])

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
        # location = '{0}/.cloudseed/{1}/{2}'.format(
        #             os.path.expanduser('~'),
        #             self.config.data.get('project'),
        #             name
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

    def _create_pair_by_name(self, name):
        return self.conn.create_key_pair(name)

    def get_all_instances(self):
        return self.conn.get_all_instances()

    def _delete_key_with_name(self, name):
        keys = self.conn.get_all_key_pairs()
        for key in keys:
            if key.name == name:
                key.delete()

    def _base_security_groups(self):
        project = self.config.data['project'].lower()
        return {
        'app': ('cloudseed-{0}'.format(project), 'Cloudseed group for {0}'.format(project)),
        'ssh': ('cloudseed-{0}-SSH'.format(project), 'Cloudseed SSH for {0}'.format(project)),
        'bootstrap': ('cloudseed-{0}-0'.format(project), 'Cloudseed group for {0} machine 0'.format(project)),
        }

    def _initialize_security_groups(self):
        groups = self._base_security_groups()

        conn = self.conn

        base_groups = (
            groups['app'],
            groups['ssh'],
            groups['bootstrap'],
        )

        current_groups = conn.get_all_security_groups()
        current_set = frozenset([(x.name, x.description) for x in current_groups])
        allowed_groups = frozenset(base_groups)
        missing_groups = allowed_groups - current_set

        self.log.debug('The following security groups will be created: %s', missing_groups)

        new_groups = list(starmap(conn.create_security_group, missing_groups))

        for group in new_groups:

            if group.name == groups['app'][0]:
                group.authorize(
                    src_group=group,
                    ip_protocol='tcp',
                    from_port=1,
                    to_port=65535)

                group.authorize(
                    src_group=group,
                    ip_protocol='udp',
                    from_port=1,
                    to_port=65535)

                group.authorize(
                    src_group=group,
                    ip_protocol='icmp',
                    from_port=-1,
                    to_port=-1)

            if group.name == groups['ssh'][0]:
                group.authorize(
                    ip_protocol='tcp',
                    from_port=22,
                    to_port=22,
                    cidr_ip='0.0.0.0/0')

        return [x[0] for x in base_groups]

    def _build_master(self, security_groups):

        with profile_key_error():
            profile = self.config.profile['bootstrap']

        {'image': 'ami-bb709dd2',
        'size': 't1.micro'}

        with profile_key_error():
            kwargs = {
            'image_id': profile['image'],
            'key_name': self.config.data['ec2.key_name'],
            'instance_type': profile['size'],
            'security_groups': security_groups,
            'user_data': bootstrap_script(profile['script'], profile, self.config)
            }

        self.log.debug('Creating instance with %s', kwargs)
        reservation = self.conn.run_instances(**kwargs)

        instance = reservation.instances[0]
        instance_name = 'cloudseed-{0}-0'.format(self.config.data['project'].lower())

        self.log.info('Waiting for instance to become available, this can take a minute or so.')

        while True:
            instance.update()

            if instance.public_dns_name:
                break;

            time.sleep(3)

        self.log.debug('Naming instance  %s', instance_name)
        self.log.debug('Instance available at %s', instance.public_dns_name)
        self.config.update_config({'master': instance.public_dns_name.encode('utf-8')})

        instance.add_tag('Name', instance_name)
        #self.kill_all_instances()

    def kill_all_instances(self):
        for r in self.conn.get_all_instances():
            self.conn.terminate_instances(r.instances[0].id)
            print(r.instances[0].id)
            print(r.instances[0].state)



    # def run_instances(image_id=None, key_name='ec2-key'):
    #     reservation = self.conn.run_instances( **WEB)
    #     #reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name=key_name)



