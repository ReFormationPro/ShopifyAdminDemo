# This Python file uses the following encoding: utf-8
from PyQt5 import QtWidgets, QtGui, QtCore
from UI.UITable import Ui_Form as UI_Table
import shopify
from UI.SearchForm import SearchForm
from Editors import CollectionListingEditor, OrderEditor, CustomerEditor, AssetEditor, ScriptTagEditor, DateField, MetafieldEditor, WebhookEditor, SmartCollectionEditor, RadioButtonWindow, StoreEditor
from Errors import showErrorMessagesOfObject, showException, showErrorMessage
from datetime import datetime, timezone, timedelta
import traceback
import csv
from ThreadHelper import ThreadHelper

TO_TIMEZONE = timezone(timedelta(hours=5, minutes=30)) # IST

class Table():
    """
    Abstract Table Class
    Editor: Editor to open
    Constructor: The constructor of the objects carrying fields
    """
    Editor = None
    Constructor = None
    LIMIT = 3
    def __init__(self, name="Table"):
        self.Form = QtWidgets.QWidget()
        self.ui = UI_Table()
        self.ui.setupUi(self.Form)
        self.ui.editorName.setText(name)
        self.Form.setWindowTitle(name)
        self.model = QtGui.QStandardItemModel()
        self.ui.tableView.setModel(self.model)
        self.ui.editButton.clicked.connect(self.onEditClk)
        self.ui.reloadButton.clicked.connect(self.onReloadClk)
        self.ui.createButton.clicked.connect(self.onCreateClk)
        self.ui.deleteButton.clicked.connect(self.onDeleteClk)
        self.ui.exportButton.clicked.connect(self.exportAsCSV)
        headers = list(map(lambda fc: fc.name, self.Editor.FieldCharacteristics))
        self.setHeaders(headers)
        hh = self.ui.tableView.horizontalHeader()
        hh.sectionClicked.connect(self.onHeaderClick)
        self.ui.prevPage.setEnabled(False)
        self.ui.prevPage.clicked.connect(self.onPrevPageClk)
        self.ui.nextPage.setEnabled(False)
        self.ui.nextPage.clicked.connect(self.onNextPageClk)
        self.page = None
        self.thread = None

    def exportAsCSV(self):
        def _exportAsCSV():
            selectedHeaders = self.getSelectedColumns()
            if len(selectedHeaders) == 0:
                showErrorMessage("You need to select columns to export")
                return
            headers = list(map(lambda h: self._headers[h], selectedHeaders))
            options = QtWidgets.QFileDialog.Options() | QtWidgets.QFileDialog.DontUseNativeDialog
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(QtWidgets.QWidget(),"Export as CSV","","All Files (*);;CSV Files (*.csv)", options=options)
            if fileName:
                with open(fileName, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows([headers])
                    try:
                        page, hasNextPage = self.getAllItemsPaginated()
                        items = map(lambda it: it.to_dict(), page)
                        items = map(lambda it: [it.get(h) for h in headers], items)
                        writer.writerows(items)
                        while hasNextPage:    # Export all items
                            page, hasNextPage = self.getAllItemsPaginated(page)
                            items = map(lambda it: it.to_dict(), page)
                            items = map(lambda it: [it.get(h) for h in headers], items)
                            writer.writerows(items)
                    except Exception as ex:
                        showException(ex)
        ThreadHelper.runThreaded(_exportAsCSV)

    def getAllItemsPaginated(self, page=None):
        try:
            if page == None:
                page = self.Constructor.find(limit=self.LIMIT)
            elif page.has_next_page():
                page = page.next_page()
            else:
                return None
        except Exception as ex:
            showErrorMessage("Error on getting all items")
            print("Error at")
            traceback.print_exc()
            return None
        return (page, page.has_next_page())

    def getSelectedColumns(self):
        columns = sorted(set(index.column() for index in
                              self.ui.tableView.selectedIndexes()))
        return columns

    def onPrevPageClk(self):
        self.changePage(False)

    def onNextPageClk(self):
        self.changePage(True)

    def onHeaderClick(self, a):
        if a == 0:
            rowIdx = 0
            result = []
            newState = 0
            try:
                newState = 0 if self.model.item(0, 0).checkState() == 2 else 2
            except:
                return
            while rowIdx < self.model.rowCount():
                checkBox = self.model.item(rowIdx, 0)
                rowIdx += 1
                checkBox.setCheckState(newState)

    def headerContextMenuRequest(self, position):
        column = self.ui.tableView.horizontalHeader().logicalIndexAt(position)
        print("pass ", column)

    def onSubwindowClose(self):
        self.update()

    def getCheckedObjects(self):
        objs = []
        for id in self.getCheckedRowIds():
            obj = self.Constructor()
            obj.id = id
            objs.append(obj)
        return objs

    def setHeaders(self, headers=None):
        if headers != None:
            self._headers = ["checked"]+headers
            self.model.setHorizontalHeaderLabels(self._headers)
        else:
            self.model.setHorizontalHeaderLabels(self._headers)

    def appendRow(self, data):
        chkBoxItem = QtGui.QStandardItem()
        chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
        row = list(map(lambda x: QtGui.QStandardItem(str(x)), data))
        row[0] = chkBoxItem
        # Convert DateFields to better readable format
        for i in range(len(self._headers)):
            h = self._headers[i]
            if h == "updated_at" or h == "created_at" or h == "published_at" or h == "accepts_marketing_updated_at" or h == "processed_at":
                if data[i] == None or data[i] == "":
                    continue
                data[i] = data[i][0:-3]+data[i][-2:]
                date = datetime.strptime(data[i], "%Y-%m-%dT%H:%M:%S%z")
                time = date.astimezone(TO_TIMEZONE).strftime("%Y/%m/%d & %H:%M:%S")
                row[i] = QtGui.QStandardItem(time)
        self.model.appendRow(row)
        # self.model.setItem(0, 0, chkBoxItem)

    def getCheckedRowIndexes(self):
        rowIdx = 0
        result = []
        while rowIdx < self.model.rowCount():
            checkBox = self.model.item(rowIdx, 0)
            rowIdx += 1
            state = checkBox.checkState()
            if state == 2:  # checked
                result.append(rowIdx)
        return result

    def getCheckedRowIds(self):
        idxs = self.getCheckedRowIndexes()
        return list(map(lambda idx: self.getIdOfRowAtIndex(idx-1), idxs))

    def show(self):
        self.Form.show()

    def changePage(self, toNextPage):
        """
        Changes the page:
            toNextPage = True  => NextPage
            toNextPage = False => PrevPage
        """
        try:
            tmpPage = None
            if toNextPage:
                tmpPage = self.page.next_page()
            else:
                tmpPage = self.page.previous_page()
            if tmpPage != None:
                self.page = tmpPage
        except Exception as ex:
            showException(ex)
            return
        self.ui.nextPage.setEnabled(self.page.has_next_page())
        self.ui.prevPage.setEnabled(self.page.has_previous_page())
        self.load(self.page)

    def update(self):
        """
        Retrieves and loads data.
        """
        def _update():
            try:
                tmpPage = self.Constructor.find(limit=self.LIMIT)
                if tmpPage != None:
                    self.page = tmpPage
                    self.load(self.page)
                else:
                    showErrorMessage("Could not retrieve entries.")
                    return
            except Exception as ex:
                showException(ex)
                return
            if self.page != None:
                self.ui.nextPage.setEnabled(self.page.has_next_page())
                self.ui.prevPage.setEnabled(self.page.has_previous_page())
            else:
                self.ui.nextPage.setEnabled(False)
                self.ui.prevPage.setEnabled(False)
        ThreadHelper.runThreaded(_update)

    def load(self, dictList):
        self.model.clear()
        self.setHeaders()
        if len(dictList) == 0:
            return
        for entry in dictList:
            entry = entry.to_dict()
            row = []
            for k in self._headers:
                try:
                    row.append(entry[k])
                except:
                    row.append("")
            self.appendRow(row)

    def onEditClk(self):
        ids = self.getCheckedRowIds()
        if len(ids) == 0:
            return
        self.editor = self.Editor(ids)
        self.editor.show(self)

    def onReloadClk(self):
        self.update()

    def onCreateClk(self):
        """
        Opens an Editor in create mode.
        """
        self.editor = self.Editor()
        self.editor.show(self)

    def onDeleteClk(self):
        toDelete = self.getCheckedRowIds()
        try:
            for rowId in toDelete:
                obj = self.Constructor()
                obj.id = rowId
                obj.destroy()
                showErrorMessagesOfObject(obj)
        except Exception as ex:
            showException(ex)
        self.update()

    def getSelectedRows(self):
        rows = sorted(set(index.row() for index in
                              self.ui.tableView.selectedIndexes()))
        return rows

    def getIdOfRowAtIndex(self, idx):
        return self.model.index(idx, 1).data()

    def getIdOfSelectedRow(self):
        """
        Returns the id at the selected row.
        """
        selectedRows = self.getSelectedRows()
        if len(selectedRows) != 1:
            print("You must exactly select 1 row")
            return
        return self.getIdOfRowAtIndex(selectedRows[0])


class MetafieldTable(Table):
    Editor = MetafieldEditor
    Constructor = shopify.Metafield
    def __init__(self):
        Table.__init__(self, "Metafields Table")


class WebhookTable(Table):
    Editor = WebhookEditor
    Constructor = shopify.Webhook
    def __init__(self):
        Table.__init__(self, "Webhook Table")


class PublishableTable(Table):
    Constructor = None
    Name = "Object"
    def __init__(self, name="Publishable Table"):
        Table.__init__(self, name)
        self.operationObjs = []

    def onPublishClk(self):
        """
        Derived class registers this listener to a button
        """
        ids = self.getCheckedRowIds()
        self.operationObjs = []
        for id in ids:
            obj = self.Constructor()
            obj.id = id
            self.operationObjs.append(obj)
        if len(self.operationObjs) != 0:
            self.rbw = RadioButtonWindow("Publish this %s?"%self.Name,
                "Publish", "Unpublish", self.onPublish, self.onUnpublish)
            self.rbw.show(self)

    def onPublish(self):
        try:
            for obj in self.operationObjs:
                obj.published = True
                obj.save()
        except Exception as ex:
            print("An exception occured at Publish:")
            print(ex)
            showException(ex)
            self.update()
        print("publish")

    def onUnpublish(self):
        try:
            for obj in self.operationObjs:
                obj.published = False
                obj.save()
        except Exception as ex:
            print("An exception occured at Unpublish:")
            print(ex)
            showException(ex)
            self.update()
        print("unpublish")



class MockPageEditor():
    from Editors import FieldCharacteristic, TextField, MultiTextField
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("author", TextField, False),
        FieldCharacteristic("body_html", TextField, False),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("published_at", TextField, True),
        FieldCharacteristic("handle", TextField, False),
        FieldCharacteristic("metafield", MultiTextField, False), #TODO
        FieldCharacteristic("shop_id", TextField, True),
        FieldCharacteristic("template_suffix", TextField, False),
        FieldCharacteristic("title", TextField, False)
    ]


class PageTable(PublishableTable):
    Constructor = shopify.Page
    Editor = MockPageEditor
    Name = "page"
    def __init__(self):
        PublishableTable.__init__(self, "Pages Table")
        self.ui.unpublishBtn = self.ui.createButton
        self.ui.publishBtn = self.ui.editButton
        self.ui.unpublishBtn.setText("UNPUBLISH")
        self.ui.publishBtn.setText("PUBLISH")
        self.ui.unpublishBtn.clicked.disconnect()
        self.ui.unpublishBtn.clicked.connect(self.onUnpublish)
        self.ui.publishBtn.clicked.disconnect()
        self.ui.publishBtn.clicked.connect(self.onPublish)

    def onPublish(self):
        self.operationObjs = self.getCheckedObjects()
        PublishableTable.onPublish(self)
        self.update()

    def onUnpublish(self):
        self.operationObjs = self.getCheckedObjects()
        PublishableTable.onUnpublish(self)
        self.update()

    def setHeaders(self, headers=None):
        if headers != None:
            self._headers = ["checked"]+headers
            try:
                self._headers.remove("body_html")
            except:
                pass
            self.model.setHorizontalHeaderLabels(self._headers)
        else:
            self.model.setHorizontalHeaderLabels(self._headers)


class CollectionListingTable(Table):
    Constructor = shopify.CollectionListing
    Editor = CollectionListingEditor
    Name = "collection listing"
    def __init__(self):
        Table.__init__(self, "Collection Listing Table")


class SmartCollectionTable(PublishableTable):
    Constructor = shopify.SmartCollection
    Editor = SmartCollectionEditor
    Name = "smart collection"
    def __init__(self):
        Table.__init__(self, "Smart Collection Table")
        # Add publish button
        self.ui.publishButton = QtWidgets.QPushButton(self.Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                           QtWidgets.QSizePolicy.Preferred)
        self.ui.publishButton.setSizePolicy(sizePolicy)
        self.ui.publishButton.setText("PUBLISH/UNPUBLISH")
        self.ui.horizontalLayout.addWidget(self.ui.publishButton)
        self.ui.publishButton.clicked.connect(self.onPublishClk)


class CustomerTable(Table):
    Constructor = shopify.Customer
    Editor = CustomerEditor
    def __init__(self):
        Table.__init__(self, "Customers Table")


class OrderTable(Table):
    Constructor = shopify.Order
    Editor = OrderEditor
    def __init__(self):
        Table.__init__(self, "Orders Table")


class ScriptTagTable(Table):
    Constructor = shopify.ScriptTag
    Editor = ScriptTagEditor
    def __init__(self):
        Table.__init__(self, "Script Tags Table")


class AssetTable(Table):
    Constructor = shopify.Asset
    Editor = AssetEditor
    def __init__(self):
        Table.__init__(self, "Assets Table")

    def getAssetIdentifiers(self, rowIdx):
        keyIdx = self._headers.index("key")
        theme_idIdx = self._headers.index("theme_id")
        key = self.model.index(rowIdx, keyIdx).data()
        theme_id = self.model.index(rowIdx, theme_idIdx).data()
        return (key, theme_id)

    def getCheckedAssets(self):
        selectedIdxs = self.getCheckedRowIndexes()
        assets = []
        try:
            for idx in selectedIdxs:
                key, theme_id = self.getAssetIdentifiers(idx)
                assets.append(shopify.Asset.find(key, theme_id=theme_id))
        except Exception as ex:
            print("An error occured on getting assets.")
            showException(ex)
            return []
        return assets

    def onEditClk(self):
        selectedIdxs = self.getCheckedRowIndexes()
        if len(selectedIdxs) == 0:
            return
        identifiers = list(map(lambda x: self.getAssetIdentifiers(x), selectedIdxs))
        self.editor = self.Editor(identifiers)
        self.editor.show(self)

    def onDeleteClk(self):
        toDelete = self.getCheckedAssets()
        try:
            for asset in toDelete:
                asset.destroy()
                showErrorMessagesOfObject(obj)
        except Exception as ex:
            showException(ex)
        self.update()


class MockProductEditor():
    from Editors import TextField, FieldCharacteristic
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("body_html", TextField, True),
        FieldCharacteristic("created_at", TextField, True),
        FieldCharacteristic("handle", TextField, True),
        FieldCharacteristic("images", TextField, True),
        FieldCharacteristic("options", TextField, True),
        FieldCharacteristic("product_type", TextField, True),
        FieldCharacteristic("published_at", TextField, True),
        FieldCharacteristic("published_scope", TextField, True),
        FieldCharacteristic("tags", TextField, True),
        FieldCharacteristic("template_suffix", TextField, True),
        FieldCharacteristic("title", TextField, True),
        FieldCharacteristic("updated_at", TextField, True),
        FieldCharacteristic("variants", TextField, True),
        FieldCharacteristic("vendor", TextField, True)
    ]


class ProductTable(Table):
    Constructor = shopify.Product
    Editor = MockProductEditor
    def __init__(self):
        PublishableTable.__init__(self, "Products Table")
        self.ui.unpublishBtn = self.ui.createButton
        self.ui.publishBtn = self.ui.editButton
        self.ui.unpublishBtn.setText("UNPUBLISH")
        self.ui.publishBtn.setText("PUBLISH")
        self.ui.unpublishBtn.clicked.disconnect()
        self.ui.unpublishBtn.clicked.connect(self.onUnpublish)
        self.ui.publishBtn.clicked.disconnect()
        self.ui.publishBtn.clicked.connect(self.onPublish)
        self.ui.searchBtn = self.ui.deleteButton
        self.ui.searchBtn.setText("SEARCH")
        self.ui.searchBtn.clicked.disconnect()
        self.ui.searchBtn.clicked.connect(self.onSearchClk)

    def onSearchClk(self):
        self.searchForm = SearchForm()
        self.searchForm.show(self)

    def onSearchById(self, id):
        try:
            self.page = self.Constructor.find(id)
        except Exception as ex:
            showException(ex)
        self.load([self.page])
        self.ui.nextPage.setEnabled(False)
        self.ui.prevPage.setEnabled(False)

    def onSearchByTitle(self, title):
        try:
            self.page = self.Constructor.find(title=title, limit=self.LIMIT)
        except Exception as ex:
            showException(ex)
        self.load(self.page)
        self.ui.nextPage.setEnabled(self.page.has_next_page())
        self.ui.prevPage.setEnabled(self.page.has_previous_page())

    def search(self, **kwargs):
        try:
            kwargs["limit"] = self.LIMIT
            self.page = self.Constructor.find(**kwargs)
            self.load(self.page)
        except Exception as ex:
            showException(ex)
        self.ui.nextPage.setEnabled(self.page.has_next_page())
        self.ui.prevPage.setEnabled(self.page.has_previous_page())

    def onPublish(self):
        try:
            ids = self.getCheckedRowIds()
            for id in self.getCheckedRowIds():
                obj = self.Constructor()
                obj.id = id
                obj.published = True
                obj.save()
        except Exception as ex:
            print("An exception occured at Publish:")
            print(ex)
            showException(ex)
        print("publish")
        self.update()

    def onUnpublish(self):
        try:
            ids = self.getCheckedRowIds()
            for id in self.getCheckedRowIds():
                obj = self.Constructor()
                obj.id = id
                obj.published = False
                obj.save()
        except Exception as ex:
            print("An exception occured at Unpublish:")
            print(ex)
            showException(ex)
        print("unpublish")
        self.update()
