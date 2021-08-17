import json
import re
import time
import traceback
from pprint import pprint

from sources import utils_
# from sources.never_blog import NaverWrapper
from sources.steem_blog import SteemWrapper
from sources.tistory_blog import TistoryWrapper

if __name__ == '__main__':

    ts = TistoryWrapper("myohyun")
    # nw = NaverWrapper("myohyun")
    # sw = SteemWrapper('ymmu')

    while True:
        # get doc list form google drive and notion
        # doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        doc_list = utils_.get_docs_from_notion()
        for (repo, doc) in doc_list:
            # pprint(doc)
            if doc["blog"] == 'tistory':
                pass
                print('{} wrap data in main : '.format(doc["blog"]))
                try:
                    rst = ts.create_post(doc)
                    rst.update({"tistory": {"title": doc["title"]}})
                    if repo == 'notion':
                        utils_.update_doc_notion(rst)
                    elif repo == 'g_docs':
                        # 발행한 글 관련 폴더로 이동시킴
                        pass

                    # pprint(rst)
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
                    # pprint(ts.wrap_data(doc))

                except Exception as e:
                    print('error ts.create_post in main')
                    traceback.print_exc()

            # elif doc["blog"] == 'steemit':
            #     print('{} wrap data : '.format(doc["blog"]))
            #
            #     try:
            #         sw.create_post(doc)
            #         # pprint(sw.wrap_data(doc))
            #     except Exception as e:
            #         print('error ts.create_post in main')
            #         traceback.print_exc()

        break
        #time.sleep(60*10) # every 10 mins
