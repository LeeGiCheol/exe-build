# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QProgressBar, QPushButton,
    QSizePolicy, QTextBrowser, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(583, 409)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.general_construction_excel_button = QPushButton(Form)
        self.general_construction_excel_button.setObjectName(u"general_construction_excel_button")

        self.gridLayout_2.addWidget(self.general_construction_excel_button, 0, 1, 1, 1)

        self.franchise_excel_download_button = QPushButton(Form)
        self.franchise_excel_download_button.setObjectName(u"franchise_excel_download_button")
        self.franchise_excel_download_button.setMaximumSize(QSize(16777215, 16777215))
        self.franchise_excel_download_button.setIconSize(QSize(16, 16))

        self.gridLayout_2.addWidget(self.franchise_excel_download_button, 0, 0, 1, 1)

        self.exit_button = QPushButton(Form)
        self.exit_button.setObjectName(u"exit_button")

        self.gridLayout_2.addWidget(self.exit_button, 1, 1, 1, 1)

        self.stop_button = QPushButton(Form)
        self.stop_button.setObjectName(u"stop_button")

        self.gridLayout_2.addWidget(self.stop_button, 1, 0, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.progress_bar = QProgressBar(Form)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)

        self.gridLayout.addWidget(self.progress_bar, 1, 0, 1, 1)

        self.contents = QTextBrowser(Form)
        self.contents.setObjectName(u"contents")

        self.gridLayout.addWidget(self.contents, 2, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.general_construction_excel_button.setText(QCoreApplication.translate("Form", u"\uc885\ud569\uac74\uc124 \uc5d1\uc140 \ub2e4\uc6b4\ub85c\ub4dc", None))
        self.franchise_excel_download_button.setText(QCoreApplication.translate("Form", u"\ud504\ub79c\ucc28\uc774\uc988 \uc5d1\uc140 \ub2e4\uc6b4\ub85c\ub4dc", None))
        self.exit_button.setText(QCoreApplication.translate("Form", u"\uc885\ub8cc", None))
        self.stop_button.setText(QCoreApplication.translate("Form", u"\uc911\uc9c0", None))
    # retranslateUi

