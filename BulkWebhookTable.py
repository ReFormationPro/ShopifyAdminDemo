from Tables import Table
from Editors import BulkWebhookEditor
import shopify
from ThreadHelper import ThreadHelper
from Errors import showErrorMessagesOfObject, showException, showErrorMessage
from ShopifyManager import ShopifyManager

class BulkWebhookTable(Table):
    Editor = BulkWebhookEditor
    Constructor = shopify.Webhook
    def __init__(self, stores):
        Table.__init__(self, "Bulk Webhook Table")
        self.stores = stores
        #For loading current page
        self.currentStoreIdx = 0
        self.since_id = -1
        self.loadStore(self.currentStoreIdx)
        #For loading next page
        self.nextStoreIdx = -1
        #For loading previous pages
        self.prevPages = []
        self._headers = ['checked', "on stores", 'updated_at', 'created_at', 'api_version', 'address', 'format', 'topic', 'admin_graphql_api_id']

    def onCreateClk(self):
        """
        Opens an Editor in create mode for creating entries in multiple stores.
        """
        self.editor = self.Editor(self, self.stores)
        self.editor.show(self)

    def onEditClk(self):
        idxs = self.getCheckedRowIndexes()
        entries = list(map(lambda idx: self.multi_entries[self.at_page*self.LIMIT+idx-1], idxs))
        self.editor = self.Editor(self, self.stores, entries)
        self.editor.show(self)

    def loadStore(self, idx):
        self.clearSession()
        domain, api_version, secret = self.stores[idx]
        self.createSession(domain, api_version, secret)
        self.currentStoreIdx = idx

    def getAllEntriesOfShops(self):
        allData = []
        for i in range(len(self.stores)):
            try:
                self.loadStore(i)
                page = self.Constructor.find(limit=self.LIMIT)
                data = page
                while page.has_next_page():
                    page = page.next_page()
                    data += page
            except:
                showErrorMessage("Unable to retrieve all items of store index " + i + " skipping.")
            allData.append((i, data))
            print("Loaded all entries of the shop: ", i)
        return allData

    def createSession(self, domain, api_version, secret):
        newSession = shopify.Session(domain, api_version, secret)
        shopify.ShopifyResource.activate_session(newSession)
        print("Shopify Session is created")

    def clearSession(self):
        shopify.ShopifyResource.clear_session()
        print("Shopify Session is cleared")

    def update(self):
        """
        Retrieves and loads data, starting from currently loaded store and
        current since_id.
        """

        def _update():
            self.multi_entries = self.parseAllData(self.getAllEntriesOfShops())
            self.at_page = 0
            self.load(self.multi_entries[0:self.LIMIT])
            self.ui.nextPage.setEnabled(len(self.multi_entries) > self.LIMIT)
            self.ui.prevPage.setEnabled(False)
        ThreadHelper.runThreaded(_update)

    def load(self, parsedData):
        self.model.clear()
        self.setHeaders()
        # (hash, [(store idx, id)], entry])
        for entry in parsedData:
            row = []
            for k in self._headers:
                if k != "on stores":
                    try:
                        row.append(entry[2][k])
                    except:# Exception as ex:
                        #showException(ex)
                        row.append("")
                else:
                    onstores = ", ".join(list(map(lambda x: str(x[0]), entry[1])))
                    row.append(onstores)
            self.appendRow(row)

    def parseAllData(self, allData):
        """
        We need to webhooks by stores if webhooks are identical in values
        """
        def hasher(entry):
            d = entry.to_dict()
            self._headers = ['checked', "on stores", 'updated_at', 'created_at', 'api_version', 'address', 'format', 'topic', 'admin_graphql_api_id']
            try:
                del d["id"]
                del d["updated_at"]
                del d["created_at"]
                del d["admin_graphql_api_id"]
            except:
                pass
            hashed = ""
            for val in d.values():
                try:
                    hashed += val
                except:
                    pass
            return hash(hashed)
        result = [] #(hash, [(store idx, id)], entry])
        # Group entries by hash, so that we get which stores has common entries
        for idx, data in allData:
            for d in data:
                hashed = hasher(d)
                for r in result:
                    if r[0] == hashed:
                        r[1].append((idx, d.id))
                        break
                else:
                    result.append((hashed, [(idx, d.id)], d.to_dict()))
        return result

    def changePage(self, toNextPage):
        """
        Changes the page:
            toNextPage = True  => NextPage
            toNextPage = False => PrevPage
        """
        if toNextPage:
            self.at_page += 1
        else:
            self.at_page -= 1
            if (self.at_page < 0):
                self.at_page = 0
        index = self.at_page*self.LIMIT
        self.load(self.multi_entries[index:index+self.LIMIT])
        self.ui.nextPage.setEnabled(len(self.multi_entries) > index+self.LIMIT)
        self.ui.prevPage.setEnabled(self.at_page > 0)
