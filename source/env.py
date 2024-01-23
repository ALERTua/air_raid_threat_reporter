# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

from dotenv import load_dotenv
# noinspection PyProtectedMember
from pip._internal.utils.misc import strtobool

try:
    from . import logger
    from . import constants
except:
    import logger
    import constants

LOG = logging.getLogger()

DOTENV_PATH = os.getenv('DOTENV_PATH', '').strip()
LOG.debug(f'ENV DOTENV_PATH: {DOTENV_PATH}')
if DOTENV_PATH:
    DOTENV_PATH = Path(DOTENV_PATH)
    if not (DOTENV_PATH / '.env').exists():
        DOTENV_PATH = None
load_dotenv(dotenv_path=DOTENV_PATH or None, verbose=True)

VERBOSE = os.getenv('VERBOSE', False)
VERBOSE = bool(strtobool(str(VERBOSE)))
print(f"VERBOSE: {VERBOSE}")
if VERBOSE:
    LOG.setLevel(logging.DEBUG)

LOG.debug('Loading env variables')

DATA_PATH = os.getenv('DATA_PATH')
LOG.debug(f'ENV DATA_PATH: {DATA_PATH}')
DATA_PATH = DATA_PATH or constants.DATA_PATH_DEFAULT
DATA_PATH = Path(DATA_PATH)
LOG.debug(f'DATA_PATH: {DATA_PATH}')

TELEGRAM_CHAT_IDS = os.getenv('TELEGRAM_CHAT_IDS')
LOG.debug(f'ENV TELEGRAM_CHAT_IDS: {TELEGRAM_CHAT_IDS}')
if TELEGRAM_CHAT_IDS:
    TELEGRAM_CHAT_IDS = TELEGRAM_CHAT_IDS.strip()
    TELEGRAM_CHAT_IDS = TELEGRAM_CHAT_IDS.strip('"\' ')
    TELEGRAM_CHAT_IDS = TELEGRAM_CHAT_IDS.strip()
    TELEGRAM_CHAT_IDS = TELEGRAM_CHAT_IDS.split(',')
    telegram_chat_ids = []
    for chat_id in TELEGRAM_CHAT_IDS:
        chat_id = chat_id.strip()
        try:
            chat_id = int(chat_id)
        except:
            chat_id = chat_id
        telegram_chat_ids.append(chat_id)
    TELEGRAM_CHAT_IDS = telegram_chat_ids
LOG.debug(f'TELEGRAM_CHAT_IDS: {TELEGRAM_CHAT_IDS}')

REPORT_CHAT_ID = os.getenv('REPORT_CHAT_ID')
REPORT_CHAT_ID = REPORT_CHAT_ID.strip()
try:
    REPORT_CHAT_ID = int(REPORT_CHAT_ID)
except:
    REPORT_CHAT_ID = REPORT_CHAT_ID
LOG.debug(f'ENV REPORT_CHAT_ID: {REPORT_CHAT_ID}')


LLM_API_BASE = os.getenv('LLM_API_BASE')
LOG.debug(f'ENV LLM_API_BASE: {LLM_API_BASE}')

LLM_MODEL = os.getenv('LLM_MODEL')
LOG.debug(f'ENV LLM_MODEL: {LLM_MODEL}')

TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
LOG.debug(f'ENV TELEGRAM_PHONE {"is set" if TELEGRAM_PHONE else "is not set"}')

TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
LOG.debug(f'ENV TELEGRAM_API_ID {"is set" if TELEGRAM_API_ID else "is not set"}')

TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
LOG.debug(f'ENV TELEGRAM_API_HASH {"is set" if TELEGRAM_API_HASH else "is not set"}')

LOG.debug('Loading env variables done')
