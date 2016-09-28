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
# Make sure ansible and boto are installed
pip install -r requirements.txt

# Make sure boto can authenticate with AWS server
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXX

# Launch and provision the instance
ansible-playbook -i localhost, -e @local_vars.yml site.yml
```

This will launch an instance and provision it with geoserver, jupyterhub and geonotebook. The hub page should be available at https://your-ec2-instance-public-dns-name.com:8000/ (Please note this is set up with a self-signed SSL certificate and so your browser may complain). 

*NOTE* if you have issues with ```"ImportError: No module named boto"``` this may be due to ansible using an incorrect python (e.g. if you installed boto in a virtualenv). In these cases your best bet is to create a temporary inventory file in ```/tmp/inventory``` with the following:


```
# /tmp/inventory
localhost ansible_python_interpreter=/path/to/.virtualenv/bin/python
```

You can then re-run the final command like so:

```
# Launch and provision the instance
ansible-playbook -i /tmp/inventory -e @local_vars.yml site.yml
```

This will ensure that ansible, when run on local host, is using the correct python.

Finally, the instance may be terminated by running:

```
ansible-playbook -i localhost, -e @local_vars.yml -e state=absent site.yml
```
