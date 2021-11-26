# This Python file uses the following encoding: utf-8
from PyQt5.QtWidgets import QMainWindow
from UI.UIShopWindow import Ui_MainWindow as Ui_ShopWindow
from Tables import ProductTable, AssetTable, ScriptTagTable, CustomerTable, OrderTable, MetafieldTable, WebhookTable, PageTable, CollectionListingTable, SmartCollectionTable

class ShopWindow(QMainWindow):
    TABLES = [(MetafieldTable, "Metafields"),
              (SmartCollectionTable, "SmartCollections"),
              (CollectionListingTable, "CollectionListings"),
              (PageTable, "Pages"),
              (WebhookTable, "Webhooks"),
              (OrderTable, "Orders"),
              (CustomerTable, "Customers"),
              (ScriptTagTable, "ScriptTags"),
              (AssetTable, "Assets"),
              (ProductTable, "Products")
    ]

    def __init__(self):
        name = "Shop Window"
        QMainWindow.__init__(self)
        self.ui = Ui_ShopWindow()
        self.ui.setupUi(self)
        self.tables = []
        self.updated = []
        for table, name in self.TABLES:
            t = table()
            self.tables.append(t)
            self.ui.tabWidget.addTab(t.Form, name)
        self.ui.tabWidget.currentChanged.connect(self.currentChanged)

    def currentChanged(self, index):
        """
        Update table when tab changed
        """
        if index != 0 and index not in self.updated:
            self.tables[index-1].update()
            self.updated.append(index)

