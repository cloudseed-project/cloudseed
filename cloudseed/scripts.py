import sys
from subprocess import call
import yaml
from docopt import docopt
import cloudseed
from cloudseed.exceptions import (NoProviderInConfig)


def cloudseed_main():
    '''
usage:
  cloudseed [--version] [--help] [-c|--config=<config>]
            <command> [<args>...]

options:
  -c --config=<config>    Profile to use [default: ./.cloudseed/config]
  -h --help               Show this screen.
  --version               Show version.

common commands:
    bootstrap <profile>   Deploy a Salt Master based on a .cloudseed profile
    init                  Initialize a new .cloudseed configuration
    status                Current cloudseed status
    '''

    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    with open(args['--config'][0]) as cfg:
        config = yaml.load(cfg)

    _validate_config(config)

    if command == 'init':
        from cloudseed.commands import initialize
        initialize.run(config, argv)

    elif command == 'bootstrap':
        from cloudseed.commands import bootstrap
        bootstrap.run(config, argv)

    elif args['<command>'] in ('help', None):
        exit(call(['cloudseed', '--help']))

    else:
        exit('{0} is not a cloudseed command. See \'cloudseed --help\'.' \
            .format(args['<command>']))


def _validate_config(config):
    try:
        provider = config['provider']
    except KeyError:
        raise NoProviderInConfig

    # plugin to validate provider config
