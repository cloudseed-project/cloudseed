'''
usage: cloudseed status
'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)
