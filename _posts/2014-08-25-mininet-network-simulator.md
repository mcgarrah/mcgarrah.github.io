---
title:  "Mininet network simulator"
layout: post
categories: vmware technical
---

I’m taking a graduate course in computer networking at Georgia Tech. The tools they are asking us to use are all open source and allow for some pretty interesting projects.

One such tool is the [Mininet](http://mininet.org/) software that allows for building realistic virtual networks with real switches, routers and applications running on a single system. We are using a virtual machine that contains a copy of the Linux operating system and the virtual networking software. So far we are encountering minor issues with the OS and VM software.

<!-- excerpt-end -->

The base VM for Mininet has an [option#2 building from source code](http://mininet.org/download/) but it needs to also include the [Pyretic software](http://frenetic-lang.org/pyretic/) to allow for Python coding of the network. I’m reviewing the documentation on [building a Pyretic VM](https://github.com/frenetic-lang/pyretic/wiki/Building-the-Pyretic-VM) on their website now. There are a lot of moving pieces in this configuration.

For my class, we have a VM that is not an LTS release several versions back for Ubuntu. It is in an unsupported version as of now. This is why I’m interested in getting this completely built from source.

```console
sudo apt-get install python-dev python-pip screen hping3
sudo pip install networkx bitarray netaddr ipaddr pytest ipdb
sudo mv asynchat.py /usr/lib/python2.7/
wget https://raw.github.com/frenetic-lang/pyretic/master/pyretic/backend/patch/asynchat.py
sudo mv asynchat.py /usr/lib/python2.7/
sudo chown root:root /usr/lib/python2.7/asynchat.py
git clone https://github.com/git/git.git
pushd git/contrib/subtree/
make
popd
rm -rf git
cd ~
git clone git://github.com/frenetic-lang/pyretic.git
rm .profile
wget http://frenetic-lang.org/pyretic/useful/.profile
chmod g-w .profile
wget http://frenetic-lang.org/pyretic/useful/.screenrc
sudo cat /dev/zero > zero.fill; sudo sync; sleep 1; sudo sync; sudo rm -f zero.fill; sudo shutdown -h now
```

2014-09-22: And the conclusion is to just accept the VM as it is. Too many dark alleys involved in building a separate VM for the class that isn’t approved by the TA. It was worth a try and let me know how many whirly-pieces of software were involved in this VM. If you are taking a class, just use the tools they provide.

I will revisit this topic later when I’m done with the class to build a toolset from this for my own purposes.
