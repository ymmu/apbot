from abc import *
import os
import json


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
    def upload_images(self, new_data, data, **kargs):
        pass

