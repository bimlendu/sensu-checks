#!/usr/bin/env python26

import feedparser
import argparse
from datetime import datetime
from pytz import timezone

parser = argparse.ArgumentParser(description='Check current status information from the AWS Service Health Dashboard (status.aws.amazon.com).')
parser.add_argument('--service')
parser.add_argument('--region')
args = parser.parse_args()

if args.region == None:
  feed = args.service
else:
  feed = args.service + '-' + args.region

try:
  d = feedparser.parse('http://status.aws.amazon.com/rss/' + feed + '.rss')
  if d.entries:
    title = d.entries[0]['title']
    pubdate = d.entries[0]['published']
    dsc = d.entries[0]['description']
  elif d['feed']['title']:
    print 'AWS OK: No events to display.'
    exit(0)
except KeyError:
  print 'AWS UNKNOWN: Feed http://status.aws.amazon.com/rss/' + feed + '.rss could not be parsed. Check command options.'
  exit(3)

# Check pudate for the first item, retrun OK if older than a day.
## strptime does not support timezones. so strip it off.
_pubdate = pubdate.rsplit(' ', 1)[0]
_pubdate = datetime.strptime(_pubdate, '%a, %d %b %Y %H:%M:%S')  ##Tue, 19 Aug 2014 16:19:21 PDT
_today = datetime.now(timezone('UTC'))
_today_PDT = _today.astimezone(timezone('US/Pacific'))
_pubdate_PDT = timezone('US/Pacific').localize(_pubdate)

_delta = _today_PDT - _pubdate_PDT
if (_delta.days > 1):
  print 'AWS OK: No events in past 24 hours.'
  exit(0)

if title.startswith("Service is operating normally"):
  status = 0
  msg = "AWS OK: "
elif (title.startswith("Informational message") or title.startswith("Performance issues")):
  status = 1
  msg = "AWS WARNING: "
elif (title.startswith("Service disruption")):
  status = 2
  msg = "AWS CRITICAL: "
else:
  status = 3
  msg = "AWS UNKNOWN: "

# Return message and exit code to Nagios
msg += title
print msg
print pubdate
print dsc

exit(status)
