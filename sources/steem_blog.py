from steem.blog import Blog
from steembase import operations, transactions
from steem import Steem, transactionbuilder
from beem import Steem as beem_steem
from steemengine.wallet import Wallet

from copy import copy
from pprint import pprint
import string
import re
import traceback
import pytz
import random
import requests

from sources import utils_, post_abstract
from sources.post_abstract import Post

from binascii import hexlify, unhexlify
import base64
import glob
import hashlib
import io
import docx
from steem.utils import compat_bytes



class SteemWrapper(Post):
    KST = pytz.timezone('Asia/Seoul')
    call_count = 0

    def __init__(self, db_pass):

        self.blog_ = 'steemit'
        self.key_ = self.get_keys(db_pass)
        self.account = self.get_account(self.blog_)
        self.form = self.get_data_form()
        self.repo = self.get_repo()
        self.s = Steem(nodes=['https://api.steemit.com'], keys=[self.key_['private_posting_key']])

    def get_private_posting_key(self):
        return self.key_['private_posting_key']

    def get_data_form(self):
        return super().get_data_form()

    def get_keys(self, db_pass):
        return super(SteemWrapper, self).get_keys(db_pass)

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
        import re
        for idx, video in enumerate(video_links):
            source = video[0]  # 0: 일반 링크, 1: iframe용 임베디드 링크
            source = re.findall('https://[a-zA-Z0-9.]+/[a-zA-Z0-9]+', source)[0]
            print('fffff', source)
            content.replace("(video:{})".format(idx), source)
        return content

    def transfer_fee(self, data):
        rst_2 = None
        if data['tags'].split(' ')[0] == 'hive-101145':
            # 스코판이면 수수료 보내는 작업
            stm = beem_steem(wif=self.key_['private_active_key'])
            # print(stm.get_steem_per_mvest())
            # pprint(stm.__dict__)

            wallet = Wallet(self.account, steem_instance=stm)
            rst_2 = wallet.transfer("sct.postingfee", 1, "SCT", memo=f"@{self.account}/{data['permlink']}")
            print('postingfee response: ')
            pprint(rst_2)
        else:
            print('It\'s not the post from steemcoinpan. ')

        return rst_2

    def create_post(self, data):
        rst_dict = {'steemit': {}}
        rst_1, rst_2 = None, None
        try:
            task = data['task']
            data = self.wrap_data(data)
            rst_1 = self.s.commit.post(**data)
            pprint(rst_1)

            rst_2 = self.transfer_fee(data)

            print("Post created successfully")
            rst_dict['steemit']['msg'] = rst_1
            rst_dict['steemit']['msg']['transfer_fee'] = rst_2
            url = 'https://steemit.com/{}/@{}/{}'.format(data['tags'][0],
                                                         self.account,
                                                         data['permlink'])
            rst_dict.update({"status": None,    # steemit은 에러 결과가 json에 담겨올 듯.
                             "url": url,
                             'task': task,
                             "title": data['title']}) # url 추가

            return rst_dict

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

        :param type: 'new'|'update'
        :param doc: 외부 저장소에서 가져온 데이터
        :param local_repo: 로컬저장소글 보관하는 위치. 나중에 구글 드라이브에서 가져올 예정.
        :return:
        '''

        form = copy(self.form['post']['write'])

        # 로컬 레포용 임시?
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
            img_links = self.upload_images(doc['images'])  # 실전
            # img_links = [('0', {'url':
            # 'https://cdn.steemitimages.com/DQmPCQ862ikNrtTmD3QEjJoGoGybuDjVB4obyMApNUGNyoL/0'})]
            print(img_links)

            # 본문에 이미지 삽입
            body = SteemWrapper.attach_images(body, img_links)

            # 유튜브 링크 붙이기
            print(doc)
            body = self.attach_youtube(body, doc["videos"])

            # <space> 바꾸기
            for idx, t in enumerate(doc["content"]):
                doc["content"][idx] = re.sub("<space>", '\n', t)

            print(body)

            tags = ' '.join(doc['tags'])
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
            # data_["reply_identifier"] = (data['parent_author'] + '/' + data['parent_permlink'])
            # parent_author 의미가 모호하네. /parent_author/parent_permlink/root_author/root_permlink 인가?
            # https://steemit.com/kr/@ymmu/9565539929
            p_permlink, permlink = doc['post_url'].split('/')[-3], doc['post_url'].split('/')[-1]
            form.update({"permlink": permlink,
                         'json_metadata': {'tags': doc['tags']},
                         "reply_identifier": ('' + '/' + p_permlink)
                         })

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

    def update_post(self, new_data, data=None, **kargs):
        rst_dict = {self.blog_: None}
        try:
            # 기존 데이터를 get함수로 steemit에서 받아와서 새 데이터로 갱신 후 업데이트
            # extract_necessary items from data
            # data_ = self.extract_params(data)

            # Validate if new data have wrong keys and
            # patch it to original data
            # if not self.validate_params(new_data):
            #     raise Exception('Wrong validate params.', new_data)
            # data_.update(new_data)

            # Notion에서 업데이트한 데이터
            data_ = self.wrap_data(new_data, type='update')

            rst = self.s.commit.post(**data_)
            # pprint(rst)
            rst_dict[self.blog_] = rst
            rst_dict[self.blog_].update({"status": None,
                                         "title": data_["title"],
                                         'task': new_data['task'],
                                         "url": new_data['post_url']})

            print("Post was updated successfully: {}".format(new_data['post_url']))
            # pprint(rst_dict)
            return rst_dict

        except Exception as e:
            traceback.print_exc()

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

    def monitor_voting_power(self, account):

        res = self.s.steemd.get_account(account=account)

