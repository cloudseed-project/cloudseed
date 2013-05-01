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

        self.script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources'))]

        self.master_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'masters'))]

        self.minion_script_paths = [os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'resources', 'minions'))]

        # TODO: EXPOSE MASTER AND MINION CONFIG PATHS SOME HOW
        # LOAD PROJECT FIRST THEN LOAD LOCAL AND MERGE THEM

    def provider_for_profile(self, profile):
        provider_name = profile['provider']

        try:
            provider_config = self.providers[provider_name]
        except KeyError:
            self.log.error('Unable to locate provider \'%s\'', provider_name)
            raise UnknownConfigProvider(provider_name)

        return self.provider_for_config(provider_config)

    def provider_for_config(self, config):
        name = config['provider']

        try:
            em = driver.DriverManager(
                'com.cloudseed.providers',
                name,
                invoke_on_load=True,
                invoke_kwds={'provider': config})
            return em.driver
        except RuntimeError:
            self.log.error('Unknown Config Provider %s', name)
            raise UnknownConfigProvider(name)

    @property
    def data(self):
        return self.resource.data

    @property
    def environment(self):
        return self.resource.environment()

    @property
    def providers(self):
        return self.resource.providers

    @property
    def profile(self):
        return self.resource.profile

    def update_providers(self, data):
        self.log.debug('Updating providers with %s', data)
        self.resource.update_providers(data)

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
    def __init__(self, data, session=None, profile=None, providers=None):

        with config_key_error():
            data['project']

        self.data = data
        self.providers = {} if providers is None else providers
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
        profile_config=None,
        provider_config=None):

        self.local_config = local_config

        try:
            self.data = self.load_config(
                local_config,
                project_config,
                global_config)
        except ConfigNotFound:
            self.log.warning('No config found, operations will be limited')
            self.data = {}
            self.profile = {}
            return

        self.providers = self.load_providers(provider_config)
        self.profile = self.load_profile(profile_config)

    def update_providers(self, data):
        path = os.path.join(
            self.local_path(),
            'providers')

        self.log.debug('Updating providers %s', path)

        providers = self.load_file(path)
        providers.update(data)

        self.write_file(path, providers)
        self.providers.update(data)

    def update_config(self, data):
        path = os.path.join(
            self.current_env(),
            'config')

        self.log.debug('Updating config %s', path)

        config = self.load_file(path)
        config.update(data)

        self.write_file(path, config)
        self.data.update(data)

    def environment(self):
        local_path = self.local_path()
        current = os.path.join(local_path, 'current')

        if os.path.exists(current):
            env_path = os.readlink(current)
            return os.path.basename(env_path)

    def activate_environment(self, value):

        local_path = self.local_path()

        current = os.path.join(local_path, 'current')
        next = os.path.join(local_path, value)

        env_key = self.environment()

        if value == env_key:
            self.log.debug('Current environment is already active: %s', value)
            return

        if os.path.islink(current):
            self.log.debug('Removing old symlink to: %s', os.readlink(current))
            os.unlink(current)

        self.log.debug('Creating symlink to: %s', next)
        os.symlink(next, current)

        self.data = self.load_config()
        self.providers = self.load_providers()
        self.profile = self.load_profile()

    def env_profile_paths(self, project):

        project_env = os.path.join(
            self.project_path(project),
            'profile')

        local_env = os.path.join(
            self.current_env(),
            'profile')

        return [project_env, local_env]

    def load_providers(self, provider_config=None):
        self.log.debug('Loading provider data')
        providers = {}

        if provider_config:
            providers = self.load_file(provider_config)
        else:
            with config_key_error():
                project = self.data['project']

                project_path = self.project_path(project)
                project_providers = os.path.join(project_path, 'providers')
                providers = self.load_file(project_providers)

            local_path = self.local_path()
            local_providers = os.path.join(local_path, 'providers')
            providers.update(self.load_file(local_providers))

        return providers

    def load_profile(self, profile_config=None):

        if not self.environment() and not profile_config:
            self.log.debug('No environment or profile currently provided')
            return {}

        # This is really dangerous, we are not checking
        # where we are loading this file from. Whatever is
        # passed here will be run though a YAML decoder
        # this is definitely a security risk
        # Whatever the user executing this script has read access
        # to is fair game.

        if profile_config and os.path.isabs(profile_config):
            self.log.debug('Loading profile data for %s', profile_config)
            return self.load_file(profile_config)
        else:
            env_paths = self.env_profile_paths(
                self.data['project'])

            self.log.debug('Loading profiles %s', env_paths)
            env = self.load_file(*env_paths)

            if not env:
                self.log.error('No environment profile information found in %s', env_paths)
                raise InvalidEnvironment

            return env

    def load_config(self, local_config=None, project_config=None, global_config=None):
        self.log.debug('Loading configuration')
        local_data = {}
        env_config = None

        if not local_config:
            local_config = os.path.join(self.local_path(), 'config')
            env_config = os.path.join(self.current_env(), 'config')

        self.log.debug('Loading local config: %s', local_config)
        local_data = self.load_file(local_config, env_config)

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
