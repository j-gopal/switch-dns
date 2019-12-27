Switch DNS
==========

For directly setting the DNS servers being used on your machine.

What is this for?
-----------------

Say you were using [Google's Public DNS](https://en.wikipedia.org/wiki/Google_Public_DNS) (8.8.8.8) as your main DNS for both IPv4 and IPv6:

```batch
C:\Users\Username>switch-dns get /curr
IPv6 Primary DNS: 2001:4860:4860::8888
IPv6 Reserve DNS: 2001:4860:4860::8844
IPv4 Primary DNS: 8.8.8.8
IPv4 Reserve DNS: 8.8.4.4
```

What if there were [faster options](https://www.dnsperf.com/#!dns-resolvers) available to you?

You could, for instance, set your DNS of choice to [Cloudflare's 1.1.1.1](https://en.wikipedia.org/wiki/1.1.1.1) like so, from an elevated command prompt:

```batch
C:\Users\Username>switch-dns set -G cloudflare
Configured IPv6 Primary DNS to 2606:4700:4700::1111
Configured IPv6 Reserve DNS to 2606:4700:4700::1001
Configured IPv4 Primary DNS to 1.1.1.1
Configured IPv4 Reserve DNS to 1.0.0.1
```

Not all DNS services are made equal. There may be a significant difference between the speed at which two DNS's resolve the same domain name. In some cases, this can noticeably affect how quickly a page will load in your browser.

Rolling Back
------------

Even after changing your DNS, there can be other problems to consider. Now that you're using Cloudflare's DNS, try going to the following page in your browser: https://archive.is/

It's not too surprising if this page doesn't load; the fact that this site and this DNS don't get along is a [known issue](https://jarv.is/notes/cloudflare-dns-archive-is-blocked/). So what can we do?

Well, with another session in an elevated command prompt, this is easily fixable!

```batch
C:\Users\Username>switch-dns set -G /prev
Configured IPv6 Primary DNS to 2001:4860:4860::8888
Configured IPv6 Reserve DNS to 2001:4860:4860::8844
Configured IPv4 Primary DNS to 8.8.8.8
Configured IPv4 Reserve DNS to 8.8.4.4
```

Alternatively, you could manually choose to use one of the other services available:

```batch
C:\Users\Username>switch-dns set -G quad9
Configured IPv6 Primary DNS to 2620:fe::fe
Configured IPv6 Reserve DNS to 2620:fe::9
Configured IPv4 Primary DNS to 9.9.9.9
Configured IPv4 Reserve DNS to 149.112.112.112
```

To-Do List
----------
- Allow new DNS groups to be added on the fly: `switch-dns add <group>`
- Add setup.py
