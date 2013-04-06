'''
usage:
  cloudseed config [options]

options:
  -h, --help               show this screen.
  --environment=<env>      set the current environment for your session

'''
from docopt import docopt


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    environment = args['--environment']

    if environment:
        config.update_session({'profile': environment})

