#!/bin/bash
mkdir -p /etc/salt
echo "{{ master }}" > /etc/salt/master

add-apt-repository ppa:saltstack/salt
apt-get update
apt-get install -y -o DPkg::Options::=--force-confold salt-master
apt-get install -y git python-pip
pip install gitpython




