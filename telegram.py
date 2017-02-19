import json
import os
import requests

from BaseHTTPServer import BaseHTTPRequestHandler
import SimpleHTTPServer
import SocketServer

import utils

CONFIG = "config"
PARAMS = utils.read_config(CONFIG, "telegram")


class TelegramBot(object):
    def __init__(self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot%(token)s/sendMessage" % {"token": token}
        self.info_url = "https://api.telegram.org/bot%(token)s/getUpdates" % {"token": token}

    @property
    def chats(self):
        if not os.path.exists(PARAMS.bot_file):
            return []
        with open(PARAMS.bot_file, 'r') as f:
            return [int(c.strip()) for c in f.read().split('\n') if c.strip() != '']

    def send_message(self, msg, chat_id):
        data = {'chat_id': chat_id, 'text': msg}
        res = requests.post(self.url, data)

    def update_chats(self):
        """Returns all chat ids that are present in getUpdates"""
        res = requests.get(self.info_url)
        messages = res.json()['result']
        chats = set(m['message']['chat']['id'] for m in messages)
        for c in chats:
            if c not in self.chats:
                self.save_chat(c)
        return [c for c in chats]

    def save_chat(self, chat):
        with open(PARAMS.bot_file, 'a') as f:
            f.write("%s\n" % chat)

    def send_all(self, msg):
        """Sends message to all chats the bot is in"""
        self.update_chats()
        for c in self.chats:
            self.send_message(msg, c)


class TelegramHandler(BaseHTTPRequestHandler):
    bot = TelegramBot(PARAMS.bot_token)

    def do_POST(self):
        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        data = json.loads(post_body)
        img = data['imageUrl']
        grafana_msg = data['message']
        name = data['ruleName']
        self.bot.send_all("Hi! Please check my %(param)s.\n%(msg)s\n%(image)s" % 
                {'param': name, 'msg': grafana_msg, 'image': img})
        self.send_response(200, 'Data sent!')

def launch_server():
    httpd = SocketServer.TCPServer(("", int(PARAMS.port)), TelegramHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    launch_server()
