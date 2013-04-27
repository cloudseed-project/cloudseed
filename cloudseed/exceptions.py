class CloudseedError(RuntimeError):
    '''An unexpected condition occurred'''


class NoProjectInConfig(CloudseedError):
    '''No provider defined in config'''


class ConfigNotFound(CloudseedError):
    '''Cloudseed config not found'''


class InvalidEnvironment(CloudseedError):
    '''Invalid Cloudseed environment'''


class UnknownConfigProvider(KeyError, CloudseedError):
    '''Unable to load requester provider'''


class ProviderError(CloudseedError):
    '''Provider was unable to fullfill request'''


class MissingIdentity(CloudseedError):
    '''Missing required identity'''


class MissingConfigKey(KeyError, CloudseedError):
    '''Missing required config key'''


class MissingProfileKey(KeyError, CloudseedError):
    '''Missing required profile key'''


class MissingSessionKey(KeyError, CloudseedError):
    '''Missing required session key'''


class KeyAndPairAlreadyExist(CloudseedError):
    ''' ec2 keypair already exists '''


class KeyNotFound(CloudseedError):
    ''' missing pem file that should exists '''


