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

        # CONSIDER APPENDING PROJECT BASED SCRIPT PATH AS WELL TO BOTH
        # MASTER AND MINION DEPLOY SCRIPT PATHS

        self.master_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'masters'))]

        self.minion_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'minions'))]


        # TODO: EXPOSE MASTER AND MINION CONFIG PATHS SOME HOW
        # LOAD PROJECT FIRST THEN LOAD LOCAL AND MERGE THEM

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

        self.data = self.load_config(
            local_config,
            project_config,
            global_config)

        self.session = self.load_session(session_config)
        self.profile = self.load_profile(profile_config)

    def update_config(self, data):

        self.log.debug('Updating local config %s', self.local_config)

        config = self.load_file(self.local_config)
        config.update(data)

        self.write_file(self.local_config, config)
        self.data.update(data)

    def update_session(self, data):

        path = self.session_paths(
            self.data['project'],
            self.data['session'])[0]

        self.log.debug('Updating session %s', path)

        session = self.load_file(path)
        session.update(data)

        self.write_file(path, session)
        self.session.update(data)

    def activate_profile(self, value):
        profile_key = self.session.setdefault('profile', None)

        if value == profile_key:
            self.log.debug('Current profile is already active: %s', value)
            return

        self.profile = self.load_profile(value)

        session_id = self.data.setdefault('session', uuid.uuid4().hex)

        self.log.debug('Updating session profile to: %s', value)
        self.session['profile'] = value

        session_path = self.session_paths(
            self.data['project'],
            session_id)[0]

        self.log.debug('Writing active profile to session %s', session_path)

        self.write_file(session_path, self.session)

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

    def load_session(self, session_config=None):
        self.log.debug('Loading session data')
        session = {}

        if session_config:
            session = self.load_file(session_config)
        else:
            with config_key_error():
                session_paths = self.session_paths(
                    self.data['project'],
                    self.data['session'])
                session = self.load_file(*session_paths)

        return session

    def load_profile(self, value):

        if not value:
            return {}

        path = os.path.abspath(value)

        # This is really dangerous, we are not checking
        # where we are loading this file from. Whatever is
        # passed here will be run though a YAML decoder
        # this is definitely a security risk
        # Whatever the user executing this script has read access
        # to is fair game.

        if os.path.isfile(path):
            self.log.debug('Loading profile data for %s', path)
            profile_key = os.path.basename(path)
            self.session['profile'] = profile_key
            return self.load_file(path)
        else:
            if not value:
                self.log.debug('No profile currently set')
                return {}

            self.log.debug('Loading profile data for %s', value)
            profile_paths = self.profile_paths(
                self.data['project'],
                value)

            profile = self.load_file(*profile_paths)

            if not profile:
                self.log.error('No profile information found in %s', profile_paths)
                raise InvalidProfile

            return profile

    def load_config(self, local_config, project_config=None, global_config=None):
        self.log.debug('Loading configuration')
        local_data = {}

        user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))
        self.log.debug('User dir %s', user_dir)

        if not global_config:
            global_config = '{0}/config'.format(user_dir)

        self.log.debug('Loading local config: %s', local_config)

        local_data = self.load_file(local_config)

        if not local_data:
            raise ConfigNotFound

        with config_key_error():
            project = local_data['project']
            self.log.debug('Project name is: %s', project)

        if not project_config:
            project_config = '{0}/{1}/config'.format(user_dir, project)

        self.log.debug(
            'Loading global and project configs: %s, %s',
            global_config, project_config)

        data = self.load_file(global_config, project_config)
        data.update(local_data)

        return data

    def load_file(self, *args):
        data = {}

        for path in args:
            try:
                self.log.debug('Loading file %s', path)

                with open(path) as f:
                    try:
                        data.update(yaml.load(f))
                    except Exception as e:
                        self.log.warning('Unable to merge data from file %s: %s', path, e.message)
            except IOError:
                self.log.warning('Failed to load file %s', path)

        return data

    def write_file(self, path, data):
        self.log.debug('Writing file to %s with %s', path, data)

        try:
            with open(path, 'w') as f:
                f.write(yaml.dump(data, default_flow_style=False))
        except IOError:
            self.log.error('Failed writing file %s with %s', path, data)
            raise
