import pytz
from datetime import datetime


# tmp
def get_timestamp():
    KST = pytz.timezone('Asia/Seoul')
    return datetime.utcnow().replace(tzinfo=KST).strftime("%Y-%m-%dT%H:%M:%S%z")
