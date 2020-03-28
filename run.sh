#!/bin/bash

# ask for sudo privilege
if [ $(id -u) != 0 ]; then
	sudo $0 $@
	exit $?
fi

docker run -it --rm fuhl/jira_logger $@
