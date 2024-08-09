---
title:  "Python TimeDate functions"
layout: post
categories: python technical
---

I needed a quick understanding of the Python 3.3.0 datetime functionality to do a difference in times across days. Python make it amazingly easy.

```python
import datetime
from datetime import timedelta

# get current timedate
now = datetime.datetime.now()
print "now: " + str(now)
# get one day of time oneday = timedelta(days=1)
# make one day in the future and past
tomorrow = now + oneday
yesterday = now - oneday
print "tomorrow: " + str(tomorrow)
print "yesterday: " + str(yesterday)
# compare times
if now < tomorrow:
  print "now < tomorrow"
elif now > tomorrow:
  print "now > tomorrow"
else:
  print "now must be equal tomorrow"
if now > yesterday:
 print "now > yesterday"
elif now < yesterday:
 print "now < yesterday"
else:
 print "now = yesterday"
```

The expected results are:

```shell
CMD> python time.py
now: 2015-03-19 14:30:31.083000
tomorrow: 2015-03-20 14:30:31.083000
yesterday: 2015-03-18 14:30:31.083000
now < tomorrow
now > yesterday
```

I hope this helps someone.
