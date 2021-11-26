# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore, QtWidgets, QtGui
from UI.UISearchForm import Ui_Form as UI_SearchForm
import shopify
from Errors import showErrorMessagesOfObject

class SearchForm(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.ui = UI_SearchForm()
        self.ui.setupUi(self)
        self.ui.byIdBtn.clicked.connect(self.onSearchById)
        self.ui.byTitleBtn.clicked.connect(self.onSearchByTitle)

    def onSearchById(self):
        id = self.ui.text.text()
        self.parentWindow.onSearchById(id)
        self.close()

    def onSearchByTitle(self):
        title = self.ui.text.text()
        self.parentWindow.onSearchByTitle(title)
        self.close()

    def show(self, parentWindow=None):
        self.parentWindow = parentWindow
        QtWidgets.QWidget.show(self)

