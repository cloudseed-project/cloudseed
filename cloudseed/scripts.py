from subprocess import call
import yaml
from docopt import docopt
import cloudseed


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
    bootstrap     Deploy a Salt Master based on your .cloudseed configuration
    init          Initialize a new .cloudseed configuration
    '''

    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    with open(args['--config'][0]) as cfg:
        config = yaml.load(cfg)

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


# def cloudseed_init(argv):
#     action = commands.Initialize()
#     action.start(argv[1:])


# def cloudseed_bootstrap(argv):
#     '''
# usage:
#   cloudseed bootstrap <profile> [-c|--config=<config>]

# options:
#   -c --config=<config>    Profile to use [default: ./.cloudseed/config]

#     '''
#     import pdb; pdb.set_trace()
#     action = commands.Bootstrap()
#     action.start(argv[1:])
