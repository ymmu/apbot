import base64
import glob
import hashlib
import io
import traceback
from binascii import hexlify, unhexlify
from copy import copy

import docx
from steem.utils import compat_bytes

from sources import utils_, post_abstract

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
from beem import Steem
from steemengine.wallet import Wallet


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

    def get_data_form(self):
        return super().get_data_form()

    def get_keys(self):
        return super(SteemWrapper, self).get_keys()

    def get_repo(self):
        return super().get_repo()

    def get_images_path(self, repo):
        return super().get_images_path(repo)

    @staticmethod
    def attach_images(text: str, img_links: list) -> str:
        """ attach image links in the text

        :param text:
        :param img_links:
        :return:
        """
        # return Post.attach_images(blog_, text, img_links)
        # image name = image order for arrangement.

        wrap_ = '<br><center>![{}](https://steemitimages.com/600x0/{})</center><br>'
        # print(type(img_links[0]))
        for img_info in img_links:
            num = img_info[0].split('.')[0]
            if 'url' in img_info[1].keys():
                wrap_img = wrap_.format(num, img_info[1]['url'])  # image name, image link
                text = text.replace('(img:{})'.format(num), wrap_img)
            else:
                pprint('No image url: ', img_info)

        return text

    def attach_youtube(self, content: str, video_links: list) -> str:
        for idx, video in enumerate(video_links):
            source = video[0]  # 0: 일반 링크, 1: iframe용 임베디드 링크
            content.replace("(video:{})".format(idx), source)
        return content

    def create_post(self, data):
        try:
            data = self.wrap_data(data)
            pprint(self.s.commit.post(**data))

            if data['tags'].split(' ')[0] == 'hive-101145':
                # 스코판이면 수수료 보내는 작업
                stm = Steem(wif=self.key_['private_active_key'])
                # print(stm.get_steem_per_mvest())
                # pprint(stm.__dict__)

                wallet = Wallet(self.account, steem_instance=stm)
                rst = wallet.transfer("sct.postingfee", 1, "SCT", memo=f"@{self.account}/{data['permlink']}")
                print('postingfee response: ')
                pprint(rst)

            print("Post created successfully")

        except Exception as e:
            print('error create_post in steem_blog. ')
            traceback.print_exc()

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

    def wrap_data(self, doc: object = None, local_repo: str = None, type='new', **kargs):
        ''' put raw data into json.

        :param doc: 외부 저장소에서 가져온 데이터
        :param local_repo: 로컬저장소글 보관하는 위치. 나중에 구글 드라이브에서 가져올 예정.
        :return:
        '''

        form = copy(self.form['post']['write'])
        img_links = [('0.png', {
            'url': 'https://cdn.steemitimages.com/DQmdBgywwgbakzBXHWLZRRRSxVFsSTV8QCzT6Nzb3KQGiBg/lotte2_s.png'}),
                     ('1.png', {
                         'url': 'https://cdn.steemitimages.com/DQmcmRtqnreEqKJq2CgpLtx5NZL2AfRPBBMnHbeJVCdGyS8/skuld_s.png'})]

        if local_repo: # 로컬레포용. 외부 레포 가져오기 전에 구현한 건데..쓰려나
            # images_, video_는 필요없음
            lines, _, _ = super(SteemWrapper, self).wrap_data(local_repo=local_repo)
            title = lines[0]
            tags = lines[1]
            body = ''.join(lines[2:])  # 리스트로 넘겨줌
            # img_links = self.upload_images()
            # test images

            body = SteemWrapper.attach_images(body, img_links)


            form.update({
                "title": title.split('\n')[0],
                "body": body,
                "author": self.account,
                "tags": tags.split('\n')[0]
            })

        else:  # 외부 data 처리

            body = ''.join(doc['content'])


            # 이미지 링크 얻어오기
            img_links = self.upload_images(doc['images']) # 실전
            # img_links = [('0', {'url': 'https://cdn.steemitimages.com/DQmPCQ862ikNrtTmD3QEjJoGoGybuDjVB4obyMApNUGNyoL/0'})]
            print(img_links)
            # 본문에 이미지 삽입
            body = SteemWrapper.attach_images(body, img_links)

            # 유튜브 링크 붙이기
            body = self.attach_youtube(body, doc["videos"])

            # 태그 붙이기
            tags = ' '.join(doc['tags'])

            print(body)
            form.update({
                "title": doc['title'],
                "body": body,
                "author": self.account,
                "tags": tags
            })

        if type == 'new':
            form["permlink"] = ''.join(random.choices(string.digits, k=10))  # random generator to create post permlink
        elif type == 'update':
            form['body'] += ' \n\n * Last update : {}'.format(utils_.now_timestamp())

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

    def upload_images(self, imgs: list, repo=None, **kargs) -> list:
        """send images to steemimages.com and get image links

        :param repo: dir path where images are stored.
        :return:
        """

        img_links = []  # results
        img_list = []   # binary images

        # get image byte data
        # if not imgs:  # get a default image (maybe for thumbnail ?)
        #     test_img_path = '../data/lotte2.PNG'
        #     with open(test_img_path, 'rb') as f:
        #         b_img = f.read()
        #         img_list.append(b_img)
        # else:
        #     imgs_path = super().get_images_path(repo=repo)
        #     for img in imgs_path:
        #         # img_name_list.append(os.path.basename(img))
        #         with open(img, 'rb') as f:
        #             b_img = f.read()
        #             img_list.append(b_img)
        # print(img_list)
        # print(img_name_list)

        # for img, img_path in zip(img_list, imgs_path): (bytes 이미지, 이미지 path)
        for idx, img in enumerate(imgs):  # (bytes 이미지)
            # digest, msg = utils_.SignImage.deriveDigest(img)

            # make TransactionBuilder instance with dummy data
            tx = transactionbuilder.TransactionBuilder(
                None,
                steemd_instance=self.s.commit.steemd,
                wallet_instance=self.s.commit.wallet,
                no_broadcast=self.s.commit.no_broadcast,
                expiration=self.s.commit.expiration)

            # make "dummy" data and append it to tx
            # data = self.wrap_data(local_repo=self.dir_path + "/../data/test.txt")
            data = copy(self.form["post"]["write"])
            data["parent_author"] = "parent_author"
            data["parent_permlink"] = "parent_permlink"
            data["permlink"] = "permlink"
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
            # img_name = os.path.basename(img_path)  # 로컬 레포가 아니기 때문에 사용 안 함
            img_name = str(idx)
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
