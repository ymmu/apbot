import os
from src_ import utils_
# 모듈변수

dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

credentials = os.path.join(dir_path, 'config/credentials.json')
token = os.path.join(dir_path, 'config/token.json')
g_service = os.path.join(dir_path, 'config/g_service.json')
ids = os.path.join(dir_path, 'config/ids.json')
bkeys = os.path.join(dir_path, 'config/key_bytes.bin')
log_config = os.path.join(dir_path, 'config/log_config_logstash.yml')
config_ = os.path.join(dir_path, 'config/config.json')
db_ = os.path.join(dir_path, 'config/.temp')
conf = None