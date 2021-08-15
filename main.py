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
        doc_list = utils_.get_docs_from_gdrive()
        # doc_list.extend(utils_.get_docs_from_notion())
        # doc_list = utils_.get_docs_from_notion()
        for doc in doc_list:
            # pprint(doc)
            if doc["blog"] == 'tistory':
                print('{} wrap data in main : '.format(doc["blog"]))
                try:
                    # rst = ts.create_post(doc)
                    # pprint(rst)
                    pprint(ts.wrap_data(doc))

                except Exception as e:
                    print('error ts.create_post in main')
                    traceback.print_exc()
            # elif doc["blog"] == 'steemit':
            #     # sw.create_post()
            #     print('{} wrp data : '.format(doc["blog"]))
            #     pprint(sw.wrap_data(doc))
        break
        #time.sleep(60*10) # every 10 mins
