import os
from subprocess import call


def create_key_for_name(instance_name, key_dir='/tmp'):
    pub = os.path.join(key_dir, '{0}.pub'.format(instance_name))
    pem = os.path.join(key_dir, '{0}.pem'.format(instance_name))

    if os.path.isfile(pub):
        os.unlink(pub)

    if os.path.isfile(pem):
        os.unlink(pem)

    cmd = 'salt-key --gen-keys-dir={0} --gen-keys={1}'\
    .format(key_dir, instance_name)

    call(cmd, shell=True)

    return (pub, pem)
