import json
import os

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        # 尝试从环境变量获取配置或使用 config.json 文件中的配置作为回退
        with open('config.json', 'r') as f:
            config = json.load(f)
            
            # 使用环境变量或配置文件的 GitHub Token
            self.github_token = os.getenv('GITHUB_TOKEN', config.get('github_token'))

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['smtp_server'] = os.getenv('EMAIL_SMTP_SERVER', self.email.get('smtp_server', ''))
            self.email['smtp_port'] = os.getenv('EMAIL_SMTP_PORT', self.email.get('smtp_port', ''))
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))
            self.email['from'] = os.getenv('EMAIL_FROM', self.email.get('from', ''))
            self.email['to'] = os.getenv('EMAIL_TO', self.email.get('to', ''))

            self.subscriptions_file = config.get('subscriptions_file')
            # 默认每天执行
            self.freq_days = config.get('github_progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.exec_time = config.get('github_progress_execution_time', "08:00") 
            
            self.hacker_news = config.get('hacker_news', {})
