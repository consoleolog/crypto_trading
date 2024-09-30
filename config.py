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
TICKER=os.getenv('TICKER')

LOG_DIR=f"{os.getcwd()}/logs"
DATA_DIR=f"{os.getcwd()}/data"

S3_AWS_ACCESS_KEY=os.getenv('S3_AWS_ACCESS_KEY')
S3_AWS_SECRET_KEY=os.getenv('S3_AWS_SECRET_KEY')
S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME')