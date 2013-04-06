'''
usage:
  cloudseed bootstrap <environment>

options:
  -h, --help               Show this screen.
  <environment>                The profile name in your .cloudseed/ folder to load

'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    environment = args['<environment>']
    config.activate_environment(environment)
    #config.provider.bootstrap()
