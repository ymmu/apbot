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

    def __init__(self, account):
        super(TistoryWrapper, self).__init__()
        self.blog_ = "tistory"
        self.account = account  # {account}.tistory.com
        self.key_ = self.get_keys()
        self.form = self.get_data_form()
        self.repo = self.get_repo()
        self.sess_ = Tistory_session(self.form['outh'], self.key_, account, self.blog_)

    def get_data_form(self):
        return super(TistoryWrapper, self).get_data_form()

    def get_keys(self):
        return super(TistoryWrapper, self).get_keys()

    def get_repo(self):
        return super().get_repo()

    @staticmethod
    def attach_images(text: str, img_links: list) -> str:
        """ attach image links in the text

        :param text:
        :param img_links:
        :return:
        """
        return Post.attach_images(text, img_links)

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
        doc["content"] = ''.join(doc["content"])

        # print(gh_md_to_html.markdown_to_html_via_github_api(doc["content"]))
        # print(doc["content"])
        # 뭐래? 코드로 찍히는구만 -_-
        # output = markdown.markdown("``` def function(): pass ```\n")
        print(markdown.markdown('* item 1 \n \t* sitem 1\n\t* sitem 2\n')) # '*하고 한칸 띄어야 함'
        # print(output)

        # 티스토리 서버에 이미지 전송하고 이미지 url 받아오기
        # image_links = self.upload_images(doc["images"])

        # test 용 이미지 -----
        image_links = [
            ('0',{'replacer': '[##_Image|kage@cbRpEb/btrb8gqjqLj/43ZOeGTRTNqTYASMSyn0a1/img.png|alignCenter|width="1600" '
                         'height="779" data-origin-width="1600" '
                         'data-origin-height="779" '
                         'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                         'filemime="image/png"|||_##]',
             'status': '200',
             'url': 'https://blog.kakaocdn.net/dn/cbRpEb/btrb8gqjqLj/43ZOeGTRTNqTYASMSyn0a1/img.png'})
            ,
            ('1',{'replacer': '[##_Image|kage@rGI4R/btrb2bYlRlG/aXCmrP7wn16klCSrbx6lRk/img.png|alignCenter|width="1600" '
                                     'height="837" data-origin-width="1600" '
                                     'data-origin-height="837" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                                     'filemime="image/png"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/rGI4R/btrb2bYlRlG/aXCmrP7wn16klCSrbx6lRk/img.png'})
            ,
            ('2',{'replacer': '[##_Image|kage@bv2g6s/btrb8hQhQSj/3iLf3mFDriqeiDPrM6k2W0/img.png|alignCenter|width="1600" '
                                     'height="777" data-origin-width="1600" '
                                     'data-origin-height="777" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                                     'filemime="image/png"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/bv2g6s/btrb8hQhQSj/3iLf3mFDriqeiDPrM6k2W0/img.png'})
            ,
            ('3',{'replacer': '[##_Image|kage@R0ns1/btrb5opnDhd/nqsDMQBloDEAkTNx3LJzxk/img.png|alignCenter|width="1600" '
                                     'height="775" data-origin-width="1600" '
                                     'data-origin-height="775" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                                     'filemime="image/png"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/R0ns1/btrb5opnDhd/nqsDMQBloDEAkTNx3LJzxk/img.png'})
            ,
            ('4',{'replacer': '[##_Image|kage@pDKSZ/btrb23MvsjD/4fWcAapnh5aPthqTDBK8Sk/img.png|alignCenter|width="1600" '
                                     'height="623" data-origin-width="1600" '
                                     'data-origin-height="623" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                                     'filemime="image/png"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/pDKSZ/btrb23MvsjD/4fWcAapnh5aPthqTDBK8Sk/img.png'})
            ,
            ('5',{'replacer': '[##_Image|kage@oYGrC/btrb5nDZSOw/m8v1UhzwU2J7o6T28fkJp0/img.jpg|alignCenter|width="591" '
                                     'height="1280" data-origin-width="591" '
                                     'data-origin-height="1280" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.jpg" '
                                     'filemime="image/jpeg"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/oYGrC/btrb5nDZSOw/m8v1UhzwU2J7o6T28fkJp0/img.jpg'})
            ,
            ('6',{'replacer': '[##_Image|kage@cjWGft/btrb24q7Q2n/QuUk74CjC67Of14rjk9ITk/img.png|alignCenter|width="1555" '
                                     'height="943" data-origin-width="1555" '
                                     'data-origin-height="943" '
                                     'data-ke-mobilestyle="widthOrigin" filename="img.png" '
                                     'filemime="image/png"|||_##]',
                         'status': '200',
                         'url': 'https://blog.kakaocdn.net/dn/cjWGft/btrb24q7Q2n/QuUk74CjC67Of14rjk9ITk/img.png'})]

        # 본문에 md 형식으로 이미지 삽입
        doc["content"] = self.attach_images(doc['content'], image_links)

        # md -> html로 변경
        doc["content"] = markdown.markdown(doc["content"])
        print(doc["content"])

        # 광고 코드 넣기
        doc["content"] = self.attach_ad(doc["content"])

        # 코드블럭 수정. 이거..왜 'pre'가 안 붙지?
        doc["content"] = self.attach_codeblock(doc["content"])

        # 유튜브 비디오 넣기
        doc["content"] = self.attach_youtube(doc["content"], doc["videos"])

        # pprint(doc)
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

    def attach_codeblock(self, content: str) -> str:
        content = re.sub("<code>", "<pre><code>", content)
        content = re.sub("</code>", "</code></pre>", content)
        return content

    def attach_ad(self, content: str) -> str:
        with open(os.path.join(self.dir_path, 'templates/tistory_ad_script.json'), 'r', encoding='utf-8')as f:
            ad_codes = json.load(f)

        # pprint(ad_codes)
        # print(type(content))
        # print(ad_codes["중간광고1"])
        content = re.sub("(중간광고1)+", ad_codes["중간광고1"], content)

        return content

    def attach_youtube(self, content: str, video_links: list) -> str:
        # ut_ = re.compile("https://www.youtube.com/embed/(.*)\?feature=oembed")
        # ut_.match(content)
        # content = re.sub("https://www.youtube.com/embed/(.*)\?feature=oembed", iframe , content)
        iframe = '<iframe width="560" height="315" src="{}" title="YouTube video player" frameborder="0" ' \
                 'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; ' \
                 'picture-in-picture" allowfullscreen></iframe> '
        for idx, video in enumerate(video_links):
            display_source = video[1]  # 0: 일반 링크, 1: iframe용 임베디드 링크
            ut_ = iframe.format(display_source.split('?')[0])
            return content.replace("(video:{})".format(idx), ut_)

    def create_post(self, data):

        data = self.wrap_data(data)
        data.pop("images")
        form = self.form['post']['write']
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account, **data})
        pprint(form)
        try:
            res = requests.post(req_url, data=form) # data field에 form을 넣어야 함 (414 코드 관련)
            if res.status_code == 200:
                return res.json()
            else:
                print(res.text)
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
            form.update({"access_token": self.sess_.get_token(), "postId": post_id, "blogName":self.account})
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

    def update_post(self, new_data, **kargs):

        form = self.form['post']['modify']
        form.update((k, new_data[k]) for k in new_data.keys() & form.keys())
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName":self.account})
        pprint(form)

        try:
            res = requests.post(req_url, data=form)
            if res.status_code == 200:
               #print(res.text)
                return res.json()
            else:
                raise Exception(res)
        except Exception as e:
            print(e)

    def upload_images(self, imgs: list, repo=None, **kargs) -> list:
        img_links = []
        form = self.form['attach']
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account})
        pprint(self.form['attach'])
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
        form = self.form['category']
        req_url = form.pop('req_url')
        form.update({"access_token": self.sess_.get_token(), "blogName": self.account})
        try:
            res = requests.get(req_url, params=form)
            if res.status_code == 200:
                # print(res.text)
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
        search = search.lower()
        default_ = 'jungle_life'

        for k, v in cate.items():
            if search == k or search == v:
                return (k, v)
            else:
                print('유사단어 찾기 구현 안 됨.  default 값: Jungle_Life \n')
                return (default_, cate[default_])  # 카테고리 이름, 번호


class Tistory_session(utils_.Session):
    def __init__(self, form, key_, account, blog_):
        super(Tistory_session, self).__init__(form, key_, account, blog_)


if __name__ == '__main__':
    ts = TistoryWrapper("myohyun")

    # ok
    # print("\n\n 1. get_category test")
    # categories = ts.get_categories()
    # pprint(categories)
    # categories = categories['tistory']['item']['categories']
    # cate_dict ={}
    # for cate in categories:
    #     cate_dict[cate['name'].lower()] = cate['id']
    #
    # with open('./templates/categories.json', 'w', encoding='utf-8') as f:
    #     cate_info = {
    #         "tistory": cate_dict
    #     }
    #     json.dump(cate_info, fp=f, ensure_ascii=False)

    # ok
    # print("\n\n 2. get_posts test")
    # res = ts.get_posts(page=1)
    # pprint(res)

    # ok
    # print("\n\n 3. get_post test")
    # res = ts.get_post(post_id="212")
    # pprint(res)


    # ok
    # print("\n\n 4. update_post test")
    # res = res['tistory']['item']
    # new_res = copy(res)
    # new_res['title'] = res['title'] + ' .. 수정'
    # new_res['category'] = ts.get_category_info(new_res['categoryId'])[0] # 카테고리명
    #
    # # 리스트 하위 리스트 잘 찍히는지 확인
    # new_res['content'] = new_res['content'] + '\n\n' + '<ul>\n' + '<li><strong>markdown</strong> </li>\n' +'</ul>\n' \
    #                         +'<ul>\n' \
    #                         +'<li>프로젝트에 이 패키지를 이용. string으로 적은 마크다운을 html로 바로 바꾸어 줌.</li>\n' \
    #                         +'</ul>\n' \
    #                         +'<ul>\n' \
    #                         +'<li>코딩시에 마크다운 변환은 [<strong><a '\
    #                         +'href="https://www.digitalocean.com/community/tutorials/how-to-use-python-markdown-to-convert-markdown-text-to-html">여기</a></strong> ' \
    #                         +'<strong>]</strong>에 예제가 잘 나와있다. </li>\n' \
    #                         +'</ul>\n'\
    #                         +'<ul>\n'\
    #                         +'<li>어떤 경우에 마크다운 변환이 제대로 안 되는 경우도 있었다. code 변환 경우가 그랬음. '\
    #                         +'멀티라인("""사용)예제 그대로 넣었는데 코드로 변환했다는...음;</li>\n'\
    #                         +'</ul>\n'\
    #                         +'<ul>\n'
    # pprint(ts.update_post(new_res))



