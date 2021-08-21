#!/bin/bash
cd /home/ubuntu/api/crons
python3 ExpoPushNotificationCrontab.py >> /home/ubuntu/logs/push-notifications.log 2>&1
