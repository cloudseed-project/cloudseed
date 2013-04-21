import paramiko


def run(client, command):
    client.exec_command(command)


def client(hostname, identity=None, username=None, password=None, port=22):

    if identity:
        return _client_with_identity(hostname, port, username, identity)
    elif username and password:
        return _client_with_password(hostname, port, username, password)


def _client_with_identity(hostname, port, username, identity):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        key_filename=identity)
    return client


def _client_with_password(hostname, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=hostname,
        port=port,
        username=username,
        password=password)

    return client
