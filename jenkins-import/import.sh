#!/bin/sh

set -e
set -u
set -x

DIR="$(dirname $0)"

dc() {
	docker-compose -p parkeerrechten -f ${DIR}/docker-compose.yml $*
}

trap 'dc kill ; dc down ; dc rm -f' EXIT

rm -rf ${DIR}/data
mkdir -p ${DIR}/data

dc down -v
dc rm -f
dc pull
dc build
dc run --rm importer
dc down -v
