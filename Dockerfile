# https://docs.docker.com/engine/reference/builder
#[Docker quickstart](https://docs.docker.com/get-started/)
#build with name, tag and save to docker hub
#docker build -t pittvax/trolley:latest .
# Specify base image
FROM mcandre/docker-jython:latest

# Install PyYAML http://pyyaml.org/wiki/PyYAML
WORKDIR /tmp
RUN wget http://pyyaml.org/download/pyyaml/PyYAML-3.12.tar.gz && \
    tar zxf PyYAML-3.12.tar.gz && rm -rf PyYAML-3.12.tar.gz && \
    cd PyYAML-3.12 && jython setup.py --without-libyaml install && \
    cd ../ && rm -rf PyYAML-3.12
WORKDIR /root

#Set ENTRYPOINT
ENTRYPOINT ["bash"]