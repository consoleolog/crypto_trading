import time

import schedule

from app import App
from service.aws_service import AWSService

from service.mail_service import MailService

schedule.every(5).seconds.do(App)

mail_service = MailService()
aws_service = AWSService()
schedule.every(1).hours.do(mail_service.send_mail, "데이터 백업")
schedule.every(1).hours.do(mail_service.send_log_file, "로그 파일 백업")
schedule.every(1).hours.do(aws_service.upload_data_files)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)