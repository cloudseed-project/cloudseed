import os
import time
from itertools import starmap
import yaml
import boto
from boto import ec2
from boto.exception import EC2ResponseError
from cloudseed.utils.deploy import bootstrap_script
from cloudseed.security import write_key_for_config
from cloudseed.utils.exceptions import config_key_error, profile_key_error
from cloudseed.exceptions import (
    CloudseedError, KeyAndPairAlreadyExist, KeyNotFound
)
from cloudseed.utils.logging import Loggable


class NeedsEc2Key(CloudseedError):
    ''' Needs Ec2 Keys'''


class EC2Provider(Loggable):

    def __init__(self, provider):
        self.pem_file = None
        self.provider = provider
        self._connect(provider)

    def _connect(self, provider):

        cfg_region = provider.get('region', 'us-east-1')

        with config_key_error():
            region = ec2.get_region(cfg_region,
                aws_access_key_id=provider['key'],
                aws_secret_access_key=provider['secret'])

            self.conn = boto.connect_ec2(
                aws_access_key_id=provider['key'],
                aws_secret_access_key=provider['secret'],
                region=region)

    def ssh_identity(self):
        return os.path.expanduser(self.provider['key_path'])

    def deploy_config(self, context=None):
        data = self.provider.copy()
        data['key_path'] = '/etc/salt/cloudseed.pem'
        return yaml.dump(data, default_flow_style=False)

    def deploy_profile(self, context=None):
        return yaml.dump(self.provider.profile, default_flow_style=False)

    def deploy_extras(self, context=None):
        key_path = os.path.expanduser(self.provider['key_path'])
        with open(key_path) as f:
            key = f.read()

        return ['echo "{0}" > /etc/salt/cloudseed.pem'.format(key)]

    def deploy(self, states, machine):
        self.log.debug('States for deploy: %s', states)

    def bootstrap(self, profile, config):
        self.log.debug('Creating bootstrap node')
        try:
            self.verify_keys()
        except NeedsEc2Key:
            self.log.debug('Createing EC2 key')
            self.create_key_pair(config)

        groups = self._initialize_security_groups(config)

        return self._build_master(
            name=config.data['project'],
            profile=profile,
            security_groups=groups)

    def verify_keys(self):

        data = self.provider

        if 'key_name' not in data \
        and 'key_path' not in data:
            self.log.debug('EC2 key settings not present')
            raise NeedsEc2Key

        with config_key_error():
            ec2_key_name = data['key_name']
            ec2_key_path = os.path.expanduser(data['key_path'])

        if not os.path.isfile(ec2_key_path):
            self.log.error('Unable to locate key at %s', ec2_key_path)
            raise KeyNotFound

        if not self._ec2_key_exists(ec2_key_name):
            self.log.error('Invalid EC2 key name %s', ec2_key_name)
            raise KeyNotFound

    def create_key_pair(self, config):
        name = '{0}_{1}_{2}'.format(
                config.data.get('project'),
                config.session.get('environment'),
                'ec2'
            )

        self.log.debug('[EC2] created key_pair with name: %s', name)
        key_pair = self.conn.create_key_pair(name)

        filename = write_key_for_config(
            key_pair.material,
            provider=self.provider,
            config=config)

        self.provider['key_name'] = name
        self.provider['key_path'] = filename

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

    def _base_security_groups(self, config):
        project = config.data['project'].lower()
        env = config.session['environment']

        return {
        'app': ('cloudseed-{0}-{1}'.format(project, env),
            'Cloudseed group for {0} {1}'.format(project, env)),

        'ssh': ('cloudseed-{0}-{1}-SSH'.format(project, env),
            'Cloudseed SSH for {0} {1}'.format(project, env)),

        'master': ('cloudseed-{0}-{1}-0'.format(project, env),
            'Cloudseed group for {0} {1} machine 0'.format(project, env)),
        }

    def _initialize_security_groups(self, config):
        groups = self._base_security_groups(config)

        conn = self.conn

        base_groups = (
            groups['app'],
            groups['ssh'],
            groups['master'],
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

    def _build_master(self, name, profile, security_groups):

        {'image': 'ami-bb709dd2',
        'size': 't1.micro'}

        with profile_key_error():
            kwargs = {
            'image_id': profile['image'],
            'key_name': self.provider['key_name'],
            'instance_type': profile['size'],
            'security_groups': security_groups,
            'user_data': None  # bootstrap_script(profile['script'], profile, self.provider)
            }

        self.log.debug('Creating instance with %s', kwargs)
        reservation = self.conn.run_instances(**kwargs)

        instance = reservation.instances[0]
        instance_name = 'cloudseed-{0}-0'.format(name.lower())

        self.log.debug('Waiting for instance to become available, this can take a minute or so.')

        while True:
            if instance.public_dns_name:
                break;

            try:
                instance.update()
            except EC2ResponseError:
                pass

            time.sleep(3)

        self.log.debug('Naming instance  %s', instance_name)
        self.log.debug('Instance available at %s', instance.public_dns_name)

        # I don't like doing this, need to think of a better way to handle
        # alternate providers
        # self.provider.update_config({
        #     'master': instance.public_dns_name.encode('utf-8'),
        #     'provider': 'ec2',
        #     })

        instance.add_tag('Name', instance_name)
        return instance.public_dns_name.encode('utf-8')

    def kill_all_instances(self, config):

        name = 'cloudseed-{0}-{1}'.format(
            config.data['project'],
            config.session['environment'])

        filters = {'instance-state-name': 'running', 'group-name': name}
        all_instances = self.conn.get_all_instances(filters=filters)

        for reservation in all_instances:
            self._destroy_reservation_instances(reservation.instances)

    def _destroy_reservation_instances(self, instances):
        for instance in instances:
            self.log.debug('Terminating instance %s', instance.id)
            self.conn.terminate_instances(instance.id)


