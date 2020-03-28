#!/bin/bash

# ask for sudo privilege
if [ $(id -u) != 0 ]; then
	sudo $0 $@
	exit $?
fi

if [ ! $# -eq 1 ]; then
	exit $?
fi

if [ "$1" = "dev" ]; then
	TAG=fuhl/jira_logger:dev
else
	TAG=fuhl/jira_logger
fi

docker build -f Dockerfile.$1 -t $TAG .
