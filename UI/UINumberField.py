# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI\NumberField.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(460, 35)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Frame.sizePolicy().hasHeightForWidth())
        Frame.setSizePolicy(sizePolicy)
        Frame.setMinimumSize(QtCore.QSize(460, 35))
        Frame.setMaximumSize(QtCore.QSize(460, 35))
        Frame.setBaseSize(QtCore.QSize(0, 45))
        self.horizontalLayout = QtWidgets.QHBoxLayout(Frame)
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(220, 0))
        self.label.setMaximumSize(QtCore.QSize(220, 25))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.text = QtWidgets.QLineEdit(Frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.text.setMinimumSize(QtCore.QSize(230, 0))
        self.text.setMaximumSize(QtCore.QSize(230, 25))
        self.text.setBaseSize(QtCore.QSize(0, 40))
        self.text.setObjectName("text")
        self.horizontalLayout.addWidget(self.text)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.label.setText(_translate("Frame", "label "))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Frame = QtWidgets.QFrame()
    ui = Ui_Frame()
    ui.setupUi(Frame)
    Frame.show()
    sys.exit(app.exec_())
