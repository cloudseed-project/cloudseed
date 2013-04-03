'''
usage:
  cloudseed bootstrap <profile>

options:
  -h, --help               Show this screen.
  <profile>                The profile name in your .cloudseed/ folder to load

'''
import sys
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    try:
        provider = config['provider']
    except KeyError:
        pass
    #import pdb; pdb.set_trace()
