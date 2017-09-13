# ansible-checker
A script to check if all playbooks would run OK

[![Build Status](https://travis-ci.org/sebastiendarocha/ansible-checker.svg?branch=master)](https://travis-ci.org/sebastiendarocha/ansible-checker)

## Install

* Copy the files in your ansible.cfg directory (i.e. /etc/ansible/)
* Move to your ansible dir.
* Disable the "retry\_files\_enabled" parameter, it would break the script if a machine is unreachable or as an error.
* Fill your ansible.yml setup file
* Call the script and it will call all the playbooks in the specified environments.


## Compatibility

Tested with Ansible 2.3.2 and Python 3.4, 3.5 and 3.6
