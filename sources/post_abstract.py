import glob
from abc import *
import os
import json
from pprint import pprint


class Post(metaclass=ABCMeta):

    blog_ = ""
    account = ""
    dir_path = "."

    def get_data_form(self):
        with open(os.path.join(self.dir_path, './templates', '{}_.json'.format(self.blog_)), 'r') as f:
            return json.load(f)

    def get_keys(self):
        with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
            return json.load(f)['keys']

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
    def attach_images(text, img_links):
        """ attach image links in the text

        :param text:
        :param img_links:
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

    @abstractmethod
    def wrap_data(self, data_dir=None, **kargs):
        """wrap raw data following blog's post format

        :param data_dir:
        :param kargs:
        :return:
        """
        pass

    @abstractmethod
    def submit_post(self, data):
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

