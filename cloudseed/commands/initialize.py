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
import yaml
import uuid
import sys
from subprocess import call
from docopt import docopt


def run(argv):
    args = docopt(__doc__, argv=argv)
    if args['<name>'] == 'env':
        sys.stdout.write('\nname cant be "env"\n\n')
        exit(call(['cloudseed', 'init', '--help']))
    elif args['<name>'] is not None:
        init_cloudseed_project(args)
    elif args['<environment>'] is not None:
        if not os.path.isdir('./.cloudseed'):
            sys.stdout.write("\nmust call 'cloudseed init <name>' first\n\n")
            exit(call(['cloudseed', 'init', '--help']))
        init_cloudseed_environment(args)


def init_cloudseed_environment(args):
    env_name = args['<environment>']
    cwd = os.getcwd()
    local_dir = '{0}/{1}'.format(cwd, '.cloudseed')
    env_dir = '{0}/{1}'.format(local_dir, env_name)
    
    if not os.path.isdir(env_dir):
        os.mkdir(env_dir)



    profile = {
        "bootstrap":{
            'image':'#place image here',
            'size': '#place size here',
            'script': '#insert script here (optional)',
            'ssh_username':'#insert ssh username',
        }
    }
    profile_path= '{0}/profile'.format(env_dir)
    
    if os.path.exists(profile_path):
        sys.stdout.write("{0} already exists, will not overwrite\n\n".format(profile_path))
    else:
        with open(profile_path, 'w') as cfg:
            cfg.write(yaml.dump(profile, default_flow_style=False))

    master = {
        "fileserver_backend":[
            'roots',
            'git'
        ],
        'gitfs_remotes':[
          'git://github.com/your/salt-states.git'  
        ]
    }
    
    master_path= '{0}/master'.format(env_dir)
    if os.path.exists(master_path):
        sys.stdout.write("{0} already exists, will not overwrite\n\n".format(master_path))
    else:
        with open(master_path, 'w') as cfg:
            cfg.write(yaml.dump(master, default_flow_style=False))
    

def init_cloudseed_project(args):
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
