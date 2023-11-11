# Ansible Collection - nephelaiio.mongodb

[![Build Status](https://github.com/nephelaiio/ansible-collection-mongodb/actions/workflows/molecule.yml/badge.svg)](https://github.com/nephelaiio/ansible-collection-mongodb/actions/wofklows/molecule.yml)
[![Ansible Galaxy](http://img.shields.io/badge/ansible--galaxy-nephelaiio.mongodb.vim-blue.svg)](https://galaxy.ansible.com/ui/repo/published/nephelaiio/mongodb/)

An [ansible collection](https://galaxy.ansible.com/ui/repo/published/nephelaiio/mongodb/) to install and manage MongoDB clusters

## Collection roles

* nephelaiio.mongodb.mongos
* nephelaiio.mongodb.mongodb

## Collection playbooks

* nephelaiio.mongodb.install: Install and (re)configure cluster
* nephelaiio.mongodb.offline: Stop mongos cluster services
* nephelaiio.mongodb.online: Start mongos cluster services
* nephelaiio.mongodb.stop: Stop all cluster services
* nephelaiio.mongodb.start: Start all cluster services

## Testing

Please make sure your environment has [docker](https://www.docker.com) installed in order to run role validation tests. Additional python dependencies are listed in the [requirements file](https://github.com/nephelaiio/ansible-role-requirements/blob/master/requirements.txt)

Role is tested against the following distributions (docker images):

  * Ubuntu Focal
  * Ubuntu Bionic
  * Debian Bookworm

You can test the collection directly from sources using command `make test`

## License

This project is licensed under the terms of the [MIT License](/LICENSE)
