#!/usr/bin/env python3

import gi
from gi.repository import GLib

gi.require_version('Playerctl', '2.0')

from gi.repository import Playerctl

import time

import json

import requests

player = Playerctl.Player()

startTime = 0.0
playbackTime = 0.0
accumulatedTime = 0.0
previousTitle = ""
previousArtist = ""
totalTime = 0.0

stage = 0
subtitles = []

def parseSubtitles (input):
    global subtitles
    global stage
    subtitles = []
    stage = 0
    lines = str.split(input, '\n')
    for l in lines:
        timestamp = l[1:8]
        parts = str.split(timestamp, ':')
        time = (int(parts[0]) * 60) + float(parts[1])
        subtitle = l[11:]
        subtitles.append((time, subtitle))

def advanceSubtitles (timein):
    global subtitles
    global stage
    for i in range(len(subtitles)):
        thisSub = subtitles[i]
        if thisSub[0] <= timein + 1:
            if stage == i:
                stage += 1
                if i < len(subtitles) -1:
                    if(len(thisSub[1]) != 0):
                        diff = subtitles[i+1][0] - thisSub[0]
                        timePerChar = (diff / len(thisSub[1])) * 0.75
                        for c in thisSub[1]:
                            print("\033[1;37;40m", end='',flush=True)
                            if (c == '.' or c == ';' or c == ","):
                                print("\033[1;32;40m", end='', flush=True)
                            if (c.isupper()):
                                print("\033[1;36;40m", end='', flush=True)
                            print(c, end='', flush=True)
                            print("\033[0m", end='', flush=True)
                            time.sleep(timePerChar)
                    print()


PARAMS = {
    'format':'json',
    'q_track':'',
    'q_artist':'',
    'user_language':'en',
    'f_subtitle_length':'0',
    'f_subtitle_length_max_deviation':'0',
    'subtitle_format':'lrc',
    'app_id':'web-desktop-app-v1.0',
    'guid':'e08e6c63-edd1-4207-86dc-d350cdf7f4bc',
    'usertoken':'1710144894f79b194e5a5866d9e084d48f227d257dcd8438261277',
}

URL = 'https://apic-desktop.musixmatch.com/ws/1.1/macro.subtitles.get'

while True:
    if (previousTitle != player.get_title() and previousArtist != player.get_artist()):
        for i in range(100):
            print()
        previousTitle = player.get_title()
        previousArtist = player.get_artist()
        PARAMS['q_track'] = previousTitle
        PARAMS['q_artist'] = previousArtist
        r = requests.get(url = URL, params = PARAMS)
        data = r.json()
        subs = data['message']['body']['macro_calls']['track.subtitles.get']['message']['body']['subtitle_list'][0]['subtitle']['subtitle_body']
        parseSubtitles(subs)
        time.sleep(5.1)
        player.previous()
        startTime = time.time()
        playbackTime = 0.0
        accumulatedTime = 0.0

    if (player.props.playback_status == Playerctl.PlaybackStatus.STOPPED or player.props.playback_status == Playerctl.PlaybackStatus.PAUSED):
        accumulatedTime += playbackTime;
        playbackTime = 0.0
        startTime = time.time()
    else:
        playbackTime = time.time() - startTime

    totalTime = accumulatedTime + playbackTime
    advanceSubtitles(totalTime)
    #print(totalTime)
    time.sleep(0.1)
