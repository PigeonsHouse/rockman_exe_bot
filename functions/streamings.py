from schemas.status import Status
from mastodon import Mastodon, StreamListener
from utils.load_env import ACCESS_TOKEN
from utils.load_yaml import config_dict
from .functions import ( get_name, rewrite, food_terro, save_toot, humor_sense, humor_sense_return, 
    random_toot, parrot_toot, greeting_toot, delete_rockman_toot, reply_random_toot, my_post_count, 
    post_count, toot_todays_info, toot_now_info, battle_operation, three_point_generator)
import time
import re

base_url = 'https://mastodon.compositecomputer.club'

class Bot(StreamListener):
    def __init__(self):
        super(Bot, self).__init__()

    def on_update(self, status: Status):
        get_status = status
        get_status['content'] = rewrite(get_status['content'])

        if get_status['account']['bot'] or get_status['reblog'] != None:
            return

        if 'ロックマン' in get_status['content']:
            client.status_favourite(get_status)
            if re.search(r'((お(腹|なか)(空|す)いた)|(腹|はら)(減|へ)った)', get_status['content']):
                food_terro(client)
                return
            if "トゥート" in get_status['content'] and "保存" in get_status['content']:
                save_toot(client, get_status['content'])
                return
            if re.search(r'(ユーモアセンス|面白い事)', get_status['content']):
                humor_sense(client)
                return
            if re.search(r'(つまらない|面白くない)', get_status['content']):
                humor_sense_return(client)
                return
            if "何か言って" in get_status['content']:
                random_toot(client)
                return
            if not "りあむ" in get_status['content']:
                if "って言" in get_status['content']:
                    parrot_toot(client, get_status['content'])
                    return
                for greet_word in config_dict['word']['ign_riam']:
                    if greet_word['input'] in get_status['content']:
                        greeting_toot(client, greet_word['output'])
                    return
                if "消して" in get_status['content']:
                    delete_rockman_toot(client, get_status['content'])
            if config_dict['tag']['rockRT_tag'] in get_status['content']:
                client.status_reblog(get_status)
                return
            if "お返事して" in get_status['content']:
                reply_random_toot(client, get_status)
                return
            if "トゥート数" in get_status['content'] and "教えて" in get_status['content']:
                if "ロックマンの" in get_status['content']:
                    my_post_count(client, get_status)
                    return
                else:
                    post_count(client, get_status)
                    return
            if "今日" in get_status['content'] and "何日" in get_status['content']:
                toot_todays_info(client, get_status)
                return
            if "今" in get_status['content'] and "何時" in get_status['content']:
                toot_now_info(client, get_status)
                return
        else:
            if re.match(r'^バトルオペレーション(、|，|！|　)?セット！*$', get_status['content']):
                battle_operation(client, get_status)
                return
            if get_status['content'].find('三点リーダージェネレーター\n') == 0 and re.search(r'(…|\.\.\.|・・・|･･･)', get_status['content']):
                three_point_generator(client, get_status)
                return

def Login():
    mastodon = Mastodon(
                access_token = ACCESS_TOKEN,
                api_base_url = base_url
                )
    return mastodon

def LTLlisten():
    bot = Bot()
    while True:
        try:
            client.stream_local(bot)
        except Exception as e:
            print(e)
            time.sleep(60)

client: Mastodon = Login()
