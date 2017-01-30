Vagrant provisioning for Geonotebook
==================================

Running
-------
From the root of the directory, running `vagrant up` will result in a running virtual machine with a message like this one:
```
Geonotebook is running at http://localhost:8888
```


Configurable Options
--------------------
Through the use of Ansible extra_vars, any of the variables documented in the [Geonotebook role docs](devops/roles/geonotebook) can be manipulated.


Environment Variables
---------------------
| variable                 | comments                                                                    |
| ------------------------ | --------------------------------------------------------------------------- |
| VAGRANT_MEMORY           | The number (in MB) of RAM to use on the virtual machine (defaults to 2048). |
| VAGRANT_CPUS             | The number of CPUs to use on the virtual machine (defaults to 2).           |
| GEONOTEBOOK_DIR          | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |
| GEONOTEBOOK_VERSION      | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |
| GEONOTEBOOK_UPDATE       | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |
| GEONOTEBOOK_FORCE        | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |
| GEONOTEBOOK_AUTH_ENABLED | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |
| GEONOTEBOOK_AUTH_TOKEN   | Documentation for this can be found in the [Geonotebook role docs](devops/roles/geonotebook).       |


Jupyter Auth
------------
By default, Jupyter authentication is disabled in the Vagrant environment as it's meant to be a development environment. Jupyter authentication should always be enabled on production systems.

If Jupyter authentication is desired, the environment variables related to `GEONOTEBOOK_AUTH_*` must be set, note the auth token must be set to the same token each time the machine is provisioned.
