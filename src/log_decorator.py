import json
import logging.config
import os
import traceback
import yaml
from google.cloud import monitoring_v3
from google.cloud import logging as g_logging
from src import vars_

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(vars_.dir_path, vars_.g_service)
with open(os.path.join(vars_.dir_path, vars_.log_config)) as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)

logging.config.dictConfig(log_config)
logger = logging.getLogger('monitoring')

# Retrieves a Cloud Logging handler based on the environment
# you're running in and integrates the handler with the
# Python logging module. By default this captures all logs
# at INFO level and higher
# client.setup_logging()
gcl_client = g_logging.Client()
gclogger = gcl_client.logger('apbot')


class Log_:
    def __init__(self):  # 데코레이터가 사용할 매개변수를 초깃값으로 받음
        pass

    def __call__(self, func):  # 호출할 함수를 매개변수로 받음

        def wrapper(self, *args, **kargs):  # 호출할 함수가 인스턴스 메서드이므로 첫 번째 매개변수는 self로 지정
            msg = {
                'function': func.__name__,
                'args': args if args else None,
                'kargs': kargs if kargs else None,
            }
            print(msg)
            try:
                r = func(self, *args, **kargs)  # self와 매개변수를 그대로 넣어줌
                msg.update({
                    'status': 'success'
                })
                logger.info(json.dumps(msg, ensure_ascii=False))
                gclogger.log_struct(msg)

                return r

            except Exception as e:
                # print(e)
                # print(traceback.format_exc())
                msg.update({
                    'status': 'error',
                    'tracback': traceback.format_exc()
                })
                logger.error(msg)

        return wrapper
