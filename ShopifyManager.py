# This Python file uses the following encoding: utf-8
import shopify
from UI.UIMainWindow import Ui_MainWindow
from PyQt5 import QtWidgets
from ShopWindow import ShopWindow


class ShopifyManager():
    API_KEY = ""
    API_SECRET = ""
    SHOP_URL = ""
    API_VERSION = '2021-02'
    #Below are unused
    REDIRECT_URI = "http://myapp.com/auth/shopify/callback"
    SHOP_NAME = ""
    SHARED_SECRET = ""

    def __init__(self, domain=None, api_version=None, api_key=None, secret=None):
        if domain == None:
            domain = self.SHOP_URL
            api_version = self.API_VERSION
            api_key = self.API_KEY
            secret = self.API_SECRET
        #shopify.Session.setup(api_key, secret)
        newSession = shopify.Session(domain, api_version, secret)
        print("Shopify Session is created")
        shopify.ShopifyResource.activate_session(newSession)
        self.shopWindow = ShopWindow()
        self.shopWindow.show()

    def __del__(self):
        shopify.ShopifyResource.clear_session()
        print("Shopify Session is cleared")

    def onClose(self, event):
        self.shopWindow = None
        print("onclose")
