import os
import requests
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAIL = os.getenv("TO_EMAIL")
DB_FILE = "exchange_rates.json"

def fetch_exchange_rate():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=GBP&to=CNY")
        data = response.json()
        return data["rates"]["CNY"], data["date"]
    except Exception as e:
        print(f"Error: {e}")
        return None, None

def send_email(rate, timestamp):
    msg = MIMEText(f"""
        汇率提醒：
        1 GBP = {rate} CNY
        更新时间：{timestamp}
    """)
    msg["Subject"] = "每日英镑兑人民币汇率提醒"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.yeah.net", 465) as server:
            server.login(FROM_EMAIL, SENDGRID_API_KEY)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败：{e}")

def job():
     """
     定期任务：获取汇率并发送邮件通知。
     
     该函数执行以下操作：
     1. 调用 `fetch_exchange_rate` 获取当前汇率和时间戳。
     2. 如果成功获取到汇率（`rate` 不为 `None`），则调用 `send_email` 发送包含汇率和时间戳的邮件通知。
     
     注意：
     - 此函数通常作为定时任务运行。
     - 依赖外部函数 `fetch_exchange_rate` 和 `send_email` 的实现。
     """
rate, timestamp = fetch_exchange_rate()
if rate is not None:
        send_email(rate, timestamp)

if __name__ == "__main__":
    # 初始化数据库
     if not os.path.exists(DB_FILE):
        fetch_exchange_rate()

    # 启动定时任务（每天12:00执行）
scheduler = BlockingScheduler()
scheduler.add_job(job, "cron", hour=12)
scheduler.start()