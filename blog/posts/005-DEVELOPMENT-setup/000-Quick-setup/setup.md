# Quick Setup on Linux

This guide describes setup on Ubuntu.

## System packages

Install basic packages:
```
apt-get install postgresql-10 rabbitmq-server redis-server python3
```

## Repository

Clone and setup the repository:
```
git clone https://github.com/mcptr/mechanoia.git
cd mechanoia
python3 -mvenv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## PostgreSQL

```
su postgres
```

Add a user and database. We assume your system username is "mechanoia".
```
createuser -SdRP mechanoia
createdb -O mechanoia mechanoia
```

## RabbitMQ

```
rabbitmq-plugins enable rabbitmq_management

rabbitmqctl add_user mechanoia mecha.noia
rabbitmqctl set_user_tags mechanoia monitoring
rabbitmqctl add_vhost mechanoia
rabbitmqctl set_permissions mechanoia -p mechanoia ".*" ".*" ".*"
```

**IMPORTANT**: Make sure your $(hostname) is present in /etc/hosts.
