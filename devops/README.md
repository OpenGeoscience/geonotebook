## Development Operations

### Local deployment
Local operation of the geonotebook currently requires a running geoserver to tile raster data for visualization. If you have a pre-existing geoserver available then you may edit the ```geonotebook.ini``` configuration file,  pointing the ```url``` variable under the ```[geoserver]``` section to this location.  Otherwise,  if you have vagrant installed,  you may launch a local virtual machine running geoserver by:
```
cd geoserver/
vagrant up
```

This will provision a default installation of geoserver on an Ubuntu 16.04 virtual machine located at http://127.0.0.1:8080/geoserver.

### AWS deployment
The geonotebook can also be deployed to AWS as a [jupyter hub](https://github.com/jupyterhub/jupyterhub) instance using ansible and the provided ```site.yml``` playbook. To do this copy the ```local_vars.example.yml``` to ```local_vars.yml``` and edit the variables to suit your needs (descriptions of required variables can be found in the comments of the file).  Once edited,  the instance may be launched with the following commands:

```
# Make sure boto is installed
pip install -r requirements.txt

# Launch and provision the instance
ansible-playbook -i localhost, -e @local_vars.yml site.yml
```

The instance may be terminated by running:

```
ansible-playbook -i localhost, -e @local_vars.yml -e state=absent site.yml
```
