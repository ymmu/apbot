import glob
import re
import shutil
from abc import *
import os
import json
from pprint import pprint

import docx


class Post(metaclass=ABCMeta):

    blog_ = ""
    account = ""
    dir_path = os.path.dirname(os.path.abspath(__file__))

    def get_data_form(self):
        with open(os.path.join(self.dir_path, './templates', '{}_.json'.format(self.blog_)), 'r') as f:
            return json.load(f)

    def get_keys(self):
        with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
            return json.load(f)['keys'][self.blog_]

    def get_repo(self):
        with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
            return json.load(f)['repo']

    def get_images_path(self, repo):
        imgs_path = []
        types = ('*.jpg', '*.png', '*.gif', '*.bmp')
        for t in types:
            imgs_path.extend(glob.glob(os.path.join(repo, t)))

        return imgs_path

    @staticmethod
    def attach_images(text: str, img_links: list) -> str:
        """ attach image links in the text

        :param text: doc contents
        :param img_links: image url list
        :return:
        """
        # image name = image order for arrangement.
        wrap_ = '<br><center>![{}](https://steemitimages.com/600x0/{})</center><br>'
        for img_info in img_links:
            num = img_info[0].split('.')[0]
            if 'url' in img_info[1].keys():
                wrap_img = wrap_.format(num, img_info[1]['url'])  # image name, image link
                text = text.replace('(img:{})'.format(num), wrap_img)
            else:
                pprint('No image url: ', img_info)

        return text

    def wrap_data(self, local_repo=None, **kargs):
        """wrap raw data following blog's post format.
        - 하나의 문서를 다룸. 로컬문서만 처리

        :param notion_docs:
        :param drive_docs:
        :param local_repo:
        :param kargs:
        :return:
        """
        lines_ =[]
        text_ = [] # [d for d in glob.glob(data_dir+"/*") if d.endswith(('.docx', '.txt', '.pdf'))]
        images_ = []
        videos_ = []

        '''
        1. 로컬레포 처리 (네이버용?)
        2. 구글 드라이브 레포 처리
        3. 노션 레포 처리
        '''
        if local_repo:
            local_repo = os.path.abspath(local_repo)
            # print(glob.glob(data_dir + "/*"))
            for idx, d in enumerate(glob.glob(local_repo + "/*")):

                if d.endswith(('.docx', '.txt', '.pdf')):
                    text_.append(d)
                elif d.lower().endswith(('.bmp', '.png', '.jpg', '.gif')):
                    # print(d)
                    img_name = os.path.basename(d).split('.')
                    img_n = ''.join(img_name[:-1])
                    num_ = re.compile('[0-9]+').findall(img_n)[-1] # 마지막숫자로
                    d_foramt_ = img_name[-1]

                    # print(d_foramt_)
                    new_ = num_ + "." + d_foramt_
                    if img_n != new_:
                        # 이미지 이름 숫자로 바꿈.
                        # 이미지는 글에 순서대로 넣어줘야 하기 때문에 번호가 붙어있음 (그러나 숫자만 들어가 있지 않을 때가 있음.)
                        # 폴더 안에서 이미지는 순서대로 나열되어 있음.
                        new_d = os.path.join(local_repo, new_)
                        # print(new_d)
                        os.rename(d, new_d) # 이미지 이름 1부터 시작하게
                    with open(new_d, 'rb') as f:
                        data = f.read()
                    images_.append((num_, data)) # (이미지 번호, 이미지 bytes 데이터) 새 이미지 이름 넣어줌
                else:
                    videos_.append(d)

            if len(text_) > 1:
                raise Exception('too many text file: {}'.format(','.join(text_)))
            elif len(text_) == 0:
                raise Exception('No text file')

            print('title: ', text_[0])
            if text_[0].endswith('docx'):
                doc = docx.Document(text_[0])
                for docpara in doc.paragraphs:
                    # print(docpara._p.xml) # 아..문서가 xml로 이루어져있는건가..하
                    # print(docpara._p.xpath("./w:hyperlink//w:r//w:t/text()")) # 문단 안에 하이퍼링크 있으면
                    hlink = docpara._p.xpath("./w:hyperlink//w:r//w:t/text()") # 하이퍼링크넣어줌. 그냥 text로 넣으면 안 들어감.
                    lines_.append(str(docpara.text)+'\n')
                    if hlink:
                        # print(str(docpara.text))
                        lines_.append(','.join(hlink)+'\n')

            else:
                with open(text_[0], 'r', encoding='utf8') as f:
                    lines = f.readlines()

        # print('lines: ', lines)
        # print('images: ', images_)
        # print('videos: ', videos_)
        return lines_, images_, videos_

    @abstractmethod
    def create_post(self, data):
        pass

    @abstractmethod
    def get_posts(self, nums=3, author=None):
        """get post list.

        :param nums:
        :param author:
        :return:
        """
        pass

    @abstractmethod
    def get_post(self, post_id):
        """get a post

        :return:
        """
        pass

    @abstractmethod
    def validate_params(self, new_data):
        pass

    @abstractmethod
    def update_post(self, new_data, data, **kargs):
        pass

    @abstractmethod
    def upload_images(self, images, **kargs):
        pass

