# Ezjail (if desired)

Network setup:
/etc/rc.conf:
```
cloned_interfaces="lo1"
ipv4_addrs_lo1="172.16.32.1/24 172.16.32.2-64/32"
```

```# service netif cloneup```



# Networking in jails (dns)

Install unbound.

/usr/local/etc/unbound/unbound.conf

```
interface: 0.0.0.0
access-control: 172.16.32.0/24 allow
```				


# ZFS ezjail

/etc/rc.conf:
```ezjail_enable="YES"```

Configure ezjail to use zfs if desired:
```
zfs create -o mountpoint /usr/jails zroot/ezjail
```

Setup ezjail.conf (enable zfs, set volume). Then:

```ezjail-admin install -p```



# pgsql jails

If setting up pgsql in a jail, you'll have to update your jail's config, e.g.
jail_somehostname_parameters="allow.sysvipc=1"

Allowing sysvipc defeats jail's security, but we can do it for other purposes anyway (e.g. separation, replication, testing, etc.).

We're creating two pgsql jails right away in order to setup replication for future use.

```
ezjail-admin create pgsql-1 172.16.32.11 
ezjail-admin create pgsql-2 172.16.32.12

ezjail-admin start pgsql-1
ezjail-admin start pgsql-2
```

# rabbitmq jail


```
ezjail-admin create mq 172.16.32.15
```

# Networking

If using jails, don't forget to setup NAT and port forwarding.

Using pf:

```

jail_pgsql_1_addr="172.16.32.11"
jail_pgsql_1_tcp_ports="{ 5432 }"

jail_mq_addr="172.16.32.15"
jail_mq_ports="{ 5672, 15672 }"


nat on $ext_if from !($ext_if) to any -> ($ext_if)
rdr pass on { $ext_if, lo0 } proto tcp from any to ($ext_if) port $jail_pgsql_1_tcp_ports -> $jail_pgsql_1_addr
rdr pass on { $ext_if, lo0 } proto { tcp, udp } from any to ($ext_if) port $jail_mq_ports -> $jail_mq_addr
```
