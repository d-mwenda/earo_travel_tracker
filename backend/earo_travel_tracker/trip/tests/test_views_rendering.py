"""
This script defines tests for how the views are rendered
in the templates.
Tests are based on selenium.
"""
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from django import test

class TestCreateTrip(test.TestCase):
    """
    Test the test create view renders and works correctly.
    """
    def setUp(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.get()

    def tearDown(self):
        self.driver.close()
