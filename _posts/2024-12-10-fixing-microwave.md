---
title:  "Attempting to fix a broken microwave in the Home"
layout: post
published: true
---

My relatively new microwave just stopped heating things for no apparent reason one morning. We bought it a couple years back (about 3 years ago), so I was not happy as I expect these to work awhile with several working for ten (10) plus years. We picked up a new one from the local white box retailer as we wanted a replacement quickly. But my wife while digging around on Youtube found [Microwave works but wont heat - Cheap and easy fix](https://www.youtube.com/watch?v=z0FON4p_4ZA) which was exactly what we experienced.

That video said it was likely a fuse or diode which are both cheap enough that they are worth an attempt at fixing. That will give me an extra microwave for the kids to use upstairs if I can fix it and save some landfill space.

| ![](/assets/images/microwave-fuse-closeup.jpg){:width="75%" height="75%"} | ![](/assets/images/microwave-diode-closeup.jpg) |
|:--:|:--:|
| Fuse | Diode |

<!-- excerpt-end -->

Here is me breaking open the microwave cabinet and paying particular attention to the capacitor in there. Obviously do not have it plugged in while poking around. I checked the capacitor with a multi-meter before poking my fingers around inside the unit and had left the microwave unplugged for a day or two before going in so didn't have much charge on it.

[![Microwave Open](/assets/images/microwave-open.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-open.jpg){:target="_blank"}

I could visually inspect the fuse which is conveniently in a fuse holder unlike in the video with the in-line fuse on a wire setup. This looks good to me so on to the next bit. I did later pull the fuse and do a multi-meter continuity check on it but a blown fuse it pretty obvious to a mark-one eyeball but you still check.

[![Microwave Fuse](/assets/images/microwave-fuse.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-fuse.jpg){:target="_blank"}

That left the "CL01-12 Microwave Oven High Voltage Diode Rectifier" which was a bit more trouble to extract. Figuring out how to test a diode was easy enough with a multi-meter which I happen to have. [Testing a microwave diode with a digital meter](https://www.youtube.com/watch?v=Cx8Q5crqKaw) was the best video I could find. Rigging up a 9v battery with the multi-meter with a bread twist-tie wire was a fun hack. My diode was definitely bad with voltage going both directions at 5.8v and 4.7v. The drop in voltage is expected for the 5.8v in one direction but the back-feed of 4.7v was showing a bad diode.

[![Microwave Diode](/assets/images/microwave-diode.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-diode.jpg){:target="_blank"}

Here are some pictures of my capacitor extracted and labeled for which wires go where. I did have some trouble getting the diode off the capacitor that required pulling out my needle nose plyers. This was the most difficult part of the extraction so far.

| Connected | Disconnected |
|:--:|:--:|
| [![Microwave Capacitor 1](/assets/images/microwave-capacitor-connected.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-capacitor-connected.jpg){:target="_blank"} | [![Microwave Capacitor 2](/assets/images/microwave-capacitor-disconnected.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-capacitor-disconnected.jpg){:target="_blank"} |

Here is the back panel with my manufacturer, model and serial numbers. It includes the Manufacture Date in December 2020 which is what started me being unhappy about how long the microwave lasted.

[![Microwave Model](/assets/images/microwave-model.jpg){:width="45%" height="45%" style="display:block; margin-left:auto; margin-right:auto"}](/assets/images/microwave-model.jpg){:target="_blank"}

Amazon search for "Microwave Diode High Voltage Diode CL01-12" found me several vendors including one that had a complete [Home Microwave Oven Repair Replacement Parts Kits](https://www.amazon.com/KOKISO-Microwave-Replacement-Capacitor-CL01-12/dp/B0B7WTRY7G/) with the capacitor, multiple fuses, and diodes including shrink wrap. I was tempted to buy the full kit, but decided to save my shelf space the extra parts that I'll never find when I need them in the future.

More to come...
