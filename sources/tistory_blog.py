import requests
from post_abstract import Post


class TistoryWrapper(Post):

    def __init__(self, account):
        super(TistoryWrapper, self).__init__()
        self.blog_name = "tistory"
        self.account = account
        self.callback = "http://myohyun.tistory.com"
        self.key_ = self.get_keys()

    def authorize(self):
        """

        :return:
        """
        url = "https://www.tistory.com/oauth/authorize"
        data = {
            "client_id": self.key_['app_id'],
            "redirect_uri": self.callback,
            "response_type": "code"
        }

        try:
            res = requests.get(url=url, params=data)
            if res.status_code == 200:
                print(res.url)
            else:
                #print(res.text)
                raise Exception(res)

        except Exception as e:
            print(e)

    def get_keys(self):
        return super(TistoryWrapper, self).get_keys()['keys'][self.blog_name]

    def wrap_data(self, data_dir=None, **kargs):
        pass

    def submit_post(self, data):
        pass

    def get_posts(self, nums=3, author=None):
        pass

    def validate_params(self, new_data):
        pass

    def update_post(self, new_data, data, **kargs):
        pass


if __name__ == '__main__':

    ts = TistoryWrapper("myohyun")
    ts.authorize()