
sudo  cp -v deploy/pza-py-platform-run.py  /usr/local/bin/pza-py-platform-run.py
sudo  cp -v  deploy/panduza-py-platform.service  /etc/systemd/system/panduza-py-platform.service

sudo systemctl daemon-reload
sudo chmod +x /usr/local/bin/pza-py-platform-run.py
