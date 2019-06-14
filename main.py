import os
import sys
import codecs
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage)

import requests
from bs4 import BeautifulSoup
import re

import urllib.request

import yahooNews
yahooNews.news()

import json

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    yahooNews.news()
    file_name = "./data.txt"
    file = open(file_name)
    data = file.read()
    if event.message.text == "やふーにゅーす":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="=== yahooにゅーす ==="+"\n"+data+"おわりだよ〜"+"\n")
        )
        print(type(event.message.text))
    elif os.path.exists("./{}.txt".format(event.message.text)):
        sp_name = "./{}.txt".format(event.message.text)
        sp = open(sp_name)
        sp_data = sp.read()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="=== {}メモ ===".format(event.message.text)+"\n"+sp_data+"おわりだよ〜"+"\n")
        )
    elif event.message.text:
        profile = line_bot_api.get_profile(event.source.user_id)
        lineid = 'LINE_ID {}'.format(profile.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=lineid)

        fighter = urllib.parse.quote(event.message.text)
        url = 'https://smamemo.herokuapp.com/test_api/'+ fighter
        res = urllib.request.urlopen(url)
        body = json.loads(res.read().decode("utf-8"))
        print(body)
        if body["result"]:
            send_text = "\n".join(body["memos"])
        else:
            send_text = "404NotFound"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=send_text)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="「やふーにゅーす」って言ってみて！")

        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
