import traceback
from pprint import pprint

from sources import utils_, log_decorator
# from sources.never_blog import NaverWrapper
from sources.steem_blog import SteemWrapper
from sources.tistory_blog import TistoryWrapper
import yaml
with open('./config/log_config.yml') as f:
    log_config = yaml.load(f, Loader=yaml.FullLoader)

# Pytohn standard logger
import logging.config
logging.config.dictConfig(log_config)
logger = logging.getLogger(name='doc_data')

# google cloud logging api
from google.cloud import logging as g_logging
gcl_client = g_logging.Client()
gclogger = gcl_client.logger('apbot-doc-data')


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
            # log wrapper로 전달
            raise Exception('error ts.create_post in main', traceback.format_exc()) from e

    elif blog_ == 'steemit':
        print('{} wrap data : '.format(doc["blog"]))
        try:
            # pass
            # pprint(sw.wrap_data(doc))
            if task == 'publish':
                rst = sw.create_post(doc)
                print('#'*20)
                pprint(rst)
            elif task == 'update':
                rst = sw.update_post(doc)
                print('Update '+'#'*20)
                pprint(rst)
            update_repo(rst, repo)

        except Exception as e:
            # print('error ts.create_post in main')
            # traceback.print_exc()
            # log wrapper로 전달
            raise Exception('error sw.create_post in main', traceback.format_exc()) from e

    # time.sleep(60*10) # every 10 mins


if __name__ == '__main__':

    db_pass = input('mongoDB db_name: ')
    ts = TistoryWrapper(db_pass)
    sw = SteemWrapper(db_pass)
    # nw = NaverWrapper(db_pass)

    while True:
        # get doc list form google drive and notion
        # doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        n_scraper = utils_.Notion_scraper()
        doc_list = n_scraper.get_docs()
        for doc in doc_list:
            # pprint(doc)

            logger.info(doc[1])
            gclogger.log_struct(doc[1])    # put original data into gcl
            perform(doc)
            pass
        break
        # time.sleep(60*10) # every 10 mins
