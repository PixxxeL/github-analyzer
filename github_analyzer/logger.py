import logging.config

import conf


logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        #'file': {
        #    'level': 'INFO',
        #    'class': 'logging.FileHandler',
        #    'filename': LOG_FILEPATH,
        #}
    },
    'loggers': {
        '': { #github_analyzer
            'handlers': ['console'],
            'level': 'DEBUG' if conf.DEBUG else 'INFO',
            'propagate': True,
        }
    }
})
