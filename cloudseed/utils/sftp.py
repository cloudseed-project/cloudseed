import os
import paramiko


def connect(hostname, username, identity):

    if os.path.isabs(identity):
        return client(
            hostname=hostname,
            username=username,
            identity=identity)
    else:
        return client(
            hostname=hostname,
            username=username,
            password=identity)


def client(hostname, identity=None, username=None, password=None, port=22):
    t = paramiko.Transport((hostname, port))

    if identity:
        pkey = paramiko.RSAKey.from_private_key_file(identity)
        t.connect(username=username, pkey=pkey)
    elif password:
        t.connect(username=username, password=password)

    return paramiko.SFTPClient.from_transport(t)


def put(client, local_path, remote_path):
    client.put(
        localpath=local_path,
        remotepath=remote_path)

