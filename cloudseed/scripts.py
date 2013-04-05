from __future__ import absolute_import
from subprocess import call
from docopt import docopt
from docopt import DocoptExit
import cloudseed
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig


def cloudseed_main():
    '''
usage:
  cloudseed [--version] [--help] [-c|--config=<config>] [-p|--profile=<profile>]
            <command> [<args>...]

options:
  -c --config=<config>    Config to use [default: ./.cloudseed/config]
  -p --profile=<profile>  Profile to use
  -h --help               Show this screen.
  --version               Show version.

common commands:
    bootstrap <profile>   Deploy a Salt Master based on a .cloudseed profile
    init <name>           Initialize a new .cloudseed configuration
    status                Current cloudseed status
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    if command == 'init':
        from cloudseed.commands import initialize
        initialize.run(argv)
    else:

        try:
            profile = args['--profile'][0]
        except IndexError:
            profile = None

        config = Config(FilesystemConfig(local_config=args['--config'][0],
                                        profile_config=profile))

        if command == 'bootstrap':
            from cloudseed.commands import bootstrap
            bootstrap.run(config, argv)

        if command == 'ssh':
            from cloudseed.commands import ssh
            ssh.run(config, argv)

        elif args['<command>'] in ('help', None):
            exit(call(['cloudseed', '--help']))

        else:
            exit('{0} is not a cloudseed command. See \'cloudseed --help\'.' \
                .format(args['<command>']))


def main():
    try:
        cloudseed_main()
    except DocoptExit:
        exit(call(['cloudseed', '--help']))

