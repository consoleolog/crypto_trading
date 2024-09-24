import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')
UPBIT_ACCESS_KEY=os.getenv('UPBIT_ACCESS_KEY')
UPBIT_SECRET_KEY=os.getenv('UPBIT_SECRET_KEY')
NAVER_ID=os.getenv('NAVER_ID')
NAVER_PASSWORD=os.getenv('NAVER_PASSWORD')
SMTP_FROM=os.getenv('SMTP_FROM')
SMTP_TO=os.getenv('SMTP_TO')