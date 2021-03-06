import sys
import os
import time
import unittest

from django.test import LiveServerTestCase
from django.contrib.auth.models import User

from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.proxy import *
from selenium.webdriver.support.wait import WebDriverWait

#pylint: skip-file

PROXY = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': 'proxy-mu.intel.com:911',
        'ftpProxy': 'proxy-mu.intel.com:911',
        'sslProxy': 'proxy-mu.intel.com:911',
        'noProxy': 'localhost,127.0.0.1,.intel.com'
        })

class FirefoxLoginTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.display = Display('xvfb', visible=0, size=(1280, 1024))
        cls.display.start()
        cls.driver = webdriver.Firefox(proxy=PROXY)
        super(FirefoxLoginTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        cls.display.stop()
        super(FirefoxLoginTest, cls).tearDownClass()

    def setUp(self):
        User.objects.create_user('test', '', 'test')

    def tearDown(self):
        User.objects.all().delete()

    def test_login_page(self):
        self.driver.get('%s%s' % (self.live_server_url, '/login/'))
        name_ele = self.driver.find_element_by_id("id_login_username");
        name_ele.send_keys('test')
        pass_ele = self.driver.find_element_by_id("id_login_password");
        pass_ele.send_keys('test')
        login_ele = self.driver.find_element_by_id("login-button");
        login_ele.submit()
        login_user_ele = self.driver.find_element_by_css_selector("#navbar-collapse p.navbar-text.navbar-right")
        self.assertIn('test', login_user_ele.text)
        sign_out_ele = self.driver.find_element_by_css_selector("#navbar-collapse button.btn.btn-default")
        self.assertEqual(sign_out_ele.text.lower().strip(), 'sign out')
        sign_out_ele.submit()

    def test_login_navbar(self):
        self.driver.get(self.live_server_url)
        name_ele = self.driver.find_element_by_name("username");
        name_ele.send_keys('test')
        pass_ele = self.driver.find_element_by_name("password");
        pass_ele.send_keys('test')
        sign_in_ele = self.driver.find_element_by_css_selector("#navbar-collapse button.btn.btn-default")
        self.assertEqual(sign_in_ele.text.lower().strip(), 'sign in')
        sign_in_ele.submit()
        login_user_ele = self.driver.find_element_by_css_selector("#navbar-collapse p.navbar-text.navbar-right")
        self.assertIn('test', login_user_ele.text)
        sign_out_ele = self.driver.find_element_by_css_selector("#navbar-collapse button.btn.btn-default")
        self.assertEqual(sign_out_ele.text.lower().strip(), 'sign out')
        sign_out_ele.submit()
        sign_in_ele = self.driver.find_element_by_css_selector("#navbar-collapse button.btn.btn-default")
        self.assertEqual(sign_in_ele.text.lower().strip(), 'sign in')


if __name__ == '__main__':
     unittest.main()
