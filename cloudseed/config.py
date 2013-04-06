import os
from stevedore import driver
from cloudseed.utils.logging import Loggable
from cloudseed.utils.filesystem import Filesystem
from cloudseed.utils.exceptions import config_key_error
from cloudseed.exceptions import (
    ConfigNotFound, UnknownConfigProvider, InvalidEnvironment,
)


class Config(Loggable):
    def __init__(self, resource, provider=None):

        self.resource = resource
        self.provider = None

        # CONSIDER APPENDING PROJECT BASED SCRIPT PATH AS WELL TO BOTH
        # MASTER AND MINION DEPLOY SCRIPT PATHS

        self.master_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'masters'))]

        self.minion_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'minions'))]

        # TODO: EXPOSE MASTER AND MINION CONFIG PATHS SOME HOW
        # LOAD PROJECT FIRST THEN LOAD LOCAL AND MERGE THEM

        if provider:
            self.provider = provider(config=self)
        elif resource.session.get('environment'):
            with config_key_error():
                provider_name = resource.data['provider']
            try:
                em = driver.DriverManager(
                    'com.cloudseed.providers',
                    provider_name,
                    invoke_on_load=True,
                    invoke_kwds={'config': self})
                self.provider = em.driver
            except RuntimeError:
                self.log.error('Unknown Config Provider %s', provider_name)
                raise UnknownConfigProvider

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

    def activate_environment(self, value):
        self.log.debug('Activating environment: %s', value)
        self.resource.activate_environment(value)


class MemoryConfig(Loggable):
    def __init__(self, data, session=None, profile=None):

        with config_key_error():
            data['project']

        self.data = data
        self.session = {} if session is None else session
        self.profile = {} if profile is None else profile

    def activate_environment(self, value):
        self.session['environment'] = value

    def update_config(self, data, _):
        self.data.update(data)

    def update_session(self, data):
        self.session.update(data)


class FilesystemConfig(Loggable, Filesystem):

    def __init__(self,
        local_config,
        project_config=None,
        global_config=None,
        session_config=None,
        profile_config=None):

        self.local_config = local_config

        try:
            self.data = self.load_config(
                local_config,
                project_config,
                global_config)
        except ConfigNotFound:
            self.log.warning('No config found, operations will be limited')
            self.data = {}
            self.session = {}
            self.profile = {}
            return

        self.session = self.load_session(session_config)

        env_key = self.session['environment'] \
        if not profile_config \
        else profile_config

        self.profile = self.load_env_profile(env_key)

    def update_config(self, data):
        path = os.path.join(
            self.local_env_path(self.session['environment']),
            'config')

        self.log.debug('Updating config %s', path)

        config = self.load_file(path)
        config.update(data)

        self.write_file(path, config)
        self.data.update(data)

    def update_session(self, data):

        path = self.session_paths(
            self.data['project'])[0]

        self.log.debug('Updating session %s', path)

        session = self.load_file(path)
        session.update(data)

        self.write_file(path, session)
        self.session.update(data)

    def activate_environment(self, value):
        env_key = self.session['environment']

        if value == env_key:
            self.log.debug('Current environment is already active: %s', value)
            return

        self.profile = self.load_env_profile(value)

        self.log.debug('Updating session profile to: %s', value)
        self.session['environment'] = value

        session_path = self.session_paths(
            self.data['project'])[0]

        self.log.debug('Writing active profile to session %s', session_path)

        self.write_file(session_path, self.session)

    def session_paths(self, project):
        path = os.path.join(
            self.project_path(project),
            'session')

        return [path]

    def env_profile_paths(self, project, value):

        if not value:
            return []

        project_env = os.path.join(
            self.project_env_path(project, value),
            'profile')

        local_env = os.path.join(
            self.local_env_path(value),
            'profile')

        return [project_env, local_env]

    def load_session(self, session_config=None):
        self.log.debug('Loading session data')
        session = {}

        if session_config:
            session = self.load_file(session_config)
        else:
            with config_key_error():
                project = self.data['project']

                session_paths = self.session_paths(project)
                session = self.load_file(*session_paths)

        try:
            env_path = self.local_env_path(session['environment'])
            env_config = os.path.join(env_path, 'config')
            self.data.update(self.load_file(env_config))
        except KeyError:
            pass

        session.setdefault('environment', None)
        return session

    def load_env_profile(self, value):

        if not value:
            self.log.debug('No environment currently set')
            return {}

        # This is really dangerous, we are not checking
        # where we are loading this file from. Whatever is
        # passed here will be run though a YAML decoder
        # this is definitely a security risk
        # Whatever the user executing this script has read access
        # to is fair game.

        if os.path.isabs(value):
            self.log.debug('Loading environment data for %s', value)
            env_key = os.path.basename(value)
            self.session['environment'] = env_key
            return self.load_file(value)
        else:
            self.log.debug('Loading environment profile for %s', value)
            env_paths = self.env_profile_paths(
                self.data['project'],
                value)

            env = self.load_file(*env_paths)

            if not env:
                self.log.error('No environment profile information found in %s', env_paths)
                raise InvalidEnvironment

            return env

    def load_config(self, local_config, project_config=None, global_config=None):
        self.log.debug('Loading configuration')
        local_data = {}

        if not local_config:
            local_config = os.path.join(self.local_path(), 'config')

        self.log.debug('Loading local config: %s', local_config)
        local_data = self.load_file(local_config)

        if not local_data:
            raise ConfigNotFound

        with config_key_error():
            project = local_data['project']
            self.log.debug('Project name is: %s', project)

        if not global_config:
            global_config = os.path.join(self.user_path(), 'config')

        if not project_config:
            project_config = os.path.join(self.project_path(project), 'config')

        self.log.debug(
            'Loading global and project configs: %s, %s',
            global_config, project_config)

        data = self.load_file(global_config, project_config)
        data.update(local_data)

        return data
