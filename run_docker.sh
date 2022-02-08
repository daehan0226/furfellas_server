echo building docker containers
COMPOSE_HTTP_TIMEOUT=600 docker-compose up -d --build --force-recreate --remove-orphans