#!/bin/bash
mkdir -p /etc/salt
echo "{{ master }}" > /etc/salt/master
echo "{{ config }}" > /etc/salt/cloudseed; chmod 600 /etc/salt/cloudseed
echo "{{ profile }}" > /etc/salt/cloudseed.profile; chmod 600 /etc/salt/cloudseed.profile

{% for item in  extras %}
{{ item }}
{% endfor %}

add-apt-repository ppa:saltstack/salt
apt-get update
apt-get install -y -o DPkg::Options::=--force-confold salt-master
apt-get install -y git python-pip
pip install gitpython
