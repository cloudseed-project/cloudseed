import os


def add_key_for_config(key, config):
    data = config.data

    filename = '{0}_{1}_{2}'.format(
        data['project'],
        data['session'],
        data['provider'])

    path = '{0}/.cloudseed/{1}/{2}'.format(
        os.path.expanduser('~'),
        data['project'],
        filename)

    with open(path, 'w') as target:
        target.write(key)

    return path
