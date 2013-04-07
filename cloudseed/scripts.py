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
  -c --config=<config>    config to use [default: ./.cloudseed/config]
  -p --profile=<profile>  profile to use
  -h --help               show this screen.
  --version               show version.

common commands:
    init <project>            initialize a new .cloudseed <project>
    init env <environment>    initialize a new .cloudseed <environment> for the current project
    bootstrap <environment>   deploy a salt master for the specified <environment>
    ssh                       ssh into the master server, requires bootstrap
    status                    current cloudseed status
    env <environment>         charge cloudseed environment to specified <environment>
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    try:
        profile = args['--profile'][0]
    except IndexError:
        profile = None

    config = Config(FilesystemConfig(local_config=args['--config'][0],
        profile_config=profile))

    if command == 'init':
        from cloudseed.commands import initialize
        initialize.run(config, argv)

    elif command == 'bootstrap':
        from cloudseed.commands import bootstrap
        bootstrap.run(config, argv)

    elif command == 'ssh':
        from cloudseed.commands import ssh
        ssh.run(config, argv)

    elif command == 'status':
        from cloudseed.commands import status
        status.run(config, argv)

    elif command == 'env':
        from cloudseed.commands import env
        env.run(config, argv)

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

