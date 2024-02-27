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
RUN python3.11 -m pip install coverage
RUN python3.11 -m pip install colorama==0.4.6
RUN python3.11 -m pip install paho-mqtt==1.6.1
RUN python3.11 -m pip install pyftdi==0.55.0
RUN python3.11 -m pip install pymodbus==3.3.2
RUN python3.11 -m pip install pyserial==3.5
RUN python3.11 -m pip install pyudev==0.24.0
RUN python3.11 -m pip install pyusb==1.2.1
RUN python3.11 -m pip install PyHamcrest==2.0.4
RUN python3.11 -m pip install aiofiles==23.2.1
RUN python3.11 -m pip install aiomonitor==0.6.0
RUN python3.11 -m pip install aioserial==1.3.1
RUN python3.11 -m pip install ThorlabsPM100==1.2.2
RUN python3.11 -m pip install python-usbtmc==0.8

# 
WORKDIR /platform
COPY . /platform/

# Create the mirror directory
RUN mkdir -p /etc/panduza

# 
RUN chmod +x /platform/ENTRYPOINT.sh
CMD /platform/ENTRYPOINT.sh

