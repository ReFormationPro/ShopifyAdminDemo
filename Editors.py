# This Python file uses the following encoding: utf-8
import sys
import shopify
import base64
import html
from UI.UIFieldEditor import Ui_Frame as Ui_FieldEditor
from UI.UITextField import Ui_Frame as UI_TextField
from UI.UINumberField import Ui_Frame as UI_NumberField
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets, QtGui
from UI.UIRadioButtonWindow import Ui_Form as Ui_RadioButtonWindow
from UI.UIRuleField import Ui_Form as Ui_RuleField
from UI.UIComboboxField import Ui_Frame as UI_ComboboxField
from UI.UIImageField import Ui_Frame as UI_ImageField
from UI.RuleEditor import RuleEditor
from Errors import showErrorMessagesOfObject, showErrorMessage, showException
from ThreadHelper import ThreadHelper

class BaseField():
    def __init__(self, name):
        self._label = name

    def getData(self):
        pass

    def getName(self):
        return self._label

    def setParent(self, parent):
        self.frame = QtWidgets.QFrame(parent)
        self.ui.setupUi(self.frame)
        self.ui.label.setText(self._label)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)

    def addTo(self, parent, widgetContainer):
        self.setParent(parent)
        widgetContainer.addWidget(self.frame)

    def remove(self):
        self.frame.setParent(None)


from PyQt5.QtWidgets import QFileDialog
class ImageField(BaseField):
    def __init__(self, name, data=None, extra=None):
        BaseField.__init__(self, name)
        self.ui = UI_ImageField()
        self._data = data
        self._attachment = ""
        if type(self._data) == dict:
            try:
                self._attachment = self._data["attachment"]
            except:
                pass
        print(self._data)

    def uploadClk(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(QtWidgets.QWidget(),"Upload image", "","PNG Files (*.png);;All Files (*)", options=options)
        if fileName:
            with open(fileName, 'rb') as file:
                self._attachment = str(base64.b64encode(file.read()))

    def downloadClk(self):
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(QtWidgets.QWidget(),"Save image","","All Files (*);;PNG Files (*.png)", options=options)
        if fileName:
            with open(fileName, 'wb') as file:
                file.write(base64.b64decode(self._attachment))

    def getData(self):
        data = {"alt": self.ui.alt.toPlainText(),
                "src": self.ui.src.toPlainText(),
                "attachment": self._attachment}
        for k in ["alt", "src", "attachment"]:
            if data[k] == "":
                del data[k]
        return data

    def setParent(self, parent):
        BaseField.setParent(self, parent)
        self.ui.uploadBtn.clicked.connect(self.uploadClk)
        self.ui.downloadBtn.clicked.connect(self.downloadClk)
        if type(self._data) == dict:
            self.ui.alt.setPlainText(self._data["alt"])
            self.ui.src.setPlainText(self._data["src"])


class MultiTextField(BaseField):
    def __init__(self, name, data, extra=None):
        BaseField.__init__(self, name)
        self.ui = UI_TextField()
        self._data = "\n".join(data)
        print(self._data)

    def getData(self):
        data = self.ui.text.toPlainText()
        return data.split("\n")

    def setParent(self, parent):
        BaseField.setParent(self, parent)
        self.ui.text.setPlainText(self._data)


class TextField(BaseField):
    def __init__(self, name, data, isReadOnly=False):
        BaseField.__init__(self, name)
        self.ui = UI_TextField()
        self._data = str(data)
        self._isReadOnly = not not isReadOnly

    def getData(self):
        return self.ui.text.toPlainText()

    def setReadonly(self, bool):
        self.ui.text.setReadOnly(bool)

    def setParent(self, parent):
        BaseField.setParent(self, parent)
        self.ui.text.setText(self._data)
        #self.ui.text.setTextAlignment(QtCore.Qt.AlignVCenter)
        self.setReadonly(self._isReadOnly)


class NumberField(TextField):
    def __init__(self, validator, name, data, isReadOnly=False):
        BaseField.__init__(self, name)
        self.ui = UI_NumberField()
        self._data = str(data)
        self._isReadOnly = not not isReadOnly
        self._validator = validator

    def setParent(self, parent):
        TextField.setParent(self, parent)
        self.ui.text.setValidator(self._validator)

    def getData(self):
        return self.ui.text.text()


class DoubleField(NumberField):
    """
    Double Field for range (999999, -999999)
    Maximum number of digits after the decimal point: 8
    """
    def __init__(self, name, data, isReadOnly=False):
        validator = QtGui.QDoubleValidator(999999, -999999, 8)
        NumberField.__init__(self, validator, name, data, isReadOnly)


class IntField(NumberField):
    """
    Integer Field for range (-2147483648, 2147483647)
    """
    def __init__(self, name, data, isReadOnly=False):
        validator = QtGui.QIntValidator(-2147483648, 2147483647)
        NumberField.__init__(self, validator, name, data, isReadOnly)


class DateField(TextField):
    def __init__(self, name, data, isReadOnly=False):
        TextField.__init__(self, name, data, isReadOnly)


class TextFieldHTML(TextField):
    def __init__(self, name, data, isReadOnly=False):
        """
        Allows displaying HTML Text
        TODO: There may be no need for html escaping (try plain text methods)
        """
        if data == None:
            data = ""
        TextField.__init__(self, name, html.escape(data), isReadOnly)

    def getData(self):
        return html.unescape(self.ui.text.toPlainText())


class ComboboxField(BaseField):
    def __init__(self, name, data, options):
        BaseField.__init__(self, name)
        self.ui = UI_ComboboxField()
        self._options = options
        self._data = data

    def getData(self):
        return self.ui.comboBox.currentText()

    def setParent(self, parent):
        BaseField.setParent(self, parent)
        self._options = list(map(lambda x: str(x), self._options))
        self.ui.comboBox.addItems(self._options)
        try:
            self.ui.comboBox.setCurrentIndex(self._options.index(self._data))
        except:
            pass

class FieldCharacteristic():
    def __init__(self, name, type, extra=None):
        """
        Describes a field.
        name: Name of the field
        type: A BaseField
        extra: A TextField's extra is its readOnlyness,
               a ComboboxField's extra is its options
        """
        self.name = name
        self.type = type
        self.extra = extra


class BaseEditor(QtWidgets.QMainWindow):
    FieldCharacteristics = []
    def __init__(self, name="Base Editor", obj=None):
        QtWidgets.QMainWindow.__init__(self)
        self.window = self
        self.ui = Ui_FieldEditor()
        self.ui.setupUi(self.window)
        self.window.setWindowTitle(name)
        self.ui.editorName.setText(name)
        self.ui.verticalLayout.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.ui.saveButton.clicked.connect(self.onSaveClk)
        self.ui.deleteButton.clicked.connect(self.onDeleteClk)
        #Setup logic
        self.fields = []
        self.obj = obj
        self.saved = None # The dictionary to compare against to find changes

    def update(self):
        pass

    def onCreateClk(self):
        pass

    def onSaveClk(self):
        pass

    def onDeleteClk(self):
        pass

    def show(self, parentWindow=None):
        self.parentWindow = parentWindow
        QtWidgets.QMainWindow.show(self)

    def closeEvent(self, event):
        if self.parentWindow != None:
            self.parentWindow.onSubwindowClose()
        event.accept()

    def toDict(self):
        dict = {}
        for f in self.fields:
            dict[f.getName()] = f.getData()
        return dict

    def fromList(self, list=[], writeAllowed=False):
        """
        Creates empty fields from field names in 'list'
        If writeAllowed, no textfield is readonly.
        """
        fields = []
        for key in list:
            fc = next(fc for fc in self.FieldCharacteristics if fc.name == key)
            if fc.type == TextField:
                fields.append(TextField(key, "", fc.extra and not writeAllowed))
            else:
                fields.append(fc.type(key, "", fc.extra))
        self.addFields(fields)
        self.saved = self.toDict()

    def fromDict(self, dict=None, writeAllowed=False):
        """
        Fills in the fields by values in 'dict'
        If writeAllowed, no textfield is readonly.
        """
        fields = []
        for fc in self.FieldCharacteristics:
            if fc.name in ["accepts_marketing_updated_at", "updated_at", "created_at", "owner_id", "admin_graphql_id", "admin_graphql_api_id"]:
                continue
            try:
                value = dict[fc.name]
            except:
                value = ""
            if fc.type == TextField and writeAllowed:
                field = TextField(fc.name, value, False)
            else: # MultiTextField and ComboboxField
                field = fc.type(fc.name, value, fc.extra)
            fields.append(field)
        self.addFields(fields)
        self.saved = self.toDict()

    def onSubwindowClose(self):
        self.update()

    def addFields(self, fields):
        """
        Adds fields of class Field to the list
        Removes all previously added fields.
        """
        for f in self.fields:
            f.remove()
        self.fields = fields
        for f in fields:
            f.addTo(self.ui.fieldList, self.ui.verticalLayout)


class FieldEditor(BaseEditor):
    Create_Keys = [] # Fields that are required in creating a new entry
    Constructor = None # Entry Object Constructor
    FieldCharacteristics = []
    def __init__(self, name="Field Editor", objectIds=[]):
        """
        If objectIds is None, then we are in Create Mode
        """
        BaseEditor.__init__(self, name, objectIds)
        self.objectIds = objectIds
        def init():
            if len(self.objectIds) == 1: # Edit Mode
                self.obj = self.Constructor()
                self.obj.id = self.objectIds[0]
                self.obj.reload()
                self.fromDict(self.obj.to_dict())
            else:   # Create and Bulk Edit Modes
                self.fromList(self.Create_Keys, True) #All read and write
        ThreadHelper.runThreaded(init)

    def update(self):
        def _update():
            if len(self.objectIds) == 1:
                self.obj.reload()
                self.fromDict(self.obj.to_dict())
        ThreadHelper.runThreaded(_update)

    def onCreateClk(self):
        print("editor create")
        dict = self.toDict()
        filtered_dict = {key:v for (key,v) in dict.items() if key in self.Create_Keys}
        print(filtered_dict)
        obj = self.Constructor(filtered_dict)
        print(obj)
        obj.save()
        showErrorMessagesOfObject(obj)
        self.objectIds.append(obj.id)

    def onSaveClk(self):
        if len(self.objectIds) == 0:
            # This is a create action
            self.onCreateClk()
            return
        print("save")
        dict = self.toDict()
        for name in self.saved:
            fc = next(fc for fc in self.FieldCharacteristics if fc.name == name)
            if self.saved[name] == dict[name] or fc.type == TextField and fc.extra == True:
                try:
                    del dict[fc.name]
                except:
                    pass
        for id in self.objectIds:
            obj = self.Constructor(dict)
            obj.id = id
            print(obj.to_dict())
            obj.save()
            showErrorMessagesOfObject(obj)

    def onDeleteClk(self):
        showErrorMessage("Removed")


class MetafieldEditor(FieldEditor):
    Create_Keys = ["namespace", "description", "key", "value",
                    "value_type", "owner_resource"] # We can use these keys to create
    Constructor = shopify.Metafield
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("namespace", TextField, True),
        FieldCharacteristic("description", TextField, False),
        FieldCharacteristic("key", TextField, True),
        FieldCharacteristic("value", TextField, False),
        FieldCharacteristic("value_type", ComboboxField, ["string", "integer", "json_string"]),
        FieldCharacteristic("owner_resource", ComboboxField, ["article", "blog", "CustomCollection", "SmartCollection", "customer", "draftorder", "order", "page", "product", "productvariant", "productimage", "shop"]),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("owner_id", TextField, True),
        FieldCharacteristic("admin_graphql_api_id", TextField, True)
    ]
    def __init__(self, metafield=[]):
        """
        If no metafield is given, then editor will be in create mode.
        """
        FieldEditor.__init__(self, "Metafield Editor", metafield)


class WebhookEditor(FieldEditor):
    Create_Keys = ["address", "format",
                    #"fields", "metafield_namespaces", "private_metafield_namespaces",
                    "topic"] # We can use these keys to create
    Constructor = shopify.Webhook
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("api_version", TextField, True),
        FieldCharacteristic("address", TextField, False),
        #FieldCharacteristic("fields", MultiTextField), #TODO this could be a checkbox based field
        #FieldCharacteristic("metafield_namespaces", MultiTextField),
        #FieldCharacteristic("private_metafield_namespaces", MultiTextField),
        FieldCharacteristic("format", ComboboxField, ["json", "xml"]),
        FieldCharacteristic("topic", ComboboxField, ["app/uninstalled","carts/create","carts/update","checkouts/create","checkouts/delete","checkouts/update","collection_listings/add","collection_listings/remove","collection_listings/update","collections/create","collections/delete","collections/update","customer_groups/create","customer_groups/delete","customer_groups/update","customers/create","customers/delete","customers/disable","customers/enable","customers/update","disputes/create","disputes/update","draft_orders/create","draft_orders/delete","draft_orders/update","fulfillment_events/create","fulfillment_events/delete","fulfillments/create","fulfillments/update","inventory_items/create","inventory_items/delete","inventory_items/update","inventory_levels/connect","inventory_levels/disconnect","inventory_levels/update","locales/create","locales/update","locations/create","locations/delete","locations/update","order_transactions/create","orders/cancelled","orders/create","orders/delete","orders/edited","orders/fulfilled","orders/paid","orders/partially_fulfilled","orders/updated","product_listings/add","product_listings/remove","product_listings/update","products/create","products/delete","products/update","refunds/create","shop/update","tender_transactions/create","themes/create","themes/delete","themes/publish"]),
        FieldCharacteristic("admin_graphql_api_id", TextField, True)
    ]
    def __init__(self, webhook=None):
        FieldEditor.__init__(self, "Webhook Editor", [])


class BulkWebhookEditor(WebhookEditor):
    def __init__(self, table, stores, entries=[]):
        WebhookEditor.__init__(self)
        self.stores = stores
        self.table = table
        self.entries = entries  # [(hash, [(store idx, id)], entry])]
        if len(entries) == 1:
            print("Loading BulkWebhookEditor entry") #TODO Not working
            self.fromDict(self.entries[0][2])

    def onCreateClk(self):
        dict = self.toDict()
        filtered_dict = {key:v for (key,v) in dict.items() if key in self.Create_Keys}
        for store in range(len(self.stores)):
            self.table.loadStore(store)
            obj = self.Constructor(filtered_dict)
            obj.save()
            showErrorMessagesOfObject(obj)
            self.objectIds.append(obj.id)

    def onSaveClk(self):
        if len(self.entries) == 0:
            self.onCreateClk()
            return
        # [(hash, [(store idx, id)], entry])]
        obj = self.Constructor(self.toDict())
        for e in self.entries:
            for storeIdx, id in e[1]:
                self.table.loadStore(storeIdx)
                obj.id = id
                obj.save()
                showErrorMessagesOfObject(obj)
                self.objectIds.append(obj.id)


class SmartCollectionEditor(FieldEditor):
    Create_Keys = ["title", "body_html", "template_suffix",
                   "sort_order", "disjunctive", "published_scope", "handle", "image"]
    Constructor = shopify.SmartCollection
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("title", TextField, False),
        FieldCharacteristic("body_html", TextFieldHTML, False),
        FieldCharacteristic("template_suffix", TextField, False),
        FieldCharacteristic("handle", TextField, False),
        FieldCharacteristic("published_scope", ComboboxField, ["web", "global"]),
        FieldCharacteristic("disjunctive", ComboboxField, ["False", "True"]),
        FieldCharacteristic("sort_order", ComboboxField, ["alpha-asc", "alpha-des", "best-selling", "created", "created-desc", "manual", "price-asc", "price-desc"]),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("published_at", DateField, True),
        FieldCharacteristic("rules", TextField, True),
        FieldCharacteristic("admin_graphql_api_id", TextField, True),
        FieldCharacteristic("image", ImageField)
    ]

    def __init__(self, smartCollectionIds=[]):
        FieldEditor.__init__(self, "Smart Collection Editor", smartCollectionIds)
        self.ui.deleteButton.setText("RULE EDITOR")

    def onCreateClk(self):
        print("SmartCollectionEditor create")
        dict = self.toDict()
        filtered_dict = {key:v for (key,v) in dict.items() if key in self.Create_Keys}
        # Mock rule because at least one rule is required
        filtered_dict["rules"] = [ {
        "column": "vendor",
        "relation": "equals",
        "condition": "At least one rule is required for creation"
        }]
        obj = self.Constructor(filtered_dict)
        print(obj.to_dict())
        obj.save()
        showErrorMessagesOfObject(obj)

    def onDeleteClk(self):
        if len(self.objectIds) == 1:
            self.ruleEditor = RuleEditor(self.objectIds, self.obj.rules)
        else:
            self.ruleEditor = RuleEditor(self.objectIds)
        self.ruleEditor.show(self)


class RadioButtonWindow(QtWidgets.QWidget):
    def __init__(self, description, leftBtnText, rightBtnText, onLeft, onRight):
        QtWidgets.QWidget.__init__(self)
        self.Form = self
        self.ui = Ui_RadioButtonWindow()
        self.ui.setupUi(self.Form)
        self.ui.description.setText(description)
        self.ui.radioLeft.setText(leftBtnText)
        self.ui.radioRight.setText(rightBtnText)
        self.onLeft = onLeft
        self.onRight = onRight
        self.ui.radioLeft.toggled.connect(lambda: self.onToggle(self.ui.radioLeft))
        self.ui.radioRight.toggled.connect(lambda: self.onToggle(self.ui.radioRight))

    def onToggle(self, btn):
        if btn == self.ui.radioLeft and self.ui.radioLeft.isChecked():
            self.onLeft()
        elif btn == self.ui.radioRight and self.ui.radioRight.isChecked():
            self.onRight()

    def show(self, parentWindow=None):
        self.parentWindow = parentWindow
        QtWidgets.QWidget.show(self)

    def closeEvent(self, event):
        if self.parentWindow != None:
            self.parentWindow.onSubwindowClose()
        event.accept()


from Store import Store
class StoreEditor(BaseEditor):
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("active", ComboboxField, [True, False]),
        FieldCharacteristic("name", TextField, False),
        FieldCharacteristic("brand_name", TextField, False),
        FieldCharacteristic("api_version", TextField, False),
        FieldCharacteristic("domain", TextField, False),
        FieldCharacteristic("api_key", TextField, False),
        FieldCharacteristic("api_password", TextField, False)
    ]
    Create_Keys = ["active", "name", "brand_name", "api_version", "domain", "api_key", "api_password"]
    def __init__(self, storeDb, storeIds=[]):
        BaseEditor.__init__(self, "Store Editor", storeIds)
        self.storeDb = storeDb
        self.storeIds = storeIds
        if len(storeIds) == 1:
            store = storeDb.getStore(storeIds[0])
            self.fromDict(store.to_dict())
        else:
            self.fromList(self.Create_Keys, True) #All read and write
        self.saved = self.toDict()

    def update(self):
        pass

    def onCreateClk(self):
        print("store create")
        d = self.toDict()
        store = Store.fromDict(d)
        id = self.storeDb.addStore(store)
        self.storeIds.append(id)

    def onSaveClk(self):
        if len(self.storeIds) == 0:
            self.onCreateClk()
            return
        print("store save")
        updates = self.toDict()
        for k in self.saved:
            if updates[k] == self.saved[k]: #If not updated
                del updates[k]
        for storeId in self.storeIds:
            store = self.storeDb.getStore(storeId)
            for update in updates:
                setattr(store, update, updates[update])
            self.storeDb.updateStore(storeId, store)

    def onDeleteClk(self):
        pass


class ScriptTagEditor(FieldEditor):
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("event", ComboboxField, ["onload"]),
        FieldCharacteristic("src", TextField, False),
        FieldCharacteristic("display_scope", ComboboxField, ["online_store", "order_status", "all"]),
    ]
    Constructor = shopify.ScriptTag
    Create_Keys = ["event", "src", "display_scope"]

    def __init__(self, scriptTag=[]):
        FieldEditor.__init__(self, "Script Tag Editor", scriptTag)


class AssetEditor(FieldEditor):
    FieldCharacteristics = [
        FieldCharacteristic("key", TextField, False),
        FieldCharacteristic("value", TextField, False),
        FieldCharacteristic("attachment", ImageField),
        FieldCharacteristic("content_type", TextField, True),
        FieldCharacteristic("public_url", TextField, True),
        FieldCharacteristic("theme_id", TextField, True),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("updated_at", DateField, True)
    ]
    Constructor = shopify.Asset
    Create_Keys = ["attachment", "key", "value", "content_type", "public_url",
                   "theme_id"]

    def __init__(self, assetIdentifiers=[]):
        BaseEditor.__init__(self, "Asset Editor", assetIdentifiers)
        self.objectIds = assetIdentifiers
        if len(self.objectIds) == 1: # Edit Mode
            key, theme_id = self.objectIds[0]
            try:
                    print("Opening editor on asset: \"%s\", theme_id=%s"%(key, theme_id))
                    self.obj = shopify.Asset.find(key, theme_id=theme_id)
            except Exception as ex:
                    print("An error occured on getting asset.")
                    showException(ex)
                    return
            self.fromDict(self.obj.to_dict())
        else:   # Create and Bulk Edit Modes
            self.fromList(self.Create_Keys, True) #All read and write

    def onSaveClk(self):
        print("asset save")
        dict = self.toDict()
        for name in self.saved:
            fc = next(fc for fc in self.FieldCharacteristics if fc.name == name)
            if self.saved[name] == dict[name] or fc.type == TextField and fc.extra == True:
                try:
                    del dict[fc.name]
                except:
                    pass
        for key, theme_id in self.objectIds:
            dict["key"] = key
            obj = self.Constructor(dict)
            debug = obj.to_dict()
            obj.save()
            showErrorMessagesOfObject(obj)


class CustomerEditor(FieldEditor):
    Constructor = shopify.Customer
    #Create_Keys = ["accepts_marketing", "currency", "email", "first_name", "last_name", "phone", "note"]
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("accepts_marketing", ComboboxField, ["False", "True"]),
        FieldCharacteristic("accepts_marketing_updated_at", DateField, True),
        #FieldCharacteristic("addresses", MultiTextField), #TODO
        FieldCharacteristic("currency", TextField, True),
        FieldCharacteristic("created_at", DateField, True),
        #FieldCharacteristic("default_address", MultiTextField), #TODO
        FieldCharacteristic("email", TextField, False),
        FieldCharacteristic("first_name", TextField, False),
        FieldCharacteristic("last_name", TextField, False),
        FieldCharacteristic("last_order_id", TextField, True),
        FieldCharacteristic("last_order_name", TextField, True),
        #FieldCharacteristic("metafield", MultiTextField), #TODO
        FieldCharacteristic("marketing_opt_in_level", TextField, True),
        FieldCharacteristic("multipass_identifier", TextField, False),
        FieldCharacteristic("note", TextField, False),
        FieldCharacteristic("orders_count", TextField, True),
        FieldCharacteristic("phone", TextField, False),
        FieldCharacteristic("state", ComboboxField, ["disabled", "invited", "enabled", "declined"]),
        #FieldCharacteristic("tags", MultiTextField, False), #TODO comma seperated list
        FieldCharacteristic("tax_exempt", ComboboxField, ["True", "False"]),
        #FieldCharacteristic("tax_exemptions", MultiTextField),
        FieldCharacteristic("total_spent", DoubleField, True),
        FieldCharacteristic("updated_at", DateField, True),
        FieldCharacteristic("verified_email", ComboboxField, ["True", "False"])
    ]

    def __init__(self, customer=[]):
        print("at customer editor")
        FieldEditor.__init__(self, "CustomerEditor", customer)

    def fromList(self, list, writeAllowed=False):
        """
        Create mode override
        """
        dict = {fc.name:"" for fc in self.FieldCharacteristics}
        self.fromDict(dict, writeAllowed)
        next(f for f in self.fields if f.getName() == "id").remove()

    def onCreateClk(self):
        dict = self.toDict()
        obj = self.Constructor(dict)
        print(obj)
        try:
            obj.save()
            showErrorMessagesOfObject(obj)
        except Exception as ex:
            showException(ex)

class OrderEditor(FieldEditor):
    Constructor = shopify.Order
    Create_Keys = ["currency", "customer"]
    FieldCharacteristics = [
        FieldCharacteristic("id", TextField, True),
        FieldCharacteristic("user_id", TextField, True),
        FieldCharacteristic("app_id", TextField, True),
        #FieldCharacteristic("billing_address", MultiTextField), #TODO
        FieldCharacteristic("browser_ip", TextField, True),
        FieldCharacteristic("buyer_accepts_marketing", ComboboxField, ["False", "True"]),
        FieldCharacteristic("cancel_reason", ComboboxField, ["customer", "fraud", "inventory", "declined", "other"]),
        FieldCharacteristic("cancelled_at", DateField, True),
        FieldCharacteristic("cart_token", TextField, True),
        FieldCharacteristic("checkout_token", TextField, True),
        #FieldCharacteristic("client_details", MultiTextField, True), #TODO
        FieldCharacteristic("closed_at", TextField, True),
        FieldCharacteristic("created_at", DateField, True),
        FieldCharacteristic("currency", TextField, False),
        #FieldCharacteristic("current_total_duties_set", TextField, True), #TODO
        #FieldCharacteristic("customer", TextField, False), #TODO
        FieldCharacteristic("customer_locale", TextField, True),
        FieldCharacteristic("discount_applications", TextField, True),
        #FieldCharacteristic("discount_codes", TextField, False), #TODO
        FieldCharacteristic("email", TextField, False),
        FieldCharacteristic("financial_status", ComboboxField, ["authorized", "pending", "partially_paid", "paid", "partially_refunded", "refunded", "voided"]),
        #FieldCharacteristic("fulfillments", TextField, False), #TODO
        FieldCharacteristic("fulfillment_status", ComboboxField, ["partial", "fulfilled", "null", "restocked"]),
        FieldCharacteristic("gateway", TextField, True),
        FieldCharacteristic("landing_site", TextField, True),
        #FieldCharacteristic("line_items", MultiTextField, True), #TODO
        FieldCharacteristic("location_id", TextField, False),
        FieldCharacteristic("name", TextField, False),
        FieldCharacteristic("note", TextField, False),
        #FieldCharacteristic("note_attributes", TextField, False), #TODO
        FieldCharacteristic("number", TextField, True),
        FieldCharacteristic("order_number", TextField, True),
        #FieldCharacteristic("original_total_duties_set ", TextField, True), #TODO
        #FieldCharacteristic("payment_details", TextField, True), #TODO
        FieldCharacteristic("payment_gateway_names ", MultiTextField, True),
        FieldCharacteristic("phone", TextField, False),
        FieldCharacteristic("presentment_currency", TextField, False),
        FieldCharacteristic("processed_at", DateField, False),
        FieldCharacteristic("processing_method", ComboboxField, ["direct", "checkout", "manual", "offsite", "express", "free"]),
        FieldCharacteristic("referring_site", TextField, False),
        #FieldCharacteristic("refunds", TextField, False), #TODO
        #FieldCharacteristic("shipping_address", TextField, True), #TODO
        #FieldCharacteristic("shipping_lines", TextField, True), #TODO
        FieldCharacteristic("source_name", TextField, False),
        FieldCharacteristic("subtotal_price", DoubleField, False),
        #FieldCharacteristic("subtotal_price_set", TextField, True), #TODO
        FieldCharacteristic("tags", TextField, False),
        #FieldCharacteristic("tax_lines", TextField, False), #TODO
        FieldCharacteristic("taxes_included", ComboboxField, ["False", "True"]),
        FieldCharacteristic("test", ComboboxField, ["False", "True"]),
        FieldCharacteristic("token", TextField, True),
        FieldCharacteristic("total_discounts", DoubleField, False),
        #FieldCharacteristic("total_discounts_set", TextField), #TODO
        FieldCharacteristic("total_line_items_price", TextField),
        #FieldCharacteristic("total_line_items_price_set", TextField), #TODO
        FieldCharacteristic("total_price", DoubleField, False),
        #FieldCharacteristic("total_price_set", TextField), #TODO
        FieldCharacteristic("total_tax", DoubleField, False),
        #FieldCharacteristic("total_tax_set", TextField, False), #TODO
        FieldCharacteristic("total_tip_received", DoubleField, False),
        FieldCharacteristic("total_weight", DoubleField, False),
        FieldCharacteristic("order_status_url", TextField, True)
    ]

    def __init__(self, order=[]):
        FieldEditor.__init__(self, "Order Editor", order)

    def fromList(self, list, writeAllowed=False):
        """
        Create mode override
        """
        dict = {fc.name:"" for fc in self.FieldCharacteristics}
        self.fromDict(dict, writeAllowed)
        next(f for f in self.fields if f.getName() == "id").remove()

    def onCreateClk(self):
        dict = self.toDict()
        obj = self.Constructor(dict)
        print(obj)
        obj.save()
        showErrorMessagesOfObject(obj)

class CollectionListingEditor(FieldEditor):
    FieldCharacteristics = [
        FieldCharacteristic("collection_id", TextField, True),
        FieldCharacteristic("body_html", TextField, True),
        FieldCharacteristic("published_at", TextField, True),
        FieldCharacteristic("default_product_image", ImageField, True),
        FieldCharacteristic("image", ImageField, True),
        FieldCharacteristic("handle", TextField, True),
        FieldCharacteristic("title", TextField, True),
        FieldCharacteristic("sort_order", TextField, True),
        FieldCharacteristic("updated_at", DateField)
    ]
    Constructor = shopify.CollectionListing
    Create_Keys = ["collection_id"]

    def __init__(self, listing=[]):
        FieldEditor.__init__(self, "Collection Listing Editor", listing)

    def onCreateClk(self):
        dict = self.toDict()
        listing = self.Constructor()
        listing.collection_id = dict["collection_id"]
        listing.save()
        showErrorMessagesOfObject(listing)
