---
title:  "Downgrading VMware ESXi 5.5 virtual machine hardware"
layout: post
categories: vmware technical
---

One of this issues I ran into with bouncing between VMware Player 6.0.3 and my VMware ESXi 5.5u1 server is the hardware level of the virtual machines. ESXi 5.5 without the vSphere licence will not manage the newer virtualHW.version = “10″ virtual machines.

The simple solution is to modify the .vmx file for your virtual machine and change the line:

{% highlight %}
.encoding = “UTF-8″
displayname = “mininet-pyretic-vm”
guestos = “ubuntu-64″
virtualhw.version = “10″
config.version = “8″
{% endhighlight %}

Notice the change in the forth line.

{% highlight %}
.encoding = “UTF-8″
displayname = “mininet-pyretic-vm”
guestos = “ubuntu-64″
virtualhw.version = “9″
config.version = “8″
{% endhighlight %}

You should shutdown the virtual machine, of course, before doing this and might want to remove it from the ESXi inventory without removing the files. Modify the VMX file, then re-add it to the inventory. You can download the VMX file to your desktop using the datastore browsers and return the file to the datastore with the same browser if you do not have SSH enabled on your ESXi server.

This trick let me add some OVA virtual machine archive provided by the [Mininet](http://mininet.org/) project that used VirtualBox originally. The import worked best in VMware Player because it seemed to clean up issues in the OVA file format.

As an aside, you can also upgrade a hw version from 8 to 9 and get the later supported version.

I hope this saves someone else troubles with their ESXi server.
