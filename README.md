This small utility helps to shutdown your host via web UI interface.

It is only tested in Ubuntu, other platforms might need to tweak a little bit, but it should be quite easy.

### Screenshot

![web interface](./img/1.gif)

### Install

1. Clone to your host
   ```
   git clone https://github.com/JerryBian/web-shutdown.git /tmp/web-shutdown
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
   User=root
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

### Enviorment variables(Optional)

#### Email notification
In order to send notifications during startup/shutdown, you have to setup 2 variables:
- `ENV_SENDGRID_API_KEY`: you could create free account to get the api key of [SendGrid](https://sendgrid.com/)
- `ENV_MAIL_TO_ADDR`: the email address send to

Optionally, you can specify more detailed configurations:
- `ENV_MAIL_TO_NAME`: the name send to
- `ENV_MAIL_FROM_ADDR`: the email address send from
- `ENV_MAIL_FROM_TO`: the name send from

#### Misc

- `ENV_SECRET_KEY`: secret key for authentication
- `ENV_USER_NAME`: user name. _Default_: `admin`
- `ENV_PASSWORD`: user password. _Default_: `adminadmin`
- `ENV_HOST`: the hostname to listen on. _Default_: `127.0.0.1`
- `ENV_PORT`: the port to listen on. _Default_: `5000`

### License

[MIT](./LICENSE)