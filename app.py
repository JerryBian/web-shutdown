from flask import Flask, send_from_directory, jsonify
from concurrent.futures import ThreadPoolExecutor
from sendgrid.helpers.mail import *
import subprocess
import traceback
import logging
import sys
import os
import time
import sendgrid

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

executor = ThreadPoolExecutor(5)
app = Flask(__name__, static_url_path='')

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-h', 'now']
        executor.submit(exeCmd, args)
        out = 'Machine has been shutdown successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})

@app.route('/reboot', methods=['POST'])
def reboot():
    out = err = str()
    try:
        args = ['sudo', 'shutdown', '-r', 'now']
        executor.submit(exeCmd, args)
        out = 'Machine has been reboot successfully'
    except Exception:
        err = traceback.format_exc()
        logger.error(err)
    logger.debug('about to send response')
    return jsonify({'stdout': out, 'stderr': err})

def exeCmd(args):
    logger.info(f'begin exec {args}')
    time.sleep(2)
    command = subprocess.run(args, capture_output=True)
    logger.info(f'end exec {args}')
    sendMail(f'<code>{args}</code> request finished.')
    return command

def sendMail(message):
    apiKey = os.getenv('ENV_SENDGRID_API_KEY')
    if apiKey is None:
        logger.warn('ENV_SENDGRID_API_KEY is not set')
        return
    mailToAddr=os.getenv('ENV_MAIL_TO_ADDR')
    if mailToAddr is None:
        logger.warn('ENV_MAIL_TO_ADDR is not set')
        return
    mailToName=os.getenv('ENV_MAIL_TO_NAME', 'admin')
    mailFromAddr=os.getenv('ENV_MAIL_FROM_ADDR', 'robot@web-shutdown.com')
    mailFromName=os.getenv('ENV_MAIL_FROM_NAME', 'robot')
    html_content = f'<div><p>{message}</p></div>'
    sg = sendgrid.SendGridAPIClient(api_key=apiKey)
    from_email = Email(mailFromAddr, name= mailFromName)
    to_email = To(mailToAddr, name = mailToName)
    subject = "Notification from web-shutdown"
    content = HtmlContent(html_content)
    tracking_settings = TrackingSettings()
    tracking_settings.click_tracking = ClickTracking(False, False)
    tracking_settings.open_tracking = OpenTracking(False)
    tracking_settings.subscription_tracking = SubscriptionTracking(False)
    tracking_settings.ganalytics = Ganalytics(False)
    mail = Mail(from_email, to_email, subject, content)
    mail.tracking_settings = tracking_settings
    response = sg.client.mail.send.post(request_body=mail.get())
    if response.status_code == 202:
        logger.info(f'send email to {mailToAddr} successfully: {message}')
    else:
        print(f'send email failed. response code: {response.status_code}, message: {response.body}.')
    
if __name__ == '__main__':
    sendMail('<code>web-shutdown</code> is ready to run.')
    app.run(host=os.getenv('ENV_HOST', '127.0.0.1'), port=os.getenv('ENV_PORT', '5000'))