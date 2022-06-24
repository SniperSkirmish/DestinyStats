import logging, requests, zipfile, os, pickle, json, sqlite3

logging.basicConfig(filename='EyesUp.log', encoding='utf-8', level=logging.DEBUG)

def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny2/Manifest/'
    header = {'X-API-Key': '3da118ce5b7d47e5876efd7a5e6e8b92'}

    #get the manifest location from the json
    r = requests.get(manifest_url, headers=header)
    manifest = r.json()
    mani_url = 'http://www.bungie.net'+manifest['Response']['mobileWorldContentPaths']['en']

    #Download the file, write it to 'MANZIP'
    r = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(r.content)
    print("Download Complete!")
    logging.debug("Manifest Download Complete!")

    #Extract the file contents, and rename the extracted file
    # to 'Manifest.content'
    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'Manifest.content')
    print('Unzipped!')
    logging.debug("Manifest Unzipped")

hashes = {
    'DestinyActivityDefinition': 'hash',
    'DestinyActivityTypeDefinition': 'hash',
    'DestinyClassDefinition': 'hash',
    'DestinyGenderDefinition': 'hash',
    'DestinyInventoryBucketDefinition': 'hash',
    'DestinyInventoryItemDefinition': 'hash',
    'DestinyProgressionDefinition': 'hash',
    'DestinyRaceDefinition': 'hash',
    # 'DestinyTalentGridDefinition': 'gridHash',
    # 'DestinyUnlockFlagDefinition': 'flagHash',
    'DestinyHistoricalStatsDefinition': 'statId',
    # 'DestinyDirectorBookDefinition': 'bookHash',
    # 'DestinyStatDefinition': 'statHash',
    # 'DestinySandboxPerkDefinition': 'perkHash',
    # 'DestinyDestinationDefinition': 'destinationHash',
    # 'DestinyPlaceDefinition': 'placeHash',
    # 'DestinyActivityBundleDefinition': 'bundleHash',
    # 'DestinyStatGroupDefinition': 'statGroupHash',
    # 'DestinySpecialEventDefinition': 'eventHash',
    # 'DestinyFactionDefinition': 'factionHash',
    # 'DestinyVendorCategoryDefinition': 'categoryHash',
    # 'DestinyEnemyRaceDefinition': 'raceHash',
    # 'DestinyScriptedSkullDefinition': 'skullHash',
    # 'DestinyGrimoireCardDefinition': 'cardId'
}

hashes_trunc = {
    'DestinyInventoryItemDefinition': 'itemHash',
    'DestinyTalentGridDefinition': 'gridHash',
    'DestinyHistoricalStatsDefinition': 'statId',
    'DestinyStatDefinition': 'statHash',
    'DestinySandboxPerkDefinition': 'perkHash',
    'DestinyStatGroupDefinition': 'statGroupHash'
}

def build_dict(hash_dict):
    #connect to the manifest
    con = sqlite3.connect('manifest.content')
    print('Connected')
    #create a cursor object
    cur = con.cursor()

    all_data = {}
    #for every table name in the dictionary
    for table_name in hash_dict.keys():
        #get a list of all the jsons from the table
        cur.execute('SELECT json from '+table_name)
        print('Generating '+table_name+' dictionary....')

        #this returns a list of tuples: the first item in each tuple is our json
        items = cur.fetchall()

        #create a list of jsons
        item_jsons = [json.loads(item[0]) for item in items]

        #create a dictionary with the hashes as keys
        #and the jsons as values
        item_dict = {}
        hash = hash_dict[table_name]
        for item in item_jsons:
            item_dict[item[hash]] = item

        #add that dictionary to our all_data using the name of the table
        #as a key.
        all_data[table_name] = item_dict

    print('Dictionary Generated!')
    return all_data

def makepickle():
    #check if pickle exists, if not create one.
    if os.path.isfile(r'path\to\file\manifest.content') == False:
        get_manifest()
        all_data = build_dict(hashes)
        with open('manifest.pickle', 'wb') as data:
            pickle.dump(all_data, data)
            print("'manifest.pickle' created!\nDONE!")
    else:
        print('Pickle Exists')

    with open('manifest.pickle', 'rb') as data:
        all_data = pickle.load(data)

# hash = 1363886209
# ghorn = all_data['DestinyInventoryItemDefinition'][hash]

# i = ghorn['displayProperties']

# print('Name: ' + ghorn['displayProperties']['name'])
# print('Type: '+ghorn['itemTypeDisplayName'])
# print('Tier: '+ghorn['tierTypeName'])
# print(ghorn['itemDescription'])
