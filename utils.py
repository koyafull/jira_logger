import argparse
import datetime
import re
import sys
from distutils.util import strtobool

from WeightedTask import WeightedTask

VALID_REGEX = '([A-Z]+\-[0-9]+)(\:(100|[0-9]{1,2}))?$'


def valid_id(s):
    try:
        pattern = re.compile(VALID_REGEX)
        match = pattern.match(s)
        if match is None:
            raise ValueError
        return WeightedTask(match.group(1), 0 if match.group(3) is None else match.group(3))
    except ValueError:
        msg = "Not a valid TASKID." \
              "\nexptected: {expected}" \
              "\nfound: {found}" \
            .format(expected=VALID_REGEX, found=s)
        raise argparse.ArgumentTypeError(msg)


def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def yes_no_question(question,
                    yes_answer, no_answer,
                    yes_action=None, no_action=None,
                    yes_action_parameters=None, no_action_parameters=None):
    while True:
        response = input(question)
        try:
            if strtobool(response):
                sys.stdout.write(yes_answer)
                if callable(yes_action):
                    yes_action(yes_action_parameters)
            else:
                sys.stdout.write(no_answer)
                if callable(no_action):
                    no_action(no_action_parameters)
            break
        except ValueError:
            sys.stdout.write("\nSupported response value: y, yes, t, true, on, 1 OR n, no, f, false, off, 0")

