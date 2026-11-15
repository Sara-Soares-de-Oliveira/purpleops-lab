# Kali VM Setup

This document records how I prepared the Kali VM for PurpleOps and checked its network configuration. No attack exercises have been performed yet.

## A dedicated copy for the lab


| Setting | Value |
|---|---|
| Host OS | openSUSE Tumbleweed |
| VirtualBox version reported during setup | `7.2.20_SUSEr175154` |
| VM name | `PurpleOps-Kali` |
| Memory | 2 GB |
| Virtual CPUs | 2 |
| Active network adapters | One |
| Network mode | Internal Network |
| Internal network name | `purpleops-lab` |



## Moving from NAT to the lab network

The clone initially used NAT. With the VM shut down, I changed Adapter 1 to **Internal Network**, entered `purpleops-lab`, and kept **Cable Connected** enabled. The remaining adapters were disabled.

The internal network name identifies the virtual network to which the adapter is connected. It does not assign an IP address. Other lab VMs will need to use the same network name and compatible addressing to communicate directly.

After booting Kali, I ran:

```bash
ip -br address
ip route
```

The first command lists interfaces and their addresses in a brief format. The second displays the main IPv4 routing table.

At this point, `eth0` was up but had no IPv4 address. It had an IPv6 link-local address beginning with `fe80::`. The IPv4 routing table was empty.

I checked the NetworkManager profiles:

```bash
nmcli connection show
```

The Ethernet profile was `Wired connection 1`, associated with `eth0`. I then inspected its saved IPv4 settings:

```bash
nmcli -f ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns connection show "Wired connection 1"
```

The result was:

```text
ipv4.method:       auto
ipv4.addresses:    --
ipv4.gateway:      --
ipv4.dns:          --
```

The profile expected automatic configuration through DHCP. No DHCP service had been configured for the lab network, so I chose a static address.

## Choosing the address


The Kali address is `192.168.50.10/24`. The proposed Linux victim address is `192.168.50.20/24`; it has not been configured yet.


## Applying the static configuration

Inside Kali, I saved the settings with:

```bash
sudo nmcli connection modify "Wired connection 1" ipv4.method manual ipv4.addresses 192.168.50.10/24 ipv4.gateway "" ipv4.dns "" ipv4.never-default yes
```

- `connection modify` changes the saved profile.
- `ipv4.method manual` selects static IPv4 configuration.
- `ipv4.addresses` sets the address and prefix.
- The empty gateway and DNS values clear those settings.
- `ipv4.never-default yes` prevents this profile from supplying an IPv4 default route.

I then activated the profile:

```bash
sudo nmcli connection up "Wired connection 1"
```

NetworkManager returned `Connection successfully activated`. This confirmed activation; I still needed to inspect the resulting addresses and routes.

## Verification results

### Address and directly connected route

```bash
ip -br address
ip -4 route
```

The output showed `eth0` up with `192.168.50.10/24`, alongside its IPv6 link-local address. The IPv4 route was:

```text
192.168.50.0/24 dev eth0 proto kernel scope link src 192.168.50.10 metric 100
```

This is a directly connected route through `eth0`. The kernel created it when the address was applied. There was no IPv4 default route.



## What I learned

An active network adapter, an assigned IP address, and a route to a destination are separate things. Connecting Kali to the internal network did not automatically give it an IPv4 address. Applying the static address created a local subnet route, but did not create a route to my home network or the Internet.
