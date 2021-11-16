import re
import datetime
import json
import sys
import os

import requests
import urllib.request

from datetime import timedelta


# GLOBALS
file_path: str      = 'Settings/twitch.json'
twitch_api: str
client_id: str
client_secret: str
OAuth: str
streamer: str
first: int          = 0



 ''' 
    Get start datetime for search
'''
def get_start_time(my_time_delta):
    return (datetime.datetime.now(datetime.timezone.utc) - timedelta(days = my_time_delta)).isoformat()


''' 
    Get end datetime for search
'''
def get_end_time():
    return (datetime.datetime.now(datetime.timezone.utc)).isoformat()

'''
    Load default parameters
'''
def load_twitch_settings(file_path):
    global twitch_api
    global client_id
    global client_secret
    global OAuth
    global streamer
    global first

    # Read settings
    with open(file_path) as inf:
        file = json.load(inf)
        twitch_api      = file['twitch']['api']['url']
        client_id       = file['twitch']['api']['client_id']
        client_secret   = file['twitch']['api']['client_secret']
        OAuth           = file['twitch']['api']['OAuth']
        streamer        = file['twitch']['streamer']
        first           = int(file['twitch']['first'])

    return

'''
    Retrieve clips urls
'''
def get_clips():
    global first
    global streamer
    
    my_time_delta = 1
    headers = {'Authorization': OAuth, 'Client-id': client_id}

    # Retrieve broadcaster_id
    url = twitch_api + 'users'
    params = {'login': streamer}
    
    r = requests.get(url, params=params, headers=headers)
    print('GET_USERS[' + str(streamer) + ']: ' + str(r.status_code))
    broadcaster_id = r.json()['data'][0]['id']

    #Rretrieve urls
    url = twitch_api + 'clips'
    ended_at =  get_end_time()
    while(True):
        started_at = get_start_time(my_time_delta)
        params = {'broadcaster_id': broadcaster_id, 'first': first, 'started_at': started_at, 'ended_at': ended_at}
        r = requests.get(url, params=params, headers=headers)
        
        if len(r.json()['data']) == 0:
            my_time_delta+= 1
        else:
            print(f'GET_CLIPS[{streamer}]: {r.status_code}')
            r = r.json()
            break

    # Store urls in an array
    clips_array = []
    for el in r['data']:
        clip_url = re.search('(.*)-preview', el['thumbnail_url']).group(1) + '.mp4'
        clips_array.append(clip_url)
    
    # Download and write out
    download_clips(clips_array)

    return clips_array

'''
    Download clips in .mp4 format
'''
def download_clips(clips_array):
    global streamer
    
    out_path = 'ClipProject/' + streamer + "/"
    
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    i = 0
    for el in clips_array:
        file_name = streamer + str(i) + '.mp4'
        urllib.request.urlretrieve(el, out_path + file_name)
        i += 1

    return


def main():
    load_twitch_settings(file_path)
    get_clips()

if __name__ == '__main__':
    main()
    print('DONE')
