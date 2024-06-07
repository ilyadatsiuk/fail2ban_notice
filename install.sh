#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "You must start this script with ROOT" 1>&2
   exit 1
fi

install -Dm755 main.py /etc/fail2ban/main.py

install -Dm644 /dev/null /etc/fail2ban/previous_banned_ips.txt

cat << EOF > /etc/systemd/system/fail2ban-notice.service
[Unit]
Description=Fail2Ban Notice Telegram
After=network.target

[Service]
ExecStart=/usr/bin/python3 /etc/fail2ban/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

systemctl enable fail2ban-main.service

systemctl start fail2ban-main.service

echo "Installation complete.\nThe name of service - fail2ban-notice.service"
