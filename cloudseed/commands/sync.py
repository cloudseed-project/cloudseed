'''
usage:
  cloudseed sync

options:
  -h, --help         Show this screen.

'''
import sys
import os
import tempfile
import tarfile
import logging
from docopt import docopt
from cloudseed.utils.filesystem import Filesystem
from cloudseed.utils import sftp
from cloudseed.utils import ssh
from cloudseed.exceptions import UnknownConfigProvider
from cloudseed.utils.exceptions import (
    profile_key_error, config_key_error, ssh_client_error
)


log = logging.getLogger(__name__)


def salt_master_config(config):

    project = config.data['project']

    master_project_path = os.path.join(
        Filesystem.project_path(project),
        'master')

    master_env_path = os.path.join(
        Filesystem.current_env(),
        'master'
        )

    merged_master = Filesystem.load_file(master_project_path, master_env_path)

    return merged_master


def run(config, argv):

    args = docopt(__doc__, argv=argv)

    # This is what we will be using or something like it:
    with ssh_client_error():
        ssh_client = ssh.client_for_config(config)

    # this is what makes up the above
    profile = config.profile['master']
    identity = None
    hostname = None
    username = None

    try:
        provider = config.provider_for_profile(profile)
    except UnknownConfigProvider as e:
        sys.stdout.write(
            'Unknown config provider \'{0}\', unable to continue.\n'\
            .format(e.message))
        return

    with profile_key_error():
        username = profile['ssh_username']

    with config_key_error():
        hostname = config.data['master']

    identity = profile.get('ssh_password', provider.ssh_identity())

    if not identity:
        log.error('No identity specificed.\n\
Please set ssh_password on the master profile or provide a private_key \
in your provider for this master')
        return

    current_env = config.environment

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return

    sys.stdout.write('Syncing states for \'{0}\'\n'.format(current_env))

    env_path = Filesystem.local_env_path(current_env)
    states_path = os.path.join(env_path, 'states')

    if not os.path.isdir(states_path):
        sys.stdout.write('States dir not found at \'%s\'\n', states_path)
        return

    master_config = salt_master_config(config)
    sys.stdout.write('Archiving contents at \'{0}\'\n'.format(states_path))

    tmp = tempfile.NamedTemporaryFile(delete=False)

    archive = tarfile.open(fileobj=tmp, mode='w:gz')
    archive.add(states_path, '.')
    archive.close()

    tmp.close()
    log.debug('Archive created at %s', tmp.name)

    try:
        remote_path = master_config['file_roots']['base'][0]
    except KeyError:
        remote_path = '/src/salt'

    remote_file = os.path.join('/tmp', os.path.basename(tmp.name))

    sftp_client = sftp.connect(
        hostname=hostname,
        username=username,
        identity=identity)

    ssh_client = ssh.connect(
        hostname=hostname,
        username=username,
        identity=identity)

    log.debug(
        'Remotely Executing: sudo sh -c "mkdir -p %s; chown -R root:root %s"',
        remote_path, remote_path)

    ssh.run(
        ssh_client,
        'sudo sh -c "mkdir -p {0}; chown -R root:root {0}"'.format(remote_path))

    sys.stdout.write('Transferring archive to \'{0}\'\n'.format(hostname))
    sftp.put(sftp_client, tmp.name, remote_file)
    sys.stdout.write('Unpacking archive to \'{0}\'\n'.format(remote_path))

    log.debug(
        'Remotely Executing: sudo sh -c "tar -C %s -xvf %s; chwon -R root:root %s"',
        remote_path, remote_file, remote_path)

    ssh.run(ssh_client,
        'sudo sh -c "tar -C {0} -xvf {1}; chown -R root:root {0}"'\
        .format(remote_path, remote_file))

    log.debug(
        'Remotely Executing: rm -rf %s',
        remote_file)

    ssh.run(ssh_client,
        'rm -f {0}'\
        .format(remote_file))

    os.unlink(tmp.name)
    sys.stdout.write('Sync complete\n')
