import os
import uuid
import yaml
from stevedore import driver
from cloudseed.exceptions import (
    NoProviderInConfig, ConfigNotFound, UnknownConfigProvider,
    NoProjectInConfig
)


class Config(object):
    def __init__(self, resource, provider=None):

        self.resource = resource

        if not provider:
            try:
                provider_name = resource.data['provider']
            except KeyError:
                raise NoProviderInConfig

            try:
                em = driver.DriverManager(
                    'com.cloudseed.providers',
                    provider_name,
                    invoke_on_load=True,
                    invoke_kwds={'config': self})
                provider = em.driver
            except RuntimeError:
                raise UnknownConfigProvider

        self.provider = provider

    def activate_profile(self, value):
        self.resource.activate_profile(value)

    @property
    def data(self):
        return self.resource.data

    @property
    def session(self):
        return self.resource.session


class MemoryConfig(object):
    def __init__(self, data, session=None, profile=None):

        if 'project' not in data:
            raise NoProjectInConfig

        self.data = data
        self.session = {} if session is None else session
        self.profile = {} if profile is None else profile

    def activate_profile(self, value):
        self.session['profile'] = value


class FilesystemConfig(object):

    def __init__(self,
        local_config,
        project_config=None,
        global_config=None,
        session_config=None,
        profile_config=None):

        self.data = self.config_for(
            local_config,
            project_config,
            global_config)

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

        if profile_config:
            profile_key = os.path.basename(profile_config)
            self.session['profile'] = profile_key
            self.profile = self.load_paths([profile_config])
        else:
            profile_paths = self.profile_paths(
                self.data['project'],
                profile_key)

            self.profile = self.load_paths(profile_paths)

    def activate_profile(self, value):

        profile_key = self.session.setdefault('profile', None)

        if value != profile_key:
            profile_paths = self.profile_paths(
                self.data['project'],
                value)

            self.profile = self.load_paths(profile_paths)

            session_id = self.data.setdefault('session', uuid.uuid4().hex)
            self.session['profile'] = value

            session_path = self.session_paths(
                self.data['project'],
                session_id)[0]

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
        local_profile = './cloudseed/{0}'.format(value)

        return [project_profile, local_profile]

    def load_paths(self, paths):
        data = {}

        for path in paths:
            try:
                with open(path) as f:
                    data.update(yaml.load(f))
            except IOError:
                pass

        return data

    def config_for(self, local_config, project_config=None, global_config=None):
        global_data = {}
        project_data = {}
        local_data = {}

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))

        if not global_config:
            global_config = '{0}/config'.format(user_dir)

        try:
            with open(local_config) as cfg:
                local_data = yaml.load(cfg)
        except IOError:
            raise ConfigNotFound

        try:
            project = local_data['project']
        except KeyError:
            raise NoProjectInConfig

        if not project_config:
            project_config = '{0}/{1}/config'.format(user_dir, project)

        try:
            with open(global_config) as cfg:
                global_data = yaml.load(cfg)
        except IOError:
            global_data = {}

        try:
            with open(project_config) as cfg:
                project_data = yaml.load(cfg)
        except IOError:
            project_data = {}

        data = {}
        data.update(global_data)
        data.update(project_data)
        data.update(local_data)

        return data
