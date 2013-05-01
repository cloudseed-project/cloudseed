'''
usage:
  cloudseed destroy <environment>


options:
  -h, --help            Show this screen.
  <environment>         Destroys a server environment (master and all boxes)

'''
import sys
import logging
from docopt import docopt
from cloudseed.exceptions import UnknownConfigProvider

log = logging.getLogger(__name__)


def run(config, argv):
    args = docopt(__doc__, argv=argv)
    env = args['<environment>']

    current_env = config.environment

    if env:

        answer = raw_input(
            'Are you sure you want to destroy \'{0}\' [y/N] '\
            .format(env))

        if answer.lower() in ('y', 'yes', 'true', 't', '1'):

            if env != current_env:
                config.activate_environment(env)

            # for now we assume that all instances will be
            # on the same provider as the master
            profile = config.profile['master']

            try:
                provider = config.provider_for_profile(profile)
            except UnknownConfigProvider as e:
                sys.stdout.write(
                    'Unknown config provider \'{0}\', unable to continue.\n'\
                    .format(e.message))
                return

            sys.stdout.write('Destroying environment \'{0}\'\n'.format(env))
            provider.kill_all_instances(config)

            if current_env != env:
                config.activate_environment(current_env)
