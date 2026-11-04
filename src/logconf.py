import logging
import os
from logging.config import dictConfig


debug = os.environ.get("DEBUG_ENABLED", "false").lower() == "true"
LOG_LEVEL = logging.DEBUG if debug else logging.INFO

# When true, log the full file path (e.g. /src/base_handler.py.141).
# When false, log only the module name (e.g. base_handler.141) for
# more compact/readable logs.
log_full_path = os.environ.get("LOG_FULL_PATH", "true").lower() == "true"
location = '%(pathname)s.%(lineno)s' if log_full_path else '%(module)s.%(lineno)s'

FMT = ('[%(asctime)s: %(levelname)s] '
       f'{location} %(funcName)s(): %(message)s')


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': FMT
        },
    },
    'handlers': {
        'default': {
            'level': LOG_LEVEL,
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': LOG_LEVEL,
            'propagate': False
        },
    }
}

dictConfig(LOGGING_CONFIG)
