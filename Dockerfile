FROM amsterdam/python_pg11

MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1
EXPOSE 8000


RUN apt-get update \
	&& apt-get install -y \
		freetds-dev \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
	&& adduser --system datapunt
RUN pip install --user Cython \
	&& pip install --user --no-binary pymssql pymssql

# force DTS protocol version to 8
COPY ./src/conf/freetds.conf /etc/freetds/freetds.conf

WORKDIR /app
COPY . /app
#COPY ./src/docker-wait.sh /app
#COPY ./src/parkeerrechten /app/parkeerrechten/
# RUN pip install --no-cache-dir -e .[test]
RUN pip install --no-cache-dir .[test]


# Do the .jenkins directory dance to enable data imports:
COPY ./src/.jenkins/import /.jenkins-import/
# COPY .jenkins /app/.jenkins

