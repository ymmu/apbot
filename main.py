import json
import re
import time
import traceback
from pprint import pprint

from sources import utils_, log_decorator
# from sources.never_blog import NaverWrapper
from sources.steem_blog import SteemWrapper
from sources.tistory_blog import TistoryWrapper
import logging.config
import yaml

with open('./config/log_config.yml') as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)

logging.config.dictConfig(log_config)
logger = logging.getLogger(name='main')


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

            if task == 'publish':  # 노션만 되어있음
                print("publish")
                rst = ts.create_post(doc)
                utils_.request_indexing(rst[blog_]["url"])
                rst[blog_].update({"title": doc["title"]})
                update_repo(rst, repo)

            elif task == 'update':  # 노션만 되어있음
                print("update")
                doc = ts.wrap_data(doc)
                rst = ts.update_post(doc)
                rst[blog_].update({"title": doc["title"]})
                update_repo(rst, repo)

            ''' rst
                            {
                              "tistory":{
                                "status":"200",
                                "postId":"74",
                                "url":"http://sampleUrl.tistory.com/74",
                                "title": "추가"
                              }
                            }
                            '''

        except Exception as e:
            # print('error ts.create_post in main')
            # traceback.print_exc()
            raise Exception('error ts.create_post in main', traceback.format_exc()) from e

    elif blog_ == 'steemit':
        print('{} wrap data : '.format(doc["blog"]))
        try:
            # pass
            # pprint(sw.wrap_data(doc))
            if task == 'publish':
                rst = sw.create_post(doc)
            # elif task == 'update': # 노션만 되어있음
            #     rst = sw.update_post(doc)

            # pprint(rst[0])
            # pprint(rst[1])

            # ''' rst
            #                 {
            #                   "tistory":{
            #                     "status":"200",
            #                     "postId":"74",
            #                     "url":"http://sampleUrl.tistory.com/74",
            #                     "title": "추가"
            #                   }
            #                 }
            #                 '''
            #
            # pprint(rst)
            # rst["tistory"].update({"title": doc["title"]})
            # if repo == 'notion':
            #     utils_.update_doc_notion(rst)
            # elif repo == 'g_docs':
            #     # 발행한 글 관련 폴더로 이동시킴
            #     pass
        except Exception as e:
            print('error ts.create_post in main')
            traceback.print_exc()

    # time.sleep(60*10) # every 10 mins


if __name__ == '__main__':

    db_pass = input('mongoDB db_name: ')
    ts = TistoryWrapper("myohyun", db_pass)
    # nw = NaverWrapper("myohyun", db_pass)
    sw = SteemWrapper('ymmu', db_pass)

    while True:
        # get doc list form google drive and notion
        # doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        n_scraper = utils_.Notion_scraper()
        doc_list = n_scraper.get_docs()
        for doc in doc_list:
            # pprint(doc)
            perform(doc)
            pass
        break
        # time.sleep(60*10) # every 10 mins
