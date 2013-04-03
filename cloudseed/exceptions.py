class CloudseedException(RuntimeError):
    '''An unexpected condition occurred'''


class NoProviderInConfig(CloudseedException):
    '''No provider defined in config'''
