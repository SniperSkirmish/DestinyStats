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
import sqlite3

# logging.basicConfig(filename='EyesUp.log', encoding='utf-8', level=logging.info)
log_format = '%(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("eyesup.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)


class guardian:
    pass

class activityClass:
    def __init__(self, period, instanceId):
        self.period = period
        self.instanceId = instanceId

    def __str__(self):
        return str(self.__dict__)

class gameStats:
    def __init__(self, period, instance, name, membershipId, characterId, score, kills, deaths, kd):
        self.period = period
        self.instance = instance
        self.name = name
        self.membershipId = membershipId
        self.characterId = characterId
        self.score = score
        self.kills = kills
        self.deaths = deaths
        self.kd = kd

    def __str__(self):
        return str(self.__dict__)

class gunStats:
    def __init__(self, referenceId, weaponKills, precisionKills, name, typeName, subType):
        self.referenceId = referenceId
        self.weaponKills = weaponKills
        self.precisionKills = precisionKills
        self.name = name
        self.typeName = typeName
        self.subType = subType

    def __str__(self):
        return str(self.__dict__)
    
def initializeGuardian(name, startDate):

    user = guardian

    activityCount = 10
    activityData = []
    activityList = []
    activityPage = 0
    # activityInfo = []
    activityUrls = []
    charActivities = []
    latestActivity = startDate
    # startDate = datetime.fromisoformat('2022-06-19T00:00:00')
    weaponStats = []

    # name = "SpacePirateKubli"

    print("Initialize Guardian " + name + " Starting at Date " + str(startDate))
    logging.info("Initialize Guardian " + name + " Starting at Date " + str(startDate))

    with open('manifest.pickle', 'rb') as data:
        destiny_data = pickle.load(data)

    connection = sqlite3.connect('eyetest.db')
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS Leaderboard (Name TEXT, MembershipId TEXT, MembershipType INT, Character1Id TEXT, Character2Id TEXT, Character3Id TEXT, LastLogin TEXT, LastActivity TEXT, SniperKills INT, SniperHeadShots INT, HeadshotPercentage REAL, MatchesPlayed INT)')

    # activityInfo = activityData('null','null')

    # print(activityInfo.period)

    searchUrl = 'https://www.bungie.net/Platform/User/Search/GlobalName/0/'
    header = {'X-API-Key': '3da118ce5b7d47e5876efd7a5e6e8b92'}
    body = {"displayNamePrefix": name}
    jbody = json.dumps(body)

    response = requests.post(searchUrl, headers=header, data=jbody)

    string = bytes.decode(response.content)
    jstring = json.loads(string)

    # IdIndex = string.find('membershipId')
    # commaIndex = string.find(',', IdIndex)
    # newString = string[IdIndex:commaIndex]
    # thirdString = newString.split('"')
    # user.membershipID = thirdString[2]

    nameSearch = munchify(jstring)

    # testList = [nameSearch, '0', '1']

    """ h = g.Response.searchResults[0].bungieGlobalDisplayName

    print(h)

    a = jstring['Response']
    b = a['searchResults']
    c = b[0]
    d = c['destinyMemberships']
    e = d[0]
    f = e['membershipId'] """

    user.globalDisplayName = nameSearch.Response.searchResults[0].bungieGlobalDisplayName
    user.membershipId = nameSearch.Response.searchResults[0].destinyMemberships[0].membershipId
    user.membershipType = nameSearch.Response.searchResults[0].destinyMemberships[0].membershipType

    cursor.execute("CREATE TABLE IF NOT EXISTS {} (Name TEXT, MembershipId INT, CharacterId INT, Period TEXT, Instance INT, Score INT, Kills INT, Deaths INT, WeaponRefId INT, WeaponKills INT, PrecisionKills INT, WeaponName TEXT, WeaponTypeName TEXT, WeaponItemSubtype INT)".format(user.globalDisplayName + 'GameData'))

    #print(a)
    #print(b)
    # print(c)
    # print(f)

    #print(IdIndex)
    #print(commaIndex)
    #print(newString)
    # print(user.globalDisplayName)
    # print(user.membershipId)

    profileUrl = 'https://www.bungie.net/Platform/Destiny2/' + str(user.membershipType) + '/Profile/'+ user.membershipId +'/?components=100'

    #print(profileUrl)

    profileResponse = requests.get(profileUrl, headers=header)

    profileString = bytes.decode(profileResponse.content)
    jprofileString = json.loads(profileString)

    profileSearch = munchify(jprofileString)

    user.characterIds = profileSearch.Response.profile.data.characterIds
    user.dateLastPlayed = profileSearch.Response.profile.data.dateLastPlayed[:-1]

    # print(user.characterIds)
    # print(user.dateLastPlayed)

    for i in range(3):

        activityCnt = 0
        activityDate = datetime.fromisoformat(user.dateLastPlayed)
        activityPage = 0

        while activityDate > startDate:
            activityUrl = 'https://www.bungie.net/Platform/Destiny2/' + str(user.membershipType) + '/Account/'+ user.membershipId + '/Character/' + user.characterIds[i] + '/Stats/Activities/?mode=5&page=' + str(activityPage) + '&count=' + str(activityCount)
            activityUrls.append(activityUrl)

            # print(activityUrl)

            activityResponse = requests.get(activityUrl, headers=header)

            activityString = bytes.decode(activityResponse.content)
            fixedActivityString = activityString.replace('values', 'bValues')
            jactivityString = json.loads(fixedActivityString)

            activitySearch = munchify(jactivityString)

            # a = activitySearch.Response.activities[0]
            # b = getmembers(a)
            # # print(b)
            # c = a.period
            # d = a.activityDetails.instanceId
            # e = unmunchify(a)
            # f = e['values']
            # g = f['score']
            # h = g['basic']
            # m = h['value']

            # n = munchify(f)
            # o = n.score.basic.value

            for j in activitySearch.Response.activities:

                # unmunchedJ = unmunchify(j)
                # valuesLookup = unmunchedJ['values']
                # remunchedValues = munchify(valuesLookup)

                if j.bValues.kills.basic.value > 0:
                    activityPeriod = j.period[:-1] #remove Z at end of string
                    activityInstance = j.activityDetails.instanceId
                    activityDate = datetime.fromisoformat(activityPeriod)
                    if activityDate > latestActivity:
                        print(str(activityDate) + " " + str(latestActivity))
                        latestActivity = activityDate
                        
                    print("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                    logging.info("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                
                else:
                    print("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))
                    logging.info("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))

                if activityDate > startDate:
                    if j.bValues.kills.basic.value > 0:
                        activityList.append(activityClass(activityPeriod,activityInstance))
                        activityCnt = activityCnt + 1
                        print("If " + str(activityDate))
                        logging.info("If " + str(activityDate))
                    else:
                        print("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                        logging.info("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                else:
                    print("Break " + str(activityDate) + " " + str(startDate))
                    logging.info("Break " + str(activityDate) + " " + str(startDate))
                    break
            
            print("Activity Page " + str(activityPage))
            logging.info("Activity Page " + str(activityPage))
            activityPage = activityPage + 1


        #print(activityResponse.json())
        charActivities.append(activityCnt)
        print("Latest Activity = " + str(latestActivity))
        logging.info("Latest Activity = " + str(latestActivity))

    for k in activityList:

        carnageUrl = 'https://stats.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/' + str(k.instanceId)

        carnageResponse = requests.get(carnageUrl, headers=header)

        carnageString = bytes.decode(carnageResponse.content)
        fixedCarnageString = carnageString.replace('values', 'bValues')
        jcarnageString = json.loads(fixedCarnageString)

        carnageReport = munchify(jcarnageString)
        carnageEntries = carnageReport.Response.entries

        #print(carnageEntries[10].characterId)

        for l in carnageReport.Response.entries:
            if user.membershipId == l.player.destinyUserInfo.membershipId:
                latestScore = l
                # print(l.player.destinyUserInfo.membershipId)
                break

        try: 
            weapons = latestScore.extended.weapons
        except Exception as e:
            print("Exception raised Weapons - " + str(e) + " in instance " + str(k.instanceId))
            logging.info("Exception raised Weapons - " + str(e) + " in instance " + str(k.instanceId))
            continue

        stats = latestScore.bValues

        try:
            matchStats = gameStats(k.period, k.instanceId, name, latestScore.player.destinyUserInfo.membershipId, latestScore.characterId, stats.score.basic.value, stats.kills.basic.value, stats.deaths.basic.value, stats.killsDeathsRatio.basic.value)
        
        except Exception as e:
                print("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                logging.info("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                continue

        for m in weapons:
            weaponId = m.referenceId
            weaponKills =  m.bValues.uniqueWeaponKills.basic.value 
            headshotKills = m.bValues.uniqueWeaponPrecisionKills.basic.value 
            weaponStats.append(gunStats(weaponId, weaponKills, headshotKills, 'null', 'null', 'null'))

        activityData.append([matchStats, weaponStats.copy()])
        weaponStats.clear()
        print(k.period)
        logging.info(k.period)

    for index, entry in enumerate(activityData):
        for slot, weapon in enumerate(entry[1]):
            try:
                weaponData = destiny_data['DestinyInventoryItemDefinition'][weapon.referenceId]
                activityData[index][1][slot].name = weaponData['displayProperties']['name']
                activityData[index][1][slot].typeName = weaponData['itemTypeDisplayName']
                activityData[index][1][slot].subType = weaponData['itemSubType']

                cursor.execute("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(user.globalDisplayName + 'GameData'), (entry[0].name, entry[0].membershipId, entry[0].characterId, entry[0].period, entry[0].instance, entry[0].score, entry[0].kills, entry[0].deaths, weapon.referenceId, weapon.weaponKills, weapon.precisionKills, weapon.name, weapon.typeName, weapon.subType))

            except:
                logging.info("Failed to get weapon info from weapon id " + str(weapon.referenceId) + " in match " + entry[0].instance)

            # print(entry[0].name + " " + str(entry[0].membershipId) + " " 
            #     + str(entry[0].characterId) + " " + entry[0].period + " " 
            #     + entry[0].instance + " " + str(entry[0].score) + " " 
            #     + str(entry[0].kills) + " " + str(entry[0].deaths) + " "
            #     + str(weapon.referenceId)  + " " + str(weapon.weaponKills) + " "
            #     + str(weapon.precisionKills)  + " " + weapon.name + " "
            #     + weapon.typeName + " " + str(weapon.subType))

    kills = cursor.execute("SELECT SUM(WeaponKills) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(user.globalDisplayName + 'GameData')).fetchone()[0]
    headshots = cursor.execute("SELECT SUM(PrecisionKills) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(user.globalDisplayName + 'GameData')).fetchone()[0]
    
    if kills == None:
        headshotPercentage = 0
    else:
        headshotPercentage = round((headshots / kills * 100), 1)

    games =  cursor.execute("SELECT COUNT(DISTINCT Instance) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(user.globalDisplayName + 'GameData')).fetchone()[0]

    cursor.execute('INSERT INTO Leaderboard VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (user.globalDisplayName, user.membershipId, user.membershipType, user.characterIds[0], user.characterIds[1], user.characterIds[2], user.dateLastPlayed, latestActivity, kills, headshots, headshotPercentage, games))

    connection.commit()
    cursor.close()
    connection.close()

    print("Done")
    logging.info("Done")

    return