---
title:  "Raspberry Pi 2 built-in LED"
layout: post
categories: python technical
---

For an assignment in my robotics class, I need to have an autonomous system react to the environment around it. Reacting can be as simple as flashing a LED if a sensor detects a change.

I have two objectives for the Raspberry Pi 2 (RasPi2) and those are to take a picture using the 5mp webcam and flash a LED. I could use the standard GPIO pins and setup a separate LED but noticed we have two perfectly good LEDs built into the board.

Reading on these built-in LED did not elicit any clear way of interacting with them from the regular Linux documentation. I informally called them the Red Power and Green DiskIO LEDs. It was by reading the headers to the source for [Windows 10 for Raspberry Pi 2](https://ms-iot.github.io/content/en-US/win10/samples/PinMappingsRPi2.htm) that I found the GPIO pinouts for these two LEDs. They are:

```
35 Red Power LED
47 Yellow DiskIO LED
```

So far as I know, these are only valid for the Raspberry Pi 2 and not older versions of the board. I’m including below a test script that has to be run as root that flashes the Red Power LED several times. The Green LED is accessible but tied to a trigger when the SSD card is accessed.

{% highlight python %}

#!/usr/bin/python

import RPi.GPIO as GPIO
import time

#channels = [35, 47]
channels = [35] # red power
#channels = [47] # green hdd/ssd

print "Start program"

print "Setup GPIO"
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(channels, GPIO.OUT)

for i in range(4):
  print " turn off LEDs"
  GPIO.output(channels, GPIO.LOW)
  time.sleep(1)
  print " turn on LEDs"
  GPIO.output(channels, GPIO.HIGH)
  time.sleep(1)

print "Cleanup GPIO"
GPIO.cleanup()

print "End program"

{% endhighlight %}

To run this script make sure you use “sudo” as access to GPIO hardware requires elevated permissions.

{% highlight console %}
pi@raspi2 ~/projects/pycam $ sudo python pyblink.py
Start program
Setup GPIO
  turn off LEDs
  turn on LEDs
  turn off LEDs
  turn on LEDs
  turn off LEDs
  turn on LEDs
  turn off LEDs
  turn on LEDs
Cleanup GPIO
End program
pi@raspi2 ~/projects/pycam $
{% endhighlight %}

Disconnecting the Green LED from the DiskIO requires changing some kernel level trigger settings. They are located in the system file /sys/class/leds/led0/trigger file. Try the following to disconnect the trigger:

{% highlight console %}
echo none | sudo tee /sys/class/leds/led0/trigger
{% endhighlight %}

You should now be able to use the Green LED. To revert back to default behavior:

{% highlight console %}
echo mmc0 | sudo tee /sys/class/leds/led0/trigger
{% endhighlight %}

I’ll be writing more about the complete system in future posts but this is just a first foray into the world that is the Raspberry Pi 2 (RasPi2). I hope this will be helpful for someone else trying to flash a LED and does not want to buy a prototyping breadboard.
