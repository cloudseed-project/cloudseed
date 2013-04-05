'''
usage:
  cloudseed ssh

options:
  -h, --help               Show this screen.
'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    profile = args['<profile>']
    config.activate_profile(profile)
    config.provider.bootstrap()
