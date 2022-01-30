import json
import traceback
from pprint import pprint
import getpass
from src import utils_, log_decorator, vars_
# from src.never_blog import NaverWrapper
from src.steem_blog import SteemWrapper
from src.tistory_blog import TistoryWrapper
from src.vars_ import db_
import yaml
import argparse

with open(vars_.log_config) as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)

# Pytohn standard logger
import logging.config

logging.config.dictConfig(log_config)
logger = logging.getLogger(name='doc')

# google cloud logging api
from google.cloud import logging as g_logging

gcl_client = g_logging.Client()
gclogger = gcl_client.logger('apbot-doc-data')

import platform, os


def update_repo(rst, repo):
    # 노션/구글드라이브 업데이트
    pprint(rst)
    # print(repo)

    if repo == 'notion':
        n_scraper.update_doc(rst)
    elif repo == 'g_docs':
        # 발행한 글 관련 폴더로 이동시킴
        pass


@log_decorator.Log_()
def perform(doc_: object):
    repo, doc = doc_[0], doc_[1]
    blog_ = doc['blog']
    task = doc['task']
    # pprint(doc)

    if blog_ == 'tistory':
        # pass
        print('{} wrap data in main : '.format(doc["task"]))
        print(doc.keys())
        try:
            if task == 'test':
                pprint(ts.wrap_data(doc))
                rst = {
                    "test": {
                        "status": "200",
                        "postId": "74",
                        "url": "http://test",
                        "title": "test"
                    }
                }
            if task == 'publish':  # 노션만 되어있음
                print("publish")
                rst = ts.create_post(doc)
                pprint(rst)
                utils_.request_indexing(rst[blog_]["url"])
                rst[blog_].update({"title": doc["title"]})
                update_repo(rst, repo)

            elif task == 'update':  # 노션만 되어있음
                print("update")
                doc = ts.wrap_data(doc)
                rst = ts.update_post(doc)
                update_repo(rst, repo)

        except Exception as e:
            # print('error ts.create_post in main')
            traceback.print_exc()
            # log wrapper로 전달
            raise Exception('error ts.create_post in main', traceback.format_exc()) from e

    elif blog_ == 'steemit':
        print('{} wrap data : '.format(doc["blog"]))
        try:
            # pass
            # pprint(sw.wrap_data(doc))
            if task == 'publish':
                rst = sw.create_post(doc)
                print('#' * 20)
                pprint(rst)
            elif task == 'update':
                rst = sw.update_post(doc)
                print('Update ' + '#' * 20)
                pprint(rst)
            update_repo(rst, repo)

        except Exception as e:
            # print('error ts.create_post in main')
            # traceback.print_exc()
            # log wrapper로 전달
            raise Exception('error sw.create_post in main', traceback.format_exc()) from e

    # time.sleep(60*10) # every 10 mins


if __name__ == '__main__':

    if platform.system() == "Linux":
        os.environ['PATH'] = os.environ.get('PATH') \
                             + ":/data/lucca/apps/apbot/mongodb-linux-x86_64-enterprise-ubuntu2004-4.4.12/bin"

    parser = argparse.ArgumentParser(description='app_home_dir')
    parser.add_argument('--app_home', help='log config', default=None)
    args = parser.parse_args()
    if args.app_home:
        vars_.dir_path = args.app_home
        print(args.app_home)
    # db_ = getpass.getpass('mongoDB passwd: ')
    # db_ = input('mongoDB passwd: ')
    # airflow 테스트
    with open(db_, 'r') as f:
        vars_.conf = utils_.get_config(f.read())
    ts = TistoryWrapper()
    sw = SteemWrapper()
    # nw = NaverWrapper()

    while True:
        # get a doc list from google drive and notion
        # doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        n_scraper = utils_.Notion_scraper()
        doc_list = n_scraper.get_docs()
        for doc in doc_list:
            # pprint(doc)

            # log 위해서 image byte pop
            images = doc[1].pop("images")
            pprint(doc[1])
            logger.info(json.dumps(doc[1], ensure_ascii=False))
            # code 파싱 에러남. 아마 특수문자때문에
            try:
                gclogger.log_struct(doc[1])  # put original data into gcl
            except Exception as e:
                gclogger.log_struct({
                    'status': 'error',
                    'tracback': traceback.format_exc()
                })
            doc[1]["images"] = images
            perform(doc)
            pass
        break
        # time.sleep(60*10) # every 10 mins
