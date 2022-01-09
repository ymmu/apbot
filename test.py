from pprint import pprint
from unittest import TestCase, main
import os

from sources.naver_blog import NaverWrapper
from sources.steem_blog import SteemWrapper
from sources.tistory_blog import TistoryWrapper


def test_naver(db_pass):
    nw = NaverWrapper(db_pass)
    # test_repo = r'C:\Users\myohy\OneDrive\문서\auto_publish'
    # p_file = os.path.join(test_repo, "publish_list.txt")
    # import pandas as pd
    # published_list = pd.read_csv(p_file,
    #                              sep='\t',
    #                              infer_datetime_format=True,
    #                              parse_dates=True)
    # # published_list['account'] = 'myohyun'
    # published_list = published_list[['account', 'filename', 'p_date', 'done', 'update']]
    # print(published_list)
    # # published_list.to_csv(p_file, sep='\t', index=False, encoding='utf-8')

    # # print(published_list.tail())
    # print(published_list.query("account=='myohyun'"))

    # p_list = published_list.query('done.isnull()')
    # print(p_list)
    # # p_list = published_list.query('filename == "{}"'.format('테스트'))
    # p_list.__setitem__('done', 'ok')
    #
    # print(p_list[['filename', 'p_date']].values)
    # published_list.update(p_list)
    # print(published_list)
    # published_list.to_csv(p_file, sep='\t', index=False, encoding='utf-8')

    for account in ['myohyun']:
        nw.smarteditor_one(account=account)

    # nw.smarteditor_one(test_repo=test_repo, published="21/08/24 06:00")
    # nw.smarteditor_one(test_repo=test_repo)C:\Users\myohy\OneDrive\문서\auto_publish\0819 청담점_청담피부관리\1.JPG

    # 폴더 삭제 테스트 ----
    # work_f = [l for l in os.listdir(test_repo) if l != 'done']
    # shutil.rmtree(test_repo+r'\샤론파스_1')

    # 폴더 이동 테스트 ----
    # for l in work_f:
    #     shutil.move(test_repo+r'\{}'.format(l), test_repo+r'\{}'.format('done'))

    # 압축해제 테스트 ----
    # zip_list = glob.glob(os.path.join(test_repo, "*.zip"))
    # for zip_p in zip_list:
    #     print(zip_p)
    #     zip_ = zipfile.ZipFile(zip_p)
    #     # print(zip_.infolist())
    #     folder_p = zip_p.split(".zip")[0]
    #     if os.path.exists(folder_p):
    #         os.remove(folder_p)
    #     os.makedirs(folder_p)
    #     for member in zip_.infolist():
    #         if member.filename.endswith(('.txt','.docx')):
    #             member.filename = member.filename.encode().decode()
    #             print(member.filename)
    #         zip_.extract(member, folder_p)
    #     # print(zip_.extractall(test_repo))
    #     # print(folder_p)

    # wrap_data 테스트
    # title, paragraphs, images_, videos_ = nw.wrap_data(data_dir=folder_p)
    # print(title)
    # print(paragraphs)
    # print(images_)
    # print(videos_)

    # temp()
    # nw = NaverWrapper("myohyun")
    # nw.upload_images()
    #
    # try:
    #     headers = {'Authorization': 'Client-ID 838a9ea86eca8a3'}
    #     res = requests.get(url='https://api.imgur.com/3/image/2MD2Rxm', headers=headers)
    #     if res.status_code == 200:
    #         print(res.json())
    #         print()
    #     else:
    #         # print(res.text)
    #         raise Exception(res)
    #
    #     res = requests.delete(url='https://api.imgur.com/3/image/sudvzlxLMMo38JY', headers=headers)
    #
    #     if res.status_code == 200:
    #         print(res.json())
    #         print()
    #     else:
    #         # print(res.text)
    #         raise Exception(res)
    #
    # except Exception as e:
    #     print(e)


def test_tistory(db_pass):
    # ad json 생성
    # ad = {
    #     "tistory": {
    #         "middle_1": '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2743596611810852" crossorigin="anonymous"></script><ins class="adsbygoogle" style="display:block; text-align:center;" data-ad-layout="in-article" data-ad-format="fluid" data-ad-client="ca-pub-2743596611810852" data-ad-slot="9584375938"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
    #                 }
    # }
    # with open('./templates/tistory_ad_script.json', 'w', encoding='utf-8') as f:
    #     json.dump(ad,f, ensure_ascii=False)

    ts = TistoryWrapper(db_pass)

    # ok
    # print("\n\n 1. get_category test")
    # categories = ts.get_categories()
    # pprint(categories)

    # ok
    # print("\n\n 1. update_category test")
    ts.update_categories()

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


def test_steemit(db_pass):
    # print(utils_.get_timestamp())
    db_pass = input('mongoDB pw: ')
    sw = SteemWrapper(db_pass)

    # pprint(sw.s.steemd.get_account('nutbox.mine'))
    # Test get my post
    # posts = sw.get_posts(nums=8)

    # Test patch data
    # post = posts[-1]
    # pprint(post)

    # 1.
    # patch_ = sw.wrap_data("./../data/test.txt", type='update')
    # print('patch: \n')
    # pprint(patch_)

    # 스코판 글수수료 지불 ---
    # data= {'permlink': ''}#, 'tags': 'hive-101145'}
    # sw.transfer_fee(data)

    # sw.update_post(patch_, post)

    # 2.
    # patch_ = {'body': post['body'] + '\n patch test : {}'.format(utils_.get_timestamp())}
    # sw.update_post(patch_, post)

    # Test convert an article txt to json data
    # patch_ = sw.wrap_data()
    # patch_["permlink"] = post["permlink"]  # only for test
    # pprint(patch_)
    # sw.update_post(patch_, post)

    # Test submit posts
    # data = sw.wrap_data("./../data/test.txt", type='new')
    # pprint(data)
    # sw.submit_post(data)
    ## print(sw.s.__dict__)

    # make data
    # data = sw.wrap_data("./../data/test.txt")
    # data["parent_author"] = ""
    # data["parent_permlink"] = ""
    # test_d = operations.Comment(data)
    #
    # # get image data
    # test_img_path = '../data/skuld_s.PNG'
    # name_img = os.path.basename(test_img_path)
    # prefix_ = 'ImageSigningChallenge'.encode('utf-8')
    # print(prefix_)
    #
    # with open(test_img_path, 'rb') as f:
    #     binary_ = f.read()
    #
    # msg = prefix_ + compat_bytes(binary_)
    # print(msg)
    # digest = hashlib.sha256(msg).digest()
    # print(digest)

    # test

    #
    #img_links = sw.upload_images(repo='../data')
    #print(img_links)


# TestCase를 작성
class CustomTests(TestCase):

    def setUp(self):
        """테스트 시작되기 전 파일 작성"""

    def tearDown(self):
        """테스트 종료 후 파일 삭제 """
        try:
            os.remove(self.file_name)
        except:
            pass

    def test_runs(self):
        """단순 실행여부 판별하는 테스트 메소드"""
        db_pass = input('mongoDB db_name: ')
        test_tistory(db_pass)
        test_steemit(db_pass)
        test_naver(db_pass)

    def test_line_count(self):
        pass
        #self.assertEqual(custom_function(self.file_name), 3)


# unittest를 실행
if __name__ == '__main__':
    main()
