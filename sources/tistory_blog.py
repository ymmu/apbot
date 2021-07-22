import json
import os.path
import sys
from pprint import pprint

import requests
from urllib.parse import urlparse, parse_qs
from post_abstract import Post
from datetime import datetime
from selenium import webdriver
import bs4
from time import sleep

from sources import utils_


class TistoryWrapper(Post):

    def __init__(self, account):
        super(TistoryWrapper, self).__init__()
        self.blog_ = "tistory"
        self.account = account  # {account}.tistory.com
        self.key_ = self.get_keys()
        self.form = self.get_data_form()
        self.sess_ = Tistory_session(self.form['outh'], self.key_)

    def get_data_form(self):
        return super(TistoryWrapper, self).get_data_form()

    def get_keys(self):
        return super(TistoryWrapper, self).get_keys()[self.blog_]

    def wrap_data(self, data_dir=None, **kargs):
        pass

    def submit_post(self, data):
        form = self.form['post']['read']
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token()})
        try:
            res = requests.post(req_url, params=form)
            if res.status_code == 200:
                return res.json()
            else:
                raise Exception(res)
        except Exception as e:
            print(e)

    def get_posts(self, page=None, author=None):
        if author == None:
            author = self.account
        form = self.form['post']['list']
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": author})

        try:
            res = requests.get(req_url, params=form)
            if res.status_code == 200:
                print(res.text)
                return res.json()
            else:
                print('request exception.')
                raise Exception(res)
        except Exception as e:
            print(e)

    def get_post(self, post_id):
        if not post_id:
            return {"error": 'No post_id.'}
        else:
            form = self.form['post']['read']
            req_url = form.pop('req_url')
            form.update({"access_token": self.sess_.get_token(), "postId": post_id})
            try:
                res = requests.get(req_url, params=form)
                if res.status_code == 200:
                   #print(res.text)
                    return res.json()
                else:
                    raise Exception(res)
            except Exception as e:
                print(e)

    def validate_params(self, new_data):
        pass

    def update_post(self, new_data, data, **kargs):
        pass


class Tistory_session:

    def __init__(self, form, key_):
        self.form = form
        self.key_ = key_
        self.access_token = None
        self.start_t = None
        self.last_sess_path = './tmp_sess.json'

        # check the last access token is valid
        # if not, get new one and save it to temp json
        if os.path.isfile(self.last_sess_path):
            with open(self.last_sess_path,'r') as f:
                last_sess_info = json.load(f)
            sess_last_start = datetime.strptime(last_sess_info["start_t"], "%Y-%m-%dT%H:%M:%S%z")
            if self.is_expired(sess_last_start):
                self.authorize()
            else:
                print('got last session token.')
                self.access_token = last_sess_info["access_token"]
                self.start_t = last_sess_info["start_t"]
        else:
            self.authorize()

    def get_token(self):
        return self.access_token

    def is_expired(self, sess_last_start=None):
        if not sess_last_start:
            sess_last_start = self.start_t
        t_diff = utils_.get_timestamp(str_=False) - sess_last_start
        if t_diff.total_seconds() / 60 >= 60:
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
                self.access_token = res.text.split('=')[1] # res.json()['access_token']
                self.start_t = utils_.get_timestamp()

                with open(self.last_sess_path, 'w') as f:
                    json.dump({"access_token":self.access_token,"start_t":self.start_t}, fp=f)
                print('got access_token at {}'.format(self.start_t))
            else:
                # print(res.text)
                raise Exception(res.text)
        except Exception as e:
            print('authrization error: ', e)


if __name__ == '__main__':
    ts = TistoryWrapper("myohyun")

    # ok
    # print("\n\nget_post test")
    # res = ts.get_post(post_id="103")
    # pprint(res)

    # ok
    # print("\n\nget_posts test")
    # res = ts.get_posts(page=1)
    # pprint(res)

