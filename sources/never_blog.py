import glob
import json
import os
import re
import traceback
from datetime import datetime
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

    def __init__(self, account):
        super(NaverWrapper, self).__init__()
        self.blog_ = "naver"
        self.account = account
        self.key_ = self.get_keys()
        self.form = self.get_data_form()
        self.repo = self.get_repo()
        # self.sess_ = Naver_session(self.form['outh'], self.key_, account, self.blog_)
        self.driver = None  # webdriver.Chrome('../chromedriver.exe')

    def get_data_form(self):
        return super().get_data_form()

    def get_keys(self):
        return super().get_keys()

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
            if line != '\n' and start_line is None:
                title = re.sub(" *제목 *:*", "", line)  # 정규식으로 제목 들어간 부분을 삭제
                start_line = idx
                tmp = ''
                continue

            if re.compile("[가-힣|a-z|A-Z]+").sub("", line) == line and line != '\n':
                img_num_sep = re.compile("[0-9]{1,2}").findall(line.replace("\n", ""))
                paragraphs.extend([tmp, line])
                paragraphs.extend(img_num_sep)
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

    def upload_video(self, videos_path: list):

        # 동영상 버튼 클릭
        self.driver.find_element_by_xpath(
            '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[1]/ul/li[3]/button').click()
        WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable((By.XPATH,
                                                                         '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div/div/div[2]/form/div/fieldset/div[1]/button[1]'))).click()

        video = videos_path.pop()
        pyperclip.copy(video)
        pyautogui.sleep(1)
        # pyautogui.write(img) # 한글 적용 안 됨
        # pyautogui.click()
        pyautogui.hotkey("ctrl", "v")  # 이건 딴데 클릭하면 망함..
        pyautogui.sleep(1)
        pyautogui.press('enter')
        print('in upload video: ', video)

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
            img = glob.glob(os.path.join(repo, '{}.*'.format(num)))[0]  # 이미지 포맷 검사해야할까?
            if not img:
                raise Exception('No img path.')

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
            pyautogui.sleep(1)
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

    def smarteditor_one(self, test_repo: str = None):

        self.driver = webdriver.Chrome('../chromedriver.exe')
        uid = self.account
        upw = self.key_['secret_key']

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
                driver.find_element_by_link_text('등록안함').click()
                time.sleep(1)
            except Exception as e:
                raise Exception('브라우저 등록시 문제')

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
        time.sleep(5)

        try:
            # 작성중 글 팝업 나오면 처리
            # print(driver.current_url)
            self.driver.switch_to.frame('mainFrame')
            self.driver.find_element_by_xpath(
                "/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[4]/div[2]/div[3]/button[1]").click()
        except Exception as e:
            print(e)
            print('No saved articles.')

        try:
            # 우측 헬프 탭 닫기
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/article/div/header/button').click()
        except Exception as e:
            print(e)
            print('No help tab.')

        try:
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
            align_ = self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/button')
            align_.click()
            time.sleep(0.5)
            center_ = self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/div/button[2]')
            center_.click()
            time.sleep(1)

            # 제목 본문 붙이기
            if not test_repo:
                test_repo = '../data/kabejin'
            title_, paragraphs, images_, videos_ = self.wrap_data(test_repo)
            # variable = 'Some really "complex" string \nwith a bunch of stuff in it.'
            pyperclip.copy(title_)

            actions = ActionChains(self.driver)
            title = self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span')
            (actions.move_to_element(title).click()
             .key_down(Keys.CONTROL)
             .send_keys('v').pause(1).key_down(Keys.ENTER)
             .perform())

            # 본문 붙여넣기
            img_nums = [str(num) for num in range(20)]

            # 방법 1
            div_n = 2
            for p in paragraphs:
                print(p, type(p))
                if p not in img_nums:  # 이미지 삽입 아니면
                    # if re.compile("[가-힣|a-z|A-Z]+").sub("", p) != p: # 문자가 있으면
                    pyperclip.copy(p)
                    context_d = '/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[*]'.format(
                        div_n)
                    self.driver.find_elements_by_xpath(context_d)[-1].click()
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

                elif '동영상' in str(p):
                    self.upload_video(videos_)
                else:
                    is_img_p = re.compile("[0-9]{1,2}").findall(p.replace("\n", ""))
                    print(is_img_p)
                    print('num:', is_img_p)
                    self.upload_images(nums=is_img_p, repo=test_repo)
                    div_n += (len(is_img_p) + 1)
                time.sleep(1)

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

            self.driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/button/span').click()

            # 카테고리
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/button').click()
            els = self.driver.find_elements_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[*]')
            # '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[30]/span/label'
            # '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[30]/span/label/span'
            print(len(els))

            for el in els:
                category = el.find_element_by_xpath('./span/label/span').get_attribute('textContent').split('하위 카테고리')[
                    -1]
                if category == 'blockchain':
                    print(category)
                    el.click()
                    break
            time.sleep(1)
            # 비공개
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[3]/div/div/ul/li[4]/span/label').click()

            # 댓글허용
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[1]/span/label').click()
            # 공감허용: 비공개면 누를 수 없음
            # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[2]/span/input')

            time.sleep(1)

            # 예약
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div/ul/li[2]/span/label').click()

            # 달력 년월일 테스트
            day = '17'
            WebDriverWait(self.driver, 10).until(ec.element_to_be_clickable(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/input')).click()
            (self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[1]/div[3]/div/div/table')
             .find_element_by_link_text(day)
             .click())

            hour_ = '15'
            (self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[2]/select/option[{}]'.format(
                    hour_))
             .click())

            min_ = '00'
            (self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[7]/div/div[2]/div/div[3]/select/option[{}]'.format(
                    min_)).click())

            # 발행
            self.driver.find_element_by_xpath(
                '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[8]/div/button').click()
        except Exception as e:
            traceback.print_exc()
            print('dddddd')
            print(e)

        1 / 0
        # time.sleep(50)
        self.driver.close()


def temp():
    # 드라이버 로딩
    driver = webdriver.Chrome('../chromedriver.exe')
    # 사용할 변수 선언
    # 네이버 로그인 주소
    url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https%3A%2F%2Fwww.naver.com'
    uid = ''
    upw = ''
    # 네이버 로그인 페이지로 이동
    driver.get(url)
    time.sleep(2)  # 로딩 대기

    # 아이디 입력폼
    tag_id = driver.find_element_by_name('id')
    # 패스워드 입력폼
    tag_pw = driver.find_element_by_name('pw')
    # id 입력
    # 입력폼 클릭 -> paperclip에 선언한 uid 내용 복사 -> 붙여넣기
    tag_id.click()
    pyperclip.copy(uid)
    tag_id.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    # pw 입력
    # 입력폼 클릭 -> paperclip에 선언한 upw 내용 복사 -> 붙여넣기
    tag_pw.click()
    pyperclip.copy(upw)
    tag_pw.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    # 로그인 버튼 클릭
    login_btn = driver.find_element_by_id('log.login')
    login_btn.click()
    time.sleep(2)

    driver.find_element_by_link_text('등록안함').click()
    # driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/form/fieldset/span[2]/a').click()
    time.sleep(3)
    # check_otp = driver.find_element_by_id('wait2')
    # if not check_otp.is_selected():
    #    check_otp.click()

    try:
        login_error = driver.find_element_by_css_selector("#error_common > div > p")
        print("로그인 실패 > ", login_error.text)
    except Exception as e:
        print("로그인 성공")

    print(driver.window_handles)
    time.sleep(1)
    # WebDriverWait(driver,20).until(ec.element_to_be_clickable((By.XPATH,'/html/body/div/div/div[1]/div[2]/div/div/div[1]/a[5]'))).click()
    driver.find_element_by_link_text('블로그').click()
    time.sleep(3)

    driver.find_element_by_xpath('/html/body/ui-view/div/main/div/aside/div/div[1]/nav/a[2]').click()
    # 작성중 글 팝업 나오면 처리
    print(driver.window_handles)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print(driver.window_handles)

    time.sleep(3)
    try:
        driver.switch_to.frame('mainFrame')
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/ul/li[3]/div[1]/p[1]/label[4]').click()
        actions = ActionChains(driver)

        # 글꼴
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/ul[1]/li[1]/button').click()
        time.sleep(1)
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/ul[1]/li[1]/div/div/ul/li[16]/button').click()

        # 글자크기
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/ul[1]/li[2]/button').click()
        time.sleep(1)
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/ul[1]/li[2]/div/div/ul/li[5]/button').click()

        # 정렬
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[2]/ul[3]/li[2]/button').click()
        time.sleep(1)
        # title
        title = driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[1]/ul/li/table/tbody/tr/td[2]/div/input')
        title.clear()
        actions.move_to_element(title).perform()
        # title.send_keys(Keys.CONTROL, "v")
        title.send_keys("푸딩 테스트")
        time.sleep(5)

        # 사진
        driver.find_element_by_xpath(
            '/html/body/div[1]/form/div[2]/div[2]/div[2]/div[1]/div/div[1]/div[1]/ul[1]/li[1]/button').click()
        time.sleep(6)
        print(driver.window_handles)
        driver.switch_to.window(driver.window_handles[-1])
        # 안내팝업 끄기
        driver.find_element_by_xpath('/html/body/div[2]/div/button').click()
        time.sleep(6)
        # 사진 불러오기
        driver.find_element_by_xpath('/html/body/div[3]/header/div[1]/input').send_keys(
            "C:\\Users\\myohy\\OneDrive\\문서\\카카오톡 받은 파일\\비타민B12\\15.jpg")
        time.sleep(4)
        # 올리기 버튼
        driver.find_element_by_xpath('/html/body/div[3]/header/div[2]/button').click()

    except Exception as e:
        print(e)
        print('article title')

    try:
        print('sssssd')
        print(driver.window_handles)
        driver.switch_to.window(driver.window_handles[0])
        print(driver.window_handles)
        driver.switch_to.frame('mainFrame')
        driver.switch_to.frame('se2_iframe')
        context = driver.find_element_by_xpath('/html/body/p')
        # script = "arguments[0].insertAdjacentHTML('afterEnd', arguments[1])"
        # driver.execute_script(script, context, "the new text")
        driver.execute_script("arguments[0].innerText = '\\n\\n\\n\\n 푸딩 \\n푸딩\\n\\n'", context)
        driver.execute_script(
            "arguments[0].setAttribute('style', 'font-family: 나눔명조, NanumMyeongjo; font-size: 12pt;')", context)
        # < span style = "font-family: 나눔명조, NanumMyeongjo; font-size: 12pt;" > &  # xFEFF;</span>

    except Exception as e:
        print(e)
        print('context part')

    driver.switch_to.parent_frame()
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/div[1]/form/div[2]/div[2]/div[2]/div[13]/a[3]').click()

    # time.sleep(5)
    try:
        pass
        # title = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[1]')
        # t_div_ = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div')
        # actions.move_to_element(title)
        # title.send_keys(Keys.CONTROL, "v")
        # driver.execute_script("arguments[0].innerText = 'test22'", title)
        # # driver.execute_script("arguments[0].setAttribute('class', 'se-module se-module-text __se-unit se-title-text se-module-fs32-min-height-for-ie')", t_div_)
        # t_div_.click()

        # element = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[1]/div[1]/div/div/p/span[2]')
        # driver.execute_script("""
        # var element = arguments[0];
        # element.parentNode.removeChild(element);
        # """, element)

        # element = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span[2]')
        # # ref: https://stackoverflow.com/questions/22515012/python-selenium-how-can-i-delete-an-element
        # driver.execute_script("""
        #     var element = arguments[0];
        #     element.parentNode.removeChild(element);
        #     """, element)

        # 정렬
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/header/div[2]/ul/li[12]/div/button').click()

        # 본문
        # context = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div/div[1]/div/div[1]/div[2]/section/article/div[2]/div/div/div/div/p/span')
        # driver.execute_script("arguments[0].innerText = 'test1 \\n test2 \\n {}'".format('https://lh3.googleusercontent.com/lr/AFBm1_byO9SPn2yJq1dhV3Ghz1XD2tIW4hlDmV8yD164e_qReilwwEZRQAdaqFl8qzInB1QKw2FXFsWFf5x6pZKt00cUttnRfnCU54qHg84QvItZwNUiDc-0VLfOY7j0xbFZZM1b5Vrl72csnXQlUp9JCIiuZyvG7wfOx90DPUX4VdsDfhtdAwuq94YT75ktGPGX3zjWc6r7xxs3ziZcGGoGNWkO5Pg-89zQ6gkIVh3pkWMEYehVnJqRBXr0m3eGN8nHc_O5KhjX2Igdwc6RzTvspVhovboj_Hc0PrSV9T48XgQ_-2CYEVhQzWCbcqeVcAFwqxNrboZBAnHVVHOaRJzDSMpCNi7wtWUDurSGDGidjKJFY_JvIhXKaeCxtWfBy4gXuB1ZnjWuvDg9d9VdJIT4Oa_8lOtzBsZCc2N9RmZ1Gi966IsJHC5ZLoIGKk6lF6QRVt068oi0YH35bu9SF6ztUGoYBcxH1jtUZ1WUxoAIwEPjp0zNtfTM_4Uk3fHhvUrlB-MLEOb6x8z9BSj6r6fnZ1WfTe7AH3zYaAZNxIUbUfLQBuXZ9vtjYkeGterS9qAn3UlW9BfOSxpU3TToRlV5PQ0kHMRjYMJoXZGTwEYmHSF63affTPidgckCLT_ggL61swZP1Eo565XvSZ5XEiL9eTaINp9lPH6Si1n1tYww6qwPZt9VEEZMibWNvY9Ax7__99TkP6iaCQfp-WM0RXcBVeCt7sYynXM6yN7O0_E1Y0CuSQOFxKTrv0Lvfoy8fGuPrL5ZIAdjULS9_dh-XKm66FIAhY3VMpKMsg7j6JEBH665H7S1JEExWlU9UsAh3RtYZG8MSII-q8lMXEZ9e8L0lpx_z5k9LtzAsgjx1g'), context)
        #
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/button/span').click()
        #
        # # 카테고리
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/button').click()
        # els = driver.find_elements_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[*]')
        # '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[30]/span/label'
        # '/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[1]/div/div/div[3]/div/ul/li[30]/span/label/span'
        # print(len(els))
        #
        # for el in els:
        #     category = el.find_element_by_xpath('./span/label/span').get_attribute('textContent').split('하위 카테고리')[-1]
        #     if category == 'blockchain':
        #         print(category)
        #         el.click()
        #         break
        # time.sleep(1)
        # # 비공개
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[3]/div/div/ul/li[4]/span/label').click()
        #
        # # 댓글허용
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[1]/span/label').click()
        # # 공감허용: 비공개면 누를 수 없음
        # #driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[4]/div/div/ul/li[2]/span/input')
        #
        # time.sleep(10)
        # driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div[3]/div/div/div/div[8]/div/button').click()
    except Exception as e:
        print('dddddd')
        print(e)

    time.sleep(50)


if __name__ == '__main__':
    nw = NaverWrapper("myohyun")
    # title, paragraphs, images_, videos_ = nw.wrap_data(data_dir='../data/kabejin')
    # print (title)
    # print(paragraphs)

    test_repo = r'C:\Users\myohy\OneDrive\문서\카카오톡 받은 파일\그레이배포2(W-A200)'
    nw.smarteditor_one(test_repo=test_repo)
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
