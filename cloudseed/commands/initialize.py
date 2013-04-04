'''
usage:
  cloudseed init <name>

options:
  -h, --help            Show this screen.
  <name>                The name of the cloudseed project.

'''
import os
import yaml
import uuid
from docopt import docopt


def run(argv):
    args = docopt(__doc__, argv=argv)

    cwd = os.getcwd()
    project_dir = '{0}/{1}'.format(cwd, '.cloudseed')

    project_name = args['<name>']

    user_dir = '{0}/.cloudseed'.format(os.path.expanduser('~'))
    project_dir = '{0}/{1}'.format(user_dir, project_name)
    local_dir = '{0}/{1}'.format(cwd, '.cloudseed')
    session_id = uuid.uuid4().hex

    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)

    if not os.path.isdir(project_dir):
        os.mkdir(project_dir)

    if not os.path.isdir(local_dir):
        os.mkdir(local_dir)

    config = {
    'project': project_name,
    'session': session_id
    }

    local_config_path = '{0}/config'.format(local_dir)
    with open(local_config_path, 'w') as cfg:
        cfg.write(yaml.dump(config, default_flow_style=False))

    session_path = '{0}/session_{1}'.format(project_dir, session_id)
    with open(session_path, 'w') as session:
        data = {
        'profile': None,
        'path': local_dir
        }

        session.write(yaml.dump(data, default_flow_style=False))
