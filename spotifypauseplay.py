import requests, pythoncom, os, subprocess, spotipy, json, pyWinhook as pyHook, pathlib
from pynput.keyboard import KeyCode, Key, Controller
from spotipy.oauth2 import SpotifyClientCredentials
from time import sleep
from pycaw.pycaw import AudioUtilities

#from spotifyAuth import (cid,csecret)

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
    stoken = spotipy.oauth2.SpotifyOAuth(client_id=cid, client_secret=csecret, redirect_uri='http://localhost:8080', scope='user-modify-playback-state user-read-playback-state', username=username)
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
print(getoauth())

keyboard = Controller()
play = True
changing = False
volume = 100

deviceCount = 0
def OnKeyboardEvent(event):
    global play, changing, sp, stoken, token, volume, devices, selecteDevice, deviceCount, deviceid
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
    if event.KeyID == 124 and changing == False: #F13 Key 124
        if play == True:
            changing = True
            try:
                sp.start_playback(device_id=deviceid)
                print('Play')
                changing = False
                play = False
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
        else:
            changing = True
            try:
                sp.pause_playback(device_id=deviceid)
                print('Pause')
                changing = False
                play = True
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
            except spotipy.client.SpotifyException as e:
                apierrors(e,event,event.KeyID)
    if event.KeyID == 128 and changing == False: #F17 Key
        try:
            changing = True
            sp.next_track(device_id=deviceid)
            print('Next Song')
            play = False
            changing = False
        except spotipy.client.SpotifyException as e:
            apierrors(e,event,event.KeyID)
    if event.KeyID == 127 and changing == False: #F16 Key
        try:
            changing = True
            sp.previous_track(device_id=deviceid)
            print('Previous Song')
            play = False
            changing = False
        except spotipy.client.SpotifyException as e:
            apierrors(e,event,event.KeyID)
    #return event.KeyID
    return True
    
def apierrors(e,event,keyid):
    global stoken, play, changing, sp, devices, selecteDevice, deviceid
    
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
            if keyid != 127:
                ite = stoken.is_token_expired(stoken.get_cached_token())
                play = not play
                changing = False
                OnKeyboardEvent(event)
            else:
                print('No Previous Song (probably due to you being on shuffle)')
                changing = False
    elif hcode == "404":
        if "Player command failed: No active device found" in e or "Player command failed: Restriction violated" in e:
            data = sp.devices()
            devices = []
            for key in data['devices']:
                devices.append([key['name'],key['id']])
            selecteDevice = True
            tmp = subprocess.call('cls',shell=True)
            if len(devices) == 1:
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
    elif hcode == "429":
        None
    elif hcode == "500":
        None
    elif hcode == "502":
        None
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
keyboard.press('a')
# wait forever
pythoncom.PumpMessages()