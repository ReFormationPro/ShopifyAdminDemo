# This Python file uses the following encoding: utf-8
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from Editors import MetafieldEditor
from ShopifyManager import ShopifyManager
from Tables import Table, CustomerTable
from Editors import RadioButtonWindow, ImageField, TextFieldHTML
import subprocess
from StoreManager import StoreManager
from ShopWindow import ShopWindow

if __name__ == "__main__":
    # subprocess.run(["generate.bat"])
    app = QApplication([])
    storeMan = StoreManager()
    #sm = ShopifyManager()
    sys.exit(app.exec_())
