if [ -f ../.env ]; then
  export $(echo $(cat ../.env | sed 's/#.*//g'| xargs) | envsubst)
else
  echo "No ../.env file"
  exit
fi

if [ $MYSQL_BACKUP = "true" ]; then
  docker exec $MYSQL /usr/bin/mysqldump -uroot --password=$MYSQL_PASSWORD $MYSQL_DATABASE >  backup/$(date '+%Y-%m-%d_%H:%M:%S').sql
fi
