#!/bin/bash
################################################################
##
## SQLite Database Backup Script
## By Nihilok
## Adapted from: https://yehiweb.com/wp-content/uploads/2021/05/mysql-backup.sh
## Last Update: Dec 19, 2021
##
################################################################

export PATH=/bin:/usr/bin:/usr/local/bin
TODAY=`date +"%d%b%Y"`

################################################################
################## Update below values ########################

DB_BACKUP_PATH='./backup/dbbackup'
BACKUP_RETAIN_DAYS=30 ## Number of days to keep local backup copy

#################################################################

cd /home/$USER/apps/OpenCentralHeating;
mkdir -p ${DB_BACKUP_PATH}/${TODAY}
echo "Backup started for database - ${DATABASE_NAME}"
sqlite3 db.sqlite3 ".backup ${DB_BACKUP_PATH}/${TODAY}/backup.sqlite3"
if [ $? -eq 0 ]; then
echo "Database backup successfully completed"
else
echo "Error found during backup"
exit 1
fi

##### Remove backups older than {BACKUP_RETAIN_DAYS} days #####

DBDELDATE=$(date +"%d%b%Y" --date="${BACKUP_RETAIN_DAYS} days ago")

if [ -n "${DB_BACKUP_PATH}" ];
  then cd ${DB_BACKUP_PATH} || exit;
  if [ -n "${DBDELDATE}" ] && [ -d "${DBDELDATE}" ];
    then rm -rf "${DBDELDATE}"
  fi
fi

### End of script ####