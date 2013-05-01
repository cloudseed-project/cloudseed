def create_master(config):

    profile = config.profile['master']

    # raises UnknownConfigProvider
    provider = config.provider_for_profile(profile)

    provider_name = profile['provider']
    provider_config = config.providers[provider_name]

    before_identity = hash(tuple(provider_config.itervalues()))
    result = provider.bootstrap(profile, config)
    after_identity = hash(tuple(provider_config.itervalues()))

    if before_identity != after_identity:
        config.update_providers({provider_name: provider_config})

    config.update_config({'master': result})


def create_instance():
    pass
