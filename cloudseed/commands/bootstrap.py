'''
usage:
  cloudseed bootstrap <profile>

options:
  -h, --help

'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    try:
        provider = config['provider']
    except KeyError:
        pass
    #import pdb; pdb.set_trace()
