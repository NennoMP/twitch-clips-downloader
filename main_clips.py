import requests
import re
import datetime
import json
import sys
import os
import urllib.request

from datetime import timedelta

# Project from auto-retriving clips from twitch and auto-publishing them on YT

# GLOBAL VARIABLES
file_path       = 'Settings/twitch.json'
twitch_api      = ''
client_id       = ''
client_secret   = ''
OAuth           = ''
streamer        = ''
first           = 0

# get start datetime for search
def get_start_time(mytimedelta):
    return (datetime.datetime.now(datetime.timezone.utc) - timedelta(days = mytimedelta)).isoformat()

# get end datetime for search
def get_end_time():
    return (datetime.datetime.now(datetime.timezone.utc)).isoformat()

# load default parameters
def load_twitch_settings(file_path):
    global twitch_api
    global client_id
    global client_secret
    global OAuth
    global streamer
    global first

    with open(file_path) as inf:
        file = json.load(inf)
        twitch_api      = file['twitch']['api']['url']
        client_id       = file['twitch']['api']['client_id']
        client_secret   = file['twitch']['api']['client_secret']
        OAuth           = file['twitch']['api']['OAuth']
        streamer        = file['twitch']['streamer']
        first           = int(file['twitch']['first'])

    return

# retrieve clips urls
def get_clips():
    global first
    global streamer
    mytimedelta = 1
    headers = {'Authorization': OAuth, 'Client-id': client_id}

    # retrieve broadcaster_id
    url = twitch_api + 'users'
    params = {'login': streamer}

    r = requests.get(url, params=params, headers=headers)
    print('GET_USERS[' + str(streamer) + ']: ' + str(r.status_code))
    broadcaster_id = r.json()['data'][0]['id']

    # retrieve urls
    url = twitch_api + 'clips'
    ended_at =  get_end_time()
    while(1):
        started_at = get_start_time(mytimedelta)
        params = {'broadcaster_id': broadcaster_id, 'first': first, 'started_at': started_at, 'ended_at': ended_at}
        r = requests.get(url, params=params, headers=headers)
        if (len(r.json()['data']) == 0):
            mytimedelta+= 1
        else:
            print('GET_CLIPS[' + str(streamer) + ']: ' + str(r.status_code))
            r = r.json()
            break

    # store urls
    clips_array = []
    for el in r['data']:
        clip_url = re.search('(.*)-preview', el['thumbnail_url']).group(1) + '.mp4'
        clips_array.append(clip_url)
    
    # download and store
    download_clips(clips_array)

    return clips_array

# download clips (.mp4)
def download_clips(clips_array):
    global streamer
    out_path = 'ClipProject/' + streamer + "/"
    
    if (not os.path.exists(out_path)):
        os.makedirs(out_path)
    
    i = 0
    for el in clips_array:
        file_name = streamer + str(i) + '.mp4'
        urllib.request.urlretrieve(el, out_path + file_name)
        i+= 1

    return


if __name__ == '__main__':
    load_twitch_settings(file_path)
    get_clips()
    print('DONE')