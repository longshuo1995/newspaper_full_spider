import smtplib
from email.mime.text import MIMEText


class EmailToos:
    def __init__(self):
        self.email_host = 'smtp.163.com'  # 邮箱地址
        self.email_user = 'longshuo111@163.com'  # 发送者账号
        self.email_pwd = 'aa1617'  # 发送者的密码

    def send_msg(self, receiver, title, send_content):
        msg = MIMEText(send_content)  # 邮件内容
        msg['Subject'] = title   # 邮件主题
        msg['From'] = self.email_host  # 发送者账号
        msg['To'] = receiver  # 接收者账号列表
        smtp = smtplib.SMTP(self.email_host, port=25)  # 连接邮箱，传入邮箱地址，和端口号，smtp的端口号是25
        # 登录
        smtp.login(self.email_user, self.email_pwd)  # 发送者的邮箱账号，密码
        # 发送
        smtp.sendmail(self.email_user, receiver, msg.as_string())


if __name__ == '__main__':
    email = EmailToos()
    email.send_msg("1522499853@qq.com", "nihao", "hello world")
