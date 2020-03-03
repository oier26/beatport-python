# -*- coding: utf-8 -*-
# This file is part of beatport-python.
# Copyright 2020, Oier Arroniz.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""
Python Beatport API <https://oauth-api.beatport.com> Wrapper.
"""
import csv
import os
from pathlib import Path

import pytest
from mediafile import MediaFile, FileTypeError

import beatport

api_key = '57713c3906af6f5def151b33601389176b37b429'
api_secret = 'b3fe08c93c80aefd749fe871a16cd2bb32e2b954'
access_token = '77beecc7fd51e69142d5d78312421f8ef421981b'
access_secret = '7b6a2178d4315ea2bbf47597306f445296465839'
auth_response = 'oauth_token=ebef014e0fac2a767c4b579840e24da887273369&oauth_verifier=' \
                '01749676015e0349f0aaf1fcccf97b9c&oauth_callback_confirmed=true'


def get_client():
    client = beatport.Client(api_key=api_key, api_secret=api_secret,
                             access_token=access_token, access_secret=access_secret)
    return client


def find_audio_files_in_folder(folder):
    audio_files_list = []
    for root, dirs, files in os.walk(folder):
        audio_files_list.extend(
            [f'{root}/{file}' for file in files if Path(file).suffix in ['.mp3', '.m4a', '.flac', '.wav']]
        )
    return audio_files_list


def get_media_file(audio_file_path):
    try:
        media_file = MediaFile(audio_file_path)
        return media_file
    except FileTypeError:
        pytest.fail(f"Audio file {audio_file_path} was not correctly opened.")


def open_csv_file_reader(csv_path):
    if not os.path.exists(csv_path):
        raise FileNotFoundError
    csv_file = open(csv_path, mode='r')
    return csv_file, csv.reader(csv_file, delimiter='|')


def open_csv_file_writer(csv_path):
    if os.path.exists(csv_path):
        raise FileExistsError
    csv_file = open(csv_path, mode='w', newline='')
    return csv_file, csv.writer(csv_file, delimiter='|', quotechar='"', quoting=csv.QUOTE_MINIMAL)


@pytest.mark.parametrize("music_folder", ['C:/Users/oarroniz/Music/iTunes/iTunes Media/Music'])
@pytest.mark.parametrize("csv_found_path", ['C:/Users/oarroniz/Downloads/found_genres.csv'])
@pytest.mark.parametrize("csv_not_found_path", ['C:/Users/oarroniz/Downloads/not_found_genres.csv'])
def test_full_fetching_process(music_folder, csv_found_path, csv_not_found_path):
    client = get_client()
    csv_found_file, csv_found_writer = open_csv_file_writer(csv_found_path)
    csv_not_found_file, csv_not_found_writer = open_csv_file_writer(csv_not_found_path)
    for audio_file_path in find_audio_files_in_folder(music_folder):
        media_file = get_media_file(audio_file_path)
        result = client.get_query(
            '/catalog/3/search/',
            query=media_file.title,
            facets=f"{'artistName:' + media_file.artist.split(',')[0] or None}"
        )
        object_track = next((objectTrack for objectTrack in result if objectTrack.get("type") == "track"), None)

        # Search genre
        if object_track is not None:
            genre_list = ", ".join([genre.get('name') for genre in object_track.get('genres')] +
                                   [subgenre.get('name') for subgenre in object_track.get('subGenres')])
            beatport_title = object_track.get("title")
            beatport_artist = ", ".join([artist.get("name") for artist in object_track.get("artists")])
            print(f'{media_file.artist}|{media_file.title}|{genre_list}|{beatport_artist}|{beatport_title}')
            csv_found_writer.writerow([audio_file_path, media_file.artist, media_file.title,
                                       genre_list, beatport_artist, beatport_title, '1'])
        else:
            print(f'{media_file.artist}|{media_file.title}|None|None')
            csv_not_found_writer.writerow([audio_file_path, media_file.artist, media_file.title, "", "", "", 0])

    csv_found_file.close()
    csv_not_found_file.close()


@pytest.mark.parametrize("music_folder", ['C:/Users/oarroniz/Music/iTunes/iTunes Media/Music'])
@pytest.mark.parametrize("csv_file", ['C:/Users/oarroniz/Downloads/found_genres.csv',
                                      'C:/Users/oarroniz/Downloads/not_found_genres.csv'])
def test_full_tagging_process(music_folder, csv_file):
    csv_file, csv_reader = open_csv_file_reader(csv_file)
    for audio_file_path in find_audio_files_in_folder(csv_reader[1]):
        media_file = get_media_file(audio_file_path)
        if csv_reader[7] == 1:
            media_file.genre = csv_reader[4]
        media_file.save()

    csv_file.close()
