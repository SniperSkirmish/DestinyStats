from base64 import decode
from dataclasses import replace
from datetime import datetime
from munch import munchify
from munch import unmunchify
from sqlite3 import Timestamp
import json
import logging
import pickle
import requests
import sqlite3

log_format = '%(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("updater.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)

# logging.basicConfig(filename='Update.log', encoding='utf-8', level=logging.info)

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

class lightBearer:
    def __init__(self, name, membershipId, membershipType, characterId, lastPlayed, lastActivity):
        self.name = name
        self.membershipId = membershipId
        self.membershipType = membershipType
        self.characterId = characterId
        self.lastPlayed = lastPlayed
        self.lastActivity = lastActivity
    
    def __str__(self):
        return str(self.__dict__)

def updateStats():
    activityCount = 10
    activityData = []
    activityList = []
    activityPage = 0
    # activityInfo = []
    activityUrls = []
    # charActivities = []
    guardians = []
    weaponCategory = 'Pulse Rifle'
    weaponStats = []

    with open('manifest.pickle', 'rb') as data:
        destiny_data = pickle.load(data)

    connection = sqlite3.connect('eyetest.db')
    cursor = connection.cursor()

    players = cursor.execute("SELECT Name, MembershipId, MembershipType, Character1Id, Character2Id, Character3Id, LastLogin, LastActivity FROM Leaderboard").fetchall()

    for index, player in enumerate(players):
        guardians.append(lightBearer(player[0], player[1], player[2], (player[3], player[4], player[5]), player[6], player[7]))

    for godSlayer in guardians:

        startDate =  datetime.fromisoformat(godSlayer.lastActivity)
        latestActivity = startDate

        profileUrl = 'https://www.bungie.net/Platform/Destiny2/' + str(godSlayer.membershipType) + '/Profile/'+ str(godSlayer.membershipId) +'/?components=100'
        header = {'X-API-Key': '3da118ce5b7d47e5876efd7a5e6e8b92'}

        #print(profileUrl)

        profileResponse = requests.get(profileUrl, headers=header)

        profileString = bytes.decode(profileResponse.content)
        jprofileString = json.loads(profileString)

        profileSearch = munchify(jprofileString)

        lastLogin = profileSearch.Response.profile.data.dateLastPlayed[:-1]
        if lastLogin == godSlayer.lastPlayed:
            print(str(godSlayer.name) + " No new games since " + str(lastLogin) + " " + str(godSlayer.lastPlayed))
            logger.info(str(godSlayer.name) + " No new games since " + str(lastLogin) + " " + str(godSlayer.lastPlayed))
            continue

        print(str(godSlayer.name) + " Last Login " + str(lastLogin) + " Last Recorded " + str(godSlayer.lastPlayed))
        logger.debug(str(godSlayer.name) + " Last Login " + str(lastLogin) + " Last Recorded " + str(godSlayer.lastPlayed))
    
        for i in range(3):

            activityCnt = 0
            activityDate = datetime.fromisoformat(lastLogin)
            activityPage = 0

            while activityDate > startDate:
                activityUrl = 'https://www.bungie.net/Platform/Destiny2/' + str(godSlayer.membershipType) + '/Account/'+ str(godSlayer.membershipId) + '/Character/' + str(godSlayer.characterId[i]) + '/Stats/Activities/?mode=5&page=' + str(activityPage) + '&count=' + str(activityCount)
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
                            latestActivity = activityDate

                        print("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                        logger.debug("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                    
                    else:
                        print("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))
                        logger.debug("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))

                    if activityDate > startDate:
                        if j.bValues.kills.basic.value > 0:
                            activityList.append(activityClass(activityPeriod,activityInstance))
                            activityCnt = activityCnt + 1
                            print("If " + str(activityDate))
                            logger.debug("If " + str(activityDate))
                        else:
                            print("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                            logger.debug("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                    else:
                        print("Break " + str(activityDate) + " " + str(startDate))
                        logger.debug("Break " + str(activityDate) + " " + str(startDate))
                        break
                
                print("Activity Page " + str(activityPage))
                logger.debug("Activity Page " + str(activityPage))
                activityPage = activityPage + 1


            #print(activityResponse.json())
            # charActivities.append(activityCnt)
            print("Latest Activity = " + str(latestActivity))
            logging.debug("Latest Activity = " + str(latestActivity))

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
                if godSlayer.membershipId == l.player.destinyUserInfo.membershipId:
                    latestScore = l
                    # print(l.player.destinyUserInfo.membershipId)
                    break

            try: 
                weapons = latestScore.extended.weapons
            except Exception as e:
                print("Exception raised Weapons - " + str(e) + " in instance " + str(k.instanceId))
                logger.critical("Exception raised Weapons - " + str(e) + " in instance " + str(k.instanceId))
                continue

            stats = latestScore.bValues

            try:
                matchStats = gameStats(k.period, k.instanceId, godSlayer.name, latestScore.player.destinyUserInfo.membershipId, latestScore.characterId, stats.score.basic.value, stats.kills.basic.value, stats.deaths.basic.value, stats.killsDeathsRatio.basic.value)
            
            except Exception as e:
                print("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                logger.critical("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                continue

            for m in weapons:
                weaponId = m.referenceId
                weaponKills =  m.bValues.uniqueWeaponKills.basic.value 
                headshotKills = m.bValues.uniqueWeaponPrecisionKills.basic.value 
                weaponStats.append(gunStats(weaponId, weaponKills, headshotKills, 'null', 'null', 'null'))

            

            activityData.append([matchStats, weaponStats.copy()])
            weaponStats.clear()
            print(k.period)
            logger.debug(k.period)

        for index, entry in enumerate(activityData):
            for slot, weapon in enumerate(entry[1]):
                try:
                    weaponData = destiny_data['DestinyInventoryItemDefinition'][weapon.referenceId]
                    activityData[index][1][slot].name = weaponData['displayProperties']['name']
                    activityData[index][1][slot].typeName = weaponData['itemTypeDisplayName']
                    activityData[index][1][slot].subType = weaponData['itemSubType']

                    cursor.execute("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(godSlayer.name + 'GameData'), (entry[0].name, entry[0].membershipId, entry[0].characterId, entry[0].period, entry[0].instance, entry[0].score, entry[0].kills, entry[0].deaths, weapon.referenceId, weapon.weaponKills, weapon.precisionKills, weapon.name, weapon.typeName, weapon.subType))
                    logger.debug(str(weapon.name) + " inserted for instance " + str(entry[0].instance))

                except:
                    logger.critical("Failed to get weapon info from weapon id " + str(weapon.referenceId) + " in match " + entry[0].instance)

                # print(entry[0].name + " " + str(entry[0].membershipId) + " " 
                #     + str(entry[0].characterId) + " " + entry[0].period + " " 
                #     + entry[0].instance + " " + str(entry[0].score) + " " 
                #     + str(entry[0].kills) + " " + str(entry[0].deaths) + " "
                #     + str(weapon.referenceId)  + " " + str(weapon.weaponKills) + " "
                #     + str(weapon.precisionKills)  + " " + weapon.name + " "
                #     + weapon.typeName + " " + str(weapon.subType))

        kills = cursor.execute("SELECT SUM(WeaponKills) FROM {} WHERE WeaponTypeName=?".format(godSlayer.name + 'GameData'), (weaponCategory,)).fetchone()[0]
        headshots = cursor.execute("SELECT SUM(PrecisionKills) FROM {} WHERE WeaponTypeName=?".format(godSlayer.name + 'GameData'), (weaponCategory,)).fetchone()[0]
        
        if headshots == None:
                kills = 0
                headshots = 0
                headshotPercentage = 0
        else:
                headshotPercentage = round((headshots / kills * 100), 1)

        games =  cursor.execute("SELECT COUNT(DISTINCT Instance) FROM {} WHERE WeaponTypeName=?".format(godSlayer.name + 'GameData'), (weaponCategory,)).fetchone()[0]

        cursor.execute("UPDATE Leaderboard SET LastLogin = ?, LastActivity = ?, SniperKills = ?, SniperHeadShots = ?, HeadshotPercentage = ?, MatchesPlayed = ? WHERE MembershipId = ?", (lastLogin, latestActivity, kills, headshots, headshotPercentage, games, godSlayer.membershipId))

        activityData.clear()
        activityList.clear()

        print(str(godSlayer.name) + "'s Data Entered")
        logger.info(str(godSlayer.name) + "'s Data Entered")

    connection.commit()
    cursor.close()
    connection.close()

    print("Update Done")
    logger.debug("Update Done")