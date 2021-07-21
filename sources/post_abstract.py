from abc import *
import os
import json


class Post(metaclass=ABCMeta):

    blog_name = ""
    account = ""
    dir_path = "."

    def get_keys(self):
        with open(os.path.join(self.dir_path, '../config', 'config.json'), 'r') as f:
            return json.load(f)

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
        pass

    @abstractmethod
    def validate_params(self, new_data):
        pass

    @abstractmethod
    def update_post(self, new_data, data, **kargs):
        pass