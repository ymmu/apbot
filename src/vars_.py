import os
from src import utils_
# 모듈변수

dir_path = os.path.dirname(os.path.abspath(__file__))

credentials = os.path.join(dir_path, '../config/credentials.json')
token = os.path.join(dir_path, '../config/token.json')
g_service = os.path.join(dir_path, '../config/g_service.json')
ids = os.path.join(dir_path, '../config/ids.json')
bkeys = os.path.join(dir_path, '../config/key_bytes.bin')
log_config = './config/log_config.yml'
db_ = os.path.join(dir_path, '../config/.temp')
conf = None