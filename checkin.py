# -*- coding: utf-8 -*-
import re
import yaml
import requests
import time
import smtplib
from email.mime.text import MIMEText

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
        test = bt_session.get(torrent_url, headers=_headers, timeout=60)
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

        return False
    except Exception as e:
        print("Attendance error:", e)
        return False


def process_station(station):
    '''处理单个站点的签到逻辑''' 
    name = station['name']
    url = station['base_url']
    cookies = station['cookies']
    retry_times = station.get('retry_times', 3)  # 默认重试3次
    print(f'正在处理 {name} 站点\t', end='')
    result = False
    for attempt in range(retry_times + 1):  # 包括第一次尝试
        session = login(url, cookies)
        if session:
            result = checkin(session, url)
            if result:
                break
            else:
                print(f'第{attempt+1}次签到失败，10s后重试...')
                time.sleep(10)  # 等待10秒后重试
    if not result:
        print(f'{name} 站点签到失败')
        return False
    else:
        return True


def send_email(recipient, message, mail_addr, auth_code, smtp_server='smtp.sina.com', smtp_port=465):
    smtpserver = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtpserver.ehlo()
    smtpserver.login(mail_addr, auth_code)
    smtpserver.sendmail(mail_addr, recipient, message.as_string())
    smtpserver.quit()


def main():
    with open("./config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    # 打印当前日期
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print(current_time, '配置文件加载成功')
    
    # 记录失败的站点
    failed_stations = []
    for station in cfg['stations']:
        success = process_station(station)
        if not success:
            failed_stations.append(station['name'])
        print('-----------------------------------')
    
    # 检查签到结果，如果有失败，发送邮件通知
    if failed_stations:
        print("检测到签到失败，发送邮件通知管理员")
        # 构建邮件内容
        content = f'签到执行时间: {current_time}\n以下站点签到失败：\n'
        content += '\n'.join(failed_stations)
        # 发送邮件
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = cfg['email']['address']
        message['To'] = cfg['email']['address']
        message['Subject'] = '签到失败通知'
        send_email(cfg['email']['address'], message, cfg['email']['address'], cfg['email']['auth_code'])


if __name__ == '__main__':
    main()
