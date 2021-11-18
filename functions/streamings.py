from schemas.status import Status
from mastodon import Mastodon, StreamListener
from utils.load_env import ACCESS_TOKEN
from utils.load_yaml import config_dict
from .functions import ( change_bot_status, rewrite, food_terro, save_toot, humor_sense, humor_sense_return, 
    random_toot, parrot_toot, greeting_toot, delete_rockman_toot, reply_random_toot, my_post_count, 
    post_count, toot_todays_info, toot_now_info, battle_operation, three_point_generator)
import time
import re

base_url = 'https://mastodon.compositecomputer.club'

class Bot(StreamListener):
    bool_keywords = {
        'ストップして': False,
        'スタートして': True,
    }
    status_keywords = {
        'chime': 'チャイム', 
        'summer': '夏休みの目標', 
        'spring': '春休みの目標', 
        'random': 'ランダムトゥート'
    }

    def __init__(self, client):
        super(Bot, self).__init__()
        self.client = client

    def on_update(self, status: Status):
        get_status = status
        get_status['content'] = rewrite(get_status['content'])

        if get_status['account']['bot'] or get_status['reblog'] != None:
            return

        if 'ロックマン' in get_status['content']:
            self.client.status_favourite(get_status)
            for b_key, b_value in self.bool_keywords.items():
                if b_key in get_status['content']:
                    for s_key, s_keyword in self.status_keywords.items():
                        if s_keyword in get_status['content']:
                            change_bot_status(self.client, s_key, b_value)
                            return

            if re.search(r'((お(腹|なか)(空|す)いた)|(腹|はら)(減|へ)った)', get_status['content']):
                food_terro(self.client)
                return
            if "トゥート" in get_status['content'] and "保存" in get_status['content']:
                save_toot(self.client, get_status['content'])
                return
            if re.search(r'(ユーモアセンス|面白い事)', get_status['content']):
                humor_sense(self.client)
                return
            if re.search(r'(つまらない|面白くない)', get_status['content']):
                humor_sense_return(self.client)
                return
            if "何か言って" in get_status['content']:
                random_toot(self.client)
                return
            if not "りあむ" in get_status['content']:
                if "って言" in get_status['content']:
                    parrot_toot(self.client, get_status['content'])
                    return
                for greet_word in config_dict['word']['ign_riam']:
                    if greet_word['input'] in get_status['content']:
                        greeting_toot(self.client, greet_word['output'])
                        return
                if "消して" in get_status['content']:
                    delete_rockman_toot(self.client, get_status['content'])
                    return
            if config_dict['tag']['boost_tag'] in get_status['content']:
                self.client.status_reblog(get_status)
                return
            if "お返事して" in get_status['content']:
                reply_random_toot(self.client, get_status)
                return
            if "トゥート数" in get_status['content'] and "教えて" in get_status['content']:
                if "ロックマンの" in get_status['content']:
                    my_post_count(self.client, get_status)
                    return
                else:
                    post_count(self.client, get_status)
                    return
            if "今日" in get_status['content'] and "何日" in get_status['content']:
                toot_todays_info(self.client, get_status)
                return
            if "今" in get_status['content'] and "何時" in get_status['content']:
                toot_now_info(self.client, get_status)
                return
        else:
            if re.match(r'^バトルオペレーション(、|，|！|　)?セット！*$', get_status['content']):
                battle_operation(self.client, get_status)
                return
            if get_status['content'].find('三点リーダージェネレーター\n') == 0 and re.search(r'(…|\.\.\.|・・・|･･･)', get_status['content']):
                three_point_generator(self.client, get_status)
                return

def Login() -> Mastodon:
    mastodon = Mastodon(
                access_token = ACCESS_TOKEN,
                api_base_url = base_url
                )
    return mastodon

def LTLlisten(client: Mastodon):
    bot = Bot(client)
    while True:
        try:
            client.stream_local(bot)
        except Exception as e:
            print(e)
            time.sleep(60)
