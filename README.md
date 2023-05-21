# Boomerang

<p align="center"><img src="https://github.com/ailothaen/boomerang/blob/main/boomerang_logo.png?raw=true" alt="Boomerang logo" width="500"></p>

Boomerang is a simple Discord bot for reminders.

You can chat with it in DMs to register reminders (for example: "in 6 hours, remind me of that thing" or "at 17:00, make me think to..."), and at the right time, the bot will send you a DM to remind you. (It is actually quite similar to the RemindMe! bot on Reddit)

There are also possibilities to setup recurrent reminders (every day, every 6 hours...)

The name "Boomerang" is an image: "I do not have time to read that right now, so remind me about that in 6 hours...", and 6 hours later, that thing comes back to you.


## Examples

<p align="center">
<img src="https://github.com/ailothaen/boomerang/blob/main/demo.webp?raw=true" alt="Demo (animated image)" width="600">
</p>


## Configuration

The file `config.yml` is used as a configuration file. As now, the only parameter is the Discord bot token.


## Installing

Here is a guide on how to setup the bot on your own Linux server (that may require some small changes depending on your exact environment):

This guide assumes that you already registered a Discord bot and have a bot token (if not, [go here](https://discord.com/developers/applications), then create a bot and get its token)

### Install system dependencies

```bash
# apt install python3-pip python3-venv
```

It is strongly advised to create a system user dedicated to the app:

```bash
# adduser boomerang
```

### Install the app

Drop all the repository content (or better, the files in a release) in a directory on your server.

Make sure the running user has write access to directories `data`, `logs` and can run `run.sh`.

```bash
# chown boomerang: . -R
# chmod 444 * -R
# chmod 744 run.sh data logs -R
```

Edit the configuration file to put the bot token.

Switch to the dedicated user, create a Python virtualenv and activate it:

```bash
# su boomerang
$ python3 -m venv env
$ source env/bin/activate
```

Install Python dependencies:

```bash
(env) $ pip install -r requirements.txt
```

Switch back to root, and copy `boomerang.service` into `/etc/systemd/system`. Do not forget to change directories and users in the file.

Then
```bash
# systemctl daemon-reload
# systemctl enable boomerang
# systemctl start boomerang
```

You should now be able to talk with the bot (in DMs)


## Licensing

This software is licensed [with MIT license](https://github.com/ailothaen/RedditArchiver/blob/main/LICENSE).
