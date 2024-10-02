import time

import schedule

from app import App

from service.mail_service import MailService

schedule.every(5).seconds.do(App)

mail_service = MailService()

schedule.every(1).hours.do(mail_service.send_mail, "데이터 백업")

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)