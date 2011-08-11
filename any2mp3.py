#!/usr/bin/env python
#
# usage: any2mp3.py <file [more files]>
#
# I use this script to normalize sound volume
# and convert music files to mp3 before uploading
# to my phone. It calls the following external programs:
#
# ffmpeg - http://www.ffmpeg.org/
# normalize - http://normalize.nongnu.org/
# midentify - http://www.mplayerhq.hu/
# lame - http://lame.sourceforge.net/
#
# Example:
#
# $ any2mp3.py Music/*
#
# The command above take all files (not directories)
# in the Music/ directory, normalizes them and
# encodes new mp3-files into the current directory.
#
# Warning. If you have the original files in mp3-format
# in the current directory they may be overwritten.
# Put the original mp3:s in a different directory if
# you want to keep the originals.
#
####################################################

import sys
import os
import re

# Recognized suffixes.
# Actually the program works with all types of files
# recognized by ffmpeg. Like .avi, .mov, .flv, .mp4 and so on.
# Add them to the suffixes list if you want to
# rip audio from video files into mp3-files.
#suffixes = [ '.mp3', '.wav', '.ogg', '.flac', '.avi', '.flv', '.mov', '.mp4', '.mpg', '.mpeg' ]
suffixes = [ '.mp3', '.wav', '.ogg', '.flac']
#bitrates = [ '128', '160', '192', '224', '256', '320']
bitrates = [ '128', '160', '192', '224' ]


# Song info
title = False
artist = False
album = False
year = False
comment = False
genre = False
track_num = False
bitrate = 224

def get_info_value(name, text):
    m = re.compile( 'ID_CLIP_INFO_NAME(\d+)=' + name).search(text)
    if m:
        num = m.group(1)
        m = re.compile( 'ID_CLIP_INFO_VALUE' + num + '=(.*)').search(text)
        if m:
            val = m.group(1)
            return val
    return False

def get_info(track):
    global title, artist, album, year, comment, genre, track_num, bitrate
    # Call midentify on track to get info text
    cmd = 'midentify "' + track + '"'
    text = os.popen(cmd).read()
    title = get_info_value('Title', text)
    artist = get_info_value('Artist', text)
    album = get_info_value('Album', text)
    year = get_info_value('Year', text)
    comment = get_info_value('Comment', text)
    track_num = get_info_value('Track', text)
    genre = get_info_value('Genre', text)
    m = re.compile( 'ID_AUDIO_BITRATE=(\d+)').search(text)
    if m:
        rate = m.group(1)
    else:
        rate = 192000 # Use 192k as fallback
    for b in bitrates:
        if int(b) * 1000 >= int(rate):
            bitrate = b
            return
    # some players don't support more than 224 kbps
    bitrate = 224

def is_music(track):
    for suffix in suffixes:
        if track.lower().endswith(suffix):
            return True
    return False

def outname(track):
    # remove dirs
    name = os.path.basename(track)
    # remove suffix
    lname = name.lower()
    for suffix in suffixes:
        idx = lname.rfind(suffix)
        if idx != -1:
            num = len(name) - idx
            name = name[:-num]
    # remove spaces
    name = name.replace('\ ', ' ')
    name = name.replace(' ', '_')
    name = name.replace('_-_', '-')
    name = name.replace("'", "")
    name = name.replace('\&', '&')
    # add .mp3
    name = name + '.mp3'
    return name

def normalize_encode_mp3(track_in, track_out):
    cmd = 'ffmpeg -y -i "' + track_in + '" tmp.wav' + ' 2> /dev/null'
    os.system(cmd)
    os.system('normalize -q tmp.wav')
    # create track_out from tmp.wav using lame
    get_info(track_in)
    # Fill in lame args
    cmd = 'lame --silent -m s -q 0 -b ' + str(bitrate)
    if title:
        cmd = cmd + " --tt '" + title + "'"
    if artist:
        cmd = cmd + " --ta '" + artist  + "'"
    if album:
        cmd = cmd + " --tl '" + album  + "'"
    if year:
        cmd = cmd + " --ty '" + year  + "'"
    if comment:
        cmd = cmd + " --tc '" + comment  + "'"
    if track_num:
        cmd = cmd + " --tn '" + track_num  + "'"
    if genre:
        cmd = cmd + " --tg '" + genre  + "'"
    cmd = cmd + " tmp.wav '" + track_out + "'"
    os.system(cmd) # Run lame
    return True


BLUE = '\033[94m'
ENDC = '\033[0m'
# Main

total = 0
for arg in sys.argv:
    if is_music(arg):
        total = total + 1

curr = 0
for arg in sys.argv:
    # Loop through all args
    # Normalize and encode to mp3 if suffix is recognized
    if is_music(arg):
        curr = curr + 1
        out = outname(arg)
        print "%s%d/%d%s: %s -> %s" %(BLUE, curr, total, ENDC, arg, out)
        normalize_encode_mp3(arg, out)
