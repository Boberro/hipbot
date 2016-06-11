# -*- coding: utf-8 -*-

import sys
import re
import pprint
from googleapiclient.discovery import build
import discord

if __name__ == '__main__':
    api_key_g = sys.argv[1]  # Google API key
    api_key_d = sys.argv[2]  # Discord bot token

    # Setup goo.gl API
    url_shortener_service = build('urlshortener', 'v1', developerKey=api_key_g)
    url_shortener = url_shortener_service.url()

    # Setup discord API
    client = discord.Client()

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')


    def find_ids(content):
        regex = '(?:\/watch\?v=|youtu.be\/)(\w+)'
        ids = re.findall(regex, content)
        return ids


    @client.event
    async def on_message(message):
        if message.channel.name == 'music':
            # Only do this stuff after last message with yt links
            if len(find_ids(message.content)) > 0:
                ids = []
                async for log in client.logs_from(message.channel, limit=100):
                    if log.author.id == client.user.id:
                        await client.delete_message(log)
                    else:
                        ids = list(set(ids + find_ids(log.content)))
                if len(ids) > 0:
                    long_url = 'http://www.youtube.com/watch_videos?video_ids={}'.format(','.join(ids))
                    body = {'longUrl': long_url}
                    resp = url_shortener.insert(body=body).execute()
                    msg = '<{}>'.format(resp.get("id", None))
                    if msg is not None:
                        tmp = await client.send_message(message.channel, msg)

    client.run(api_key_d)
