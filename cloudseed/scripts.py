from __future__ import absolute_import
import logging
from subprocess import call
from docopt import docopt
from docopt import DocoptExit
import cloudseed
from cloudseed.config import Config
from cloudseed.config import FilesystemConfig


def cloudseed_main():
    '''
usage:
  cloudseed [--version] [--verbose] [--help] [-c|--config=<config>] [-p|--profile=<profile>]
            <command> [<args>...]

options:
  -c --config=<config>    config to use
  -p --profile=<profile>  profile to use
  -h --help               show this screen
  --verbose               show debug output
  --version               show version



common commands:
    init <project>            initialize a new .cloudseed <project>
    init env <environment>    initialize a new .cloudseed <environment> for the current project
    bootstrap <environment>   deploy a salt master for the specified <environment>
    ssh                       ssh into the master server, requires bootstrap
    status                    current cloudseed status
    env <environment>         charge cloudseed environment to specified <environment>
    destroy <environment>     destroys all boxes associated with this environment
    deploy <state>            deploy a state to a machine
    sync                      sync states and modules to the currently bootstrapped environment
    '''
    args = docopt(
        cloudseed_main.__doc__,
        version=cloudseed.__version__,
        options_first=True)

    command = args['<command>']
    argv = [args['<command>']] + args['<args>']

    initialize_logging(verbose=args['--verbose'])

    try:
        profile_config = args['--profile'][0]
    except IndexError:
        profile_config = None

    try:
        local_config = args['--config'][0]
    except IndexError:
        local_config = None

    config = Config(FilesystemConfig(
        local_config=local_config,
        profile_config=profile_config))

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

    elif command == 'destroy':
        from cloudseed.commands import destroy
        destroy.run(config, argv)

    elif command == 'deploy':
        from cloudseed.commands import deploy
        deploy.run(config, argv)

    elif command == 'sync':
        from cloudseed.commands import sync
        sync.run(config, argv)

    elif args['<command>'] in ('help', None):
        exit(call(['cloudseed', '--help']))

    else:
        exit('{0} is not a cloudseed command. See \'cloudseed --help\'.' \
            .format(args['<command>']))


def initialize_logging(verbose=False):
    log_level = logging.DEBUG if verbose else logging.INFO

    logger = logging.getLogger('cloudseed')
    logger.setLevel(log_level)

    console = logging.StreamHandler()
    console.setLevel(log_level)

    formatter = logging.Formatter('[%(levelname)s] : %(name)s - %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)


def main():

    try:
        cloudseed_main()
    except DocoptExit:
        exit(call(['cloudseed', '--help']))
    except KeyboardInterrupt:
        pass

