# Running Geonotebook in Docker

Geonotebook relies on a complex stack of technologies that are not always easy to install and properly configure. To ease this complexity we provide a docker container for running the notebook on docker compatible systems. To install docker on your system please see docker's [documentation](https://docs.docker.com/engine/installation/) for your operating system.

## Build the container
First you must build the docker container.  After checking out the current repository, you can run

```
docker build -t geonotebook .
```

This will build and install the container on your system,  making it available to run. This may take some time (between 10 and 20 minutes) depending on your network connection. 

## Run the container

To run the container (after building it)  issue the following command:

```
docker run -p 8888:8888 -v /path/to/your/notebooks:/notebooks  -it --rm geonotebook
```

This does several things.  

**First** it maps the docker container's ```8888``` port to your system's ```8888``` port.  This makes the container available to your host systems web browser.

**Second**,  it maps a host system path ```/path/to/your/notebooks``` to the docker containers ```/notebooks``` directory.  This ensures that the notebooks you create, edit, and save are available on your host system,  and are not *destroyed* when the you exit the container.

**Third**, the notebook starts in an interactive terminal and is accessible through http://localhost:8888.

**Finally**,  we include the ```--rm``` option to clean up the notebook after you exit the process.

## Final Notes
+ You actually *can* run the docker container without the ```-it``` option and still get access to the initial URL (though this is somewhat more complicated). It is possible to get the notebook's container name (e.g. with ```docker ps```) and then print the output of the container with ```docker logs [OPTIONS] CONTAINER```  For more information see ```docker logs --help```

+ You may want to keep your data separate from your notebook files.  If this is the case you can map additional directories from your host into the docker container using the -v option.  E.g.


```
docker run -p 8888:8888 \
  -v /path/to/your/notebooks:/notebooks  \
  -v /path/to/your/data:/data -it --rm geonotebook
```

