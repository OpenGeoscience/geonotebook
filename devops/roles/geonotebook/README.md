geonotebook
===========

An Ansible role to install [Geonotebook](https://github.com/opengeoscience/geonotebook).

Requirements
------------

This is intended to be run on a clean Ubuntu 16.04 system.

Role Variables
--------------

| parameter                | required | default          | comments                                                                                                                        |
| ------------------------ | -------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| geonotebook_dir          | no       | /opt/geonotebook | Path to download and build Geonotebook in.                                                                                      |
| geonotebook_version      | no       | master           | Git commit-ish for fetching Geonotebook.                                                                                        |
| geonotebook_update       | no       | no               | Whether provisioning should fetch new versions via git.                                                                         |
| geonotebook_force        | no       | no               | Whether provisioning should discard modified files in the working directory.                                                    |
| geonotebook_auth_enabled | no       | yes              | Whether or not Jupyter token based authentication should be enabled.                                                            |
| geonotebook_auth_token   | no       |                  | A token to use for Jupyter token based authentication. If this is blank, it is equivalent to geonotebook_auth_enabled being no. |
