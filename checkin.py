# -*- coding: utf-8 -*-
import re
import yaml
import requests
import time

_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41"
}

def login(url, cookies):
    '''
    获取登陆会话
    '''
    cookies = requests.utils.cookiejar_from_dict(
        {
            'c_secure_pass': cookies
        }
    )
    bt_session = requests.session()
    bt_session.cookies = cookies
    try:
        torrent_url = f'https://{url}/torrents.php'
        test = bt_session.get(torrent_url, headers=_headers)
        if test.status_code != 200 or test.url != torrent_url:
            print('测试获取torrents.php失败，疑似cookie失效，请重新登录')
            return None
    except Exception as e:
        print("cookie失效，请重新登录:", e)
        return None
    return bt_session

def checkin(session, url):
    '''
    签到
    '''
    attendance_php = f'https://{url}/attendance.php'
    try:
        checkin_page = session.get(attendance_php, headers=_headers)
        
        if checkin_page.status_code == 200 and ('签到成功' in checkin_page.text or '簽到成功' in checkin_page.text):
            nowtime = time.strftime('%Y-%m-%d', time.localtime(time.time()))
            # 使用正则获取签到天数和获得魔力值
            signindays = re.search(r'已(?:连续签|連續簽)到 <b>(\d+)</b>', checkin_page.text, re.DOTALL).group(1)
            integral = re.search(r'本次(?:签到获得|簽到獲得) <b>(\d+)</b> .魔力值', checkin_page.text, re.DOTALL).group(1)
            signinrank = re.search(r'今日(?:签到|簽到)排名：(<b>\d+</b> / <b>\d+</b>)', checkin_page.text, re.DOTALL).group(1)
            signinrank = signinrank.replace('<b>', '').replace('</b>', '')
            print(nowtime + ' 签到成功    连续签到：' + signindays + '天    获得魔力值：' + integral + '    签到排名：' + signinrank)
            return True
        else:
            print("签到失败，可能是今日已签到或网络异常")
            return False
    except Exception as e:
        print("Attendance error:", e)
        return False

def main():
    with open("./config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    # 打印当前日期
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '配置文件加载成功')
    for station in cfg['stations']:
        name = station['name']
        url = station['base_url']
        cookies = station['cookies']
        print(f'正在处理 {name} 站点\t', end='')
        session = login(url, cookies)
        if session:
            result = checkin(session, url)
            if not result:
                print(f'{name} 站点签到失败')
        else:
            print(f'{name} 站点登录失败')
        print('-----------------------------------')


if __name__ == '__main__':
    main()
