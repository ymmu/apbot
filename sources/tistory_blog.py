import json
import os.path
import re
import sys
from copy import copy
from pprint import pprint

import gh_md_to_html
import requests
from urllib.parse import urlparse, parse_qs
from sources.post_abstract import Post
from datetime import datetime
from selenium import webdriver
import bs4
from time import sleep

from sources import utils_, post_abstract
import markdown


class TistoryWrapper(Post):

    def __init__(self, db_pass):
        super(TistoryWrapper, self).__init__()
        self.blog_ = "tistory"
        self.form = self.get_data_form()
        self.repo = self.get_repo()
        self.account = self.get_account(self.blog_)
        self.key_ = self.get_keys(db_pass)[self.account]
        self.sess_ = Tistory_session(self.form['outh'], self.key_, self.account, self.blog_)

    def get_data_form(self):
        return super(TistoryWrapper, self).get_data_form()

    def get_keys(self, db_pass):
        return super(TistoryWrapper, self).get_keys(db_pass)

    def get_repo(self):
        return super().get_repo()

    @staticmethod
    def attach_images(text: str, img_links: list, type: str = "replacer") -> str:
        """ attach image links in the text

        :param blog_:
        :param text:
        :param img_links:
        :return:
        """
        # return Post.attach_images(blog_, text, img_links)
        for img_info in img_links:
            num = img_info[0].split('.')[0]
            if type == 'replacer' and type in img_info[1].keys():
                text = text.replace('(img:{})'.format(num), img_info[1]['replacer'])
            if type == 'url' and type in img_info[1].keys():
                wrap_ = '<center><img src="{}" alt="0" /></center>'.format(img_info[1]['url'])
                text = text.replace('(img:{})'.format(num), wrap_)
            else:
                print('No image replacer or url: ', img_info)

        return text

    def wrap_data(self, doc: object = None, local_repo=None, **kargs):
        """ html데이터로 포장하기. 왜냐하면 코드같은 것도 넣어야 하기 때문에. 템플릿 적용해야

        :param doc:
        :param local_repo:
        :param kargs:
        :return:
        """
        # json
        # article_ = super(TistoryWrapper, self).wrap_data(drive_docs=drive_docs, local_repo=local_repo)
        # pprint(doc)
        doc['tag'] = ','.join(doc.pop('tags'))
        doc["category"] = self.get_category_info(doc['category'])
        doc['published'] = doc.pop('timestamp')
        if doc['published']:
            doc['visibility'] = '2'

        # md -> html로 변경
        for idx, t in enumerate(doc["content"]):
            t = re.sub("<space>", '&nbsp;', t)
            doc["content"][idx] = markdown.markdown(t)

        doc["content"] = ''.join(doc["content"])

        # print(gh_md_to_html.markdown_to_html_via_github_api(doc["content"]))
        # print(doc["content"])
        # 뭐래? 코드로 찍히는구만 -_-
        # output = markdown.markdown("``` def function(): pass ```\n")
        # print(markdown.markdown('* item 1 \n \t* sitem 1\n\t* sitem 2\n')) # '*하고 한칸 띄어야 함'
        # print(output)

        # 티스토리 서버에 이미지 전송하고 이미지 url 받아오기
        image_links = self.upload_images(doc["images"])

        # 본문에 md 형식으로 이미지 삽입
        doc["content"] = self.attach_images(doc['content'], image_links)
        # doc["content"] += image_links[0][1]['replacer']

        # print(doc["content"])

        # 기타 html 수정..inline 코드 때문에 codeblock 메서드보다 앞에
        doc["content"] = self.edjust_html(doc["content"])

        # 광고 코드 넣기
        doc["content"] = self.attach_ad(doc["content"])

        # 코드블럭 수정. 이거..왜 'pre'가 안 붙지?
        doc["content"] = self.attach_codeblock(doc["content"], doc["codes"])

        # 유튜브 비디오 넣기
        doc["content"] = self.attach_youtube(doc["content"], doc["videos"])

        # print(doc["content"])
        '''
            "write": {
              "req_url": "https://www.tistory.com/apis/post/write",
              "access_token": "",
              "output": "json",
              "blogName": "",
              "title": "",
              "content": "",
              "visibility": "0",
              "category": "",
              "published": "",
              "slogan": "",
              "tag": "", 쉼표로 구분
              "acceptComment": "",
              "password": null
            }
        '''
        return doc

    def attach_codeblock(self, text: str, codes: list) -> str:
        """ attach image links in the text

        :param text: doc contents
        :param img_links: image url list
        :return:
        """
        # image name = image order for arrangement.
        wrap_ = """<pre class="codeblock" data-ke-language="{}"><code>\n{}\n\n</code></pre>"""
        # print(type(img_links[0]))
        for idx, code in enumerate(codes):
            wrap_code = wrap_.format(code[0],code[1])  # image name, image link
            text = text.replace('(code:{})'.format(idx), '\n'+wrap_code+'\n')

        return text

    def attach_codeblock_old(self, content: str) -> str:
        content = re.sub("<code>", "<pre><code>", content)
        content = re.sub("</code>", "</code></pre>", content)
        return content

    def edjust_html(self, content: str) -> str:
        """기타 html 수정..

        :param content:
        :return:
        """
        # 은근히 마음에 들게 처리할려면 뭐가 많아지네..
        # 인용구 스타일
        content = re.sub("<blockquote>", '<blockquote data-ke-style="style2">', content)

        # inline 코드블럭 수정. codeblock 메서드보다 먼저 작업되야 함
        content = re.sub("<code>", '<span style="color: #ee2323;"><code><b>', content)
        content = re.sub("</code>", '</b></code></span>', content)

        # 글씨배경 색상 정해져있음
        content = re.sub("<bgc>", '<span style="background-color: #c1bef9;">', content)
        content = re.sub("</bgc>", '</span>', content)

        content = re.sub("<c>", '<span style="color: #ee2323;">', content)
        content = re.sub("</c>", '</span>', content)

        content = re.sub("<bgcc1>", '<span style="background-color: #dddddd; color: #ee2323;">', content)
        content = re.sub("</bgcc1>", '</span>', content)

        content = re.sub("<hr />", '<hr contenteditable="false" data-ke-type="horizontalRule" data-ke-style="style6" />', content)
        #

        return content

    def attach_ad(self, content: str) -> str:
        with open(os.path.join(self.dir_path, 'templates/tistory_ad_script.json'), 'r', encoding='utf-8') as f:
            ad_codes = json.load(f)['tistory']

        # pprint(ad_codes)
        # print(type(content))
        # print(ad_codes["중간광고1"])
        content = re.sub("(중간광고1)+", ad_codes["middle_1"], content)

        return content

    def attach_youtube(self, content: str, video_links: list) -> str:
        # ut_ = re.compile("https://www.youtube.com/embed/(.*)\?feature=oembed")
        # ut_.match(content)
        # content = re.sub("https://www.youtube.com/embed/(.*)\?feature=oembed", iframe , content)
        iframe = '<p align="middle"><iframe width="560" height="315" src="{}" title="YouTube video player" frameborder="0" ' \
                 'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; ' \
                 'picture-in-picture" allowfullscreen></iframe></p>'
        for idx, video in enumerate(video_links):
            display_source = video[1]  # 0: 일반 링크, 1: iframe용 임베디드 링크
            ut_ = iframe.format(display_source.split('?')[0])
            content = content.replace("(video:{})".format(idx), ut_)
        return content

    def create_post(self, data):

        data = self.wrap_data(data)
        # data.pop("images")
        # print('data: ')
        # pprint(data)
        form = copy(self.form['post']['write'])
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account,
                     **{k: data[k] for k in data.keys() & form.keys()}})
        pprint(form)
        try:
            # pass
            res = requests.post(req_url, data=form)  # data field에 form을 넣어야 함 (414 코드 관련)
            if res.status_code == 200:
                return res.json()
            else:
                # print(res.text)
                print(res.json())
                raise Exception(res)
        except Exception as e:
            print(e)

    def get_posts(self, page=None, author=None):
        """ get post list of the specific author.
            must put author of url {author}.tistory.com

        :param page:
        :param author:
        :return:
        """
        if not author:
            author = self.account
        form = copy(self.form['post']['list'])
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
            form = copy(self.form['post']['read'])
            req_url = form.pop('req_url')
            form.update({"access_token": self.sess_.get_token(), "postId": post_id, "blogName": self.account})
            try:
                res = requests.get(req_url, params=form)
                if res.status_code == 200:
                    # print(res.text)
                    return res.json()
                else:
                    raise Exception(res)
            except Exception as e:
                print(e)

    def validate_params(self, new_data):
        pass

    def update_post(self, new_data, **kargs):

        form = copy(self.form['post']['modify'])
        new_data["postId"] = new_data.pop("post_url").split("/")[-1]  # 수정할 포스트번호
        form.update((k, new_data[k]) for k in new_data.keys() & form.keys())
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account})
        pprint(form)

        try:
            res = requests.post(req_url, data=form)
            if res.status_code == 200:
                # print(res.text)
                return res.json()
            else:
                raise Exception(res)
        except Exception as e:
            print(e)

    def upload_images(self, imgs: list, repo=None, **kargs) -> list:
        img_links = []
        form = copy(self.form['attach'])
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account})
        # pprint(form)
        url = form.pop('req_url')

        for idx, img in enumerate(imgs):
            img_name = str(idx)
            content = {"uploadedfile": img}
            # print(type(img))

            try:
                res = requests.post(url, params=form, files=content)
                if res.status_code == 200:
                    pprint(res.json())
                    '''
                    {
                      "tistory":{
                        "status":"200",
                        "url":"http://cfile6.uf.tistory.com/image/1328CE504DB79F5932B13F",
                        "replacer":"%5b%23%23_1N%7ccfile6.uf%401328CE504DB79F5932B13F%7cwidth%3d\"500\"+height%3d\"300\"%7c_%23%23%5d"
                      }
                    }
                    '''
                    img_links.append((img_name, res.json()['tistory']))
                else:
                    pprint(res.json())
                    img_links.append((img_name, None))
            except Exception as e:
                print('upload_images error : ', e)

        return img_links

    def get_categories(self):
        form = copy(self.form['category'])
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account})
        try:
            res = requests.get(req_url, params=form)
            if res.status_code == 200:
                return res.json()
            else:
                print('get_cate func')
                raise Exception(res)
        except Exception as e:
            print(e)

    def get_category_info(self, search: str) -> tuple:
        with open(os.path.join(self.dir_path, './templates/categories.json'), 'r', encoding='utf-8') as f:
            cate = json.load(f)['tistory']

        lower_k = [k.lower() for k in cate.keys()]
        default_ = 'jungle_life'

        # if not search:
        #     print('category값 없음.')
        #     return (default_, cate[default_])

        search = search.lower()

        for k, v in cate.items():
            if search == k or search == v:
                return (k, v)
            else:
                print('유사단어 찾기 구현 안 됨.  default 값: Jungle_Life \n')
                return (default_, cate[default_])  # 카테고리 이름, 번호

    def update_categories(self):
        """카테고리 이름:번호 업데이트 후 json 저장

        :return:
        """
        categories = self.get_categories()
        # pprint(categories)
        categories = categories['tistory']['item']['categories']
        cate_dict = {}
        for cate in categories:
            cate_dict[cate['name'].lower()] = cate['id']

        with open(self.dir_path + '/templates/categories.json', 'w', encoding='utf-8') as f:
            cate_info = {
                "tistory": cate_dict
            }
            json.dump(cate_info, fp=f, ensure_ascii=False)

        print('tistory categories were updated.')


class Tistory_session(utils_.Session):
    def __init__(self, form, key_, account, blog_):
        super(Tistory_session, self).__init__(form, key_, account, blog_)
