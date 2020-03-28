

# ====== JIRA LOGGER ======

### Introduction
Will log 8 hours a day from 8:00am to 4:00pm GMT+0000 from start date to end date, on the specified tasks.
You can assign percentage to each task. If the percentage sum is not 100, unweighted tasks, if provided, will be used to fill the period.
Oh, and of course, it manages business days.

Jira login will be asked via command line input.

# Run it

## Using Docker

1. Set the Dockerfile to your Jira URL

   ```bash
   nano Dockerfile.prod
   ...
   ENV JIRA_URL=<prod_jira_url>
   ...
   ```
   
2. Build & run

   ```bash
   ./build.sh prod
   ./run.sh STARTDATE STOPDATE TASKID[:WEIGHT] [TASKID[:WEIGHT] ...]
   ```

## Using Python

```bash
JIRA_URL=<jira_url> python3 jira_logger.py STARTDATE STOPDATE TASKID[:WEIGHT] [TASKID[:WEIGHT] ...]
```

## Example

```bash
JIRA_URL="https://my_jira_url" python3 jira_logger.py 2019-09-14 2019-12-31 FOO-42:30 BAR-103:20 ANY-683 
```

# Parameters

## `STARTDATE`

Date to start login

Format: `YYYY-MM-DD`

Example: 2018-11-23

## `STOPDATE`

Date to login to

## `TASKID`

Jira ID of the task.

Example: DEV-104

## `WEIGHT`

A percentage of the spend time to be assigned to the task.

Format: `[0-100]`

# Known limitations

* Not really fault-tolerant, basic error management

* Business-day management is set to French holiday for now

# Improvment ideas

* Holiday management

* Log management

* Allow configuration of start time and timezone
