# This Python file uses the following encoding: utf-8

from PyQt5 import QtWidgets
import traceback

error_dialog = None
def showErrorMessagesOfObject(obj):
    global error_dialog
    errors = obj.errors.full_messages()
    if len(errors) != 0:
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage("\n".join(errors))
        print(errors)

def showException(ex):
    global error_dialog
    error_dialog = QtWidgets.QErrorMessage()
    error_dialog.showMessage(str(ex))
    print(ex)
    traceback.print_exc()

def showErrorMessage(msg):
    global error_dialog
    error_dialog = QtWidgets.QErrorMessage()
    error_dialog.showMessage(msg)
    print(msg)
