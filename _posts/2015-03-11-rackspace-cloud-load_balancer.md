---
title:  "Rackspace Cloud Load Balancer with Windows 2012 IIS"
layout: post
categories: technical
---

I’m working on a problem with Windows 2012 RTM server running an IIS web service. To load balance it, we decided to use Rackspace Cloud Load Balancers. Periodically we receive some errors that appear in the system event logs.

```
"A fatal alert was generated and sent to the remote endpoint. This may result in termination of the connection. The TLS protocol defined fatal error code is 40. The Windows SChannel error state is 1205."
```

My guess is that the Rackspace Load Balancer is actually an F5. The LBs are trying to encrypt the communication to the web servers using TLSv1.2 for the connection checks but by default Windows 2012 does not have TLSv1.2 enabled.

Below is an EnabledTLS12.reg file for enabling TLSv1.2 on a Windows 2012 server.

{% highlight ini %}

Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2]

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Client]
"Enabled"=dword:00000001
"DisabledByDefault"=dword:00000000

[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Protocols\TLS 1.2\Server]
"Enabled"=dword:ffffffff
"DisabledByDefault"=dword:00000000

{% endhighlight %}

If you control the F5 Load Balancer, you could also remove TLSv1.2 from your SSL Forward Proxy settings.  If you do not then you need to enable TLSv1.2 on the Windows server like we did above.
