import argparse
import datetime
import os
import sys

import requests
from requests.auth import HTTPBasicAuth
import json
from bdateutil import isbday, relativedelta
import holidays
import random
import getpass
from distutils.util import strtobool

from WeightedTask import WeightedTask
from utils import valid_date, valid_id, yes_no_question

MONTH_MAX_BUSINESS_DAY = 23
HOLIDAYS = holidays.FRA()

# ======================================================================================================================
# ================================================= ARGUMENT GATHERING =================================================
# ======================================================================================================================

# environment variables scrapping
JIRA_URL = os.environ['JIRA_URL']

# argument parsing
parser = argparse.ArgumentParser(
    prog="JIRA_LOGGER",
    epilog="\nThe sum of the weights should not go over 100."
)
parser.add_argument("start_date", help="Start date of time login - format: YYYY-MM-DD", type=valid_date)
parser.add_argument("stop_date", help="Stop date of time login - format: YYYY-MM-DD", type=valid_date)
parser.add_argument("id", help="Weighted task ID: <taskId>:<weight>", nargs="+", type=valid_id)
args = parser.parse_args()

if args.start_date > args.stop_date:
    sys.stdout.write("\nOh oh, seems that you confused between START and STOP date. Try again.\nEXIT")
    exit(1)

start_date = args.start_date
stop_date = args.stop_date
number_of_business_days = relativedelta(stop_date, start_date, holidays=HOLIDAYS).bdays
if isbday(start_date, holidays=HOLIDAYS):
    number_of_business_days += 1
    # sys.stdout.write("\nAdded one business day.")

sys.stdout.write("\nFound {} business days.".format(number_of_business_days))

# ======================================================================================================================
# =================================================== WEIGHT MAPPING ===================================================
# ======================================================================================================================

weight_sum = 0
mapped_tasks = dict()
for task in args.id:
    mapped_task = WeightedTask(task.id, round(task.weight * number_of_business_days / 100))
    if mapped_task.id in mapped_tasks:
        mapped_tasks[mapped_task.id] += mapped_task.weight
    else:
        mapped_tasks[mapped_task.id] = mapped_task.weight
    weight_sum += task.weight

unweighted_tasks = {task_id: weight for task_id, weight in mapped_tasks.items() if weight == 0}

# ======================================================================================================================
# ================================================ COHERENCE VALIDATION ================================================
# ======================================================================================================================

if number_of_business_days > MONTH_MAX_BUSINESS_DAY:
    yes_no_question(
        question="\n============================= WARNINGS! ============================="
                 "\nYou are about to logs for {} days. It is more than a business month."
                 "\nAre you sure? [y/n]"
            .format(number_of_business_days),
        yes_answer="\nOk, you have asked for it.",
        no_answer="\nWell, that's safer.\nEXIT",
        no_action=exit,
        no_action_parameters=0
    )

if weight_sum > 100:
    sys.stdout.write("\nOh oh, seems that you are too effective for me! You have weighted for {}%. Try again.\nEXIT"
                     .format(weight_sum))
    exit(1)

if weight_sum == 100:
    yes_no_question(
        question="\nYou have weighted for 100%. Remaining unweighted provided tasks will be ignored."
                 "\nIs it fine for you? [y/n]".format(weight_sum),
        yes_answer="\nGreat, let's do this.",
        no_answer="\nOk, try again.\nEXIT",
        no_action=exit,
        no_action_parameters=0
    )

if weight_sum < 100:
    yes_no_question(
        question="\nYou have weighted for less than 100% ({})."
                 "Work period will be completed with randomly picked unweighted provided tasks."
                 "\nIs it fine for you? [y/n]".format(weight_sum),
        yes_answer="\nGreat, let's do this.",
        no_answer="\nOk, try again.\nEXIT",
        no_action=exit,
        no_action_parameters=0
    )

    if len(list(unweighted_tasks.keys())) > 0:
        i = number_of_business_days - sum(mapped_tasks.values())
        while i > 0:
            mapped_tasks[random.choice(list(unweighted_tasks.keys()))] += 1
            i -= 1

# ======================================================================================================================
# ================================================= RECAP BEFORE GOING =================================================
# ======================================================================================================================

sys.stdout.write(
    "\n\n======================== RECAP BEFORE WE GO ========================="
    "\nYou are about to log:"
)
tmp_sum = 0
recap = ""
for task_id, weight in mapped_tasks.items():
    recap += "\n{k}:\t\t{v} days".format(k=task_id, v=weight)
    tmp_sum += weight

recap += "\nTotal:\t\t{} days".format(tmp_sum)

sys.stdout.write(recap)

yes_no_question(
    question="\nDo you agree? [y/n]",
    yes_answer="\nPerfect!",
    no_answer="\nTry again.\nEXIT",
    no_action=exit,
    no_action_parameters=0
)

# ======================================================================================================================
# ================================================ JIRA WORKLOG LOOPING ================================================
# ======================================================================================================================

# API authentication inputs
sys.stdout.write("\n")
user = input("Username:")
password = getpass.getpass("Password for " + user + ":")

headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache"
}

success_count = 0
business_day_count = 0
current_date = start_date

# login loop
while current_date <= stop_date:

    current_delta = relativedelta(stop_date, current_date, holidays=HOLIDAYS).bdays

    if isbday(current_date, holidays=HOLIDAYS):

        selected_task_id = random.choice(list(
            {task_id: weight for task_id, weight in mapped_tasks.items() if weight > 0}.keys())
        )

        endpoint = "{}/rest/api/2/issue/{}/worklog".format(JIRA_URL, selected_task_id)
        payload = json.dumps({'comment': '',
                              'started': '{}T08:00:00.000+0000'.format(current_date.strftime("%Y-%m-%d")),
                              'timeSpentSeconds': 28800})

        response = requests.post(endpoint, data=payload, headers=headers, auth=HTTPBasicAuth(user, password))

        success_count += 1 if response.status_code == 201 else 0
        business_day_count += 1

        sys.stdout.write("\n[{}] {} {}".format(
            current_date.strftime("%Y-%m-%d"),
            selected_task_id,
            "| " + str(response.status_code) if response.status_code != 201 else ""))

        mapped_tasks[selected_task_id] -= 1

    current_sum = sum(mapped_tasks.values())

    if current_delta < current_sum:
        sys.stdout.write("\nERROR: Loop error: loop count = {loop_count} vs task queue length = {len}\n"
                         .format(loop_count=current_delta, len=current_sum))
        exit(1)
    current_date += datetime.timedelta(days=1)

if success_count == business_day_count:
    sys.stdout.write(
        "\n============================= CONGRATS! ============================="
        "\nSeems that everything went well, you've logged every working day from {} to {}."
            .format(args.start_date.strftime("%Y-%m-%d"), args.stop_date.strftime("%Y-%m-%d"))
    )
else:
    sys.stdout.write(
        "\n============================ Oh no... :( ============================"
        "\nIt seems that {} login try(ies) went wrong. Have a look at the report above to identify mistakes"
        "\n".format(business_day_count - success_count)
    )
