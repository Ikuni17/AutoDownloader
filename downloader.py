import os
from bs4 import BeautifulSoup
import requests
import datetime
import re
import shutil
import subprocess

# Switched to checking for new episodes for each show everyday to avoid missing delayed releases
# The logs file will avoid downloading duplicate episodes
# {Weekday : [Show Names]}. Monday = 1 and Sunday = 7 from date.isoweekday()
'''dEmily = {1: [],
          2: [],
          3: ["Sousei no Onmyouji"],
          4: [],
          5: [],
          6: ["Shuumatsu no Izetta", "Udon no Kuni no Kiniro Kemari", "Watashi ga Motete Dousunda"],
          7: []}
dBrad = {1: [],
         2: [],
         3: [],
         4: [],
         5: [],
         6: [],
         7: []}
dBoth = {1: [],
         2: [],
         3: [],
         4: [],
         5: [],
         6: ["Bubuki Buranki"],
         7: []}'''

lEmily = ["ACCA 13-ku Kansatsu-ka", "Chain Chronicle ~Hekuseitasu no Hikari~", "Demi-chan wa Kataritai", "Fuuka",
          "Gabriel Dropout", "Kobayashi-san Chi no Maid Dragon", "Kuzu no Honkai", "Little Witch Academia",
          "Masamune-kun no Revenge", "Seiren", "Urara Meirochou"]
lBrad = ["Ao no Exorcist: Kyoto Fujouou-Hen", "Onihei", "Schoolgirl Strikers: Animation Channel"]
lBoth = ["CHAOS;CHILD", "Hand Shakers", "Tales of Zestiria the X", "Youjo Senki"]

# Commands to have aria download to the correct location, rather than moving files with the OS
escapedQuote = "\""
bothCommand = "aria2c --conf-path=\"aria2.conf\" -d D:\\Anime\\"
emilyCommand = "aria2c --conf-path=\"aria2.conf\" -d D:\\Anime\\Emily\\"
bradCommand = "aria2c --conf-path=\"aria2.conf\" -d D:\\Anime\\Brad\\"

# Directory to store torrent files
torrentDir = (".\Torrents")
sTorrentDir = ".\Torrents\\"

# Base URL used to find the correct torrent
searchUrl = "http://www.nyaa.se/?page=search&cats=1_37&filter=0&term="
qualityUrl = "+horriblesubs+1080"

# Keep a list of filenames of the torrents for aria commands
lTorrents = []

# Log of downloaded episodes
sLogs = ".\\logs.txt"


# Creates a large aria command that starts all torrents for a group
def startTorrents(command):
    # Append all torrents to the command file for simultaneous download
    for torrents in lTorrents:
        command = command + " " + escapedQuote + sTorrentDir + torrents + escapedQuote
    print((subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, universal_newlines=True).communicate())[0])


# Example aria command that starts three torrents
# os.system("aria2c --conf-path=\"aria2.conf\" -d D:\\Anime\\ \"[HorribleSubs] Bloodivores - 01 [1080p].mkv.torrent\" \"[HorribleSubs] Bloodivores - 02 [1080p].mkv.torrent\" \"[HorribleSubs] Bloodivores - 03 [1080p].mkv.torrent\"")

# Returns the download URL for a torrent of the most recent episode of a show
def findUrl(showName):
    # logsFile = open(sLogs, "r")
    showName = showName.replace(" ", "+")
    # Setup the complete URL
    url = searchUrl + showName + qualityUrl
    # Send an HTTP get request
    r = requests.get(url)
    # Parse the HTML
    parser = BeautifulSoup(r.content, "html.parser")
    # Create a list of URLs with the matching tag
    # For NYAA, this is the download button in the search results table
    tdTag = parser.select("td.tlistdownload a")
    downloadList = []
    for item in tdTag:
        downloadUrl = item['href'].replace("//", "http://")

        # Check if the episode has been downloaded before
        if downloadUrl in open(sLogs).read():
            continue
        # If not, update the log and append the torrent URL
        else:
            logsFile = open(sLogs, "a")
            logsFile.write(downloadUrl + "\n")
            logsFile.close()
            downloadList.append(downloadUrl)

    return downloadList


# Iterate through all download URLs and get the .torrent files
def downloadTorrents(urlList):
    for url in urlList:
        # Get the header from the server
        r = requests.get(url)
        # Parse the header for the filename
        filename = re.findall(r'"([^"]*)"', r.headers['Content-Disposition'])
        # Store the filename for use later
        lTorrents.append(filename[0])
        # Download the torrent file
        command = 'curl -OJLs "' + url + '"'
        subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()

    # Avoid directory already exists errors
    if not os.path.isdir(torrentDir):
        os.makedirs(torrentDir)

    # Move the torrent files into a seperate directory
    subprocess.Popen(["move", "*.torrent", sTorrentDir], stdout=subprocess.PIPE, shell=True).communicate()


# Find torrent urls, download them then start the torrents for each set: Emily, Brad, Both
def runSet(showList, command):
    allUrls = []
    # Search for all shows
    for show in showList:
        showUrls = findUrl(show)
        if showUrls is not None:
            allUrls = allUrls + showUrls
    downloadTorrents(allUrls)
    startTorrents(command)


# Clear the list of torrents and delete the files after completion
def clearTorrents():
    global lTorrents

    # Clear the filenames list
    lTorrents = []
    # Remove the folder with the torrent files
    shutil.rmtree(torrentDir)


def main():
    # Get the current weekday
    # now = datetime.datetime.now()
    # weekday = now.isoweekday()

    # Pass in the list of shows for each set, and the corresponding command
    '''runSet(dEmily[weekday], emilyCommand)
    clearTorrents()
    runSet(dBrad[weekday], bradCommand)
    clearTorrents()
    runSet(dBoth[weekday], bothCommand)
    clearTorrents()'''
    runSet(lEmily, emilyCommand)
    clearTorrents()
    runSet(lBrad, bradCommand)
    clearTorrents()
    runSet(lBoth, bothCommand)
    clearTorrents()


# Start!
main()
