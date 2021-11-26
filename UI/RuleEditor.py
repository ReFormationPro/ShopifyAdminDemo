# This Python file uses the following encoding: utf-8
from PyQt5 import QtCore, QtWidgets, QtGui
from UI.UIRuleEditor import Ui_Form as UI_RuleEditor
from UI.UIRuleField import Ui_Form as UI_RuleField
import shopify
from Errors import showErrorMessagesOfObject

class RuleField(QtWidgets.QWidget):
    ColumnText = ["title", "type", "vendor", "variant_title"]
    ColumnNumber = ["variant_compare_at_price", "variant_weight", "variant_inventory", "variant_price"]
    ColumnEquals = ["tag"]
    RelationNumber = ["greater_than", "less_than", "equals", "not_equals"]
    RelationText = ["equals", "not_equals", "starts_with", "ends_with", "contains", "not_contains"]
    def __init__(self, parent, column=None, relation=None, condition=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = UI_RuleField()
        self.ui.setupUi(self)
        columnItems = self.ColumnText + self.ColumnNumber + self.ColumnEquals
        self.ui.comboL.addItems(columnItems)
        self.ui.comboL.activated[str].connect(self.onColumnChange)
        self.onColumnChange()
        if column != None and column in columnItems:
            self.ui.comboL.setCurrentIndex(columnItems.index(column))
            self.onColumnChange()
            comboMItems = [self.ui.comboM.itemText(i) for i in range(self.ui.comboM.count())]
            try:
                self.ui.comboM.setCurrentIndex(comboMItems.index(relation))
            except:
                pass
            self.ui.data.setText(condition)

    def getData(self):
        return self.ui.data.toPlainText()

    def getOutput(self):
        obj = {"column": self.ui.comboL.currentText(),
               "relation": self.ui.comboM.currentText(),
               "condition": self.getData()}
        return obj

    def isToDelete(self):
        return self.ui.delete.isChecked()

    def onColumnChange(self):
        curr = self.ui.comboL.currentText()
        if curr in self.ColumnText:
            self.ui.comboM.clear()
            self.ui.comboM.addItems(self.RelationText)
        elif curr in self.ColumnNumber:
            self.ui.comboM.clear()
            self.ui.comboM.addItems(self.RelationNumber)
            if curr == "variant_inventory": #"not_equals" does not work with variant_inventory
                self.ui.comboM.removeItem(3)
        else:   #Equals works only with "tag"
            self.ui.comboM.clear()
            self.ui.comboM.addItems(["equals"])


class RuleEditor(QtWidgets.QWidget):
    def __init__(self, smartCollectionIds, rules=None):
        QtWidgets.QWidget.__init__(self)
        self.smartCollectionIds = smartCollectionIds
        self.ui = UI_RuleEditor()
        self.ui.setupUi(self)
        self.ui.verticalLayout.setAlignment (QtCore.Qt.AlignTop)
        self.setWindowTitle("Rule Editor")
        self.rules = []
        self.ui.addBtn.clicked.connect(self.addRule)
        self.ui.deleteBtn.clicked.connect(self.deleteRules)
        self.ui.saveBtn.clicked.connect(self.saveChanges)
        if rules == None:
            self.addRule()
        else:
            self.loadRules(rules)

    def show(self, parentWindow=None):
        self.parentWindow = parentWindow
        QtWidgets.QWidget.show(self)

    def closeEvent(self, event):
        if self.parentWindow != None:
            self.parentWindow.onSubwindowClose()
        event.accept()

    def loadRules(self, rules):
        for r in rules:
            self.addRule(r.column, r.relation, r.condition)

    def addRule(self, column=None, relation=None, condition=None):
        rule = RuleField(self.ui.ruleList, column, relation, condition)
        self.ui.verticalLayout.addWidget(rule)
        self.rules.append(rule)

    def deleteRules(self):
        toDelete = filter(lambda r: r.isToDelete(), self.rules)
        for r in toDelete:
            r.setParent(None)
            self.rules.remove(r)

    def saveChanges(self):
        rules = list(map(lambda rf: rf.getOutput(), self.rules))
        print(rules)
        for id in self.smartCollectionIds:
            sc = shopify.SmartCollection()
            sc.id = id
            sc.rules = rules
            sc.save()
            showErrorMessagesOfObject(sc)
