FROM ubuntu:22.04

# Attach to the repository
LABEL org.opencontainers.image.source https://github.com/Panduza/panduza-py

# Install Packages
RUN apt-get update && DEBIAN_FRONTEND=noninteractive TZ=Europe/Paris \
    apt-get -y install python3.11 python3-pip git

# Append udev and libusb for device autodetection
RUN apt-get -y install udev
RUN apt-get -y install ffmpeg
RUN apt-get -y install libusb-1.0-0

# 
WORKDIR /platform
COPY . /platform/

#
RUN python3.11 -m pip install coverage
RUN python3.11 -m pip install -r /platform/requirements.txt

# Create the mirror directory
RUN mkdir -p /etc/panduza

# 
RUN chmod +x /platform/ENTRYPOINT.sh
CMD /platform/ENTRYPOINT.sh

