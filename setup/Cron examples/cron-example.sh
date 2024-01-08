#!/bin/bash
cd /home/ubuntu/api/crons
export PYTHONPATH=$PYTHONPATH:"/home/ubuntu/api"
python3 ExpoPushNotificationCrontab.py >> /home/ubuntu/logs/push-notifications.log 2>&1
