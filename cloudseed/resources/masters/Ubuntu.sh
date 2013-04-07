#!/bin/bash
mkdir -p /etc/salt
echo "{{ master }}" > /etc/salt/master
echo "{{ minion }}" > /etc/salt/minion
echo "{{ config }}" > /etc/salt/cloudseed; chmod 600 /etc/salt/cloudseed
echo "{{ profile }}" > /etc/salt/cloudseed.profile; chmod 600 /etc/salt/cloudseed.profile

{% for item in  extras %}
{{ item }}
{% endfor %}

add-apt-repository ppa:saltstack/salt
apt-get update
apt-get install -y git python-pip
pip install gitpython
apt-get install -y -o DPkg::Options::=--force-confold salt-master
salt-key --gen-keys=master
cp master.pub /etc/salt/pki/master/minions/master.pub
mkdir -p /etc/salt/pki/minion
mv master.pub /etc/salt/pki/minion/minion.pub
mv master.pem /etc/salt/pki/minion/minion.pem
apt-get install -y -o DPkg::Options::=--force-confold salt-minion
salt 'master' state.highstate
