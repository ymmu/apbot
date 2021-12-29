import glob
import json
import os
import re
import shutil
import traceback
from datetime import datetime
import zipfile
import pandas as pd
from pprint import pprint
from urllib.parse import urlparse, parse_qs

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import pyperclip
import pyautogui
from sources import utils_
from sources.post_abstract import Post
from imgurpython import ImgurClient
from selenium.webdriver.common.action_chains import ActionChains
from pathlib import Path


class NaverWrapper(Post):

    def __init__(self, db_pass):
        super(NaverWrapper, self).__init__()
        self.blog_ = "naver"
        # self.account = account
        self.key_ = self.get_keys(db_pass)
        self.repo = self.get_repo()
        self.driver = None  # 실제 발행할 때 만들기. 먼저 드라이버 객체 만들면 창이 뜸

    def get_data_form(self):
        return super().get_data_form()

    def get_keys(self, db_pass):
        return super().get_keys(db_pass)

    def get_repo(self):
        return super().get_repo()

    def get_images_path(self, repo):
        return super().get_images_path(repo)

    @staticmethod
    def attach_images(text, img_links):
        return super().attach_images(text, img_links)

    def wrap_data(self, data_dir=None, **kargs):
        lines, images_, videos_ = super(NaverWrapper, self).wrap_data(local_repo=data_dir)
        print(lines)
        start_line, title = None, None
        img_nums = [str(num) for num in range(20)]
        paragraphs = []
        tmp = ''
        for idx, line in enumerate(lines):
            if line != '\n' and start_line is None:  # 제목뽑기
                title = re.sub("[ @#$%^&\*\-_!]*제목 *:*", "", line)  # 정규식으로 제목 들어간 부분을 삭제
                start_line = idx
                tmp = ''
                continue

            # 이미지
            # if (re.sub("[가-힣a-zA-Z*\"\'~#@&\^\(\)\-_ ]+", "", line) == line and line != '\n')
            # or len((re.findall("[ *사진* *]*[0-9]{1,2}", line))) > 0:
            if re.match("( *(대표)* *(사진)* *[\[\(]*[0-9]{1,2}[\)\] ,./]*){1,3}\n", line):
                img_num_sep = re.compile("[0-9]{1,2}").findall(line.replace("\n", ""))
                # paragraphs.extend([tmp, line]) # 이미지 표시 그대로 넣는건데 막음
                paragraphs.extend([tmp + '\n\n'])  # 그 대신 띄어쓰기로
                paragraphs.extend(img_num_sep)
                tmp = '\n\n'

            # 동영상
            # elif re.sub("[\[\]\(\)* \n0-9]", "", line) == '동영상':
            elif "영상" in line:
                paragraphs.extend([tmp + '\n', line + '\n'])
                paragraphs.extend(["동영상"])
                tmp = ''

            else:
                tmp = tmp + line

            if idx == (len(lines) - 1):  # 라인 끝이면 마지막 문단 저장
                paragraphs.extend([tmp])

        # print(title)
        # print(paragraphs)
        return title, paragraphs, images_, videos_

    def create_post(self, data):
        pass

    def get_posts(self, nums=3, author=None):
        pass

    def get_post(self, post_id):
        pass

    def validate_params(self, new_data):
        pass

    def update_post(self, new_data, data, **kargs):
        pass

    def upload_video(self, title, videos_path: list):

        # 동영상 버튼 클릭
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[1]/ul/li[3]/button').click()
        time.sleep(2)
        WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.XPATH,
                                                                         '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div/div[2]/form/div/fieldset/div[1]/button[1]'))).click()
        try:
            video = videos_path.pop(0)  # 첫번째 것부터 팝. 간혹 동영상 여러 개일 때 있음

            print(video)
            pyperclip.copy(video)
            pyautogui.sleep(1)
            # pyautogui.write(img) # 한글 적용 안 됨
            # pyautogui.click()
            pyautogui.hotkey("ctrl", "v")  # 이건 딴데 클릭하면 망함..
            pyautogui.sleep(1)
            pyautogui.press('enter')

            time.sleep(1)
            # 제목입력
            (self.driver
             .find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div/div[2]/form/div[3]/div[2]/div[2]/fieldset/div[1]/div[2]/input')
             .send_keys(title)
             )
            time.sleep(50)
            (self.driver
             .find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div/div[2]/form/div[4]/button')
             .click()
             )

            print('in upload video: ', video)

        except IndexError as e:
            # 동영상이 없으면 그냥 나감
            (self.driver
             .find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div/div[2]/div[1]/button')
             .click()
             )

    def upload_images(self, nums: list, repo: str = None, **kargs):
        """네이버 이미지는 셀레니움으로 조작해서 올림
            repo를 뺴도 될 지도
        """
        img = None
        # 테스트용으로 쓰는걸로
        if not repo:
            repo = "C:\\Users\\myohy\\OneDrive\\문서\\카카오톡 받은 파일\\비타민B12"
        repo = os.path.abspath(repo)
        # print(repo)
        for num in nums:
            img = glob.glob(os.path.join(repo, '{}.*'.format(num)))  # 이미지 포맷 검사해야할까? -> 해야하네..;
            if not img:
                print('No img path: {}'.format(img))

            else:
                if img[0].lower().endswith(('mp4', 'mp3', 'mov')):  # 숫자(보통 이미지)인데 영상일 때가 있음..
                    # 별로임..
                    print('It\'s not an image. The upload_video method will be called.')
                    self.upload_video(kargs['title'], kargs['videos'])
                else:
                    img = img[0]
                    # 사진 버튼 클릭
                    pyperclip.copy(img)
                    photo_b = self.driver.find_element_by_xpath(
                        '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[1]/ul/li[1]/button/span[1]')
                    photo_b.click()

                    # 안 됨. 작동 안 함. dialog에 적용되는게 아니고 그냥 버튼에 계속 적용되는 듯.
                    # input 클릭하면 되는데..
                    # key_down을 잘못 넣으면 webelement 필요하다고 에러남. 엉뚱한 에러..
                    # actions = ActionChains(self.driver)
                    # (actions.move_to_element(photo_b).click()
                    #  .pause(3)
                    #  #.key_down(Keys.CONTROL)
                    #  #.send_keys("v")
                    #  .send_keys(img)
                    #  .pause(3)
                    #  .key_down(Keys.ENTER).perform())
                    # print('dddfdssdfsdfsdfsdf')

                    # gui로 다이얼로그 컨트롤
                    pyautogui.sleep(2)
                    # pyautogui.write(img) # 한글 적용 안 됨
                    # pyautogui.click()
                    pyautogui.hotkey("ctrl", "v")  # 이건 딴데 클릭하면 망함..
                    pyautogui.sleep(1)
                    pyautogui.press('enter')
                    time.sleep(2)

                    # win32com으로 다이얼로그 컨트롤
                    # import win32com.client
                    # shell = win32com.client.Dispatch("WScript.Shell")
                    # shell.Sendkeys(img)
                    # time.sleep(1)
                    # shell.Sendkeys("{ENTER}")
                    # time.sleep(1)

                    # 그냥 install 말고 다른 설정을 해줘야 하는 듯.
                    # import autoit
                    # autoit.win_active("Open")
                    # # autoit.control_send("Open", "Edit1", r"C:\Users\uu\Desktop\TestUpload.txt")
                    # # autoit.control_send("Open", "Edit1", "{ENTER}")
                    # autoit.control_set_text("Open", "Edit1", img)
                    # print('in upload images: ', img)

    def get_articles(self, account):
        """발행할 글 publish_list에서 체크 -> 해당 zip 압축풀고 가져오기

        :param test_repo:
        :return:
        """
        p_file = os.path.join(self.key_[account]['local_repo'], "publish_list.txt")
        published_list = pd.read_csv(p_file,
                                     sep='\t',
                                     infer_datetime_format=True,
                                     parse_dates=True)
        published_list = published_list.query(f"account=='{account}'")
        #print(published_list.tail())
        p_list = published_list.query("done.isnull() or done=='update'")
        p_date = p_list[['filename', 'p_date']].values  # list
        print(p_date)
        import zipfile
        zip_list = glob.glob(os.path.join(self.key_[account]['local_repo'], "*.zip"))

        def is_same(name):
            filename = os.path.basename(name).split(".")[0]  # 확장자 뺀 파일 이름만
            rst = None  # (name, filename, None)
            # print(name, filename)
            for p in p_date:
                if filename == p[0]:
                    print('here')
                    rst = (name, filename, p[1])
                    break
                    # print(p[0],filename)
            # print(rst)
            return rst

        # [(name, filename, None), ...]
        return published_list, list(set(map(is_same, zip_list)) - set([None]))

    def record_article(self, publish_list, zip_name):
        """발행을 끝낸 글은 ok처리하고 publish_list.txt에 기록

        :param zip_name: 파일 이름
        :return: None
        """
        p_file = os.path.join(self.key_[account]['local_repo'], "publish_list.txt")
        p_list = publish_list.query('filename == "{}"'.format(zip_name))
        p_list.__setitem__('done', 'ok')

        # print(p_list[['filename', 'p_date']].values)
        publish_list.update(p_list)
        print(publish_list)
        publish_list.to_csv(p_file, sep='\t', index=False, encoding='utf-8')

    def smarteditor_one(self, account):

        # 발행할 글리스트 가져옴. 실행할 때마다
        published_list, result = self.get_articles(account)

        self.driver = webdriver.Chrome('../chromedriver_.exe')
        uid = account  # self.account
        upw = self.key_[account]['secret_key']

        # login : 코드는 너무 길어서 분리하고 싶고,
        # 그렇다고 클래스 매서드로는 두기 싫고 해서 이렇게 했는데..
        def login_(driver, uid: str, upw: str):
            login_url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'

            driver.get(login_url)
            time.sleep(1)
            tag_id = driver.find_element_by_name('id')
            tag_pw = driver.find_element_by_name('pw')

            # clipboard copy and paste
            tag_id.click()
            pyperclip.copy(uid)
            tag_id.send_keys(Keys.CONTROL, 'v')
            time.sleep(1)

            tag_pw.click()
            pyperclip.copy(upw)
            tag_pw.send_keys(Keys.CONTROL, 'v')
            time.sleep(1)

            login_btn = driver.find_element_by_id('log.login')
            login_btn.click()
            time.sleep(1)

            try:
                while True:
                    login_error = driver.find_element_by_xpath(
                        "/html/body/div[2]/div[3]/div/form/fieldset/div[2]/div[2]")
                    if not login_error:  # 에러 안 나면 (None)
                        break
                    print(login_error.text)

                    # retry pw
                    time.sleep(1)
                    tag_pw.click()
                    pyperclip.copy(upw)
                    tag_pw.send_keys(Keys.CONTROL, 'v')
                    time.sleep(1)

                    login_btn = driver.find_element_by_id('log.login')
                    login_btn.click()
                    time.sleep(2)

            except Exception as e:
                print()

            try:
                # 브라우저 등록
                # driver.find_element_by_link_text('등록안함').click()
                time.sleep(10)
            except Exception as e:
                pass
                # raise Exception('브라우저 등록시 문제')

        login_(self.driver, uid, upw)

        # click the blog tab on the main page
        print(self.driver.window_handles)
        time.sleep(1)

        # 메인에서 블로그 클릭
        self.driver.find_element_by_link_text('블로그').click()
        time.sleep(1)
        # 글쓰기 버튼
        self.driver.find_element_by_xpath('/html/body/ui-view/div/main/div/aside/div/div[1]/nav/a[2]').click()

        # 현재 탭 확인 뒤 글쓰기 탭 이외는 종료
        # print(driver.window_handles)
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])
        # print(driver.window_handles)
        time.sleep(10)

        def check_editor_tab(driver):
            try:
                # 작성중 글 팝업 나오면 처리
                # print(driver.current_url)
                driver.switch_to.frame('mainFrame')
                WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button[1]"))).click()

            except Exception as e:
                print(e)
                print('No saved articles.')

            try:
                # 우측 헬프 탭 닫기
                WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.XPATH,
                                                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/article/div/header/button'))).click()

            except Exception as e:
                print(e)
                print('No help tab.')

        check_editor_tab(self.driver)

        try:

            for zip_info in result:
                print(zip_info)
                zip_p, filename, published = zip_info
                print(zip_p, filename, published)
                zip_ = zipfile.ZipFile(zip_p)
                folder_p = zip_p.split(".zip")[0]

                if os.path.exists(folder_p):  # 있으면 삭제하고 다시 생성
                    # os.remove(folder_p) # 퍼미션 에러 남 shutil 사용
                    shutil.rmtree(folder_p)

                os.makedirs(folder_p)
                zip_.extractall(folder_p)

                title_, paragraphs, images_, videos_ = self.wrap_data(folder_p)

                # ---------------

                # # 템플릿 불러오기
                # def choose_template(driver):
                #     driver.find_element_by_xpath(
                #         '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[1]/ul/li[18]/button').click()
                #     time.sleep(2)
                #     # 내 템플릿
                #     driver.find_element_by_xpath(
                #         '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/aside/div/div[2]/ul/li[3]/button').click()
                #     time.sleep(2)
                #     # 가장 상단의 템플릿 선택
                #     driver.find_element_by_xpath(
                #         '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/aside/div/div[3]/div[1]/div[2]/ul/li[1]/a').click()
                #

                # 정렬
                WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH,
                                                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/button'))).click()

                # align_ = self.driver.find_element_by_xpath(
                #     '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/button')
                # align_.click()
                time.sleep(0.5)
                WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH,
                                                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/div/button[2]'))).click()
                time.sleep(1)

                # 업데이트 글일 경우, 그 포스팅 주소로 들어감 -> 수정하기
                u_list = published_list.query('not update.isnull()')
                u_items = [u_item[1] for u_item in u_list[['filename', 'update']].values if u_item[0] == filename]
                print('업데이트 url: ', u_items)
                if len(u_items) > 0:
                    update_url = u_items.pop(0)
                    self.driver.get(update_url)
                    self.driver.switch_to.frame('mainFrame')
                    # 수정버튼 누르기
                    WebDriverWait(self.driver, 5).until(
                        ec.element_to_be_clickable((By.XPATH,
                                                    '/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[10]/div[1]/div/table[2]/tbody/tr/td[2]/div[1]/div/div[1]/div/div/div[4]/div'))).click()
                    WebDriverWait(self.driver, 5).until(
                        ec.element_to_be_clickable((By.XPATH,
                                                    '/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[2]/div/div/div[10]/div[1]/div/table[2]/tbody/tr/td[2]/div[1]/div/div[1]/div/div/div[4]/div/div/a[1]'))).click()
                    time.sleep(3)
                    self.driver.switch_to.frame('mainFrame')


                # variable = 'Some really "complex" string \nwith a bunch of stuff in it.'
                pyperclip.copy(title_)


                # 있던 내용 삭제 (update 일때 필요해서 붙임)
                actions = ActionChains(self.driver)
                try:
                    title = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located((By.XPATH,
                                                    '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span'))).click()
                except Exception as e:
                    pass

                title = self.driver.find_element_by_xpath(
                     '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span')
                context_ = self.driver.find_element_by_xpath(
                    '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]')
                (actions.pause(2).move_to_element(title).click()  #
                 .key_down(Keys.CONTROL)
                 .send_keys('a').pause(1).key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).pause(1)
                 .key_down(Keys.CONTROL)
                 .send_keys('v').pause(1).key_down(Keys.ENTER)
                 .move_to_element(context_).click()
                 .key_down(Keys.CONTROL)
                 .send_keys('a').send_keys(Keys.BACK_SPACE).pause(1)
                 .perform())

                # 본문 붙여넣기
                img_nums = [str(num) for num in range(100)]

                # 글 붙이기 : 방법 1
                div_n = 2
                for p in paragraphs:
                    print(p, type(p))
                    if str(p) == "동영상":
                        print('here')
                        self.upload_video(title_, videos_)
                    elif p not in img_nums:  # 이미지 삽입 아니면
                        # if re.compile("[가-힣|a-z|A-Z]+").sub("", p) != p: # 문자가 있으면
                        pyperclip.copy(p)
                        time.sleep(2)
                        context_d = '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[*]'.format(
                            div_n)
                        WebDriverWait(self.driver, 20).until(ec.element_to_be_clickable((By.XPATH, context_d))).click()
                        # self.driver.find_elements_by_xpath(context_d)[-1].click()
                        time.sleep(1)
                        context = self.driver.find_elements_by_xpath(context_d + '/div/div/div/div/p[*]/span')[-1]
                        actions = ActionChains(self.driver)
                        (actions.move_to_element(context)
                         .click()
                         .key_down(Keys.ENTER)
                         .pause(1)
                         .key_down(Keys.CONTROL)
                         .send_keys('v')
                         .key_down(Keys.ENTER)
                         .perform())

                    else:  # 이미지 삽입이면
                        is_img_p = re.compile("[0-9]{1,2}").findall(p.replace("\n", "")) # (\(* *대표 *\)*)*
                        # is_img_p = re.search("[0-9]{1,2}", is_img_p).group()
                        print(is_img_p)
                        print('num:', is_img_p)
                        self.upload_images(nums=is_img_p,
                                           repo=folder_p,
                                           videos=videos_,
                                           title=title_)  # 동영상이라 표기 안 되어있고 숫자로 표기된 경우.(예외)
                        div_n += (len(is_img_p) + 1)
                    time.sleep(1)

                    # /html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/aside/div/div[2]/div/div/ul/li[1]/div
                    # /html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/aside/div/div[2]/div/div/ul/li[2]/div

                # 방법 2
                # p = '\n'.join(paragraphs)
                # pyperclip.copy(p)
                # context_d = self.driver.find_element_by_xpath(
                #     '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div')
                # context_d.click()
                # time.sleep(2)
                # context = self.driver.find_elements_by_xpath(
                #     '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p[*]/span')[-1]
                # actions = ActionChains(self.driver)
                # (actions.move_to_element(context).click().key_down(Keys.ENTER).pause(2).key_down(Keys.CONTROL).send_keys(
                #     'v').key_down(Keys.ENTER).pause(2)
                #  #.move_to_element(title).click()
                #  #.move_to_element(context_d).click()
                #  .perform())
                #
                # els = self.driver.find_elements_by_xpath(
                #      '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p[*]/span')
                # print('len els: ', len(els))
                # for num in range(1, len(images_)+1): # 이미지 삽입
                #     for el in els:
                #         text = el.find_element_by_xpath("//span[text()='{}']".format(num)).text
                #         print('el text: ', text)
                #         if str(text) == str(num):
                #             actions = ActionChains(self.driver)
                #             (actions.move_to_element(el)
                #              .click()
                #              .key_down(Keys.ENTER)
                #              .pause(2)
                #              .perform())
                #             print('here')
                #             #actions = ActionChains(self.driver)
                #             #actions.move_to_element(el).click().key_down(Keys.ENTER).perform()
                #             self.upload_images(num=num, repo=test_repo)
                #             time.sleep(5)
                #             break

                # model_ = WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CLASS_NAME, "se-popup-button se-popup-button-cancel"))).click()
                # driver.execute_script("arguments[0].innerText = 'test1 {}'".format('https://lh3.googleusercontent.com/lr/AFBm1_byO9SPn2yJq1dhV3Ghz1XD2tIW4hlDmV8yD164e_qReilwwEZRQAdaqFl8qzInB1QKw2FXFsWFf5x6pZKt00cUttnRfnCU54qHg84QvItZwNUiDc-0VLfOY7j0xbFZZM1b5Vrl72csnXQlUp9JCIiuZyvG7wfOx90DPUX4VdsDfhtdAwuq94YT75ktGPGX3zjWc6r7xxs3ziZcGGoGNWkO5Pg-89zQ6gkIVh3pkWMEYehVnJqRBXr0m3eGN8nHc_O5KhjX2Igdwc6RzTvspVhovboj_Hc0PrSV9T48XgQ_-2CYEVhQzWCbcqeVcAFwqxNrboZBAnHVVHOaRJzDSMpCNi7wtWUDurSGDGidjKJFY_JvIhXKaeCxtWfBy4gXuB1ZnjWuvDg9d9VdJIT4Oa_8lOtzBsZCc2N9RmZ1Gi966IsJHC5ZLoIGKk6lF6QRVt068oi0YH35bu9SF6ztUGoYBcxH1jtUZ1WUxoAIwEPjp0zNtfTM_4Uk3fHhvUrlB-MLEOb6x8z9BSj6r6fnZ1WfTe7AH3zYaAZNxIUbUfLQBuXZ9vtjYkeGterS9qAn3UlW9BfOSxpU3TToRlV5PQ0kHMRjYMJoXZGTwEYmHSF63affTPidgckCLT_ggL61swZP1Eo565XvSZ5XEiL9eTaINp9lPH6Si1n1tYww6qwPZt9VEEZMibWNvY9Ax7__99TkP6iaCQfp-WM0RXcBVeCt7sYynXM6yN7O0_E1Y0CuSQOFxKTrv0Lvfoy8fGuPrL5ZIAdjULS9_dh-XKm66FIAhY3VMpKMsg7j6JEBH665H7S1JEExWlU9UsAh3RtYZG8MSII-q8lMXEZ9e8L0lpx_z5k9LtzAsgjx1g'), context)
                # WebDriverWait(driver, 10).until(
                #     ec.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p[2]/span'))).click()

                # context.click()

                # 발행버튼

                # 발행 설정 ----
                def publish_setting(driver, published):
                    # 발행설정 ----

                    # 발행버튼
                    try:
                        # create 시
                        driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/button/span').click()
                    except Exception as e:
                        # update 시
                        driver.find_element_by_xpath(
                            '/html/body/div[1]/div/div[1]/div/div[1]/div[3]/button/span').click()

                    # 카테고리
                    driver.find_element_by_xpath(
                        '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/button').click()
                    els = driver.find_elements_by_xpath(
                        '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[*]')

                    print(len(els))

                    for el in els:
                        category = \
                            el.find_element_by_xpath('./span/label/span').get_attribute('textContent').split('하위 카테고리')[
                                -1]
                        if category == 'product_support':
                            # print(category)
                            el.click()
                            break
                    time.sleep(1)
                    # 서로이웃
                    driver.find_element_by_xpath(
                        '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[3]/div/div/ul/li[1]/span/label').click()

                    # 댓글 비허용 이미 눌러져있음
                    # self.driver.find_element_by_xpath(
                    #     '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[1]/span/label').click()

                    # 공감허용: 비공개면 누를 수 없음
                    # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[2]/span/input')

                    time.sleep(1)

                    if published:  # 예약시간 있으면

                        # 예약 버튼
                        driver.find_element_by_xpath(
                            '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div/ul/li[2]/span/label').click()

                        published_t = utils_.convert_to_timestamp(published)
                        # print(published_t)
                        if published_t:
                            published_t = datetime.fromtimestamp(published_t)
                            # 달력 년월일 테스트
                            month = str(published_t.month)
                            day = str(published_t.day)
                            WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH,
                                                                                        '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/input'))).click()

                            # month
                            m_ = driver.find_element_by_xpath(
                                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/div[3]/div/div/div/span[2]')
                            print('캘린더 월 text: ', m_.text)
                            if m_.text != '{}월'.format(int(month)):
                                # 다음 달로 넘김
                                driver.find_element_by_xpath(
                                    '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/div[3]/div/div/button[2]/span').click()

                            # day
                            d_table_ = driver.find_element_by_xpath(
                                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/div[3]/div/div/table')
                            d_table_.find_element_by_xpath("//button[text()='{}']".format(day)).click()

                            hour_ = str(published_t.hour + 1)  # '15'
                            (driver.find_element_by_xpath(
                                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[2]/select/option[{}]'.format(
                                    hour_))
                             .click())

                            min_ = 1  # str(published_t.minute) if published_t.minute != 0 else '00' # '00'
                            if published_t.minute >= 0 and published_t.minute < 10:
                                min_ = 1
                            elif published_t.minute >= 10 and published_t.minute < 20:
                                min_ = 2
                            elif published_t.minute >= 20 and published_t.minute < 30:
                                min_ = 3
                            elif published_t.minute >= 30 and published_t.minute < 40:
                                min_ = 4
                            elif published_t.minute >= 40 and published_t.minute < 50:
                                min_ = 5
                            elif published_t.minute >= 50 and published_t.minute < 60:
                                min_ = 6

                            (driver.find_element_by_xpath(
                                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[3]/select/option[{}]'.format(
                                    min_)).click())

                publish_setting(self.driver, published)

                print('wait for 30 secs .')
                time.sleep(30)

                # 발행
                # 발행버튼
                # self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/button/span').click()
                self.driver.find_element_by_xpath(
                    '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[8]/div/button').click()

                self.record_article(publish_list=published_list, zip_name=filename)

                time.sleep(5)
                # 블로그 메인에서 글쓰기 클릭
                login_url = 'https://blog.naver.com/myohyun'
                self.driver.get(login_url)
                self.driver.switch_to.frame('mainFrame')
                WebDriverWait(self.driver, 10).until(
                    ec.element_to_be_clickable((By.XPATH,
                                                '/html/body/div[6]/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[1]/div/div[2]/div[2]/a[1]'))).click()

                # 폴더삭제
                # shutil.rmtree(folder_p)
                # 뭐 올렸는지 로그 남기자 -> publish_list에 예약리스트 기록중
                # zip 파일 이동
                # z_name = os.path.basename(zip_p)
                # shutil.move(zip_p, test_repo+r'\{}\{}'.format('done', z_name))

        except Exception as e:
            traceback.print_exc()
            print(e)

        while True:
            ans = input("검수 완료?(완료=ok): ")
            if ans == "ok":
                # time.sleep(50)
                print("Close the chrome web driver.")
                self.driver.close()
                break


if __name__ == '__main__':

    db_pass = input('mongoDB db_name: ')
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

    for account in ['myohyun']:  # 'lucca_ymmu'
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
