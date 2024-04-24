#!/bin/bash
# wait-for-mysql.sh

set -e
set -x

cmd="$@"

until mysql -h ${DB_HOST} -P ${DB_PORT} -u ${DB_USER} ${DB_NAME} -e 'select 1'; do
  >&2 echo ${DB_HOST} ${DB_USER} ${DB_NAME}
  >&2 echo "MySQL is unavailable - sleeping"
  >&2 echo "It can take an insanly long time (about 40 mins)."
  sleep 10
done

>&2 echo "MySQL is up - executing command"
exec $cmd
