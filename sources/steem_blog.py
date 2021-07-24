import base64
import glob
import hashlib
import io
from binascii import hexlify, unhexlify

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

from sources.post_abstract import Post


class SteemWrapper(Post):
    KST = pytz.timezone('Asia/Seoul')
    call_count = 0

    def __init__(self, account):

        self.blog_ = 'steem'
        self.account = account
        self.key_ = self.get_keys()
        self.form = self.get_data_form()
        self.repo = self.get_repo()
        self.s = Steem(nodes=['https://api.steemit.com'], keys=[self.key_['private_posting_key']])

    def get_private_posting_key(self):
        return self.key_['private_posting_key']

    def get_keys(self):
        return super(SteemWrapper, self).get_keys()[self.blog_]

    def get_repo(self):
        return super().get_repo()

    def get_data_form(self):
        return super().get_data_form()

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

    def wrap_data(self, data_dir, type='new', **kargs):
        ''' put raw data into json.

        :param data_dir: 외부 글 보관하는 위치. 나중에 구글 드라이브에서 가져올 예정.
        :return:
        '''

        with open(data_dir, 'r', encoding='utf8') as f:
            lines = f.readlines()
            title = lines[0]
            tags = lines[1]
            body = ''.join(lines[2:])  # 리스트로 넘겨줌


        # img_links = self.upload_images()
        #
        img_links = [('0.png', {'url': 'https://cdn.steemitimages.com/DQmdBgywwgbakzBXHWLZRRRSxVFsSTV8QCzT6Nzb3KQGiBg/lotte2_s.png'}),
                     ('1.png', {'url': 'https://cdn.steemitimages.com/DQmcmRtqnreEqKJq2CgpLtx5NZL2AfRPBBMnHbeJVCdGyS8/skuld_s.png'})]

        body = SteemWrapper.attach_images(body, img_links)

        form = self.form['post']['write']
        form.update({
            "title": title.split('\n')[0],
            "body": body,
            "author": self.account,
            "tags": tags.split('\n')[0]
        })

        if type == 'new':
            form["permlink"] = ''.join(random.choices(string.digits, k=10))  # random generator to create post permlink
        elif type == 'update':
            form['body'] += ' \n\n * Last update : {}'.format(utils_.get_timestamp())

        return form

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

    def upload_images(self, repo=None, **kargs):
        """send images to steemimages.com and get image links

        :param repo: dir path where images are stored.
        :return:
        """

        img_links = []  # results
        img_list = []   # binary images
        img_name_list = []

        # get image byte data
        if not repo:  # get a default image (maybe for thumbnail ?)
            test_img_path = '../data/lotte2.PNG'
            # img_name_list.append(os.path.basename(test_img_path))
            with open(test_img_path, 'rb') as f:
                b_img = f.read()
                img_list.append(b_img)
        else:
            imgs_path = super().get_images_path(repo=repo)
            for img in imgs_path:
                # img_name_list.append(os.path.basename(img))
                with open(img, 'rb') as f:
                    b_img = f.read()
                    img_list.append(b_img)
        # print(img_list)
        # print(img_name_list)
        for img, img_path in zip(img_list, imgs_path):

            # digest, msg = utils_.SignImage.deriveDigest(img)

            # make TransactionBuilder instance with dummy data
            tx = transactionbuilder.TransactionBuilder(
                None,
                steemd_instance=sw.s.commit.steemd,
                wallet_instance=sw.s.commit.wallet,
                no_broadcast=sw.s.commit.no_broadcast,
                expiration=sw.s.commit.expiration)

            # make "dummy" data and append it to tx
            data = sw.wrap_data("./../data/test.txt")
            test_d = operations.Comment(data)
            tx.appendOps([test_d])
            # pprint(tx.json())

            # - original code : signedtx = transactions.SignedTransaction(**tx.json())
            # The utils_.SignProcess class inherited steembase.transactions.SignedTransaction
            signedtx = utils_.SignImage(steemd_instance=self.s.commit.steemd, **tx.json())

            wifs = [self.get_private_posting_key()]
            # print('wifs_len: {}, wifs: {}'.format(len(wifs),wifs))
            signedtx.sign(img, wifs)
            # it's original code: signedtx.sign(wifs, chain=tx.steemd.chain_params)
            # the overridden function does't need chain param.
            # pprint(signedtx.json())

            tx["signatures"].extend(signedtx.json().get("signatures"))
            # print('sssss: ', signedtx.verify(message=b_img)[0]) # chain=tx.steemd.chain_params))

            # ref: https://johyungen.tistory.com/489
            # content = {"image": (os.path.basename(img_path), open(img_path, 'rb'))}
            img_name = os.path.basename(img_path)
            content = {"image": (img_name, img)}
            end_point = "https://steemitimages.com"
            url = "{}/{}/{}".format(end_point, self.account, tx["signatures"][0])
            # print("url: ", url)

            try:
                res = requests.post(url, files=content)
                if res.status_code == 200:
                    pprint(res.json())
                    img_links.append((img_name, res.json()))
                else:
                    img_links.append((img_name, res.json()))
            except Exception as e:
                print(e)  # Python 3.6

        return img_links

    def get_post(self, post_id):
        pass


if __name__ == '__main__':
    # print(utils_.get_timestamp())

    sw = SteemWrapper('ymmu')
    # Test get my post
    posts = sw.get_posts(nums=8)

    # Test patch data
    post = posts[-1]
    # pprint(post)

    # 1.
    patch_ = sw.wrap_data("./../data/test.txt", type='update')
    print('patch: \n')
    pprint(patch_)
    # sw.update_post(patch_, post)

    # 2.
    # patch_ = {'body': post['body'] + '\n patch test : {}'.format(utils_.get_timestamp())}
    # sw.update_post(patch_, post)

    # Test convert an article txt to json data
    # patch_ = sw.wrap_data()
    # patch_["permlink"] = post["permlink"]  # only for test
    # pprint(patch_)
    # sw.update_post(patch_, post)

    # Test submit posts
    # data = sw.wrap_data("./../data/test.txt", type='new')
    # pprint(data)
    # sw.submit_post(data)
    ## print(sw.s.__dict__)

    # make data
    # data = sw.wrap_data("./../data/test.txt")
    # data["parent_author"] = ""
    # data["parent_permlink"] = ""
    # test_d = operations.Comment(data)
    #
    # # get image data
    # test_img_path = '../data/skuld_s.PNG'
    # name_img = os.path.basename(test_img_path)
    # prefix_ = 'ImageSigningChallenge'.encode('utf-8')
    # print(prefix_)
    #
    # with open(test_img_path, 'rb') as f:
    #     binary_ = f.read()
    #
    # msg = prefix_ + compat_bytes(binary_)
    # print(msg)
    # digest = hashlib.sha256(msg).digest()
    # print(digest)

    # test

    #
    #img_links = sw.upload_images(repo='../data')
    #print(img_links)


