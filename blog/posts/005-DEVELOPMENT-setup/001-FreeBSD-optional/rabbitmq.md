# RabbitMQ:

```
pkg install rabbitmq
service rabbitmq start

rabbitmq-plugins enable rabbitmq_management

rabbitmqctl add_user mechanoia mecha.noia
rabbitmqctl set_user_tags mechanoia monitoring
rabbitmqctl add_vhost mechanoia
rabbitmqctl set_permissions mechanoia -p mechanoia ".*" ".*" ".*"
```

**IMPORTANT**: Make sure your $(hostname) is present in /etc/hosts.
