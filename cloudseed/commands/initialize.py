'''
usage: cloudseed init
'''
import os
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    cwd = os.getcwd()
    project_dir = '{0}/{1}'.format(cwd, '.cloudseed')

    try:
        os.mkdir(project_dir)
    except OSError:
        return

    # create base files
    with open('{0}/{1}'.format(project_dir, 'config'), 'w'):
        pass

    with open('{0}/{1}'.format(project_dir, 'development'), 'w'):
        pass

    with open('{0}/{1}'.format(project_dir, 'production'), 'w'):
        pass
