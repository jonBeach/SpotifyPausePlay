import requests, pythoncom, os, subprocess, spotipy, json, pyWinhook as pyHook, pathlib, random
from spotipy.oauth2 import SpotifyClientCredentials
#from pynput.keyboard import KeyCode, Key, Controller
#from time import sleep

sp = None
stoken = None
token = None
username = None
cid = None
csecret = None
filelist = None
deviceid = None
selecteDevice = False
devices = None
errorcount = 0
path = pathlib.Path(__file__).parent.absolute()

def setup():
    global filelist, path
    filelist = os.listdir(path)
    if os.path.exists(str(path)+"\spotifypauseplay.txt"):
        getinfo()
    else:
        print('CTRL+V and Right Click Should both work to paste')
        username = input("Enter Username:")
        cid = input("Enter Client ID:")
        csecret = input("Enter Client Secret:")
        deviceid = input("Enter device ID\n(You can enter nothing and it will automatically selecte a device for you\n \
        If you have spotify open on two different devices and neither is playing you will get an error and have to select a device but the program will help you with that!):")
        data = {}
        data.update({
            'username': username,
            'cid': cid,
            'csecret': csecret,
            'deviceid': deviceid})
        with open(str(path)+"\spotifypauseplay.txt", "w", encoding="utf8") as a:
            json.dump(data, a)
            a.close()
        getinfo()

def getinfo():
    global path, username, cid, csecret, deviceid
    with open(str(path)+"\spotifypauseplay.txt", "r", encoding="utf8") as a:
        data = json.loads(a.read())
        username = data['username']
        cid = data['cid']
        csecret = data['csecret']
        deviceid = data['deviceid']
        if deviceid.strip() == "":
            deviceid = None
            
def ConvertToJson(text, edit, number):
    if text == "None":
        return text
    if edit == True:
        if number == 1:
            totalcount = 0
            count = 0
            t1 = text.split()
            for word in t1:
                totalcount += 1
                if word == "'name':":
                    count += 1
                if count == 7:
                    newcount = totalcount    # THE FUCK IS THIS UGLY ASS CODE?!?!?!?
                    newstring = ""
                    oldstring = ""
                    while t1[newcount] != "'popularity':":
                        newstring += t1[newcount]+" "
                        newcount += 1
                    oldstring = newstring
                    newstring = newstring.strip()
                    newstring = newstring[1:(len(newstring))-2]
                    if "'" in newstring or '"' in newstring:
                        newstring = newstring.replace("'","")
                        newstring = newstring.replace('"',"")
                    text = text.replace(oldstring,('"'+newstring+'",'))
                    break
    text = text.replace("'",'"')
    text = text.replace("False", '"False"')
    text = text.replace("True", '"True"')
    text = text.replace("None", '"None"')
    text = json.loads(text)
    return text

def checkcachefile():
    global path, filelist
    count = 0
    cachefilelist = []
    for file in filelist:
        if file.find(".cache-") == 0:
            count += 1
            cachefilelist.append(file)
    if count > 0:
        if count == 1:
            if os.path.exists(cachefilelist[0]):
                print(cachefilelist[0])
                if (cachefilelist[0])[(str(cachefilelist).find('-'))+1:] == username:
                    return True
                else:
                    return False
        else:
            print('multiple files detected')
            for file in cachefilelist:
                print(file)
            return True
    else:
        return False

def getoauth():
    global sp, stoken, token, username, cid, csecret, path
    setup()
    stoken = spotipy.oauth2.SpotifyOAuth(client_id=cid, client_secret=csecret, redirect_uri='http://localhost:8080', scope='user-modify-playback-state user-read-playback-state user-read-recently-played', username=username)
    cacheExists = checkcachefile()
    if cacheExists == False:
        try:
            token = stoken.get_access_token()
        except Exception as e:
            tmp = subprocess.call('cls',shell=True)
            print(e)
            os.remove(str(path)+"\spotifypauseplay.txt")
            getoauth()
    token = stoken.get_cached_token()
    token = str(token).replace('\'','"')
    token = json.loads(token)
    token = token['access_token']
    sp = spotipy.Spotify(auth=token)
    tmp = subprocess.call('cls',shell=True)
    return token[0:(len(token))//2]

def GetDeviceList():
    global stoken, play, changing, sp, devices, selecteDevice, deviceid
    data = sp.devices()
    devices = []
    for key in data['devices']:
        devices.append([key['name'],key['id']])
    selecteDevice = True
    tmp = subprocess.call('cls',shell=True)
    if len(devices) == 0:
        print("No Active Device Found, please open Spotify on a device!\nPress Enter too refresh!")
    elif len(devices) == 1:
        name, did = devices[0]
        deviceid = did
        tmp = subprocess.call('cls',shell=True)
        print('Device Selected: Name: {0} ID: {1}'.format(name,did))
        changing = False
        print("Ready")
    else:
        print('\nSelect a device to play on (use arrow keys and enter)\n')
        for device in devices:
            name, did = device
            if device == devices[0]:
                print('>>> {0}'.format(name))
            else:
                print(name)

def GetDeviceInfo(info):
    global globals
    deviceinfo = ConvertToJson(str(sp.current_playback()),True,1)
    if deviceinfo == '"None"' or deviceinfo == "None":
        GetDeviceList()
    else:
        if info == "Start":
            deviceid = deviceinfo['device']['id']
            name = deviceinfo['device']['name']
            print('Device Selected: Name: {0} ID: {1}'.format(name,deviceid))
        elif info == "ID":
            deviceid = deviceinfo['device']['id']
            return deviceid

play = True
changing = False
volume = 100
getoauth()
GetDeviceInfo("Start")

deviceCount = 0
def OnKeyboardEvent(event):
    global play, changing, sp, stoken, token, volume, devices, selecteDevice, deviceCount, deviceid, errorcount
    if devices != None and len(devices) == 0 and event.KeyID == 13 and selecteDevice == True: #Enter Key
        GetDeviceList()
    if selecteDevice == True:
        if event.KeyID == 38: #up arrow
            if deviceCount > 0:
                deviceCount -= 1
                tmp = subprocess.call('cls',shell=True)
                print('\nSelect a device to play on (use arrow keys and enter)\n')
                for device in devices:
                    name, did = device
                    if device == devices[deviceCount]:
                        print('>>> {0}'.format(name))
                    else:
                        print(name)
        if event.KeyID == 40: #down arrow
            if deviceCount < len(devices)-1:
                deviceCount += 1
                tmp = subprocess.call('cls',shell=True)
                print('\nSelect a device to play on (use arrow keys and enter)\n')
                for device in devices:
                    name, did = device
                    if device == devices[deviceCount]:
                        print('>>> {0}'.format(name))
                    else:
                        print(name)
        if event.KeyID == 13: #Enter Key
            for device in devices:
                name, did = device
                if device == devices[deviceCount]:
                    deviceid = did
                    tmp = subprocess.call('cls',shell=True)
                    print('Device Selected: Name: {0} ID: {1}'.format(name,did))
                    print("Ready")
                    changing = False
                    break
    if event.KeyID == 124 and changing == False: #F13 Key
        if play == True:
            changing = True
            try:
                sp.start_playback(device_id=deviceid)
                print('Play')
                changing = False
                play = False
                errorcount = 0
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
        else:
            changing = True
            try:
                sp.pause_playback(device_id=deviceid)
                print('Pause')
                changing = False
                play = True
                errorcount = 0
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
    if event.KeyID == 125: #F14 Key
        if volume != 100:
            try:
                sp.volume(volume_percent=volume+10, device_id=deviceid)
                volume = volume+10
                if volume > 100:
                    volume = 100
                print('Volume Up: {0}'.format(volume))
                errorcount = 0
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
    if event.KeyID == 126: #F15 Key
        if volume != 0:
            try:
                sp.volume(volume_percent=volume-10, device_id=deviceid)
                volume = volume-10
                if volume < 0:
                    volume = 0
                print('Volume Down: {0}'.format(volume))
                errorcount = 0
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
    if event.KeyID == 128 and changing == False: #F17 Key
        try:
            changing = True
            sp.next_track(device_id=deviceid)
            print('Next Song')
            play = False
            changing = False
            errorcount = 0
        except spotipy.client.SpotifyException as e:
            apierrors(e,event,event.KeyID)
    if event.KeyID == 127 and changing == False: #F16 Key
        try:
            changing = True
            sp.previous_track(device_id=deviceid)
            print('Previous Song')
            play = False
            changing = False
            errorcount = 0
        except spotipy.client.SpotifyException as e:
            apierrors(e,event,event.KeyID)
    return True
    
def apierrors(e,event,keyid):
    global stoken, play, changing, sp, devices, selecteDevice, deviceid, errorcount
    
    #print(e)
    e = str(e)
    hcode = (e[e.find(':')+1:e.find(',')]).strip()
    
    if hcode == "200":
        None
    elif hcode == "201":
        None
    elif hcode == "202":
        None
    elif hcode == "204":
        None
    elif hcode == "304":
        None
    elif hcode == "400":
        None
    elif hcode == "401":
        if "The access token expired" in e:
            getoauth()
            changing = False
            OnKeyboardEvent(event)
    elif hcode == "403":
        if "Player command failed: Restriction violated" in e:
            if keyid == 124:
                errorcount += 1
                teste = "".join(((e.replace(" ", "")).splitlines()))
                if "httpstatus:403,code:-1-https://api.spotify.com/v1/me/player/play?" in teste or "httpstatus:403,code:-1-https://api.spotify.com/v1/me/player/pause?" in teste:
                    if errorcount > 15:
                        GetDeviceList()
                        lastsonguri = ConvertToJson(str(sp.current_user_recently_played(limit=1)),False,0)
                        lastsonguri = lastsonguri['items'][0]['track']['uri']
                        rannum = random.randint(1,7)
                        if rannum < 5 or lastsonguri.strip() == "" or lastsonguri == None or lastsonguri == '"None"':
                            sp.start_playback(device_id=deviceid,context_uri='spotify:playlist:02NrlaHwiz1FyqdR6wHLXl')
                            errorcount = 0
                            print(errorcount)
                        elif rannum == 6:
                            sp.start_playback(device_id=deviceid,uris=[lastsonguri])
                            errorcount = 0
                            print(errorcount)
                        else:
                            #sp.start_playback(device_id=deviceid,uris=["spotify:track:0IH3D0P8OrQFs6ajcqbm0R"])
                            sp.start_playback(device_id=deviceid,context_uri='spotify:playlist:1d50HXU36BFMPk5rpMPUyF',offset={"position":580}) #579
                            errorcount = 0
                            print(errorcount)
                        ite = stoken.is_token_expired(stoken.get_cached_token())
                        play = False
                        changing = False
                        print('You Broke Spotify :(')
                        print("Play")
                        errorcount = 0
                    else:
                        deviceid = GetDeviceInfo("ID")
                        #play = not play
                        changing = False
                        OnKeyboardEvent(event)
                else:
                    '''if errorcount > 15:
                        lastsonguri = ConvertToJson(str(sp.current_user_recently_played(limit=1)),False,0)
                        lastsonguri = lastsonguri['items'][0]['track']['uri']
                        rannum = random.randint(1,7)
                        if rannum < 5 or lastsonguri.strip() == "" or lastsonguri == None or lastsonguri == '"None"':
                            sp.start_playback(device_id=deviceid,context_uri='spotify:playlist:02NrlaHwiz1FyqdR6wHLXl')
                        elif rannum == 6:
                            sp.start_playback(device_id=deviceid,uris=[lastsonguri])
                        else:
                            sp.start_playback(device_id=deviceid,uris=["spotify:track:0IH3D0P8OrQFs6ajcqbm0R"])
                        ite = stoken.is_token_expired(stoken.get_cached_token())
                        play = not play
                        changing = False
                        print("Play")
                    else:
                        ite = stoken.is_token_expired(stoken.get_cached_token())
                        play = not play
                        changing = False
                        OnKeyboardEvent(event)'''
                    ite = stoken.is_token_expired(stoken.get_cached_token())
                    play = not play
                    changing = False
                    OnKeyboardEvent(event)
            elif keyid == 125:
                print("Error Putting Volume Up")
            elif keyid == 126:
                print("Error Putting Volume Down")
            elif keyid == 127:
                print('No Previous Song (probably due to you being on shuffle)')
            elif keyid == 128:
                print('Error Changing to Next Song!')
            changing = False
    elif hcode == "404":
        if "Player command failed: No active device found" in e or "Player command failed: Restriction violated" in e or "Device not found" in e:
            GetDeviceList()
    elif hcode == "429":
        None
    elif hcode == "500":
        print("500 - Error, I don't think i can fix this. There response to this error is...\nInternal Server Error. You should never receive this error because our\
        clever coders catch them all …\
        but if you are unlucky enough to get one, please report it to us through a comment at the bottom of this page.\
        \nSo yea I don't know...")
    elif hcode == "502":
        if "Bad gateway." in e:
            GetDeviceList()
    elif hcode == "503":
        None
    return
    
try:
    sp.volume(volume_percent=100, device_id=deviceid)
    print("Ready")
except spotipy.client.SpotifyException as e:
    print('Error setting volume')
    apierrors(e,None,-1000)

# create a hook manager
hm = pyHook.HookManager()
# watch for all keyboard events
hm.KeyDown = OnKeyboardEvent
# set the hook
hm.HookKeyboard()
# wait forever
pythoncom.PumpMessages()