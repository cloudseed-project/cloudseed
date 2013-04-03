class CloudseedException(RuntimeError):
    '''An unexpected condition occurred'''


class NoProviderInConfig(CloudseedException):
    '''No provider defined in config'''


class NoProjectInConfig(CloudseedException):
    '''No provider defined in config'''


class ConfigNotFound(CloudseedException):
    '''Cloudseed config not found'''


class UnknownConfigProvider(CloudseedException):
    '''Unable to load requester provider'''
