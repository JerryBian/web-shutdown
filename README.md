This small utility helps to shutdown your host via web UI interface.

This is only tested in Ubuntu, other platforms might need to tweak a little bit, but it should be quite easy.

### Screenshot

![web interface](./img/1.png)

### Install

1. Clone to your host
   ```
   git clone https://github.com/hb-org/web-shutdown.git /tmp/web-shutdown
   ```
2. Install modules
   ```
   cd /tmp/web-shutdown
   pip3 install -r requirements.txt
   ```
3. Create Systemd unit file
   ```
   python3_bin=$(which python3)
   echo "
   [Unit]
   Description=shutdown via web
   After=network.target

   [Service]
   User=$USER
   WorkingDirectory=/tmp/web-shutdown
   Restart=on-failure
   RestartSec=5s
   ExecStart=$python3_bin app.py

   [Install]
   WantedBy=multi-user.target
    " > /etc/systemd/system/web-shutdown.service
   systemctl enable web-shutdown
   systemctl start web-shutdown
   ```

### License

MIT.