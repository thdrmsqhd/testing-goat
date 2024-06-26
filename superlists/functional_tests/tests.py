import os
import sys
import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class NewVisitorTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
            super().setUpClass()
            cls.server_url = cls.live_server_url
    
    @classmethod
    def tearDownClass(cls) -> None:
        if cls.server_url == cls.live_server_url:
            super().tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        staging_server = os.environ.get('STAGING_SERVER')
        if staging_server:
            self.server_url = 'http://' + staging_server
    
    def tearDown(self):
        self.browser.quit()

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(By.ID, 'id_list_table')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        self.assertIn(row_text, [row_text for row in rows])

    def test_can_start_a_list_and_retrive_it_later(self):
        # 에디스는 멋진 작업 목록 온라인 앱이 나왔다는 소식을 듣고
        # 해당 웹사이트를 확인하러 간다.
        self.browser.get(self.server_url)

        # 웹 페이지 타이틀과 헤더가 'To-Do's 표시하고 있다.
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn('작업 목록 시작', header_text)

        # 그녀는 바로 작업을 추가하기로 한다.
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), '작업 아이템 입력')

        # "공작깃털 사기" 라고 텍스트 상자에 입력한다.
        # (에디스의 취미는 날치 잡이용 그물을 만드는 것이다.)
        inputbox.send_keys('공작깃털 사기')

        # 엔터키를 치면 페이지가 갱신되고 작업목록에
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)
        # "1: 공작깃털 사기" 아이템이 추가된다.

        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')
        self.check_for_row_in_list_table('1: 공작깃털 사기')


        # 추가 아이템을 입력할 수 있는 여분의 텍스트 상자가 존재한다.
        # 다시 "공작깃털을 이용해서 그물 만들기"라고 입력한다.(에디스는 매우 체계적인 사람이다.)
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('공작깃털을 이용해서 그물 만들기')

        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)


        self.check_for_row_in_list_table('2: 공작깃털을 이용해서 그물 만들기')
        self.check_for_row_in_list_table('1: 공작깃털을 사기')
        
        # 페이지는 다시 갱신되고, 두 개 아이템이 목록에 보인다.

        # 새로운 사용자인 프란시스가 사이트에 접속한다.

        # 새로운 브라우저 세션을 이용해서 에디스의 정보가
        # 쿠키를 통해 유입되는 것을 방지한다.
        self.browser.quit()
        self.browser = webdriver.Firefox()
        
        # 프란시스가 홈페이지에 접속한다.
        # 에디스의 리스트는 보이지 않는다.

        self.browser.get(self.server_url)
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertNotIn('공작깃털을 이용해서 그물 만들기', page_text)

        # 프란시스가 새로운 작업 아이템을 입력하기 시작한다.
        # 그는 에디스보다 재미가 없다.
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        inputbox.send_keys('우유 사기')
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)

        # 프란시스의 목록에는 에디스의 목록이 보이지 않는다.
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(francis_list_url, edith_list_url)

        # 에디스가 입력한 흔적이 없다는 것을 다시 확인한다.
        page_text = self.browser.find_element(By.TAG_NAME, 'body').text
        self.assertNotIn('공작깃털 사기', page_text)
        self.assertIn('우유 사기', page_text)

        # 둘 다 만족하고 잠자리에 든다.

    def test_layout_and_styling(self):
        # 에디스는 홈페이지를 방문한다.
        self.browser.get(self.server_url)
        self.browser.set_window_size(1024, 768)
        
        window_size = self.browser.get_window_size()

        self.assertEqual(window_size['width'], 1024)
        self.assertEqual(window_size['height'], 768)
        
        # 그녀는 입력 상자가 가운데 배치된 것을 본다.
        inputbox = self.browser.find_element(By.ID, 'id_new_item')
        self.assertAlmostEqual(
            inputbox.location['x'] + inputbox.size['width'] / 2,
            512,
            delta=10
        )