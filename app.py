#!/usr/bin/env python3

import httplib2
import os
import sys
import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from pyvirtualdisplay import Display

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at
# https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

CLIENT_SECRETS_FILE = "client_secret.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

%s

with information from the Cloud Console
https://cloud.google.com/console

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                           CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# main stuff
timeout = 180  # check new video every 3 minutes
url = 'http://awsmtv.com'
playlist_id = "PLW8EHElJMrAHgbyntXjGSVxfif4Sx-jjE"

def get_current_video_id():

    video_id = ""

    display = Display(visible=0, size=(800, 600))
    display.start()

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it("tvPlayer_1"))

    try:
      element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CLASS_NAME, "ytp-title-link")))
      link = element.get_attribute('href')
      video_id = link.replace('https://www.youtube.com/watch?v=', '')
    finally:
      driver.quit()
      display.stop()
      return video_id

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def add_video_to_playlist(youtube, videoID, playlistID):
    add_video_request=youtube.playlistItems().insert(
    part="snippet",
    body={
        'snippet': {
          'playlistId': playlistID, 
          'resourceId': {
                  'kind': 'youtube#video',
              'videoId': videoID
            }
        }
    }
    ).execute()
    return True

def list_videos_in_playlist(youtube, playlistID):
  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=playlistID,
    part='snippet',
    maxResults=5
  )
  playlistitems_list_response = playlistitems_list_request.execute()
  playlistitems = playlistitems_list_response['items']
  videos_in_playlist = []
  for item in playlistitems:
    video_id = item['snippet']['resourceId']['videoId']
    videos_in_playlist.append(video_id)
  return videos_in_playlist

def main():
    while True:
        print("Getting current video...")
        video_id = get_current_video_id()
        if not video_id:
            print("Cannot get current video")
            continue
        print("Video ID is %s" % video_id)
        youtube = get_authenticated_service()
        videos_in_playlist = list_videos_in_playlist(youtube,
                                                     playlist_id)
        if video_id not in videos_in_playlist:
            if not add_video_to_playlist(youtube, video_id, playlist_id):
                print("Cannot add video ID %s to playlist" % video_id)
                continue
            print("Video ID %s is added to playlist" % video_id)
        else:
            print('Video ID %s already exists in playlist' % video_id)
        time.sleep(timeout)

if __name__ == '__main__':
    main()