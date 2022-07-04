from base64 import decode
from dataclasses import replace
from datetime import datetime
from inspect import getmembers
from itertools import count
from munch import munchify
from munch import unmunchify
from sqlite3 import Timestamp
import json
import logging
import pickle
import requests

import EyesUp
import GetManifest

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use FileHandler() to log to a file
fh = logging.FileHandler("getmanifest.log", mode='w', encoding=None, delay=False)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

guardians = ('SpacePirateKubli', 'DeathAngelx101', 'blacksun23')
startDate = datetime.fromisoformat('2022-05-24T00:00:00')
# startDate = '2022-06-22T00:00:00'

GetManifest.makepickle()

for guardian in guardians:
    gameData = EyesUp.initializeGuardian(guardian, startDate)
