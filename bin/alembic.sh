#!/usr/bin/env bash
export PYTHONPATH=..:../contrib/python_base_app:

SCRIPT_DIR=$(dirname $0)
WORK_DIR=$(realpath ${SCRIPT_DIR}/..)

if [ "$1" == "" ] ; then
    echo "Usage (for example):"
    echo ""
    echo "* Compare metadata model and database and derive migration script from differences:"
    echo "  $0 revision  --autogenerate  -m 'DESCRIPTION TEXT'"
    echo "* Bring database up to latest migration version (called 'head'):"
    echo "  $0 upgrade head"
    exit 1
fi

cd ${WORK_DIR}/little_brother
alembic "$@"
