
`vim /etc/systemd/resolved.conf`

```ini
[Resolve]
DNS=1.1.1.1
#FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no
DNSStubListener=no
#ReadEtcHosts=yes
```

`sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf`

`reboot`

https://www.linuxuprising.com/2020/07/ubuntu-how-to-free-up-port-53-used-by.html
