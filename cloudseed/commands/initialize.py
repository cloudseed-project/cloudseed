'''
usage:
  cloudseed init env <environment>
  cloudseed init <name>

options:
  -h, --help            Show this screen.
  <name>                The name of the cloudseed project.
  <environment>         Initialize a new environment

'''
import os
import logging
import sys
from subprocess import call
from docopt import docopt
from cloudseed.utils.filesystem import (Filesystem)

log = logging.getLogger(__name__)


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    if args['<name>'] == 'env':
        sys.stdout.write('\nname cant be "env"\n\n')
        exit(call(['cloudseed', 'init', '--help']))
    elif args['<name>'] is not None:
        init_cloudseed_project(config, args)
    elif args['<environment>'] is not None:
        if not os.path.isdir('./.cloudseed'):
            sys.stdout.write("\nmust call 'cloudseed init <name>' first\n\n")
            exit(call(['cloudseed', 'init', '--help']))
        init_cloudseed_environment(config, args)


def init_cloudseed_environment(config, args):
    env_name = args['<environment>']
    project_name = config.data['project']

    write_file = Filesystem.write_file

    env_dir = Filesystem.local_env_path(env_name)
    profile_path = os.path.join(env_dir, 'profile')
    master_path = os.path.join(env_dir, 'master')
    config_path = os.path.join(env_dir, 'config')
    project_env_dir = Filesystem.project_env_path(project_name, env_name)

    profile = {
        'bootstrap': {
            'image': '<server image>',
            'size': '<server size>',
            'script': '<bootstrap script>',
            'ssh_username': '<ssh username>',
        }
    }

    master = {
        'fileserver_backend': [
            'roots',
            'git'
        ],
        'gitfs_remotes': [
          'git://github.com/your/salt-states.git'
        ]
    }

    config = {

    }

    if not os.path.isdir(env_dir):
        log.debug('Creating directory %s', env_dir)
        os.mkdir(env_dir)

    if os.path.exists(profile_path):
        log.debug('%s already exists, will not overwrite', profile_path)
    else:
        write_file(profile_path, profile)

    if os.path.exists(config_path):
        log.debug('%s already exists, will not overwrite', config_path)
    else:
        open(config_path, 'w').close()

    if os.path.exists(master_path):
        log.debug('%s already exists, will not overwrite', master_path)
    else:
        write_file(master_path, master)

    if not os.path.isdir(project_env_dir):
        os.mkdir(project_env_dir)

        project_env_profile = os.path.join(project_env_dir, 'profile')
        project_env_master = os.path.join(project_env_dir, 'master')

        log.debug(
            'Creating empty project profile %s',
            project_env_profile)

        open(project_env_profile, 'w').close()

        log.debug(
            'Creating empty project master %s',
            project_env_master)

        open(project_env_master, 'w').close()


def init_cloudseed_project(config, args):
    write_file = Filesystem.write_file
    project_name = args['<name>']

    user_dir = Filesystem.user_path()
    local_dir = Filesystem.local_path()
    project_dir = Filesystem.project_path(project_name)

    local_config_path = os.path.join(local_dir, 'config')

    local_data = {
        'project': project_name,
    }

    if not os.path.isdir(user_dir):
        log.debug('Creating directory %s', user_dir)
        os.mkdir(user_dir)

        # make empty global level config
        global_config = os.path.join(user_dir, 'config')
        log.debug('Creating empty config %s', global_config)
        open(global_config, 'w').close()

    if not os.path.isdir(project_dir):
        log.debug('Creating directory %s', project_dir)
        os.mkdir(project_dir)

        # make empty project level config
        project_config = os.path.join(project_dir, 'config')
        session_config = os.path.join(project_dir, 'session')

        log.debug('Creating empty config %s', project_config)
        open(project_config, 'w').close()

        log.debug('Creating empty session %s', session_config)
        open(session_config, 'w').close()

    if not os.path.isdir(local_dir):
        log.debug('Creating directory %s', local_dir)
        os.mkdir(local_dir)

    if not os.path.isfile(local_config_path):
        write_file(local_config_path, local_data)
