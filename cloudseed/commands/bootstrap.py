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

    # TODO: use a SYM LINK for the environment:
    # ./cloudseed/current -> ./cloudseed/prod
    # then read the basename off the path os.readlink
    # activate_environment should create a symlink to ./cloudseed/current
    # that way you can swithc config options with something like
    # vagrant and you won't need the session anymore as current
    # will represnet it.

    env = args['<environment>']
    current_env = config.environment

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


