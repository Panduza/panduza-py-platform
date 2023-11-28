FROM ubuntu:22.04

# Attach to the repository
LABEL org.opencontainers.image.source https://github.com/Panduza/panduza-py

# Install Packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Europe/Paris \
    apt-get -y install \
        python3 python3-pip \
        git

# Pip installations
# COPY requirements.txt /setup/requirements.txt
# RUN python3 -m pip install -r /setup/requirements.txt

# # Install platform inside
# WORKDIR /setup
# COPY . /setup/
# RUN python3 -m pip install .

# Allow plugin insertion here
# ENV PYTHONPATH="/etc/panduza/plugins/py"

#
WORKDIR /work

# Create the directory for platform plugins
# Then run the platform
# CMD mkdir -p /etc/panduza/plugins/py; \
#     python3 /usr/local/lib/python3.10/dist-packages/panduza_platform/__main__.py
