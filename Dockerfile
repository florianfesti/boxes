# Simple Fedora based Docker container for running Boxes.py

# Build the docker container
# docker build -t boxes.py .

# Run the docker container
# docker run -ti -p 4000:8000 boxes.py
# Run the docker container with a bind mount
# docker run -ti -p 4000:8000 -v %cd%/scripts:/boxes/scripts boxes.py

# Get the web interface at http://localhost:4000
# First access may take a while as the Python files need to be complied

# Use latest Fedora release as base
FROM fedora:latest

# Install requirements
RUN dnf install -y git-core python3-markdown python3-setuptools python3-affine python3-shapely pstoedit && dnf clean all

# Get Boxes.py sources to /boxes
COPY . ./boxes/

# Internal port used
EXPOSE 8000

# Start the boxes web server on container start up
CMD ["/boxes/scripts/boxesserver"]
