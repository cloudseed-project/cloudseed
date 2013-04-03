import optparse
from saltcloud.utils import parsers


class CloudseedConfigMixIn(parsers.SaltCloudParser):
    __metaclass__ = parsers.MixInMeta
    _mixin_prio_ = 0    # First options seen

    def _mixin_setup(self):
        self.master_config = {}
        self.cloud_config = {}
        self.profiles_config = {}
        group = self.config_group = optparse.OptionGroup(
            self,
            "Configuration Options",
            # Include description here as a string
        )
        group.add_option(
            '-C', '--cloud-config',
            default='./.cloudseed/config',
            help='The location of the saltcloud config file. Default: %default'
        )

        group.add_option(
            '-V', '--profiles', '--vm_config',
            dest='vm_config',
            default=None,
            help='The location of the saltcloud VM config file. '
                 'Default: ./.cloudseed/cloud.profiles'
        )

        self.add_option_group(group)
