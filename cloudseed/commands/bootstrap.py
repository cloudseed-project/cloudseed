'''
usage:
  cloudseed bootstrap [<environment>]

options:
  -h, --help               Show this screen.
  <environment>            The profile name in your .cloudseed/ folder to load

'''
import sys
from docopt import docopt
from cloudseed.exceptions import UnknownConfigProvider


def run(config, argv):
    args = docopt(__doc__, argv=argv)

    env = args['<environment>']
    current_env = config.session.get('environment', None)

    if env:
        if env != current_env:
            config.activate_environment(env)
            current_env = env

    if not current_env:
        sys.stdout.write('No environment available.\n')
        sys.stdout.write('Have you run \'cloudseed init env <environment>\'?\n')
        return

    profile = config.profile['master']

    try:
        provider = config.provider_for_profile(profile)
    except UnknownConfigProvider as e:
        sys.stdout.write(
            'Unknown config provider \'{0}\', unable to continue.\n'\
            .format(e.message))
        return

    provider_name = profile['provider']
    provider_config = config.providers[provider_name]

    sys.stdout.write('Bootstrapping \'{0}\'\n'.format(current_env))
    sys.stdout.write('This may take a minute, please wait...\n')

    before_identity = hash(tuple(provider_config.itervalues()))
    result = provider.bootstrap(profile, config)
    after_identity = hash(tuple(provider_config.itervalues()))

    if before_identity != after_identity:
        config.update_providers({provider_name: provider_config})

    config.update_config({'master': result})


