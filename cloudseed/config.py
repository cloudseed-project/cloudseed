import os
import uuid
import yaml
from stevedore import driver
from cloudseed.utils.logging import Loggable
from cloudseed.utils.exceptions import config_key_error
from cloudseed.exceptions import (
    ConfigNotFound, UnknownConfigProvider, InvalidProfile,
)


class Config(Loggable):
    def __init__(self, resource, provider=None):

        self.resource = resource

        if not provider:
            with config_key_error():
                provider_name = resource.data['provider']

            try:
                em = driver.DriverManager(
                    'com.cloudseed.providers',
                    provider_name,
                    invoke_on_load=True,
                    invoke_kwds={'config': self})
                provider = em.driver
            except RuntimeError:
                self.log.error('Unknown Config Provider %s', provider_name)
                raise UnknownConfigProvider
        else:
            provider = provider(config=self)

        self.provider = provider

    @property
    def data(self):
        return self.resource.data

    @property
    def session(self):
        return self.resource.session

    @property
    def profile(self):
        return self.resource.profile

    def update_config(self, data):
        self.log.debug('Updating config with %s', data)
        self.resource.update_config(data)

    def update_session(self, data):
        self.log.debug('Updating session with %s', data)
        self.resource.update_session(data)

    def activate_profile(self, value):
        self.log.debug('Activating profile: %s', value)
        self.resource.activate_profile(value)


class MemoryConfig(Loggable):
    def __init__(self, data, session=None, profile=None):

        with config_key_error():
            data['project']

        self.data = data
        self.session = {} if session is None else session
        self.profile = {} if profile is None else profile

    def activate_profile(self, value):
        self.session['profile'] = value

    def update_config(self, data):
        self.data.update(data)

    def update_session(self, data):
        self.session.update(data)


class FilesystemConfig(Loggable):

    def __init__(self,
        local_config,
        project_config=None,
        global_config=None,
        session_config=None,
        profile_config=None):

        self.local_config = local_config

        self.data = self.config_for(
            local_config,
            project_config,
            global_config)

        self.log.debug('Loading session data')
        if session_config:
            self.session = self.load_paths([session_config])
        else:
            try:
                session_paths = self.session_paths(
                    self.data['project'],
                    self.data['session'])
                self.session = self.load_paths(session_paths)
            except KeyError:
                self.session = {}

        profile_key = self.session.setdefault('profile', None)

        self.log.debug('Loading profile data')

        if profile_config:
            profile_key = os.path.basename(profile_config)
            self.session['profile'] = profile_key
            self.profile = self.load_paths([profile_config])
        else:
            if profile_key:
                profile_paths = self.profile_paths(
                    self.data['project'],
                    profile_key)

                profile = self.load_paths(profile_paths)

                if not profile:
                    self.log.error('No profile information found in %s', profile_paths)
                    raise InvalidProfile

                self.profile = profile
            else:
                self.profile = {}

    def update_config(self, data):

        self.data.update(data)

        self.log.debug('Reading local config for merge %s', self.local_config)
        with open(self.local_config) as f:
            config = yaml.load(f)

        config.update(data)

        self.log.debug('Writing merged config %s to %s', config, self.local_config)
        with open(self.local_config, 'w') as f:
            f.write(yaml.dump(config, default_flow_style=False))

    def update_session(self, data):

        self.session.update(data)

        path = self.session_paths(
            self.data['project'],
            self.data['session'])[0]

        self.log.debug('Reading local session for merge %s', path)

        with open(path) as f:
            session = yaml.load(f)

        session.update(data)

        self.log.debug('Writing merged session %s to %s', session, path)

        with open(path, 'w') as f:
            f.write(yaml.dump(session, default_flow_style=False))

    def activate_profile(self, value):
        profile_key = self.session.setdefault('profile', None)

        if value != profile_key:
            self.log.debug('Updating session profile to: %s', value)

            profile_paths = self.profile_paths(
                self.data['project'],
                value)

            self.log.debug('Loading profile data for: %s', value)
            profile = self.load_paths(profile_paths)

            if not profile:
                self.log.error('No profile information found in %s', profile_paths)
                raise InvalidProfile
            else:
                self.profile = profile

            session_id = self.data.setdefault('session', uuid.uuid4().hex)

            self.session['profile'] = value

            session_path = self.session_paths(
                self.data['project'],
                session_id)[0]

            self.log.debug('Writing active profile to session %s', session_path)

            with open(session_path, 'w') as f:
                f.write(yaml.dump(self.session, default_flow_style=False))

    def session_paths(self, project, session_id):

        path = '{0}/.cloudseed/{1}/session_{2}'.format(
            os.path.expanduser('~'),
            project,
            session_id)

        return [path]

    def profile_paths(self, project, value):

        if not value:
            return []

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))
        project_profile = '{0}/{1}/{2}'.format(user_dir, project, value)
        local_profile = './.cloudseed/{0}'.format(value)

        return [project_profile, local_profile]

    def load_paths(self, paths):
        self.log.debug('Loading paths %s', paths)
        data = {}

        for path in paths:
            try:
                with open(path) as f:
                    data.update(yaml.load(f))
            except IOError:
                pass

        return data

    def config_for(self, local_config, project_config=None, global_config=None):
        self.log.debug('Loading configuration')
        global_data = {}
        project_data = {}
        local_data = {}

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))
        self.log.debug('User dir %s', user_dir)

        if not global_config:
            global_config = '{0}/config'.format(user_dir)

        self.log.debug('Loading local config: %s', local_config)

        try:
            with open(local_config) as cfg:
                local_data = yaml.load(cfg)
        except IOError:
            raise ConfigNotFound

        with config_key_error():
            project = local_data['project']
            self.log.debug('Project name is: %s', project)

        if not project_config:
            project_config = '{0}/{1}/config'.format(user_dir, project)

        self.log.debug('Loading global config: %s', global_config)
        try:
            with open(global_config) as cfg:
                global_data = yaml.load(cfg)
        except IOError:
            global_data = {}

        self.log.debug('Loading project config: %s', project_config)
        try:
            with open(project_config) as cfg:
                project_data = yaml.load(cfg)
        except IOError:
            project_data = {}

        data = {}

        if global_data:
            data.update(global_data)

        if project_data:
            data.update(project_data)

        data.update(local_data)

        return data
