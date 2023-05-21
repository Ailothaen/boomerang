# Project libs
import models, utils
from configs import log

# 3rd-party libs
import discord, pytz
from dateutil.relativedelta import relativedelta

# Standard libs
import datetime, random, re


async def handler(client, payload):
    """
    Main router. Detects the underlying command and sends the input to the right command.

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    command = payload.content.split(' ')[0].lower()

    # Command "timezone" or "tz"
    if command in ('timezone', 'tz'):
        await cmd_tz(client, payload)

    # Command "in" (relative reminder)
    elif command == 'in':
        await cmd_in(client, payload)

    # Command "at" or "on" (absolute reminder)
    elif command in ('at', 'on'):
        await cmd_at(client, payload)

    # Command "list"
    elif command in ('list', 'ls'):
        await cmd_list(client, payload)

    # Command "remove"
    elif command in ('remove', 'rm', "delete", "del"):
        await cmd_remove(client, payload)

    # Command "help"
    elif command in ('help', '?'):
        await cmd_help(client, payload)

    # Unrecognized command
    else:
        await utils.notify('error_unrecognizedCommand', payload.author)


async def cmd_tz(client, payload):
    """
    timezone command
    Syntax: tz Europe/Paris

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    try:
        timezone = payload.content.split(' ')[1]
    except IndexError:
        await utils.notify('error_badSyntax', payload.author)
        return

    if timezone in pytz.all_timezones_set:
        tz = pytz.timezone(timezone)
        
        db = models.Database()
        db.update_user_timezone(payload.author, tz)

        await utils.notify('success_timezoneChanged', payload.author, {'timezone': str(tz)})
    else:
        await utils.notify('error_timezoneNotRecognized', payload.author)


async def cmd_in(client, payload):
    """
    in command
    Syntax: in 1n 2w 3h 4m, send me this very text

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    message = payload.content

    # parsing the reminder
    units = re.search(r'^in((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?)(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', message)
    if units is None: # If parsing fails
        await utils.notify('error_badSyntax', payload.author)
        return

    g = units.groups()
    timepoint = g[0].strip() # "7h 3m" for example
    reminder_recurrence = g[1].strip() if g[1] is not None else None # same format as timepoint
    reminder_text = g[2].strip() # what is after the comma

    # Calculating now + specification
    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)
    try:
        reminder_time = utils.timepoint_calculation(now, timepoint)
    except ValueError:
        await utils.notify('error_badSyntax', payload.author)
        return

    color = discord.Colour.from_hsv(random.uniform(0, 1), 0.85, 0.88).value

    # reminder was parsed, now putting it into db
    db = models.Database()
    db.insert_reminder(payload.author, now, reminder_time, reminder_text, color, reminder_recurrence)
    
    await utils.notify('success_reminderRegistered', payload.author, {'reminder_time': int(datetime.datetime.timestamp(reminder_time)), 'reminder_text': reminder_text})


async def cmd_at(client, payload):
    """
    at command
    Syntax: at 19, send me this very text
    (there are several variants, see the regexes)

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    regexes = (
        {'expression': r'^at ([0-9]{1,2})h?(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', 'scope': 'day'},
        {'expression': r'^at ([0-9]{1,2})(?:h|:)?([0-9]{1,2})(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', 'scope': 'day'},
        {'expression': r'^on ([0-9]{1,2})(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', 'scope': 'month'},
        {'expression': r'^on ([0-9]{1,2}) at ([0-9]{1,2})h?(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', 'scope': 'month'},
        {'expression': r'^on ([0-9]{1,2}) at ([0-9]{1,2})(?:h|:)?([0-9]{1,2})(?:\severy((?:\s[0-9]+(?:M|n))?(?:\s[0-9]+w)?(?:\s[0-9]+d)?(?:\s[0-9]+h)?(?:\s[0-9]+m)?))?,(.*)$', 'scope': 'month'}
    )

    message = payload.content

    for i, regex in enumerate(regexes):
        units = re.search(regex['expression'], message)
        if units is not None:
            regex_id = i
            break
    else:
        await utils.notify('error_badSyntax', payload.author)
        return
    
    g = units.groups()

    # Parsing the command depending of the matched regex
    default = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    reminder_time_components = {
        "year": default.year,
        "month": default.month,
        "day": default.day,
        "hour": default.hour,
        "minute": default.minute
    }

    if regex_id == 0:
        reminder_time_components["hour"] = int(g[0])
        reminder_recurrence = g[1]
        reminder_text = g[2]
    elif regex_id == 1:
        reminder_time_components["hour"] = int(g[0])
        reminder_time_components["minute"] = int(g[1])
        reminder_recurrence = g[2]
        reminder_text = g[3]
    elif regex_id == 2:
        reminder_time_components["day"] = int(g[0])
        reminder_recurrence = g[1]
        reminder_text = g[2]
    elif regex_id == 3:
        reminder_time_components["day"] = int(g[0])
        reminder_time_components["hour"] = int(g[1])
        reminder_recurrence = g[2]
        reminder_text = g[3]
    elif regex_id == 4:
        reminder_time_components["day"] = int(g[0])
        reminder_time_components["hour"] = int(g[1])
        reminder_time_components["minute"] = int(g[2])
        reminder_recurrence = g[3]
        reminder_text = g[4]

    now = datetime.datetime.now(datetime.timezone.utc).replace(second=0, microsecond=0)

    # fetching user timezone
    db = models.Database()
    try:
        timezone = db.select_user_timezone(payload.author)
    except IndexError:
        await utils.notify('error_noTimezoneDefined', payload.author)
        return
        
    reminder_time = datetime.datetime(reminder_time_components['year'], reminder_time_components['month'], reminder_time_components['day'], reminder_time_components['hour'], reminder_time_components['minute'], 0)
    tzinfo = pytz.timezone(timezone)
    reminder_time = tzinfo.localize(reminder_time)
    log.debug(reminder_time)

    # checking if the event has not already passed
    # if not, we have to increment for 1 day/week/month...
    if now > reminder_time:
        increase_by = regexes[regex_id]['scope']
        if increase_by == 'day':
            reminder_time += relativedelta(days=1)
        elif increase_by == 'month':
            reminder_time += relativedelta(months=1)

    color = discord.Colour.from_hsv(random.uniform(0, 1), 0.85, 0.88).value

    # reminder was parsed, now putting it into db
    db = models.Database()
    db.insert_reminder(payload.author, now, reminder_time, reminder_text, color, reminder_recurrence)

    await utils.notify('success_reminderRegistered', payload.author, {'reminder_time': int(datetime.datetime.timestamp(reminder_time)), 'reminder_text': reminder_text})


async def cmd_list(client, payload):
    """
    list command

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    db = models.Database()
    reminders = db.select_reminders_user(payload.author)
    await utils.notify('info_list', payload.author, vars={"reminders": reminders})


async def cmd_remove(client, payload):
    """
    remove command
    Syntax: remove 1

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    message = payload.content

    regex = re.search(r'^(?:remove|rm|delete|del) ([0-9]+)$', message)
    try:
        reminder_to_delete = regex.group(1)
    except:
        await utils.notify('error_badSyntax', payload.author)
        return

    # Checking if the user is the author of the reminder
    db = models.Database()
    try:
        reminder = db.select_reminder(reminder_to_delete)
        if reminder["author"] != payload.author.id:
            raise ValueError
    except (IndexError, ValueError):
        await utils.notify('error_reminderNotExist', payload.author)
        return

    # Deleting
    db.delete_reminder(reminder_to_delete)
    await utils.notify('success_reminderRemoved', payload.author)
        

async def cmd_help(client, payload):
    """
    help command
    Syntax: help (for just general help) or help in (for the command in for example)

    Args:
        client (discord.Client): Discord client object
        payload (discord.Message): Discord message object
    """
    message = payload.content
    try:
        command = message.split(' ')[1]
    except IndexError:
        await utils.notify('help_general', payload.author)
        return

    if command in ('at', 'on'):
        await utils.notify('help_at', payload.author)
    elif command == 'in':
        await utils.notify('help_in', payload.author)
    else:
        await utils.notify('help_general', payload.author)
