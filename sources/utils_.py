import json
import os
from pprint import pprint
from urllib.parse import parse_qs, urlparse

import markdown
import notion
import pytz
from datetime import datetime, date

import requests
from PIL import Image
import io
import steembase

import hashlib
import logging
import struct
import time
import array
import sys
from binascii import hexlify, unhexlify
from collections import OrderedDict
from datetime import datetime
import os.path
import re
import json
from pprint import pprint

from notion.client import NotionClient

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from apiclient import errors

import ecdsa
from steem.utils import compat_bytes, compat_chr
from steembase.account import PrivateKey, PublicKey
from steembase.chains import known_chains
from steembase.operations import Operation, GrapheneObject, isArgsThisClass
from steembase.types import (
    Array,
    Set,
    Signature,
    PointInTime,
    Uint16,
    Uint32,
)

try:
    import secp256k1

    USE_SECP256K1 = True
    # log.debug("Loaded secp256k1 binding.")
except:  # noqa FIXME(sneak)
    USE_SECP256K1 = False
    # log.debug("To speed up transactions signing install \n"
    #          "    pip install secp256k1")


class SignImage(steembase.transactions.SignedTransaction):
    """
    # get signedTransaction as parent class to use sign message function explicitly.
    # (override) adjust original sign function from SignedTransaction class.
    # New overridden sign function need a message param and doesn't need a chain param

    """

    def __init__(self, steemd_instance, *args, **kwargs):
        # super 인자에 아무것도 안 적어주면 디폴트로 현 클래스명이 들어감
        self.steemd = steemd_instance
        super(SignImage, self).__init__(*args, **kwargs)

    @staticmethod
    def deriveDigest(message):  # chain=None
        """ it was overriden and makes image hash and byte message with prefix.

        :param message:
        :return: digest(image_hash) and byte message
        """

        # 1. convert prefix to byte type
        prefix_ = 'ImageSigningChallenge'.encode('utf-8')
        # print(prefix_)

        # 3. concat prefix and image
        msg = prefix_ + compat_bytes(message)
        # print('msg: ', msg)

        # 4. get image hash
        digest = hashlib.sha256(msg).digest()
        print('data hash: ', digest)
        return digest, msg

        # test ----
        # chain_params = self.getChainParams(chain)
        # pprint(chain_params)
        # # Chain ID
        # self.chainid = chain_params["chain_id"]
        # message2 = unhexlify(self.chainid) + compat_bytes(self)
        # message2 = hashlib.sha256(message2).digest()
        # print(type(message2), message2)
        # print(type(self.digest), self.digest)

    def sign(self, message, wifkeys):
        """ Sign the transaction with the provided private keys.
            :param list wifkeys: Array of wif keys
            :param str chain: identifier for the chain
        """

        self.digest, message = SignImage.deriveDigest(message)

        # Get Unique private keys
        self.privkeys = []
        [
            self.privkeys.append(item) for item in wifkeys
            if item not in self.privkeys
        ]

        # Sign the message with every private key given!
        sigs = []
        for wif in self.privkeys:
            # print(wif)
            # print(self.digest)
            p = compat_bytes(PrivateKey(wif))
            i = 0
            if USE_SECP256K1:
                ndata = secp256k1.ffi.new("const int *ndata")
                ndata[0] = 0
                while True:
                    ndata[0] += 1
                    privkey = secp256k1.PrivateKey(p, raw=True)
                    sig = secp256k1.ffi.new(
                        'secp256k1_ecdsa_recoverable_signature *')
                    signed = secp256k1.lib.secp256k1_ecdsa_sign_recoverable(
                        privkey.ctx, sig, self.digest, privkey.private_key,
                        secp256k1.ffi.NULL, ndata)
                    assert signed == 1
                    signature, i = privkey.ecdsa_recoverable_serialize(sig)
                    if self._is_canonical(signature):
                        i += 4  # compressed
                        i += 27  # compact
                        break
            else:
                cnt = 0
                sk = ecdsa.SigningKey.from_string(p, curve=ecdsa.SECP256k1)
                while 1:
                    cnt += 1
                    if not cnt % 20:
                        print("Still searching for a canonical signature. "
                              "Tried %d times already!" % cnt)

                    # Deterministic k
                    k = ecdsa.rfc6979.generate_k(
                        sk.curve.generator.order(),
                        sk.privkey.secret_multiplier,
                        hashlib.sha256,
                        hashlib.sha256(
                            self.digest + struct.pack("d", time.time(
                            ))  # use the local time to randomize the signature
                        ).digest())

                    # Sign message
                    #
                    sigder = sk.sign_digest(
                        self.digest, sigencode=ecdsa.util.sigencode_der, k=k)

                    # Reformating of signature
                    #
                    r, s = ecdsa.util.sigdecode_der(sigder,
                                                    sk.curve.generator.order())
                    signature = ecdsa.util.sigencode_string(
                        r, s, sk.curve.generator.order())

                    # This line allows us to convert a 2.7 byte array(which is just binary) to an array of byte values.
                    # We can then use the elements in sigder as integers, as in the following two lines.
                    sigder = array.array('B', sigder)

                    # Make sure signature is canonical!
                    #
                    lenR = sigder[3]
                    lenS = sigder[5 + lenR]
                    if lenR == 32 and lenS == 32:
                        # Derive the recovery parameter
                        #
                        i = self.recoverPubkeyParameter(
                            self.digest, signature, sk.get_verifying_key())
                        i += 4  # compressed
                        i += 27  # compact
                        break

            # pack signature
            #
            sigstr = struct.pack("<B", i)
            sigstr += signature

            sigs.append(Signature(sigstr))

        self.data["signatures"] = Array(sigs)
        return self

    def verify(self, message, pubkeys=[], chain=None):
        '''
        if not chain:
            raise ValueError("Chain needs to be provided!")
        chain_params = self.getChainParams(chain)
        self.deriveDigest(chain)
        '''

        digest, message = SignImage.deriveDigest(message)

        signatures = self.data["signatures"].data
        print('signatures in verify: ', signatures[0])
        pubKeysFound = []

        for signature in signatures:
            sig = compat_bytes(signature)[1:]
            if sys.version >= '3.0':
                recoverParameter = (compat_bytes(signature)[0]) - 4 - 27  # recover parameter only
            else:
                recoverParameter = ord((compat_bytes(signature)[0])) - 4 - 27

            if USE_SECP256K1:
                ALL_FLAGS = secp256k1.lib.SECP256K1_CONTEXT_VERIFY | \
                            secp256k1.lib.SECP256K1_CONTEXT_SIGN
                # Placeholder
                pub = secp256k1.PublicKey(flags=ALL_FLAGS)
                # Recover raw signature
                sig = pub.ecdsa_recoverable_deserialize(sig, recoverParameter)
                # Recover PublicKey
                verifyPub = secp256k1.PublicKey(
                    pub.ecdsa_recover(compat_bytes(message), sig))
                # Convert recoverable sig to normal sig
                normalSig = verifyPub.ecdsa_recoverable_convert(sig)
                # Verify
                verifyPub.ecdsa_verify(compat_bytes(message), normalSig)
                phex = hexlify(
                    verifyPub.serialize(compressed=True)).decode('ascii')
                pubKeysFound.append(phex)
            else:
                p = self.recover_public_key(digest, sig, recoverParameter)
                # Will throw an exception of not valid
                p.verify_digest(
                    sig, digest, sigdecode=ecdsa.util.sigdecode_string)
                phex = hexlify(self.compressedPubkey(p)).decode('ascii')
                pubKeysFound.append(phex)

        for pubkey in pubkeys:
            if not isinstance(pubkey, PublicKey):
                raise Exception("Pubkeys must be array of 'PublicKey'")

            k = pubkey.unCompressed()[2:]
            if k not in pubKeysFound and repr(pubkey) not in pubKeysFound:
                k = PublicKey(PublicKey(k).compressed())
                # f = format(k, chain_params["prefix"])
                # f = format(k, )
                # raise Exception("Signature for %s missing!" % f)
        return pubKeysFound


# tmp
def now_timestamp(str_=True):
    KST = pytz.timezone('Asia/Seoul')
    now_ = datetime.utcnow().replace(tzinfo=KST)
    if str_:
        return now_.strftime("%Y-%m-%dT%H:%M:%S%z")
    else:
        return now_


def img2byte(img_path=None):
    if not img_path:
        img_path = "./data/lotte.png"
    img = Image.open(img_path)
    bytearr = io.BytesIO()
    img.save(bytearr, format="png")
    return bytearr.getvalue()


class Session:

    def __init__(self, form, key_, account, blog_):
        self.cwd_ = os.path.dirname(os.path.abspath(__file__))
        self.form = form
        self.key_ = key_
        self.blog_ = blog_
        self.access_token = None
        self.start_t = None
        self.last_sess_path = os.path.join(self.cwd_, './tmp_sess.json')
        self.last_sess_info = None
        self.t = 60
        for k in self.form.keys():
            self.form[k]['redirect_uri'] = self.form[k]['redirect_uri'].format(account)

        # check the last access token is valid
        # if not, get new one and save it to temp json
        if os.path.isfile(self.last_sess_path):
            with open(self.last_sess_path, 'r') as f:
                self.last_sess_info = json.load(f)
            if self.blog_ in self.last_sess_info.keys():
                last_sess_info = self.last_sess_info[self.blog_]
                sess_last_start = datetime.strptime(last_sess_info["start_t"], "%Y-%m-%dT%H:%M:%S%z")
                print('last session was started at ', sess_last_start)
                if self.is_expired(sess_last_start):
                    self.authorize()
                else:
                    print('got last session token.')
                    self.access_token = last_sess_info["access_token"]
                    self.start_t = last_sess_info["start_t"]
            else:
                self.authorize()
        else:
            self.authorize()

    def get_token(self):
        return self.access_token

    def is_expired(self, sess_last_start=None):
        if not sess_last_start:
            sess_last_start = self.start_t
        t_diff = now_timestamp(str_=False) - sess_last_start
        print('{} mins went after authorization. '.format(t_diff.total_seconds()/60))  # 분처리로 하세
        if t_diff.total_seconds() / 60 >= self.t:  # 분 기준임
            return True
        else:
            return False

    def authorize(self):
        """ get access_token

        :return:
        """
        forms = self.form["code_params"]
        code_url = forms.pop('req_url')
        forms.update({
            "client_id": self.key_['app_id']
        })

        # print(code_url, forms)

        try:
            res = requests.get(url=code_url, params=forms)
            if res.status_code == 200:
                auth_page = res.url
                print(auth_page)
            else:
                # print(res.text)
                raise Exception(res)

            # get code using selenium
            # 안 된다..불가능한 듯
            # chrome = webdriver.Chrome('../chromedriver.exe')
            # print(auth_page)
            # chrome.get(auth_page)
            # chrome.implicitly_wait(2)
            #
            # chrome.implicitly_wait(1)
            # chrome.find_element_by_xpath('// *[ @ id = "contents"] / div[4] / button[1]').click()
            # chrome.implicitly_wait(2)
            # print(chrome.current_url)
            res_url = input()
            code = parse_qs(urlparse(res_url).query)['code']
            forms = self.form["token_params"]
            token_url = forms.pop('req_url')
            forms.update({
                "client_id": self.key_['app_id'],
                "code": code,
                "client_secret": self.key_['secret_key']
            })

            # print(res_url)

            res = requests.get(url=token_url, params=forms)
            if res.status_code == 200:
                print(res.text)
                self.access_token = res.text.split('=')[1]  # res.json()['access_token']
                self.start_t = now_timestamp()

                if not self.last_sess_info:
                    print('res')
                    self.last_sess_info = {}

                with open(self.last_sess_path, 'w') as f:
                    self.last_sess_info.update({
                        self.blog_: {
                            "access_token": self.access_token,
                            "start_t": self.start_t
                        }})
                    json.dump(self.last_sess_info, fp=f)
                print('got access_token at {}'.format(self.start_t))
            else:
                # print(res.text)
                raise Exception(res.text)
        except Exception as e:
            print('authrization error: ', e)


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/documents',
          'https://www.googleapis.com/auth/drive']

article_info = {
    "blog": None,
    "category": None,
    "timestamp": None,
    "title": None,
    "tags": [],
    "images": [],
    "codes": [],
    "task": "",
    "post_url": "",
    "repo": "",
    "content": []
}


def get_google_api_token():
    """
    """
    creds = None
    cwd_ = os.path.dirname(os.path.abspath(__file__))
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = cwd_ + '/../config/token.json'
    credential_path = cwd_ + '/../config/credentials.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cwd_ + '/../config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return creds


def update_docs_gdocs():
    # token 작업
    creds = get_google_api_token()
    service = build('drive', 'v3', credentials=creds)

    file_id = '1sTWaJ_j7PkjzaBWtNc3IzovK5hQf21FbOw9yLeeLPNQ'
    folder_id = '0BwwA4oUTeiV1TGRPeTVjaWRDY1E'
    # Retrieve the existing parents to remove
    file = service.files().get(fileId=file_id,
                                     fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    # Move the file to the new folder
    file = service.files().update(fileId=file_id,
                                        addParents=folder_id,
                                        removeParents=previous_parents,
                                        fields='id, parents').execute()


def get_docs_from_gdrive() -> object:
    """
    """

    # token 작업
    creds = get_google_api_token()

    # google photo api ---
    # 'https://photoslibrary.googleapis.com/v1/albums'
    # service = build('photoslibrary', 'v1', credentials=creds, static_discovery=False)
    # results = service.albums().list().execute() #앨범리스트
    # results = service.mediaItems().list().execute()

    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'test : {0} ({1})'.format(item['name'], item['id']))

    # drive 에서 업데이트된 파일들 retrieve
    response = service.changes().getStartPageToken().execute()
    page_token = response.get('startPageToken')
    # print(page_token)
    while page_token is not None:
        response = service.changes().list(pageToken=page_token,
                                          spaces='drive').execute()
        for change in response.get('changes'):
            # Process change
            print('Change found for file: %s' % change.get('fileId'))
        if 'newStartPageToken' in response:
            # Last page, save this token for the next polling interval
            saved_start_page_token = response.get('newStartPageToken')
        page_token = response.get('nextPageToken')

    # dir_id = '19GkUURxCJWQV-LNZpoCszz4Bgvq_Pdv9'  # 드라이브 내 auto_publish 폴더 id
    publish_id = '1J7SueMXQuEUBPikUJF9hJNPn3yH8kgXq'  # publish 폴더

    response = service.files().list(q="'{}' in parents".format(publish_id),  # "mimeType='image/jpeg'",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken=page_token).execute()
    items = response.get('files', [])
    for item in items:
        print(u'in publish : {0} ({1})'.format(item['name'], item['id']))

    article_list = []  # json양식으로 정리된 발행글들 모음
    for item in items:  # 발행할 글 폴더들
        response = service.files().list(q="'{}' in parents".format(item['id']),  # "mimeType='image/jpeg'",
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()

        # response_img = service.files().list(q="'{}' in parents mimeType='image/jpeg'",
        #                                 spaces='drive',
        #                                 fields='nextPageToken, files(id, name)',
        #                                 pageToken=page_token).execute()

        spliter = re.compile("\|")
        # "[가-힣|a-z|A-Z]+\|[가-힣|a-z|A-Z]+\|[0-9]{2,4}-*[0-9]{1,2}-*[0-9]{1,2}(T[0-9]{2}:[0-9]{2}:[0-9]{2})*\|.*")
        for file in response.get('files', []):  # 하나의 글 폴더 안에서
            file_list = []
            image_list = []
            print('Found a file in the folder: %s (%s)' % (file.get('name'), file.get('id')))
            f_name = file.get('name')

            items = spliter.split(f_name)
            print(items)

            if len(items) == 4:  # 글 파일은 하나여야 함
                # timestamp 처리 ----
                timestamp_ = convert_to_timestamp(items[2])

                article_info.update({
                    "blog": items[0],
                    "category": items[1],
                    "timestamp": timestamp_,
                    "title": items[3]
                })

                file_list.append(file.get('id'))

            else:  # 이미지 파일 (이어야 함)
                # print('ddd :', rst.group())
                # print('Check file name format : ', file.get('name'))
                request = service.files().get_media(fileId=file.get('id'))

                if f_name.lower().endswith(('.jpg', '.gif', '.bmp', '.png')):
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        print("Download %d%%." % int(status.progress() * 100))
                        # from PIL import Image
                        # Image.open(fh)
                        # print(type(fh.getvalue()), type(f_name))
                        # print(bytes(list(fh.getvalue())) == fh.getvalue())
                        image_list.append([f_name, fh.getvalue()])
                elif f_name.lower().endswith(('.mov', '.mp4', '.mp3')):
                    pass

            # google docs 작업----
            # doc 가져와서 내용,이미지 읽음
            service_doc = build('docs', 'v1', credentials=creds, static_discovery=False)

            doc_list = []
            for doc_id in file_list:  # for문 해놨지만 글 파일은 1개여야 함
                doc = service_doc.documents().get(documentId=doc_id).execute()

                if 'inlineObjects' in doc.keys():
                    for v in doc['inlineObjects'].values():
                        img_url = v['inlineObjectProperties']['embeddedObject']['imageProperties']['contentUri']
                        image_list.append(download_img(img_url))  # bytes 저장임

                # doc_list.append(doc)
                doc_lines = doc['body']['content']
                lines_ = []
                img_num = 0
                for idx, line in enumerate(doc_lines):
                    if 'paragraph' in line.keys():
                        if idx == 1:  # 맨 첫줄 태그 떼어내기
                            tags = \
                                [l['textRun']['content'] for l in line['paragraph']['elements'] if
                                 'textRun' in l.keys()][0]
                            tags = [tag.lower() for tag in tags.replace("\n", "").split(',')]


                        else:
                            for l in line['paragraph']['elements']:
                                if 'textRun' in l.keys():  # 텍스트
                                    lines_.append(l['textRun']['content'])
                                elif 'inlineObjectElement' in l.keys():  # 이미지
                                    lines_.append("<br>(img:{})<br>".format(img_num))
                                    img_num += 1
                                    # lines_.extend(l['inlineObjectElement']['inlineObjectId'])

                article_info.update({"content": lines_,
                                     "images": image_list,
                                     "tags": tags})

        article_list.append(('g_docs',article_info))

    return article_list


def get_notion_article_table():
    cwd_ = os.path.dirname(os.path.abspath(__file__))
    with open(cwd_ + '/../config/config.json', 'r') as f:
        token_v2 = json.load(f)['keys']['notion']['token_v2']
    client = NotionClient(token_v2=token_v2)

    # 글쓰기 페이지임
    page = client.get_block("https://www.notion.so/ymmu/ad61d409d6fd47adad133fdd81ba67a8")
    print("The title is:", page.title)
    page.children  # 이거 안 해주면 밑에 block을 못 가져옴.
    # for child in page.children:
    #     print(type(child), child.__dict__)
    #     print(child.id)

    # 글쓰기 페이지에서 글 table
    cv = client.get_block(
        "https://www.notion.so/ymmu/49b8df47b05b4ce4aa7aca477e1640ca?v=f20d702158194ba5b21b24e3e231b88f")

    return cv


def update_doc_notion(rst: object) -> object:
    """ 글이 발행되면 publish -> done 변경 , url 넣기

    :param rst:
    :return:
    """
    # 글쓰기 페이지 > 소재 테이블 가져옴
    cv = get_notion_article_table()
    blog_ = list(rst.keys())[0]
    for search in ["publish", "update"]:
        for row in cv.collection.get_rows(search=search):
            if row.blog == blog_ and row.title == rst[blog_]["title"]:
                if rst[blog_]["status"] == "200":
                    row.status = "done"
                    row.post_url = rst[blog_]['url']
                    log_t = datetime.now().strftime("%Y/%m/%d %H:%M")
                    if search == "publish":
                        row.published = log_t
                    elif search == "update":
                        row.updated = log_t
                else:
                    row.error_msg = rst[blog_]["msg"]
                    row.status = rst[blog_]["status"] + " error"


def get_docs_from_notion():
    # 글쓰기 페이지 > 소재 테이블 가져옴
    cv = get_notion_article_table()

    article_list = []  # 발행할 글들(=publish 처리 된 글들) json 형태로 만들어서 저장
    search_k = ["publish", "update", "test"]
    for s_k in search_k:
        for row in cv.collection.get_rows(search=s_k):
            # print(row.get_all_properties())
            # print(row.__dir__())
            # print(row._str_fields)
            # print(row.timestamp.start, row.timestamp.end, row.timestamp.timezone)
            # print(type(row.timestamp.start), row.timestamp.end, type(row.timestamp.timezone))
            timestamp_ = convert_to_timestamp(row.timestamp)
            article_info = {
                "title": row.title,
                "blog": row.blog,
                "category": row.category,
                "timestamp": timestamp_,
                "tags": [tag.lower() for tag in row.tags],
                "images": [],
                "videos": [],
                "codes": [],
                "task": row.status,
                "post_url": "",
                "repo": "notion",
                "content": []
            }
            if row.status == 'update':
                article_info["post_url"] = re.search(r"https://[a-z]+.tistory.com/[0-9]{1,7}", row.post_url).group()

            for child in row.children:
                # print(child.title, child.space_info, child.__dict__, type(child), child.type, child.__dir__())
                if child.type == 'image':
                    # article_info['images'].append(child.caption)
                    article_info['images'].append(download_img(child.source))  # bytes 저장임
                    article_info["content"].append("\n(img:{})\n".format(len(article_info['images']) - 1))

                elif child.type == 'header':
                    article_info["content"].append('# {}'.format(child.title))

                elif child.type == 'sub_header':
                    article_info["content"].append('## {}'.format(child.title))

                elif child.type == 'sub_sub_header':
                    article_info["content"].append('### {}'.format(child.title))

                elif child.type == 'text':
                    # print(child.title_plaintext, child.__dir__())
                    if re.sub(" +", "", child.title) == "": # 그냥 공백
                        # print('enter')
                        article_info["content"].append('&nbsp;'.format(child.title))
                    else:
                        article_info["content"].append('{} &nbsp;'.format(child.title))

                elif child.type == 'code':
                    # article_info["content"].append('```\n {} \n```'.format(child.title))
                    # print(child.title)
                    article_info['codes'].append(child.title)  # (유튜브링크, 임베디드링크)
                    article_info["content"].append("\n\n(code:{})\n\n".format(len(article_info['codes']) - 1))

                elif child.type == 'bulleted_list' or child.type == 'numbered_list':
                    def attach_list(parent, list_b, sub_num=0):
                        list_b += '    '*sub_num +' - {} \n'.format(parent.title)
                        # print(list_b) 제대로 찍힘
                        sub_num += 1
                        for c in parent.children:
                            list_b = attach_list(c, list_b, sub_num)
                            # article_info["content"].append(markdown.markdown('\t * {}'.format(c.title)))
                            # article_info["content"].append('\n')
                        return list_b

                    list_b = '\n'
                    article_info["content"].append(attach_list(child, list_b))
                # elif child.type == 'numbered_list':  # 블럭에 번호기록 안 함?..답답하구먼.
                #     article_info["content"].append(' * {}'.format(child.title))
                #     article_info["content"].append('\n')
                #     print(child._str_fields(), child.title_plaintext, child._client, type(child), child.type, child.__dir__())

                elif child.type == "quote" or child.type == "callout":
                    article_info["content"].append(' > {}'.format(child.title))
                    article_info["content"].append('\n')

                elif child.type == "divider":
                    article_info["content"].append('---')
                    article_info["content"].append('\n')

                elif child.type == 'video':
                    # print(type(child), child.type, child.__dir__())
                    # print(child.source)
                    print(child.display_source)
                    article_info['videos'].append((child.source, child.display_source))  # (유튜브링크, 임베디드링크)
                    article_info["content"].append("\n(video:{})\n".format(len(article_info['videos']) - 1))

                elif child.type == 'bookmark':
                    article_info["content"].append('{}'.format(child.link))

                else:
                    print(child.child_list_key, child.id, type(child), child.type, child.__dir__())
            # child.title,
            article_list.append(('notion', article_info))

    return article_list


def convert_to_timestamp(time_):
    """ string 형태 시간을 timestamp로 변환.

    :param time_:
    :return:
    """
    print(type(time_))
    timestamp_ = None

    if isinstance(time_, datetime):
        timestamp_ = time_
    elif isinstance(time_, date):  # 시간이 안 들어가있으면 date로 저장이 되네..;
        timestamp_ = datetime.combine(time_, datetime.min.time())
    else:
        # google docs
        re_base = r"[0-9]{2,4}(-|/)*[0-9]{1,2}(-|/)*[0-9]{1,2}"

        if re.match(re_base + "T[0-9]{2}:[0-9]{2}", time_):
            timestamp_ = datetime.strptime(time_, "%y-%m-%dT%H:%M")

        elif re.match(re_base + " *[0-9]{2}:[0-9]{2}", time_):
            timestamp_ = datetime.strptime(time_, "%y/%m/%d %H:%M")

        # notion
        elif re.match(re_base + " *[0-9]{1,2}:*[0-9]{1,2}:*[0-9]{1,2}", time_):  # notion-py에서 시간 전달 형식
            timestamp_ = datetime.strptime(time_, "%y/%m/%d %H:%M")

        elif re.match(re_base + " *[0-9]{1,2}:*[0-9]{1,2} (AM|PM)", time_):  # notion 에서 시간형식
            timestamp_ = datetime.strptime(time_, "%y/%m/%d %m:%M %p")

        elif re.match(r"[0-9]{2,4}(/)*[0-9]{1,2}(/)*[0-9]{1,2}", time_):
            timestamp_ = datetime.strptime(time_, "%y/%m/%d")
            # print(datetime.strptime(items[2], "%y-%m-%d").timetuple())
            # time.struct_time(tm_year=2021,
            # tm_mon=8, tm_mday=11, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=2, tm_yday=223, tm_isdst=-1)
        elif re.match(r"[0-9]{2}(/)*[0-9]{1,2}(/)*[0-9]{1,2}", time_):
            timestamp_ = datetime.strptime(time_, "%y/%m/%d")

        elif re.match(r"[0-9]{2}(-)*[0-9]{1,2}(-)*[0-9]{1,2}", time_):
            timestamp_ = datetime.strptime(time_, "%y/%m/%d")

    if timestamp_ and (timestamp_ - datetime.now()).total_seconds() > 0:  # 예약시간이 현재보다 과거일 때
        # timestamp_ = time.mktime(timestamp_.timetuple())
        # print(datetime.fromtimestamp(timestamp_))
        timestamp_ = timestamp_.timestamp()
    else:
        timestamp_ = None

    return timestamp_


def download_img(img_url: str) -> bytes:
    try:
        return requests.get(img_url).content
        # print(type(img_data)) # bytes
    except Exception as e:
        print('image url download error: {}', img_url)
        return None
