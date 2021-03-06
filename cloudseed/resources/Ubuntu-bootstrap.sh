#!/bin/bash
mkdir -p /etc/salt/cloudseed
echo "{{ data.salt.master }}" > /etc/salt/master
echo "{{ data.salt.minion }}" > /etc/salt/minion
echo "{{ data.cloudseed.providers }}" > /etc/salt/cloudseed/providers; chmod 600 /etc/salt/cloudseed/providers
echo "{{ data.cloudseed.profiles }}" > /etc/salt/cloudseed/profile; chmod 600 /etc/salt/cloudseed/profile
echo "{{ data.cloudseed.config }}" > /etc/salt/cloudseed/config; chmod 600 /etc/salt/cloudseed/config

{% for item in data.cloudseed.ssh_keys -%}
{{ item }}
{% endfor -%}

# add-apt-repository requires an additional dep and is in different packages
# on different systems. Although seemingly ubiquitous it is not a standard,
# and is only a convenience script intended to accomplish the below two steps
# doing it this way is universal across all debian and ubuntu systems.
echo deb http://ppa.launchpad.net/saltstack/salt/ubuntu `lsb_release -sc` main | tee /etc/apt/sources.list.d/saltstack.list
wget -q -O- "http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x4759FA960E27C0A6" | apt-key add -

apt-get update
apt-get install -y git python-pip
pip install gitpython
apt-get install -y -o DPkg::Options::=--force-confold salt-master
salt-key --gen-keys=master
cp master.pub /etc/salt/pki/master/minions/master
mkdir -p /etc/salt/pki/minion
mv master.pub /etc/salt/pki/minion/minion.pub
mv master.pem /etc/salt/pki/minion/minion.pem
apt-get install -y -o DPkg::Options::=--force-confold salt-minion
sleep 3; /usr/bin/salt "master" state.highstate
