import base64
import hashlib
import io
from binascii import hexlify

from steem.utils import compat_bytes

import utils_

import string
from steem.blog import Blog
from steembase import operations, transactions
from steem import Steem, transactionbuilder
from pprint import pprint
import json
import pytz
import os
import random
import requests
from requests.exceptions import HTTPError

import numpy as np
import pandas as pd
import requests
from pick import pick
from datetime import datetime
import time
import argparse
from diff_match_patch import diff_match_patch


class SteemWrapper:
    KST = pytz.timezone('Asia/Seoul')
    call_count = 0

    def __init__(self, account, dir_path=None):
        if not dir_path:
            self.dir_path = '.'
        else:
            self.dir_path = dir_path  # os.getcwd()

        key_ = self.get_keys()['steem']
        self.s = Steem(nodes=['https://api.steemit.com'], keys=[key_['private_posting_key']])
        self.account = account

    def get_private_posting_key(self):
        return self.get_keys()['private_posting_key']

    def get_keys(self):
        with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
            return json.load(f)

    def submit_post(self, data):

        try:
            self.s.commit.post(**data)
            print("Post created successfully")

        except Exception as e:
            print(e)

    def get_posts(self, nums=3):

        try:
            b = Blog(self.account)
            posts = b.take(nums)
            post_list = []
            for p in posts:
                post_list.append(p.export())

            return post_list

        except Exception as e:
            print(e)

    def wrap_data(self, data_dir=None, **kargs):
        '''

        :param data_dir: 외부 글 보관하는 위치. 나중에 구글 드라이브에서 가져올 예정.
        :return:
        '''

        if not data_dir:
            data_dir = os.path.join(self.dir_path, '../data', 'test.txt')

        with open(data_dir, 'r', encoding='utf8') as f:
            lines = f.readlines()
            title = lines[0]
            tags = lines[1]
            body = ''.join(lines[2:])  # 리스트로 넘겨줌

        data = {**kargs}
        data["title"] = title.split('\n')[0]
        data["body"] = body
        data["author"] = self.account
        data["tags"] = tags.split('\n')[0]

        # random generator to create post permlink
        permlink = ''.join(random.choices(string.digits, k=10))
        data["permlink"] = permlink

        return data

        # with open(data_dir, 'w', encoding='utf8') as f:
        #    json.dump({'d': body_list}, f, ensure_ascii=False)

    def validate_params(self, new_data):
        '''
        Check the params for post function.
        Return False if there are params not for post function.
        :return:
        '''
        rst = True
        return rst

    def extract_params(self, data):
        """
        Extract params for submit function from data.
        :param data:
        :return:
        """
        keys = ["title", "body", "author", "tags", "permlink", 'json_metadata']
        data = {k: data[k] if k in data.keys() else None for k in keys}
        data['tags'] = " ".join(data['tags'])

        return data

    def update_post(self, new_data, data, **kargs):

        try:
            # extract_necessary items from data
            data_ = self.extract_params(data)

            # Validate if new data have wrong keys and
            # patch it to original data
            if not self.validate_params(new_data):
                raise Exception('Wrong validate params.', new_data)

            data_.update(new_data)
            # needed for update
            data_["reply_identifier"] = (data['parent_author'] + '/' + data['parent_permlink'])
            pprint(data_)

            self.s.commit.post(**data_)

            # return the url of edited post
            post_url = 'https://steemit.com/{}/@{}/{}'.format(data_['tags'].split(" ")[0], self.account,
                                                              data_['permlink'])
            # print(post_url)
            print("Post was updated successfully: {}".format(post_url))

        except Exception as e:
            print(e)

    def upload_image(self, images):
        """send images to steemimages.com and get image links

        :param images:
        :return:
        """
        pass


if __name__ == '__main__':
    # print(utils_.get_timestamp())

    sw = SteemWrapper('ymmu','.')
    # Test get my post
    # posts = sw.get_posts(nums=1)

    # Test patch data
    # post = posts[0]
    # pprint(post)
    # patch_ = {'body': post['body'] + '\n patch test : {}'.format(utils_.get_timestamp())}
    # sw.update_post(patch_, post)

    # Test convert an article txt to json data
    # patch_ = sw.wrap_data()
    # patch_["permlink"] = post["permlink"]  # only for test
    # pprint(patch_)
    # sw.update_post(patch_, post)

    # Test submit posts
    # data = sw.wrap_data()
    # sw.submit_post(data)
    ## print(sw.s.__dict__)

    # make data
    data = sw.wrap_data()
    data["parent_author"] = ""
    data["parent_permlink"] = ""
    test_d = operations.Comment(data)

    # get image data
    test_img_path = '../data/skuld_s.PNG'
    name_img = os.path.basename(test_img_path)
    prefix_ = 'ImageSigningChallenge'.encode('utf-8')
    print(prefix_)

    with open(test_img_path, 'rb') as f:
        binary_ = f.read()

    msg = prefix_ + compat_bytes(binary_)
    print(msg)
    digest = hashlib.sha256(msg).digest()
    print(digest)


    #''' TransactionBuilder test
    tx = transactionbuilder.TransactionBuilder(
        None,
        steemd_instance=sw.s.commit.steemd,
        wallet_instance=sw.s.commit.wallet,
        no_broadcast=sw.s.commit.no_broadcast,
        expiration=sw.s.commit.expiration)

    tx.appendOps([test_d])
    #pprint(tx.json())
    #pprint()
    # get signedTransaction to sign message
    # signedtx = transactions.SignedTransaction(**tx.json())
    signedtx = utils_.SignProcess(steemd_instance=sw.s.commit.steemd, **tx.json())

    #signedtx.digest = digest
    wifs = [sw.get_private_posting_key()]
    #print(wifs, len(wifs))
    #signedtx.sign(wifs, chain=tx.steemd.chain_params)
    signedtx.sign(msg, wifs)
    # pprint(signedtx.json())
    tx["signatures"].extend(signedtx.json().get("signatures"))

    print('sssss: ', signedtx.verify(chain=tx.steemd.chain_params))


    # post_op = operations.Comment(
    #         **{
    #             "parent_author": parent_author,
    #             "parent_permlink": parent_permlink,
    #             "author": author,
    #             "permlink": permlink,
    #             "title": title,
    #             "body": body,
    #             "json_metadata": json_metadata
    #         })
    #     ops = [post_op]

    # ref: https://johyungen.tistory.com/489
    # up = {'image':(filename, open(filename, 'rb'), "multipart/form-data")}
    content = {"image": (name_img, open(test_img_path, 'rb'))}
    end_point = "https://steemitimages.com"
    url = "{}/{}/{}".format(end_point, sw.account, tx["signatures"][0])

    print("url: ", url)
    try:
        res = requests.post(url, files=content)
        print(res.status_code)
        pprint(res.json())

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

