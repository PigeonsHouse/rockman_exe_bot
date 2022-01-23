from datetime import datetime, timezone, timedelta
from io import TextIOWrapper
from dateutil.relativedelta import relativedelta
from typing import List
from schemas.status import Status, User
from mastodon import Mastodon
from utils.load_yaml import status_dict, config_dict, update_status
import time
import random
import re
import bs4
import urllib
import os
import pytz

base_url = 'https://mastodon.compositecomputer.club'

def get_name(account: User):
    if len(account['display_name']) == 0:
        return account['username']
    else:
        return account['display_name']

def rewrite(text: str, doRet: bool = True):
    if doRet:
        text = text.replace('</p><p>', '\n\n')
        text = text.replace('<br />','\n')
    else:
        text = text.replace('</p><p>', ' ')
        text = text.replace('<br />',' ')
    text = bs4.BeautifulSoup(text, 'html.parser').get_text()
    text = text.replace('&apos;', '\'')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '\"')
    return text

def chime(client: Mastodon, chime_time: str, class_time: int = 0):
    dt_now = datetime.now()
    print("start chime func!!")
    print(f'now time is {dt_now}')
    print(f'chime time is {chime_time}')
    if dt_now.weekday() < 5 and status_dict['schedule_bool']['chime']:
        if class_time:
            toottext = "今は" + chime_time + "\nもうすぐ" + str(class_time) + "時限目が始まるよ。遅刻しないようにね！"
        else:
            toottext = "今は" + chime_time + "\nお昼休みだね。"
        print(toottext)
        print('\n')
        client.toot(toottext)
        time.sleep(1)
        return

def task_boost(client: Mastodon):
    task_boost_today(client)
    time.sleep(120)
    task_boost_tomorrow(client)

def task_boost_today(client: Mastodon):
    tasklist = client.timeline_hashtag("今日やること")
    todaystart = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for tl in tasklist:
        if tl.application:
            if tl.application.name == 'hatoBot':
                continue
        toottime = tl['created_at'].replace(tzinfo=None) + timedelta(hours=9)
        if  todaystart <= toottime:
            time.sleep(5)
            client.status_unreblog(tl)
            time.sleep(5)
            client.status_reblog(tl)
        else:
            break

def task_boost_tomorrow(client: Mastodon):
    tasklist = client.timeline_hashtag("明日やること")
    todaystart = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    yeststart = todaystart - timedelta(hours=24)
    for tl in tasklist:
        if tl.application:
            if tl.application.name == 'hatoBot':
                continue
        toottime = tl['created_at'].replace(tzinfo=None) + timedelta(hours=9)
        if yeststart <= toottime < todaystart:
            time.sleep(5)
            client.status_unreblog(tl)
            time.sleep(5)
            client.status_reblog(tl)
        else:
            break

def day_change(client: Mastodon):
    dt_now = datetime.now()
    if dt_now.strftime("%j") == "001":
        client.account_update_credentials(avatar="medias/new_icon.png")
        client.toot("あけましておめでとう！皆、今年もよろしくね！")
    else:
        client.account_update_credentials(avatar="medias/nomal_icon.png")
        if dt_now.day == 1:
            client.status_post(
                status = '月が変わってお知らせよ！',
                media_ids = [client.media_post("medias/sailormoon.jpg")]
            )
            buzz_toot(client)
        else:
            client.toot("日付が変わったよ！\n「＃今日やること」でトゥートすると僕が日中何度もブーストするよ！")

def summer_target(client: Mastodon):
    if status_dict['schedule_bool']['summer']:
        client.status_post("皆が投稿した夏休みの目標をブーストするよ。\n目標は順調かな？", visibility='unlisted')
        time.sleep(1)
        tasklist = client.timeline_hashtag("夏休みの目標")
        thissummerstart = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        for tl in tasklist:
            toottime = tl['created_at'].replace(tzinfo=None) + timedelta(hours=9)
            if  thissummerstart <= toottime:
                time.sleep(5)
                client.status_unreblog(tl)
                time.sleep(5)
                client.status_reblog(tl)
            else:
                break

def spring_target(client: Mastodon):
    if status_dict['schedule_bool']['spring']:
        client.status_post("皆が投稿した春休みにやることをブーストするよ。\n目標は順調かな？", visibility='unlisted')
        time.sleep(1)
        tasklist = client.timeline_hashtag("春休みにやりたいこと")
        thissummerstart = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        for tl in tasklist:
            toottime = tl['created_at'].replace(tzinfo=None) + timedelta(hours=9)
            if  thissummerstart <= toottime:
                time.sleep(5)
                client.status_unreblog(tl)
                time.sleep(5)
                client.status_reblog(tl)
            else:
                break

def change_bot_status(client: Mastodon, key: str, bool: bool, status_for_reply: Status):
    global status_dict
    status_dict['schedule_bool'][key] = bool
    update_status()
    toot_text = ''
    for new_key, new_bool in status_dict['schedule_bool'].items():
        toot_text += f'\n{new_key}: {"ON" if new_bool else "OFF"}'
    client.status_reply(status_for_reply, toot_text)

def food_terro(client: Mastodon):
    dishlist = client.timeline_hashtag("CompositeCookingClub", only_media = True)
    dishtoot = random.choice(dishlist)
    toottext = get_name(dishtoot['account']) + "さんの投稿した料理だよ！\nおいしそうだね！"
    dish_madiafile = []
    for media in dishtoot['media_attachments']:
        print(media['url'])
        urllib.request.urlretrieve(
            media['url'],
            str(media['id']) + "_dish.jpg"
            )
        dish_madiafile.append(client.media_post(str(media['id']) + "_dish.jpg"))
        time.sleep(1)
    client.status_post(
        status = toottext,
        media_ids = dish_madiafile
        )
    for media in dishtoot['media_attachments']:
        os.remove(str(media['id']) + "_dish.jpg")

def save_toot(client: Mastodon, content: str):
            timeline_length = 40
            timeline = client.timeline_local(limit = timeline_length)
            chase = 1
            if re.search(r'\[\d\d\]', content):
                if int(content[content.find('[')+1:content.find(']')]) < 40:
                    chase = int(content[content.find('[')+1:content.find(']')])
            saved_toot = timeline[chase]
            saved_content = rewrite(saved_toot['content'])
            fish_madiafile = []
            for media in saved_toot['media_attachments']:
                urllib.request.urlretrieve(
                    media['url'], 
                    str(media['id']) + "_fish.jpg"
                    )
                fish_madiafile.append(client.media_post(str(media['id']) + "_fish.jpg"))
                time.sleep(1)
            sptxt = ""
            if len(saved_content) < 90:
                toottext = "[" + get_name(saved_toot['account']) + "]\n" + saved_content
            else:
                toottext = saved_content
                sptxt = "[" + get_name(saved_toot['account']) + "]"
                if len(toottext) > 500:
                    toottext = toottext[0 : 499-len(sptxt)] + '…'
            time.sleep(1)
            client.status_post(
                status = toottext,
                media_ids = fish_madiafile,
                spoiler_text = sptxt
            )
            for media in saved_toot['media_attachments']:
                os.remove(str(media['id']) + "_fish.jpg")

def humor_sense(client: Mastodon):
    client.toot(random.choice(config_dict['word']['humor']))

def humor_sense_return(client):
    client.toot(random.choice(config_dict['word']['humor_reacts']))

def random_toot(client: Mastodon):
    if status_dict['schedule_bool']['random']:
        client.status_post(random.choice(config_dict['word']['rndtoot']), visibility='unlisted')

def parrot_toot(client: Mastodon, content: str):
    newtoot = content
    if content.find("ロックマン") == 0:
        if content.find("ロックマン、") == 0:
            newtoot = content.replace("ロックマン、", "")
        else:
            newtoot = content.replace("ロックマン", "")
    if len(newtoot[0 : newtoot.find("って言")]) > 0:
        toottext = newtoot[0 : newtoot.find("って言")]
        sptxt = ''
        if len(toottext) > 90:
            sptxt = '長文注意'
            if len(toottext) > 500:
                toottext = toottext[0 : 499-len(sptxt)] + '…'
        client.status_post(
            status = toottext,
            spoiler_text = sptxt
        )
    else:
        client.toot("ごめん、もう一度言い直してくれる？")

def greeting_toot(client: Mastodon, greeting_word_list: List[str]):
    client.toot(random.choice(greeting_word_list))

def delete_rockman_toot(client: Mastodon, content: str):
    me = client.account_verify_credentials()
    time.sleep(1)
    rock_timeline_length = 10
    rock_timeline = client.account_statuses(me['id'], limit = rock_timeline_length)
    chase = 0
    if re.search(r'\[\d\]', content):
        chase = int(content[content.find('[')+1:content.find(']')])
    delete_toot = rock_timeline[chase]
    if delete_toot['reblog'] == None:
        time.sleep(1)
        client.status_delete(delete_toot)

def reply_random_toot(client: Mastodon, status: Status):
    client.status_reply(status, random.choice(config_dict['word']['rndtoot']))

def my_post_count(client: Mastodon, status: Status):
    me = client.account_verify_credentials()
    time.sleep(1)
    client.status_reply(status, "今の僕の総トゥート数は" + str(me['statuses_count']) + "件だよ。")

def post_count(client: Mastodon, status: Status):
    client.status_reply(status, "今の" + get_name(status['account']) + "さんの総トゥート数は" + str(status['account']['statuses_count']) + "件だよ。")

def toot_todays_info(client: Mastodon, status: Status):
    now_time = datetime.now()
    client.status_reply(status, "今日は" + now_time.strftime('%Y年%m月%d日') + "だよ。")

def toot_now_info(client: Mastodon, status: Status):
    now_time = datetime.now()
    rocktoot = "今は" + now_time.strftime('%H:%M') + "だよ。\n"
    if 5 <= now_time.hour < 11:
        rocktoot += "おはよう。今は朝だね。"
    elif 11 <= now_time.hour < 16:
        rocktoot += "こんにちは。今は昼だね。"
    elif 16 <= now_time.hour < 19:
        rocktoot += "こんばんは。今は夕方だね。"
    elif 19 <= now_time.hour <= 24:
        rocktoot += "こんばんは。今は夜だね。"
    else:
        rocktoot += "今は深夜だね。おやすみ。"
    client.status_reply(status, rocktoot)

def battle_operation(client: Mastodon, status: Status):
    client.status_reply(status, "イン！")

def three_point_generator(client: Mastodon, status: Status):
    print('hoge')
    rocktoot = status['content'][14:].replace('…', 'ｯ!!').replace('、', 'ｯ!!').replace('，', 'ｯ!!').replace(',', 'ｯ!!').replace('...', 'ｯ!!').replace('・・・', 'ｯ!!').replace('･･･', 'ｯ!!')
    rocktoot = "[" + get_name(status['account']) + "]\n" + rocktoot
    sptxt = ''
    if len(rocktoot) > 90:
        sptxt = '三点リーダージェネレーター'
    if len(rocktoot) > 500:
        rocktoot = rocktoot[0:486] + '…'
    client.status_post(
        status = rocktoot,
        spoiler_text = sptxt
    )

def buzz_toot(client: Mastodon):
    whole_timeline = []
    max_id = None
    limit_datetime = datetime.now(tz=pytz.UTC) - relativedelta(months=1)
    print(limit_datetime)
    while True:
        get_timeline = client.timeline_local(max_id=max_id)
        whole_timeline += get_timeline[:]
        oldest_datetime = get_timeline[-1]['created_at']
        time.sleep(2)
        if oldest_datetime < limit_datetime:
            break
        max_id = get_timeline[-1]['id']
    
    top_five_id = []

    for toot in whole_timeline:
        favorite_count = toot['favourites_count']
        boost_count = toot['reblogs_count']
        content = rewrite(toot['content'])
        if len(content) > 15:
            content = content[:14]+'…'
        top_five_id.append({
            "id": toot['id'],
            "user_id": toot['account']['acct'],
            "username": get_name(toot['account']),
            "content": content,
            "point": boost_count * 2 + favorite_count
        })
        if len(top_five_id) > 5:
            top_five_id = sorted(top_five_id, key=lambda x: x['point'], reverse=True)[:5]

    toot_text = "先月のバズったトゥートTOP5発表！\n\n"
    for i in range(5):
        toot = top_five_id[i]
        username = toot['username'][0:10]
        toot_text += f"{i+1}. {username} 「{toot['content']}」\n{base_url}/@{toot['user_id']}/{toot['id']}\n"
    client.toot(toot_text)
