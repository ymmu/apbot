import glob
import re
import traceback
from abc import *
import os
import json
import docx
from src_ import utils_, vars_
from pprint import pprint


class Post(metaclass=ABCMeta):

    blog_ = ""
    account = ""
    dir_path = os.path.dirname(os.path.abspath(__file__))

    def get_account(self, blog_):
        with open(os.path.join(self.dir_path, vars_.ids), 'r', encoding='utf-8') as f:
            return json.load(f)[blog_]  # {account}.tistory.com

    def get_data_form(self):
        with open(os.path.join(self.dir_path, './templates', '{}_.json'.format(self.blog_)), 'r') as f:
            return json.load(f)

    def get_keys(self, db_pass=None):
        # config_ = utils_.get_config(password=db_pass)
        return vars_.conf['keys'][self.blog_]

    def get_keys_old(self):
        pass
        # with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r', encoding='utf-8') as f:
        #     return json.load(f)['keys'][self.blog_]

    def get_repo(self):
        return None
        # with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
        #     return json.load(f)['repo']

    def get_images_path(self, repo):
        imgs_path = []
        types = ('*.jpg', '*.png', '*.gif', '*.bmp')
        for t in types:
            imgs_path.extend(glob.glob(os.path.join(repo, t)))

        return imgs_path

    @staticmethod
    def attach_images(blog_: str, text: str, img_links: list) -> str:
        """ attach image links in the text

        :param blog_: 블로그 종류
        :param text: doc contents
        :param img_links: image url list
        :return:
        """
        # image name = image order for arrangement.
        if blog_ == "steemit":
            wrap_ = '<br><center>![{}](https://steemitimages.com/600x0/{})</center><br>'
        elif blog_ == "tistory":
            wrap_ = '{}'
        # print(type(img_links[0]))
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
            print(local_repo)
            repo_data = glob.glob(local_repo + r"\*")
            while len(repo_data) == 1 and os.path.isdir(repo_data[0]):  # 안에 또 디렉토리로 들어가 있으면
                repo_data = glob.glob(repo_data[0] + r"\*")

            for idx, d in enumerate(repo_data):

                if d.endswith(('.docx', '.txt', '.pdf')):

                    text_.append(d)
                elif d.lower().endswith(('.bmp', '.png', '.jpg', '.gif')):
                    # print(d)
                    img_name = os.path.basename(d).split('.')
                    img_n = ''.join(img_name[:-1])
                    try:
                        num_ = re.compile('[0-9]+').findall(img_n)[-1] # 마지막숫자로
                    except Exception as e:
                        traceback.print_exc()
                        print(f'Exception when changing image name (Maybe no numbers in the name?): {img_name}')
                        num_ = img_name[0]

                    d_foramt_ = img_name[-1]

                    # print(d_foramt_)
                    new_ = num_ + "." + d_foramt_
                    new_d = os.path.join(local_repo, new_)
                    # print(new_d)
                    if img_n != new_:
                        # 이미지 이름 숫자로 바꿈.
                        # 이미지는 글에 순서대로 넣어줘야 하기 때문에 번호가 붙어있음 (그러나 숫자만 들어가 있지 않을 때가 있음.)
                        # 폴더 안에서 이미지는 순서대로 나열되어 있음.
                        os.rename(d, new_d)  # 이미지 이름 1부터 시작하게
                    with open(new_d, 'rb') as f:
                        data = f.read()
                    images_.append((num_, data)) # (이미지 번호, 이미지 bytes 데이터) 새 이미지 이름 넣어줌
                else:  # 동영상
                    videos_.append(d)

            if len(text_) > 1:
                raise Exception('too many text file: {}'.format(','.join(text_)))
            elif len(text_) == 0:
                raise Exception('No text file')

            print('text path: ', text_[0])
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


            # # docx파일 ->txt로 변환. 다른방법. 이거..변환하면 \n이 줄마다 들어감..;
            # if text_[0].endswith('docx'):
            #     import docx2txt
            #     # Passing docx file to process function
            #     text = docx2txt.process(text_[0])
            #     # Saving content inside docx file into output.txt file
            #     f_new_path = os.path.splitext(text_[0])[0] + ".txt"
            #     with open(f_new_path, "w", encoding='utf-8') as text_file:
            #         print(text, file=text_file)
            #     # txt 파일로 재지정
            #     text_[0] = f_new_path

            else:
                with open(text_[0], 'r', encoding='utf8') as f:
                    lines_ = f.readlines()

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
