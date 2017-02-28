# to run me locally:
# source .env
# flask run

import json
import os
from flask import Flask, request
import requests
from twilio.util import RequestValidator

app = Flask(__name__)


# TODO need to find out valid IPs for requests from twilio
# so we can guard against spoofing.

# TODO - set up a process to send a 'keep-alive' text every 29
# days to stop the free number from being reclaimed. Make sure our
# code ignores those messages and does not propagate them to Slack.
# This can probably be done with AWS.


@app.route('/', methods=['POST'])
def incoming_sms():
    form =  request.form
    validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
    url = request.url.replace("http:", "https:")
    sig = request.headers['X-Twilio-Signature']
    if not validator.validate(url, form, sig):
        return "oops, invalid signature, no spoofs accepted"
    if not form['To'] == os.getenv('RRN_PHONE_NUMBER'):
        return "ignoring you, wrong To: phone number"
    if not form['AccountSid'] == os.getenv('TWILIO_ACCOUNT_SID'):
        return "ignoring you, wrong Twilio SID"
    text = "<!channel> Message from: {}: {}".format(form['From'],
                                                  form['Body'])
    media_keys = [x for x in form.keys() if x.startswith("MediaUrl")]
    media_urls = [form[x] for x in sorted(media_keys)]
    if len(media_urls):
        text = "{} \nAttachments: \n{}".format(text,
                                               "\n".join(media_urls))

    payload = dict(channel=os.getenv('SLACK_CHANNEL'),
                   username=os.getenv('SLACK_USERNAME'),
                   icon_emoji=os.getenv('SLACK_ICON_EMOJI'),
                   text=text)
    response = requests.post(os.getenv('SLACK_POST_URL'),
                             json.dumps(payload))
    # FIXME check response return code
    # FIXME deal with MMS attachments

    # import IPython;IPython.embed()
    return 'OK'
