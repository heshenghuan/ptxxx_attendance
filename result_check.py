# -*- coding: utf-8 -*-
import yaml
import smtplib
from email.mime.text import MIMEText


def check_attendance_result():
    '''检查history.txt中是否有登录失败或签到失败的记录'''
    with open('history.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)
        if '登录失败' in content or '签到失败' in content:
            return False
    return True

def send_email(recipient, message, mail_addr, auth_code, 
               smtp_server='smtp.sina.com', smtp_port=465):
    smtpserver = smtplib.SMTP_SSL(smtp_server, smtp_port)
    smtpserver.ehlo()
    smtpserver.login(mail_addr, auth_code)
    smtpserver.sendmail(mail_addr, recipient, message.as_string())
    smtpserver.quit()

def main():
    with open("./config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    MAIL_ADDR = cfg['email']['address']
    MAIL_PASS = cfg['email']['auth_code']
    # 检查签到结果，如果有失败，发送邮件通知
    attendance_result = check_attendance_result()
    if not attendance_result:
        print("检测到签到失败，发送邮件通知管理员")
        # 这里可以调用发送邮件的函数
        with open('history.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = MAIL_ADDR
        message['To'] = MAIL_ADDR
        message['Subject'] = '签到失败通知'
        send_email(MAIL_ADDR, message, MAIL_ADDR, MAIL_PASS)


if __name__ == '__main__':
    main()
