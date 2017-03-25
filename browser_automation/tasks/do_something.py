import logging
import unittest

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


logger = logging.getLogger(__name__)
message_ex = "An exception of type {0} occurred. Arguments:\n{1!r}"
url = "https://www.google.com"


class SomethingTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        opts = Options()
        cls.driver = webdriver.Chrome(chrome_options=opts)
        cls.driver.implicitly_wait(30)
        cls.driver.get(url)
    
    @classmethod
    def tearDownClass(cls):
        super(SomethingTest, cls).tearDownClass()
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)
 
