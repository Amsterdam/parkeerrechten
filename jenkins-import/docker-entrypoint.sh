#!/bin/sh

set -e

/app/jenkins-import/wait-for-it.sh "$NPR_DB_HOST:$NPR_DB_PORT"
/app/jenkins-import/wait-for-it.sh "${LOCAL_DB_HOST:-database}:${LOCAL_DB_PORT:-5432}"


# Run the main container command.
exec "$@"
