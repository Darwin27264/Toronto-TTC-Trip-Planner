# start from base
FROM ubuntu:20.04

LABEL maintainer="Christian Muise <christian.muise@queensu.ca>"

# install system-wide deps for python
RUN apt-get -yqq update
RUN apt-get -yqq install python3-pip python3-dev curl gnupg build-essential vim git

# copy our application code
RUN mkdir /PROJECT
WORKDIR /PROJECT

# install required elements
RUN pip3 install --upgrade pip
RUN pip3 install nnf
RUN pip3 install bauhaus
# install/upgrade SSL certificate
RUN pip3 install --upgrade certifi
# install Geocoder & Geopy
RUN pip3 install geocoder
RUN pip3 install geopy
# install os.path
RUN pip3 install os
# install SQLite
RUN pip3 install sqlite3
# install datetime Library
RUN pip3 install datetime
# install JSON, os.path in case of needing to unzip
RUN pip3 install json
RUN pip3 install os.path
# install itertools
RUN pip3 install itertools
# install ast
RUN pip3 install ast
# install math
RUN pip3 install math
# install input
RUN pip3 install input

# install dsharp to run in the container
RUN curl https://mulab.ai/cisc-204/dsharp -o /usr/local/bin/dsharp
RUN chmod u+x /usr/local/bin/dsharp

# default command to execute when container starts
CMD /bin/bash
