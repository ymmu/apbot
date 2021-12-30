import logging.config
import os
import traceback
import yaml

dir_path = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(dir_path, '../config/log_config.yml')) as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)

logging.config.dictConfig(log_config)
logger = logging.getLogger()


class Log_:
    def __init__(self):  # 데코레이터가 사용할 매개변수를 초깃값으로 받음
        pass

    def __call__(self, func):  # 호출할 함수를 매개변수로 받음

        def wrapper(self, *args, **kargs):  # 호출할 함수가 인스턴스 메서드이므로 첫 번째 매개변수는 self로 지정
            msg = {
                'function': func.__name__,
                'args': args,
                'kargs': kargs
            }
            print(msg)
            try:
                r = func(self, *args, **kargs)  # self와 매개변수를 그대로 넣어줌
                msg.update({
                    'status': 'success'
                })
                logger.info(msg)
                # with open(log_dir, 'a', encoding='utf-8') as f:
                #     f.write(json.dumps(msg, ensure_ascii=False))
                #     f.write('\n')
                return r

            except Exception as e:
                # print(e)
                print(traceback.format_exc())
                msg.update({
                    'status': 'error',
                    'tracback': traceback.format_exc()
                })
                logger.error(msg)

        return wrapper
