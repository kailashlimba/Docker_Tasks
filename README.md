This REST App contains two POST api's:
* localhost:8000/validate_finite_value/
* localhost:8000/validate_numeric_value/

### Docker
* Dockerfile is present in the root directory, this uses python base image, copies the project content to docker environment, installs the packages mentioned in the requirements.txt and starts the server
* To build docker image run this below command:
`docker build -t image_name:version .`
* Once the image is built, the container can be started using command:
`docker run -p 8000:8000 -t image_name:version` or `docker run -p 8000:8000 image_id`
* The docker image size is `193MB`
