#!/usr/bin/bash

# ========== Note ==========
#
# 1. The argument '--hostname' is required to make RabbitMQ metadata persistent
#   References:
#   - https://stackoverflow.com/questions/41330514/docker-rabbitmq-persistency
#   - https://github.com/docker-library/rabbitmq/issues/106#issuecomment-241882358
#
# 2. The management UI is listening at port 15672. The default user and password are 'guest' and 'guest'

docker run --rm -d -p 5672:5672 -p 15672:15672 -v $(realpath .)/rabbitmq_data:/var/lib/rabbitmq --hostname rmq_host --name rmq rabbitmq:3-management
