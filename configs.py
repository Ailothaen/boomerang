# Project libs
import ailolog

# 3rd-party libs
import yaml


# Loading config
with open('config.yml', 'r', encoding="utf-8") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# Setting up logs
log = ailolog.logger("boomerang")
log_discord = ailolog.logger("discord")
ailolog.add_rotatingfile(log, "logs/boomerang.log", size=100000, rotate=5, minlevel='debug')
ailolog.add_rotatingfile(log_discord, "logs/boomerang.log", size=100000, rotate=5, minlevel='warning')
log.info("Start of process")
