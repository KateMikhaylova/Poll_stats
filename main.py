import configparser

from telethon import TelegramClient
from poll_stats import PollStats

def run():
    config = configparser.ConfigParser()
    config.read('settings.ini')
    api_id = config['Telegram']['api_id']
    api_hash = config['Telegram']['api_hash']

    client = TelegramClient('telethon_session', int(api_id), api_hash)

    poll_stats = PollStats(client)

    with client:
        poll_stats.get_channels()
        polls = client.loop.run_until_complete(poll_stats.get_polls())
        result = poll_stats.calculate_result(polls)
        template = poll_stats.create_template(result)
        client.loop.run_until_complete(poll_stats.send_result(template))

if __name__ == '__main__':
    run()
