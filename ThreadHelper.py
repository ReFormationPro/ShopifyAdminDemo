# This Python file uses the following encoding: utf-8
import threading
from PyQt5 import QtCore

class ThreadHelper():
    Threads = []
    def runThreaded(function):
        thread = QtCore.QThread()
        def tmp():
            function()
            thread.quit()
            ThreadHelper.Threads = list(filter(lambda x: not x.isFinished(),
                                          ThreadHelper.Threads))
        thread.started.connect(tmp)
        thread.start()
        ThreadHelper.Threads.append(thread)
