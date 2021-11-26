# This Python file uses the following encoding: utf-8

import sqlite3
from urllib.request import pathname2url
from ShopifyManager import ShopifyManager
from Tables import Table
from Store import Store
from Editors import StoreEditor
from PyQt5 import QtWidgets
from BulkWebhookTable import BulkWebhookTable

class StoreTable(Table):
    Editor = StoreEditor
    def __init__(self, storeDb):
        Table.__init__(self, "Stores")
        self.storeDb = storeDb
        # Repurpose buttons
        self.ui.openBtn = self.ui.createButton
        self.ui.updateBtn = self.ui.editButton
        self.ui.createBtn = self.ui.deleteButton
        self.ui.deleteBtn = self.ui.reloadButton
        self.ui.openBtn.setText("OPEN")
        self.ui.updateBtn.setText("UPDATE")
        self.ui.createBtn.setText("CREATE")
        self.ui.deleteBtn.setText("DELETE")
        self.ui.openBtn.clicked.disconnect()
        self.ui.updateBtn.clicked.disconnect()
        self.ui.createBtn.clicked.disconnect()
        self.ui.deleteBtn.clicked.disconnect()
        self.ui.openBtn.clicked.connect(self.onOpenClk)
        self.ui.updateBtn.clicked.connect(self.onUpdateClk)
        self.ui.createBtn.clicked.connect(self.onCreateClk)
        self.ui.deleteBtn.clicked.connect(self.onDeleteClk)
        #BulkWebhookBtn
        self.ui.bulkWebhookBtn = QtWidgets.QPushButton(self.Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ui.bulkWebhookBtn.sizePolicy().hasHeightForWidth())
        self.ui.bulkWebhookBtn.setSizePolicy(sizePolicy)
        self.ui.bulkWebhookBtn.setObjectName("bulkWebhookBtn")
        self.ui.bulkWebhookBtn.setText("Bulk Webhook")
        self.ui.horizontalLayout_2.addWidget(self.ui.bulkWebhookBtn)
        self.ui.bulkWebhookBtn.clicked.connect(self.onBulkWebhook)
        self.update()
        self.offset = 0

    def onBulkWebhook(self):
        allStores = list(map(lambda s: (s.domain, s.api_version, s.api_password), self.getAllItems()))
        self.BulkWebhookTable = BulkWebhookTable(allStores)
        self.BulkWebhookTable.show()
        self.BulkWebhookTable.update()

    def getAllItems(self):
        return list(self.storeDb.getAllStores())

    def getAllItemsPaginated(self, page=None):
        """
        TODO
        Returns a tuple ([stores], hasNextPage)
        """
        try:
            if page == None:
                page = self.storeDb.getAllStores(limit=self.LIMIT)
            elif page.has_next_page():
                page = all.next_page()
            else:
                return None
        except Exception as ex:
            showErrorMessage("Error on getting all items")
            print("Error at")
            traceback.print_exc()
            return None
        return (page, False)

    def getSelectedStore(self):
        ids = self.getCheckedRowIds()
        if len(ids) == 0:
            return None
        return self.storeDb.getStore(ids[0])

    def changePage(self, toNextPage):
        loadedStoreCount = self.model.rowCount()
        if toNextPage:
            stores = list(self.storeDb.getAllStores(self.LIMIT,
                                                    self.offset+loadedStoreCount))
            self.load(stores)
            self.offset += len(stores)
        else:
            startOffset = self.offset - self.LIMIT
            if startOffset < 0:
                startOffset = 0
            stores = list(self.storeDb.getAllStores(self.LIMIT,
                                                    startOffset))
            self.load(stores)
            self.offset = startOffset
        self.ui.nextPage.setEnabled(self.storeDb.hasNextPage(self.offset+loadedStoreCount))
        self.ui.prevPage.setEnabled(self.offset != 0)

    def update(self):
        stores = list(self.storeDb.getAllStores(self.LIMIT))
        self.offset = 0
        self.ui.nextPage.setEnabled(self.storeDb.hasNextPage(self.offset+len(stores)))
        self.ui.prevPage.setEnabled(False)
        self.load(stores)

    def onOpenClk(self):
        ids = self.getCheckedRowIds()
        if len(ids) == 0:
            return
        s = self.storeDb.getStore(ids[0])
        self.store = None  #Shopify Session Bug Fix
        self.store = ShopifyManager(s.name+".myshopify.com", s.api_version, s.api_key, s.api_password)

    def onUpdateClk(self):
        print("update")
        storeIds = self.getCheckedRowIds()
        if len(storeIds) == 0:
            return
        self.editor = self.Editor(self.storeDb, storeIds)
        self.editor.show(self)

    def onCreateClk(self):
        print("create")
        self.editor = self.Editor(self.storeDb)
        self.editor.show(self)

    def onDeleteClk(self):
        print("delete")
        toDelete = self.getCheckedRowIds()
        print(toDelete)
        try:
            for rowId in toDelete:
                self.storeDb.deleteStore(rowId)
        except Exception as ex:
            showException(ex)
        self.update()

    def load(self, dictList):
        self.model.clear()
        self.setHeaders()
        if len(dictList) == 0:
            return
        for entry in dictList:
            row = []
            for k in self._headers:
                try:
                    row.append(entry.__getattribute__(k))
                except:
                    row.append("")
            self.appendRow(row)



class StoreDatabase():
    DATABASE_PATH = "stores.db"
    def __init__(self):
        try:
            dburi = 'file:{}?mode=rw'.format(pathname2url(self.DATABASE_PATH))
            self.conn = sqlite3.connect(dburi, uri=True)
        except sqlite3.OperationalError:
            # Create new database
            self.conn = sqlite3.connect(self.DATABASE_PATH)
            self.setup()
        self.curr = self.conn.cursor()

    def setup(self):
        # Create table
        self.curr.execute('''CREATE TABLE Stores
                     (id INTEGER NOT NULL PRIMARY KEY, active text, name text, brand_name text,
                     api_version text, domain text, api_key text, api_password text)''')
        self.conn.commit()

    def getStore(self, id):
        self.curr.execute('SELECT * FROM Stores WHERE id = ?', id)
        s = self.curr.fetchone()
        return Store(s[0], s[1], s[2], s[3], s[4],s[5], s[6], s[7])

    def addStore(self, store):
        self.curr.execute('''INSERT INTO Stores
                            (active, name, brand_name, api_version
                            , domain, api_key, api_password)
                            VALUES (?,?,?,?,?,?,?)''', store.toList())
        self.curr.execute('SELECT last_insert_rowid()')
        id = self.curr.fetchone()
        self.conn.commit()
        return str(id[0])

    def deleteStore(self, id):
        self.curr.execute('DELETE FROM Stores WHERE id = ?;', id)
        self.conn.commit()

    def updateStore(self, id, store):
        self.curr.execute('''UPDATE Stores SET
            active = ?, name= ?,
            brand_name = ?, api_version= ?,
            domain = ?,
            api_key = ?, api_password= ?
            WHERE id = ?;''', store.toList() + [id])
        self.conn.commit()

    def getAllStores(self, limit=-1, offset=-1):
        if limit == -1 and offset == -1:
            self.curr.execute('SELECT * FROM Stores')
        elif limit == -1:
            self.curr.execute("SELECT * FROM Stores offset %d"% offset)
        elif offset == -1:
            self.curr.execute('SELECT * FROM Stores limit %d'% limit)
        else:
            self.curr.execute('SELECT * FROM Stores limit %d offset %d'%(limit, offset))
        return map(lambda s: Store(s[0], s[1], s[2],
                            s[3], s[4],
                            s[5], s[6], s[7]),
                   self.curr.fetchall())

    def hasNextPage(self, offset):
        self.curr.execute('SELECT * FROM Stores limit 1 offset %d'%offset)
        return self.curr.fetchone() != None

    def __del__(self):
        self.curr.close()
        self.conn.close()


class StoreManager():
    def __init__(self):
        self.db = StoreDatabase()
        stores = self.db.getAllStores()
        self.StoreTable = StoreTable(self.db)
        self.StoreTable.show()

