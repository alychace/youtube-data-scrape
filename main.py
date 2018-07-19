#!/usr/bin/python

import httplib2
import os
import sys
import csv

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains

# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:
   %s
with information from the APIs Console
https://console.developers.google.com

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))
class Csv:
  def __init__(self, output):
    self.output = open(output, "w")
    self.output.write("Title,Author,Date,Channel URL, Video URL\n")

  def add(self, title, author, date, channel_url, url):
    self.output.write(title.replace(",", "-") + "," + author + "," + date.split("T")[0] + "," + channel_url + "," + url + "\n")

  def close(self):
    self.output.close()

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()
  args = argparser.parse_args()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))


def list_info(youtube, video_id, output):
  results = youtube.videos().list(part="snippet", id=video_id).execute()

  title = results["items"][0]["snippet"]["title"]
  author = results["items"][0]["snippet"]["channelTitle"]
  channel_url = ("https://www.youtube.com/channel/" + results["items"][0]["snippet"]["channelId"])
  date = results["items"][0]["snippet"]["publishedAt"]
  url = ("https://www.youtube.com/watch?v=" + results["items"][0]['id'])
  description = results["items"][0]["snippet"]["description"]

  output.add(title, author, date, channel_url, url)

if __name__ == "__main__":
  argparser.add_argument("--input", help="Input filename.")
  # The "default_language" option specifies the language of the video's default metadata.
  argparser.add_argument("--output", help="Output filename.")
  args = argparser.parse_args()
  # The "action" option specifies the action to be processed.
  youtube = get_authenticated_service(args)
  output_file = Csv(args.output)
  input_file = open(args.input, 'r')

  ## Parses our opened file as a comma-delineated CSV file.
  csvreader = csv.reader(input_file, delimiter=',', quotechar='"')

  for row in csvreader:
    try:
      youtube_id = row[0].strip().split("watch?v=")[1].split("&")[0]
      list_info(youtube, youtube_id, output_file)
    except:
        output_file.add("Error looking up " + row[0].strip(), "", "", "", "")
        print("An error occured looking up " + row[0].strip())

  input_file.close()
  output_file.close()