from __future__ import print_function

import os
import shlex
import subprocess

from . import config


def _get_address(instance_ip):

    username = config.get('ssh.username')

    # Don't add the username to the address when it is the current user,
    # because it would make no difference.
    if username == os.environ.get('USER'):
        username = None

    if username:
        return username + '@' + instance_ip
    else:
        return instance_ip


def connect(instance, bastion, cmd):

    command = ['ssh']

    if config.get('verbose'):
        command += ['-v']

    if cmd:
        command += ['-t']

    user_known_hosts_file = config.get('ssh.user_known_hosts_file')
    if user_known_hosts_file:
        command += ['-o', 'UserKnownHostsFile={}'.format(user_known_hosts_file)]

    if bastion:
        instance_ip = get_ip(bastion, connect_through_bastion=False)
        config.add('bastion.address', _get_address(instance_ip))
        proxy_command = config.get('ssh.proxy_command')
        command += ['-o', 'ProxyCommand={}'.format(proxy_command)]

    instance_ip = get_ip(instance, connect_through_bastion=bool(bastion))
    command += [_get_address(instance_ip)]

    if cmd:
        command += shlex.split(cmd)

    print('[ssha] running {}'.format(format_command(command)))
    subprocess.call(command)


def format_command(command):
    args = []
    for arg in command:
        if ' ' in arg:
            args.append('"' + arg + '"')
        else:
            args.append(arg)
    return ' '.join(args)


def get_ip(instance, connect_through_bastion):
    if connect_through_bastion:
        return instance['PrivateIpAddress']
    return instance.get('PublicIpAddress') or instance['PrivateIpAddress']
