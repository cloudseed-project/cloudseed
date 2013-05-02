import os
import time
from itertools import starmap
import boto
from boto import ec2
from boto.exception import EC2ResponseError
from cloudseed.utils.deploy import script
from cloudseed.security import write_key_for_config
from cloudseed.utils.exceptions import config_key_error, profile_key_error
from cloudseed.exceptions import (
    CloudseedError, KeyAndPairAlreadyExist, KeyNotFound
)
from cloudseed.utils.logging import Loggable


class NeedsEc2Key(CloudseedError):
    ''' Needs Ec2 Keys'''


class EC2Provider(Loggable):

    def __init__(self, key, data):
        self.pem_file = None
        self.key = key
        self.provider = data

        self._connect(data)

    def _connect(self, provider):

        cfg_region = provider.get('region', 'us-east-1')

        with config_key_error():
            region = ec2.get_region(cfg_region,
                aws_access_key_id=provider['id'],
                aws_secret_access_key=provider['key'])

            self.conn = boto.connect_ec2(
                aws_access_key_id=provider['id'],
                aws_secret_access_key=provider['key'],
                region=region)

    def ssh_identity(self):
        try:
            return os.path.expanduser(self.provider['private_key'])
        except KeyError:
            return None

    def deploy(self, states, machine):
        self.log.debug('States for deploy: %s', states)

    def create_instance(self, profile, config, instance_name, state, data):
        self.log.debug('Creating instance')

        base_groups = self._base_security_groups(config)

        try:
            self.verify_keys()
        except NeedsEc2Key:
            self.log.debug('Createing EC2 key')
            self.create_key_pair(config)

        groups = [instance_name, base_groups['app'][0]]

        self._initialize_security_groups(config)
        self._create_security_group(instance_name, config, profile)

        if state == 'master':
            groups.append(base_groups['ssh'][0])

        user_data = script(
            profile['script'],
            config=config,
            data=data)

        return self._create_instance(
            instance_name=instance_name,
            profile=profile,
            security_groups=groups,
            user_data=user_data)

    def verify_keys(self):

        data = self.provider

        if 'keyname' not in data \
        and 'private_key' not in data:
            self.log.debug('EC2 key settings not present')
            raise NeedsEc2Key

        with config_key_error():
            ec2_key_name = data['keyname']
            ec2_key_path = os.path.expanduser(data['private_key'])

        if not os.path.isfile(ec2_key_path):
            self.log.error('Unable to locate key at %s', ec2_key_path)
            raise KeyNotFound

        if not self._ec2_key_exists(ec2_key_name):
            self.log.error('Invalid EC2 key name %s', ec2_key_name)
            raise KeyNotFound

    def create_key_pair(self, config):
        name = '{0}_{1}_{2}'.format(
                config.data.get('project'),
                config.environment,
                'ec2'
            )

        self.log.debug('[EC2] created key_pair with name: %s', name)
        key_pair = self.conn.create_key_pair(name)

        filename = write_key_for_config(
            key_pair.material,
            provider=self.provider,
            config=config)

        self.provider['keyname'] = name
        self.provider['private_key'] = filename

        # We have a write operation here that does not happen
        # on the CLI level. I feel a little weird about it
        # but have not though of a better way to handle this
        # situation, so for now, it is what it is.
        config.update_providers({self.key: self.provider})

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

    def _create_security_group(self, name, config, profile):
        conn = self.conn
        current_groups = conn.get_all_security_groups()
        current_set = frozenset([x.name for x in current_groups])

        if name in current_set:
            return

        instance_id = name.split('-')[-1]
        description = 'Cloudseed group for {0} {1} machine {2}'\
        .format(
            config.data['project'].lower(),
            config.environment,
            instance_id)

        group = conn.create_security_group(name, description)

        for port in profile.get('exposes', ()):
            group.authorize(
                    ip_protocol='tcp',
                    from_port=port,
                    to_port=port,
                    cidr_ip='0.0.0.0/0')

    def _base_security_groups(self, config):
        project = config.data['project'].lower()
        env = config.environment

        return {
        'app': ('cloudseed-{0}-{1}'.format(project, env),
            'Cloudseed group for {0} {1}'.format(project, env)),

        'ssh': ('cloudseed-{0}-{1}-SSH'.format(project, env),
            'Cloudseed SSH for {0} {1}'.format(project, env)),
        }

    def _initialize_security_groups(self, config):
        groups = self._base_security_groups(config)

        conn = self.conn

        base_groups = (
            groups['app'],
            groups['ssh'],
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

    def _extras_user_data(self, config):
        return []

    def _create_instance(self, instance_name, profile, security_groups, user_data):

        with profile_key_error():
            kwargs = {
            'image_id': profile['image'],
            'key_name': self.provider['keyname'],
            'instance_type': profile['size'],
            'security_groups': security_groups,
            'user_data': user_data
            }

        self.log.debug('Creating instance with %s', kwargs)
        reservation = self.conn.run_instances(**kwargs)

        instance = reservation.instances[0]

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

        instance.add_tag('Name', instance_name)
        return instance.public_dns_name.encode('utf-8')

    def kill_all_instances(self, config):

        name = 'cloudseed-{0}-{1}'.format(
            config.data['project'],
            config.environment)

        filters = {'instance-state-name': 'running', 'group-name': name}
        all_instances = self.conn.get_all_instances(filters=filters)

        for reservation in all_instances:
            self._destroy_reservation_instances(reservation.instances)

    def _destroy_reservation_instances(self, instances):
        for instance in instances:
            self.log.debug('Terminating instance %s', instance.id)
            self.conn.terminate_instances(instance.id)


