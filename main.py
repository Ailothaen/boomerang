# Project libs
from configs import config, log
import commands, models, utils

# 3rd-party libs
import discord

# Standard libs
import asyncio, sys


# ------------------------------------- #
# Main class                            #
# ------------------------------------- #

class Client(discord.Client):
    """
    Discord client class
    """
    async def on_ready(self):
        pyversion = sys.version.replace('\n', ' ')
        print('Connected!')
        print(f'Name: {self.user.name}#{self.user.discriminator}')
        print(f'Snowflake: {self.user.id}')
        print(f'Python version: {pyversion}')
        print(f'discord.py version: {discord.__version__}')
        log.info('Connected!')
        log.info(f'Name: {self.user.name}#{self.user.discriminator}')
        log.info(f'Snowflake: {self.user.id}')
        log.info(f'Python version: {pyversion}')
        log.info(f'discord.py version: {discord.__version__}')

        # Creating the fetch loop
        self.loop.create_task(loop(self))

    # DMs only
    async def on_message(self, payload):
        # do not reply to yourself, silly
        if payload.author.id == self.user.id:
            return None

        log.debug(payload)

        # Give an indication to the author
        await payload.channel.typing()

        # Main handler
        try:
            await commands.handler(self, payload)
        except Exception as e:
            await utils.notify('error_general', payload.author)
            log.error(f'Uncaught exception: {e}', exc_info=True)


# ------------------------------------- #
# Event loop                            #
# ------------------------------------- #

async def loop(client):
    """
    Loop that regularly looks for reminders to be sent.

    Args:
        client (discord.Client): Discord client object
    """
    await client.wait_until_ready()
    previous_count = -1
    while True:
        await asyncio.sleep(40)
        log.debug("Event loop begins")

        # Getting reminders that are happening now
        db = models.Database()
        count = db.count_reminders()
        reminders = db.select_reminders_now()

        for reminder in reminders:
            log.info(f"Reminder {reminder['id']} fired!")

            # do not ask me why I have to use fetch instead of get here...
            # probably because get is relying on cache, so requires the bot to be in a guild? idk
            user = await client.fetch_user(reminder["author"])
            next = utils.reminder_fate(db, reminder["id"])

            content = discord.Embed(title='Reminder!', description=reminder["text"], color=discord.Colour(reminder["color"]))
            content.add_field(name='Added on', value=f'<t:{reminder["date_creation"]}>', inline=True)
            if next:
                content.add_field(name='Next occurrence on', value=f'<t:{int(next.timestamp())}>', inline=True)
            await user.send(embed=content)

        # prevent sending useless requests
        if count == 0 and previous_count != 0:
            await client.change_presence(status=discord.Status.idle)
        elif count != 0 and previous_count == 0:
            await client.change_presence(status=discord.Status.online)
        previous_count = count


# ------------------------------------- #
# Putting it all together               #
# ------------------------------------- #

# Setting up and running client
intents = discord.Intents(dm_messages=True)
client = Client(intents=intents, status=discord.Status.online)

# Creating the DB if it does not exist yet
db = models.Database()

client.run(config['token'])
