from datetime import datetime
from user import User
from flask import Flask, jsonify, request, render_template, url_for
from flask_login import LoginManager
from flask_login.utils import login_required, login_user, logout_user
from werkzeug.utils import redirect
from concurrent.futures import ThreadPoolExecutor
from sendgrid.helpers.mail import *
import subprocess
import traceback
import logging
import sys
import os
import time
import datetime
import sendgrid
import socket

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

executor = ThreadPoolExecutor(5)
app = Flask(__name__, static_url_path='/assets', static_folder='assets')
app.secret_key = os.getenv('ENV_SECRET_KEY', 'SECRET_KEY_DEFAULT')
login_manager = LoginManager()
login_manager.init_app(app)
user_name = os.getenv('ENV_USER_NAME', 'admin')
user_pwd = os.getenv('ENV_PASSWORD', 'adminadmin')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(name):
    if user_name == name:
        u = User(name)
        u.is_authenticated = True
        return u

    return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    global user_name, user_pwd
    if request.method == 'POST':
        request_user_name = request.form.get('user_name')
        request_user_pwd = request.form.get('user_pwd')
        request_user_remember = request.form.get('user_remember')
        if request_user_name == user_name:
            u = User(user_name)
            u.verify_pwd(request_user_pwd, user_pwd)
            if u.is_authenticated:
                login_user(u, remember=request_user_remember == 'on',
                           duration=datetime.timedelta(days=7))
                return redirect(url_for('index'))

        error = 'Invalid credentials'

    return render_template('login.html', error=error)


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/shutdown', methods=['POST'])
@login_required
def shutdown():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-h', 'now']
        executor.submit(exeCmd, args)
        out = f'Machine(<small class="text-muted fs-6">{get_machine()}</small>) has been shutdown successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})


@app.route('/reboot', methods=['POST'])
@login_required
def reboot():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-r', 'now']
        executor.submit(exeCmd, args)
        out = f'Machine(<small class="text-muted fs-6">{get_machine()}</small>) has been reboot successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})


def exeCmd(args):
    logger.info(f'begin exec {args}')
    time.sleep(1)
    sendMail(f'<code>{args}</code> request finished.')
    command = subprocess.run(args, capture_output=True)
    logger.info(f'end exec {args}')
    return command

def get_machine():
    return f'{socket.gethostname()} @{get_ip()}'


def sendMail(message):
    apiKey = os.getenv('ENV_SENDGRID_API_KEY')
    if apiKey is None:
        logger.warn('ENV_SENDGRID_API_KEY is not set')
        return
    mailToAddr = os.getenv('ENV_MAIL_TO_ADDR')
    if mailToAddr is None:
        logger.warn('ENV_MAIL_TO_ADDR is not set')
        return
    mailToName = os.getenv('ENV_MAIL_TO_NAME', 'admin')
    mailFromAddr = os.getenv('ENV_MAIL_FROM_ADDR', 'robot@web-shutdown.com')
    mailFromName = os.getenv('ENV_MAIL_FROM_NAME', 'robot')
    html_content = f'<div><p>{message}</p></div><div style="text-align:center;margin-top:1.2rem;"><small>{get_machine()}</small></div>'
    sg = sendgrid.SendGridAPIClient(api_key=apiKey)
    from_email = Email(mailFromAddr, name=mailFromName)
    to_email = To(mailToAddr, name=mailToName)
    subject = "Notification from web-shutdown"
    content = HtmlContent(html_content)
    tracking_settings = TrackingSettings()
    tracking_settings.click_tracking = ClickTracking(False, False)
    tracking_settings.open_tracking = OpenTracking(False)
    tracking_settings.subscription_tracking = SubscriptionTracking(False)
    tracking_settings.ganalytics = Ganalytics(False)
    mail = Mail(from_email=from_email, to_emails=to_email, subject=subject, html_content=content)
    mail.tracking_settings = tracking_settings
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 202:
        logger.info(f'send email to {mailToAddr} successfully: {message}')
    else:
        print(
            f'send email failed. response code: {response.status_code}, message: {response.body}.')

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


if __name__ == '__main__':
    sendMail('<code>web-shutdown</code> is ready to run.')
    app.run(host=os.getenv('ENV_HOST', '127.0.0.1'),
            port=os.getenv('ENV_PORT', '5000'))
