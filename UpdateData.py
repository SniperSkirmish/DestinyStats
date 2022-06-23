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

logging.basicConfig(filename='Update.log', encoding='utf-8', level=logging.DEBUG)

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
    def __init__(self, name, membershipId, membershipType, characterId, lastPlayed):
        self.name = name
        self.membershipId = membershipId
        self.membershipType = membershipType
        self.characterId = characterId
        self.lastPlayed = lastPlayed
    
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
    latestActivity = []
    weaponStats = []

    with open('manifest.pickle', 'rb') as data:
        destiny_data = pickle.load(data)

    connection = sqlite3.connect('eyetest.db')
    cursor = connection.cursor()

    players = cursor.execute("SELECT Name, MembershipId, MembershipType, Character1Id, Character2Id, Character3Id, LastPlayed FROM Leaderboard").fetchall()

    for index, player in enumerate(players):
        guardians.append(lightBearer(player[0], player[1], player[2], (player[3], player[4], player[5]), player[6]))

    for godSlayer in guardians:

        startDate =  datetime.fromisoformat(godSlayer.lastPlayed)

        profileUrl = 'https://www.bungie.net/Platform/Destiny2/' + str(godSlayer.membershipType) + '/Profile/'+ str(godSlayer.membershipId) +'/?components=100'
        header = {'X-API-Key': '3da118ce5b7d47e5876efd7a5e6e8b92'}

        #print(profileUrl)

        profileResponse = requests.get(profileUrl, headers=header)

        profileString = bytes.decode(profileResponse.content)
        jprofileString = json.loads(profileString)

        profileSearch = munchify(jprofileString)

        print(str(godSlayer.name))
        logging.debug(str(godSlayer.name))

        lastLogin = profileSearch.Response.profile.data.dateLastPlayed[:-1]
        if lastLogin == godSlayer.lastPlayed:
            print(str(godSlayer.name) + " No new games since " + str(lastLogin) + " " + str(godSlayer.lastPlayed))
            logging.debug(str(godSlayer.name) + " No new games since " + str(lastLogin) + " " + str(godSlayer.lastPlayed))
            continue
    
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
                        print("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                        logging.debug("Activity = " + str(activityPeriod) + ", " + str(activityInstance))
                    
                    else:
                        print("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))
                        logging.debug("Kills = " + str(j.bValues.kills.basic.value) + ", Period = " + str(j.period) + ", Instance = " + str(j.activityDetails.instanceId))

                    if activityDate > startDate:
                        if j.bValues.kills.basic.value > 0:
                            activityList.append(activityClass(activityPeriod,activityInstance))
                            activityCnt = activityCnt + 1
                            print("If " + str(activityDate))
                            logging.debug("If " + str(activityDate))
                        else:
                            print("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                            logging.debug("If DNF" + str(datetime.fromisoformat(j.period[:-1])))
                    else:
                        print("Break " + str(activityDate) + " " + str(startDate))
                        logging.debug("Break " + str(activityDate) + " " + str(startDate))
                        break
                
                print("Activity Page " + str(activityPage))
                logging.debug("Activity Page " + str(activityPage))
                activityPage = activityPage + 1


            #print(activityResponse.json())
            # charActivities.append(activityCnt)

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
                logging.debug("Exception raised Weapons - " + str(e) + " in instance " + str(k.instanceId))
                continue

            stats = latestScore.bValues

            try:
                matchStats = gameStats(k.period, k.instanceId, latestScore.player.destinyUserInfo.displayName, latestScore.player.destinyUserInfo.membershipId, latestScore.characterId, stats.score.basic.value, stats.kills.basic.value, stats.deaths.basic.value, stats.killsDeathsRatio.basic.value)
            
            except Exception as e:
                print("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                logging.debug("Exception raised MatchStats - " + str(e) + " in instance " + str(k.instanceId))
                continue

            for m in weapons:
                weaponId = m.referenceId
                weaponKills =  m.bValues.uniqueWeaponKills.basic.value 
                headshotKills = m.bValues.uniqueWeaponPrecisionKills.basic.value 
                weaponStats.append(gunStats(weaponId, weaponKills, headshotKills, 'null', 'null', 'null'))

            

            activityData.append([matchStats, weaponStats.copy()])
            weaponStats.clear()
            print(k.period)
            logging.debug(k.period)

        for index, entry in enumerate(activityData):
            for slot, weapon in enumerate(entry[1]):
                weaponData = destiny_data['DestinyInventoryItemDefinition'][weapon.referenceId]
                activityData[index][1][slot].name = weaponData['displayProperties']['name']
                activityData[index][1][slot].typeName = weaponData['itemTypeDisplayName']
                activityData[index][1][slot].subType = weaponData['itemSubType']

                cursor.execute("INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)".format(godSlayer.name + 'GameData'), (entry[0].name, entry[0].membershipId, entry[0].characterId, entry[0].period, entry[0].instance, entry[0].score, entry[0].kills, entry[0].deaths, weapon.referenceId, weapon.weaponKills, weapon.precisionKills, weapon.name, weapon.typeName, weapon.subType))


                # print(entry[0].name + " " + str(entry[0].membershipId) + " " 
                #     + str(entry[0].characterId) + " " + entry[0].period + " " 
                #     + entry[0].instance + " " + str(entry[0].score) + " " 
                #     + str(entry[0].kills) + " " + str(entry[0].deaths) + " "
                #     + str(weapon.referenceId)  + " " + str(weapon.weaponKills) + " "
                #     + str(weapon.precisionKills)  + " " + weapon.name + " "
                #     + weapon.typeName + " " + str(weapon.subType))

        kills = cursor.execute("SELECT SUM(WeaponKills) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(godSlayer.name + 'GameData')).fetchone()[0]
        headshots = cursor.execute("SELECT SUM(PrecisionKills) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(godSlayer.name + 'GameData')).fetchone()[0]
        headshotPercentage = round((headshots / kills * 100), 1)
        games =  cursor.execute("SELECT COUNT(Instance) FROM {} WHERE WeaponTypeName='Pulse Rifle'".format(godSlayer.name + 'GameData')).fetchone()[0]

        cursor.execute("UPDATE Leaderboard SET LastPlayed = ?, SniperKills = ?, SniperHeadShots = ?, HeadshotPercentage = ?, MatchesPlayed = ? WHERE MembershipId = ?", (lastLogin, kills, headshots, headshotPercentage, games, godSlayer.membershipId))

        activityData.clear()
        activityList.clear()

        print(str(godSlayer.name) + "'s Data Entered")
        logging.debug(str(godSlayer.name) + "'s Data Entered")

    connection.commit()
    cursor.close()
    connection.close()

    print("Update Done")
    logging.debug("Update Done")