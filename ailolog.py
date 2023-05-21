import logging
from logging.handlers import RotatingFileHandler

"""
Wrapper for the logging module, which is an hell in terms of design.
Also adds the NOTICE level, between INFO and WARNING.

Usage:
```
import ailolog

l = ailolog.logger('test')

ailolog.add_console(l)
ailolog.add_file(l, 'test.log', minlevel="debug")

l.debug('coucou')
```
"""

DEFAULT_LINE_FORMAT = '[%(asctime)s][%(name)s][%(levelname)s] %(message)s'
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'

# Adding NOTICE level because python devs were too lazy to add it!
# https://stackoverflow.com/q/2183233/5418422
logging.addLevelName(25, 'NOTICE')
def notice(self, msg, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, msg, args, **kwargs) 
logging.Logger.notice = notice

# and TRACE level too
logging.addLevelName(5, 'TRACE')
def trace(self, msg, *args, **kwargs):
    if self.isEnabledFor(5):
        self._log(5, msg, args, **kwargs) 
logging.Logger.trace = trace


def logger(name=''):
    logger = logging.getLogger(name)
    logger.setLevel(1) # seriously, who cares about that? it's supposed to be managed at handler level
    return logger

def add_file(logger, path, minlevel='trace', mode='a', line_format=DEFAULT_LINE_FORMAT, time_format=DEFAULT_TIME_FORMAT):
    level = _string_to_levelname(minlevel)
    handler = logging.FileHandler(path, mode=mode, encoding='utf-8')
    formatter = logging.Formatter(line_format, time_format)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def add_rotatingfile(logger, path, minlevel='trace', mode='a', line_format=DEFAULT_LINE_FORMAT, time_format=DEFAULT_TIME_FORMAT, size=1000000, rotate=7):
    level = _string_to_levelname(minlevel)
    handler = RotatingFileHandler(path, mode=mode, maxBytes=size, backupCount=rotate, encoding='utf-8')
    formatter = logging.Formatter(line_format, time_format)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def add_console(logger, minlevel='trace', line_format=DEFAULT_LINE_FORMAT, time_format=DEFAULT_TIME_FORMAT):
    level = _string_to_levelname(minlevel)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(line_format, time_format)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def _string_to_levelname(string):
    if string in ('critical', 'CRITICAL', 'crit', 'CRIT'):
        return logging.CRITICAL
    elif string in ('error', 'ERROR', 'err', 'ERR'):
        return logging.ERROR
    elif string in ('warning', 'WARNING', 'warn', 'WARN'):
        return logging.WARNING
    elif string in ('notice', 'NOTICE'):
        return 25
    elif string in ('info', 'INFO'):
        return logging.INFO
    elif string in ('trace', 'TRACE'):
        return 5
    else:
        return logging.DEBUG