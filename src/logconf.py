import logging
import os
from logging.config import dictConfig


debug = os.environ.get("DEBUG_ENABLED", "false").lower() == "true"
LOG_LEVEL = logging.DEBUG if debug else logging.INFO

FMT = ('[%(asctime)s: %(levelname)s] '
       '%(pathname)s.%(lineno)s %(funcName)s(): %(message)s')


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
