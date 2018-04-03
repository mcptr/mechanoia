# User

Add *mechanoia* user on the freebsd node.
Point mechanoia.local to your server (e.g. via /etc/hosts).

Create a ssh key your local host:

```
ssh-keygen -t ed25519 -f ~/.ssh/you@mechanoia.local
```

Update your ssh client config:
```
	Host mechanoia.local
		user mechanoia
		port 22
		IdentityFile ~/.ssh/you@mechanoia.local
```

and copy the public key to fbsd server:

```
ssh-copy-id -i ~/.ssh/you@mechanoia.local mechanoia@mechanoia.local
```

# SSHD:

On the server: turn off password auth in /etc/ssh/sshd_config:
```
PasswordAuthentication no
ChallengeResponseAuthentication no
PermitRootLogin no
```

```# service sshd restart```


# FreeBSD dns:

If using local_unbound, and if if it doesn't forward dns queries:
add "module-config: iterator" to server section in /etc/unbound/unbound.conf
