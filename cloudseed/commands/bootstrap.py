'''
usage:
  cloudseed bootstrap <profile>

options:
  -h, --help               Show this screen.
  <profile>                The profile name in your .cloudseed/ folder to load

'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    profile = args['<profile>']
    config.activate_profile(profile)
    provider = config.provider
    # provider.?????
