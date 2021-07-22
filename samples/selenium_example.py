from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from selenium import webdriver
import bs4
from time import sleep

chrome = webdriver.Chrome('./chromedriver.exe')
chrome.get('https://shopping.naver.com/')
chrome.implicitly_wait(2)

el = chrome.find_element_by_xpath('//*[@id="autocompleteWrapper"]/input[1]')
el.clear()
el.send_keys('미피 무드등')
chrome.implicitly_wait(1)
chrome.find_element_by_xpath('//*[@id="autocompleteWrapper"]/a[2]').click()

chrome.implicitly_wait(2)
all_items = []
last_height = chrome.execute_script('return document.body.scrollHeight')
while True:
    chrome.execute_script('window.scrollTo(0, document.body.scrollHeight);')

    chrome.implicitly_wait(1)
    # 스크롤 다운 후 스크롤 높이 다시 가져옴
    new_height = chrome.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

sleep(1)
items = chrome.find_element_by_xpath('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div')
start = 0
for idx, el in enumerate(items.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div[*]')):
    print(idx)

    # 화면에 안 보이면 이미지 로딩이 안 되게 해두었나봄 (before 때문인가) html 공부 좀 해야하나 ;;
    print(el.find_element_by_xpath('.//li/div/div[1]/div/a/img').get_attribute('src'))
    # print(el.find_element_by_xpath('./li/div/div[2]/div[2]/button').text)  # //li에서 /li로 바꿔줬더니 해결됨.. 흠..

    # 상품제목, 가격, 카테고리, 등록일, 찍하기 등등

    # 전체텍스트 ---
    # print(el.find_element_by_xpath('.//li/div/div[2]').text)

    # 제목
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[1]/a')])
    # 가격
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[2]/strong/span/span')])
    # 카테고리
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[3]/a')])
    # 상품 특징
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[4]/div[1]/a')])
    # 할인혜택
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[4]/div[2]/a')])
    # 리뷰, 구매건수, 등록일, 찜하기, 신고하기
    print([i.text for i in el.find_elements_by_xpath('.//li/div/div[2]/div[5]/span')])

    # 배송비, 배송출발날짜, 할인, 구매정보(할인,반품배송비 등등, 클릭하면 뜸)
    # print(el.find_element_by_xpath('.//li/div/div[3]').text)
    chrome.execute_script('window.scrollTo({}, {});'.format(start, start + 200))
    sleep(1)
    start += 200

    # 각 div에서 필요한 정보 선별해서 저장
    # 페이지 넘겨서 다시 긁을 수 있게
    '''
    내가 원하는 모습:
        내가 원하는 키워드를 입력하면 -> 
        (해외구매대행만?) 상품들 이름 / 가격/ 판매량/ 등록일/리뷰수/이미지 비교할 수 있게
        이미지는 미피등이라 들어가있지만 미피등이 아닌 유사상품들도 있으므로 눈으로 비교하고 걸러낼 수 있게 (필터기능)

    '''

# print(page_item_nums)
'''
for i in range(1, page_item_nums+1, 1):
    element_to_hover_over = chrome.find_element_by_xpath('//*[@id="productList"]/div[{}]/div/div/div[4]/div[2]/a'.format(i))
    # print('item_num: {}, item name: {}'.format(i, element_to_hover_over.text))

    hover = ActionChains(chrome).move_to_element(element_to_hover_over)
    hover.perform()
    # li 개수
    # print(len(chrome.find_element_by_xpath(
    #'//*[@id="productList"]/div[{}]/div/div/div[6]/div[2]/ul'.format(i)).find_elements_by_tag_name('li')))
    size_item = []
    for item in chrome.find_element_by_xpath('//*[@id="productList"]/div[{}]/div/div/div[6]/div[2]/ul'.format(i)).find_elements_by_tag_name('li'):
        # print(item.find_element_by_class_name('size-item').get_attribute('data-size'))
        size_item.append(item.find_element_by_class_name('size-item').get_attribute('data-size'))
    print('item_num: {}, item name: {}'.format(i, element_to_hover_over.text), size_item)
    # print(size_item)
    all_items.append(size_item)
    print(len(all_items),all_items)
'''

'''
for i, el in enumerate(chrome.find_elements_by_xpath('//*[@class="description-name"]')):
    if i > 0:
        hover.reset_actions()
    hover = ActionChains(chrome).move_to_element(el)
    hover.perform()
    # li 개수
    # print(len(chrome.find_element_by_xpath(
    # '//*[@id="productList"]/div[{}]/div/div/div[6]/div[2]/ul'.format(i)).find_elements_by_tag_name('li')))
    size_item = []
    for item in el.find_element_by_xpath(
            '//*[@id="productList"]/div[{}]/div/div/div[6]/div[2]/ul'.format(i+1)).find_elements_by_tag_name('li'):
        # print(item.find_element_by_class_name('size-item').get_attribute('data-size'))
        size_item.append(item.find_element_by_class_name('size-item').get_attribute('data-size'))
    print('item_num: {}, item name: {}'.format(i+1, el.text), size_item)
    # print(size_item)
    all_items.append(size_item)
print(len(all_items), all_items)

'''
'''
# 안됨 값이 쌓임 ---
for i, el in enumerate(chrome.find_elements_by_xpath('//*[@class="description-name"]')):
    if i > 0:
        hover.reset_actions()
    hover = ActionChains(chrome).move_to_element(el)
    hover.perform()
    hover.reset_actions()

    size_item = []
    for item in el.find_elements_by_xpath('//*[@class="size-item"]'):#.find_elements_by_tag_name('li'):
        # print(item.find_element_by_class_name('size-item').get_attribute('data-size'))
        size_item.append(item.get_attribute('data-size'))

    print('item_num: {}, item name: {}'.format(i + 1, el.text), size_item)
    # print(size_item)
    all_items.append(size_item)
'''