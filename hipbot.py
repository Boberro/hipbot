# -*- coding: utf-8 -*-

import sys
import re
import json
from datetime import datetime
import atexit
from googleapiclient.discovery import build
import discord


class HipBot(object):
    data_per_server = {}

    def __init__(self):
        """
        data: {server_id: {last_message_parsed, ids}}
        """

        try:
            with open('hipbot-data.txt', 'r') as f:
                data = json.load(f)
            print('Loaded data from file.')
        except FileNotFoundError:
            data = {}

        for server_id in data.keys():
            if data[server_id]['last_message_parsed'] is not None:
                data[server_id]['last_message_parsed'] = datetime.strptime(
                    data[server_id]['last_message_parsed'],
                    '%Y-%m-%d %H:%M:%S.%f'
                )

        HipBot.data_per_server = data


if __name__ == '__main__':
    api_key_g = sys.argv[1]  # Google API key
    api_key_d = sys.argv[2]  # Discord bot token

    # Setup goo.gl API
    url_shortener_service = build('urlshortener', 'v1', developerKey=api_key_g)
    url_shortener = url_shortener_service.url()

    # Setup discord API
    client = discord.Client()

    hipbot = HipBot()


    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')


    def find_ids(content):
        regex = '(?:\/watch\?v=|youtu.be\/)([\w-]+)'
        _ids = re.findall(regex, content)
        return _ids


    @client.event
    async def on_message(message):
        if message.channel.name == 'music':
            # Only do this stuff after last message with yt links
            if message.author.id != client.user.id and len(find_ids(message.content)) > 0:
                server_data = HipBot.data_per_server.get(message.server.id, {})
                last_message_parsed = server_data.get('last_message_parsed', None)
                ids = server_data.get('ids', [])

                async for log in client.logs_from(message.channel, limit=1000, after=last_message_parsed):
                    if log.author.id == client.user.id:
                        await client.delete_message(log)
                    else:
                        ids = list(set(ids + find_ids(log.content)))
                    if last_message_parsed is None or log.timestamp > last_message_parsed:
                        last_message_parsed = log.timestamp

                if len(ids) > 0:
                    long_url = 'http://www.youtube.com/watch_videos?video_ids={}'.format(','.join(ids))
                    body = {'longUrl': long_url}
                    resp = url_shortener.insert(body=body).execute()
                    short_url = resp.get("id", None)
                    if short_url is not None:
                        msg = '<{}>'.format(short_url)
                        await client.send_message(message.channel, msg)

                # Finally, update the data
                HipBot.data_per_server[message.server.id] = {
                    'last_message_parsed': last_message_parsed,
                    'ids': ids,
                }


    def on_exit():
        with open('hipbot-data.txt', 'w') as f:
            data = HipBot.data_per_server
            for server_id in data.keys():
                if data[server_id]['last_message_parsed'] is not None:
                    data[server_id]['last_message_parsed'] = str(data[server_id]['last_message_parsed'])
            json.dump(data, f)
        print('Data saved.')
        print('Bye bye!')


    atexit.register(on_exit)
    client.run(api_key_d)
