# Project libs
from configs import log

# 3rd-party libs
from dateutil.relativedelta import relativedelta
import jinja2

# Standard libs
import datetime, os


async def notify(template_name, user, vars=None):
    """
    Loads a reply template, fills it with vars and sends it to the user in DM

    Args:
        template ([str]): Name of the template file to search in ./templates
        user ([discord.User/Member]): User or Member object of Discord
        vars ([dict], optional): List of variables to replace in the template with format(). Defaults to None.
    """
    if vars is None:
        vars = {}

    with open(os.path.join("templates", f'{template_name}.md'), 'r') as f:
        text = f.read()

    if vars is not None:
        template = jinja2.Template(text, trim_blocks=True)
        text = template.render(**vars)

    await user.send(text)


def reminder_fate(db, reminder_id):
    """
    Decides the "fate" of a reminder (should it be deleted? should its next firing date be updated?)

    Args:
        db (models.Database): Database instance (this function makes queries on DB)
        reminder_id (id): Reminder ID

    Returns:
        datetime.datetime: Datetime of the next fire time of the reminder. None if there is none (reminder deleted)
    """
    reminder = db.select_reminder(reminder_id)
    now = datetime.datetime.now(datetime.timezone.utc)
    next = None

    if reminder["recurrence"] is None:
        db.delete_reminder(reminder_id)
        log.info(f"Reminder {reminder_id} was oneshot. Deleting it")

    elif reminder["recurrence_limit"] is not None:
        if reminder["recurrence_limit"] <= 1:
            db.delete_reminder(reminder_id)
            log.info(f"Reminder {reminder_id} (recurring) has no more occurrences. Deleting it")
        else:
            recurrence_limit = reminder["recurrence_limit"]-1
            # Getting next reminder occurrence
            next = reminder_next(now, reminder["recurrence"])
            db.update_reminder_recurrence(reminder_id, next, recurrence_limit)
            log.info(f"Reminder {reminder_id} (recurring) has {recurrence_limit} more occurrences. Next occurrence: {next.strftime('%Y-%m-%d %H:%M %Z')}")
    else:
        # Getting next reminder occurrence
        next = reminder_next(now, reminder["recurrence"])
        db.update_reminder_recurrence(reminder_id, next, None)
        log.info(f"Reminder {reminder_id} (recurring) has no limit on occurrences. Next occurrence: {next.strftime('%Y-%m-%d %H:%M %Z')}")
    
    return next


def reminder_next(current_next, recurrence):
    """
    Calculates the next time the reminder is supposed to fire.
    (This is an easy function, but maybe in the future I will implement cron syntax in it as well...)

    Args:
        current_next (datetime.datetime): Datetime to update (usually now)
        recurrence (str): Recurrence information from DB (is an expression like "4d 3h")

    Returns:
        datetime.datetime: Updated datetime
    """
    return timepoint_calculation(current_next, recurrence)


def timepoint_calculation(date, timepoint):
    """
    Returns a datetime object according to the timepoint specification
    ("4d 3h", "2m"...)

    Args:
        current_next (datetime.datetime): Datetime to update
        timepoint (str): Expression like "4d 3h"

    Returns:
        datetime.datetime: Updated datetime
    """
    timepoint_g = timepoint.split(' ')
    if '' in timepoint_g: # No time specified
        raise ValueError
    
    for block in timepoint_g:
        metric = block[-1]
        value = int(block[:-1])

        if metric in ('M', 'n'):
            date += relativedelta(months=value)
        elif metric == 'w':
            date += relativedelta(weeks=value)
        elif metric == 'd':
            date += relativedelta(days=value)
        elif metric == 'h':
            date += relativedelta(hours=value)
        elif metric == 'm':
            date += relativedelta(minutes=value)
        
    return date
