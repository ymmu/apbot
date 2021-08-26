import json
import re
import time
import traceback
from pprint import pprint

from sources import utils_
# from sources.never_blog import NaverWrapper
from sources.steem_blog import SteemWrapper
from sources.tistory_blog import TistoryWrapper


def update_repo(rst, repo):
    # 노션/구글드라이브 업데이트
    pprint(rst)
    # print(repo)

    if repo == 'notion':
        utils_.update_doc_notion(rst)
    elif repo == 'g_docs':
        # 발행한 글 관련 폴더로 이동시킴
        pass


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

            if task == 'publish': # 노션만 되어있음
                print("publish")
                rst = ts.create_post(doc)
                rst[blog_].update({"title": doc["title"]})
                update_repo(rst, repo)

            elif task == 'update': # 노션만 되어있음
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
            print('error ts.create_post in main')
            traceback.print_exc()

    elif blog_ == 'steemit':
        print('{} wrap data : '.format(doc["blog"]))
        try:
            # pass
            pprint(sw.wrap_data(doc))
            # if doc["status"] == 'publish': # 노션만 되어있음
            #     rst = sw.create_post(doc)
            # elif doc["status"] == 'update': # 노션만 되어있음
            #     rst = sw.update_post(doc)
            #
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

    # ts = TistoryWrapper("myohyun")
    # nw = NaverWrapper("myohyun")
    sw = SteemWrapper('ymmu')

    while True:
        # get doc list form google drive and notion
        # doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        doc_list = utils_.get_docs_from_notion()
        for doc in doc_list:
            # pprint(doc)
            perform(doc)

        break
        #time.sleep(60*10) # every 10 mins
