#!/usr/bin/env python

import argparse
from datetime import datetime
from urllib import FancyURLopener
import json
import subprocess

parser = argparse.ArgumentParser(description='Compute FRC rankings simulations.')
parser.add_argument('eventcode')
parser.add_argument('depth')

args = parser.parse_args()

year = str(datetime.now().year)
eventCode = str(args.eventcode)
event = str(year + eventCode)
depth = str(args.depth)

#put into file
file = open(year+eventCode+'.py', 'w+')

class AugurOpener(FancyURLopener):
	version = 'brennon-brimhall:augur:2'

opener = AugurOpener()

# Get current rankings
url = "https://www.thebluealliance.com/api/v2/event/" + event + "/rankings?X-TBA-App-Id=brennon-brimhall:augur:2"
response = opener.open(url)
rankings = json.loads(response.read())

# Get matches
url = "https://www.thebluealliance.com/api/v2/event/" + event +"/matches?X-TBA-App-Id=brennon-brimhall:augur:2"
response = opener.open(url)
matches = json.loads(response.read())

# Get OPR or CCWM
url = "https://www.thebluealliance.com/api/v2/event/" + event +"/stats?X-TBA-App-Id=brennon-brimhall:augur:2"
response = opener.open(url)
stats = json.loads(response.read())["oprs"]

file.write('#!/usr/bin/env python\n\n')

file.write("import event\n")
file.write(eventCode + " = event.Event(" + depth + ")\n")

file.write("\n") #will put in a newline

#counter to ignore the header
i = 0;
for rank in rankings:
	if (i > 0):
		team = str(rank[1])
		rp = str(round(rank[2]*rank[9]))
		matchesPlayed = rank[9]
		
		#Normalize sorts; we don't simulate those.
		firstSort = str(round((rank[3] / matchesPlayed), 2))
		secondSort = str(round((rank[4] / matchesPlayed), 2))
		thirdSort = str(round((rank[5] / matchesPlayed), 2))
		fourthSort = str(round((rank[6] / matchesPlayed), 2))
		fifthSort = str(round((rank[7] / matchesPlayed), 2))

		file.write(eventCode + ".addTeam(" + team + ",\t" + rp + ",\t" + firstSort + ",\t" + secondSort + ",\t" + thirdSort + ",\t" + fourthSort + ",\t" + fifthSort + ")\n")
	i += 1

file.write("\n") #will put int a newline

for match in matches:
	matchType = match['comp_level']

	if (matchType != "qm"):
		continue

	matchNumber = str(match['match_number'])
	red1 = match['alliances']['red']['teams'][0][3:]
	red2 = match['alliances']['red']['teams'][1][3:]
	red3 = match['alliances']['red']['teams'][2][3:]
	blue1 = match['alliances']['blue']['teams'][0][3:]
	blue2 = match['alliances']['blue']['teams'][1][3:]
	blue3 = match['alliances']['blue']['teams'][2][3:]

	#Calculate probability via OPR if available; fall back to straight 50% if not.
	prob = '.5'

	redTotal = (stats[red1] + stats[red2] + stats[red3])
	blueTotal = (stats[blue1] + stats[blue2] + stats[blue3])

	if ((redTotal + blueTotal) != 0):
		prob = str(round((stats[red1] + stats[red2] + stats[red3]) / (stats[red1] + stats[red2] + stats[red3] + stats[blue1] + stats[blue2] + stats[blue3]),2))

	if (match['score_breakdown'] == None):
		file.write(eventCode + ".addMatch(" + red1 + ",\t" + red2 + ",\t" + red3 + ",\t" + blue1 + ",\t" + blue2 + ",\t" + blue3 + ",\t" + prob + ")\t#Match " + matchNumber + "\n")
	else:
		file.write("#" + eventCode + ".addMatch(" + red1 + ",\t" + red2 + ",\t" + red3 + ",\t" + blue1 + ",\t" + blue2 + ",\t" + blue3 + ",\t" + prob + ")\t#Match " + matchNumber + "\n")

file.write("\n") #newline
file.write(eventCode + ".calculate()\n")
file.write("print \"\"\n")