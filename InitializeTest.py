from base64 import decode
from dataclasses import replace
from datetime import datetime
from inspect import getmembers
from itertools import count
from munch import munchify
from munch import unmunchify
from sqlite3 import Timestamp
import json
import pickle
import requests

import EyesUp
import GetManifest

guardians = ('SpacePirateKubli', 'DeathAngelx101', 'blacksun23')
startDate = datetime.fromisoformat('2022-06-19T00:00:00')

GetManifest.makepickle()

for guardian in guardians:
    gameData = EyesUp.initializeGuardian(guardian, startDate)
