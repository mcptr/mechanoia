# PostgreSQL:


```
pkg install postgresql10-server
/usr/local/etc/rc.d/postgresql initdb
```

Install postgres contrib.
Create pgcrypto and uuid-ossp in template1.

```
createuser -SdRP mechanoia
createdb -O mechanoia mechanoia
```


# Replication

On your primary, psql:
```
CREATE USER replication WITH REPLICATION PASSWORD 'replication.password' LOGIN;
```
Edit pg_hba and set md5 auth for external network.
Reload/restart primary pgsql instance.


On another postgres node, take a basebackup:
```
pg_basebackup -h 172.16.32.11 -U replication -D /var/db/postgres/data10 -v
```

Enter password, and create /var/db/postgres/data10/recovery.conf:
```
standby_mode = 'on'                                                              
primary_conninfo = 'host=172.16.32.11 port=5432 user=replication password=replication.password'
```

Start the slave and the streaming replication should be working.
Test it by creating a database on primary.

Also check 'select pg_is_in_recovery()' on both nodes.
On primary it will yield false, and tru on slave.
Primary should have wal sender process, slave should have wal receiver process.
