# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'daangn_land_main.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QProgressBar, QPushButton,
    QSizePolicy, QTextBrowser, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(825, 635)
        self.gridLayout_3 = QGridLayout(Form)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)

        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"font-weight: bold;")

        self.gridLayout_2.addWidget(self.label_7, 3, 2, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 11, 0, 1, 1)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 7, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.one_room_check_box = QCheckBox(Form)
        self.one_room_check_box.setObjectName(u"one_room_check_box")

        self.verticalLayout_5.addWidget(self.one_room_check_box)

        self.two_room_checkbox = QCheckBox(Form)
        self.two_room_checkbox.setObjectName(u"two_room_checkbox")

        self.verticalLayout_5.addWidget(self.two_room_checkbox)

        self.officetel_check_box = QCheckBox(Form)
        self.officetel_check_box.setObjectName(u"officetel_check_box")

        self.verticalLayout_5.addWidget(self.officetel_check_box)

        self.apart_check_box = QCheckBox(Form)
        self.apart_check_box.setObjectName(u"apart_check_box")

        self.verticalLayout_5.addWidget(self.apart_check_box)

        self.store_check_box = QCheckBox(Form)
        self.store_check_box.setObjectName(u"store_check_box")

        self.verticalLayout_5.addWidget(self.store_check_box)


        self.horizontalLayout_6.addLayout(self.verticalLayout_5)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.house_check_box = QCheckBox(Form)
        self.house_check_box.setObjectName(u"house_check_box")

        self.verticalLayout_6.addWidget(self.house_check_box)

        self.office_check_box = QCheckBox(Form)
        self.office_check_box.setObjectName(u"office_check_box")

        self.verticalLayout_6.addWidget(self.office_check_box)

        self.building_check_box = QCheckBox(Form)
        self.building_check_box.setObjectName(u"building_check_box")

        self.verticalLayout_6.addWidget(self.building_check_box)

        self.factory_check_box = QCheckBox(Form)
        self.factory_check_box.setObjectName(u"factory_check_box")

        self.verticalLayout_6.addWidget(self.factory_check_box)

        self.land_check_box = QCheckBox(Form)
        self.land_check_box.setObjectName(u"land_check_box")

        self.verticalLayout_6.addWidget(self.land_check_box)


        self.horizontalLayout_6.addLayout(self.verticalLayout_6)


        self.gridLayout_2.addLayout(self.horizontalLayout_6, 7, 2, 1, 1)

        self.label_9 = QLabel(Form)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_2.addWidget(self.label_9, 14, 0, 1, 1)

        self.progressBar_2 = QProgressBar(Form)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setValue(0)

        self.gridLayout_2.addWidget(self.progressBar_2, 13, 2, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.month_check_box = QCheckBox(Form)
        self.month_check_box.setObjectName(u"month_check_box")

        self.verticalLayout_9.addWidget(self.month_check_box)

        self.borrow_check_box = QCheckBox(Form)
        self.borrow_check_box.setObjectName(u"borrow_check_box")

        self.verticalLayout_9.addWidget(self.borrow_check_box)


        self.horizontalLayout_7.addLayout(self.verticalLayout_9)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.buy_check_box = QCheckBox(Form)
        self.buy_check_box.setObjectName(u"buy_check_box")

        self.verticalLayout_12.addWidget(self.buy_check_box)

        self.short_check_box = QCheckBox(Form)
        self.short_check_box.setObjectName(u"short_check_box")

        self.verticalLayout_12.addWidget(self.short_check_box)


        self.horizontalLayout_7.addLayout(self.verticalLayout_12)


        self.gridLayout_2.addLayout(self.horizontalLayout_7, 9, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.region_input = QLineEdit(Form)
        self.region_input.setObjectName(u"region_input")

        self.horizontalLayout.addWidget(self.region_input)

        self.region_search_button = QPushButton(Form)
        self.region_search_button.setObjectName(u"region_search_button")

        self.horizontalLayout.addWidget(self.region_search_button)

        self.reset_button = QPushButton(Form)
        self.reset_button.setObjectName(u"reset_button")

        self.horizontalLayout.addWidget(self.reset_button)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 2, 1, 1)

        self.frame_4 = QFrame(Form)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(0, 1))
        self.frame_4.setStyleSheet(u"background-color: #808080;")
        self.frame_4.setFrameShape(QFrame.Shape.HLine)
        self.frame_4.setFrameShadow(QFrame.Shadow.Raised)
        self.frame_4.setLineWidth(1)

        self.gridLayout_2.addWidget(self.frame_4, 10, 0, 1, 3)

        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_4 = QLabel(Form)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 9, 0, 1, 1)

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 12, 0, 1, 1)

        self.progressBar_3 = QProgressBar(Form)
        self.progressBar_3.setObjectName(u"progressBar_3")
        self.progressBar_3.setStyleSheet(u"")
        self.progressBar_3.setValue(0)
        self.progressBar_3.setInvertedAppearance(False)

        self.gridLayout_2.addWidget(self.progressBar_3, 14, 2, 1, 1)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(799, 1))
        self.frame.setStyleSheet(u"background-color: #808080;")
        self.frame.setFrameShape(QFrame.Shape.HLine)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_2.addWidget(self.frame, 2, 0, 1, 3)

        self.frame_3 = QFrame(Form)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 1))
        self.frame_3.setStyleSheet(u"background-color: #808080;")
        self.frame_3.setFrameShape(QFrame.Shape.HLine)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout_2.addWidget(self.frame_3, 8, 0, 1, 3)

        self.label_8 = QLabel(Form)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 13, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.region_list_widget = QListWidget(Form)
        self.region_list_widget.setObjectName(u"region_list_widget")
        self.region_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.horizontalLayout_2.addWidget(self.region_list_widget)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.use_button = QPushButton(Form)
        self.use_button.setObjectName(u"use_button")

        self.verticalLayout_7.addWidget(self.use_button)

        self.disable_button = QPushButton(Form)
        self.disable_button.setObjectName(u"disable_button")

        self.verticalLayout_7.addWidget(self.disable_button)


        self.horizontalLayout_2.addLayout(self.verticalLayout_7)

        self.used_region_list_widget = QListWidget(Form)
        self.used_region_list_widget.setObjectName(u"used_region_list_widget")
        self.used_region_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.horizontalLayout_2.addWidget(self.used_region_list_widget)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 4, 2, 1, 1)

        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 1))
        self.frame_2.setStyleSheet(u"background-color: #808080;")
        self.frame_2.setFrameShape(QFrame.Shape.HLine)
        self.frame_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_2.addWidget(self.frame_2, 5, 0, 1, 3)

        self.progressBar = QProgressBar(Form)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.gridLayout_2.addWidget(self.progressBar, 12, 2, 1, 1)

        self.excel_name = QLineEdit(Form)
        self.excel_name.setObjectName(u"excel_name")

        self.gridLayout_2.addWidget(self.excel_name, 11, 2, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.contents = QTextBrowser(Form)
        self.contents.setObjectName(u"contents")

        self.verticalLayout_3.addWidget(self.contents)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.excel_save_button = QPushButton(Form)
        self.excel_save_button.setObjectName(u"excel_save_button")

        self.horizontalLayout_3.addWidget(self.excel_save_button)

        self.exit_button = QPushButton(Form)
        self.exit_button.setObjectName(u"exit_button")

        self.horizontalLayout_3.addWidget(self.exit_button)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)


        self.gridLayout_3.addLayout(self.verticalLayout_3, 3, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\uc9c0\uc5ed\uba85 \uac80\uc0c9", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"* \uc870\ud68c\ud560 \uc9c0\uc5ed\uc744 \uc120\ud0dd \ud6c4 \ud654\uc0b4\ud45c\ub97c \ub20c\ub7ec\uc8fc\uc138\uc694.", None))
        self.label.setText(QCoreApplication.translate("Form", u"\ud30c\uc77c\uba85", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\ub9e4\ubb3c \uc885\ub958", None))
        self.one_room_check_box.setText(QCoreApplication.translate("Form", u"\uc6d0\ub8f8", None))
        self.two_room_checkbox.setText(QCoreApplication.translate("Form", u"\ud22c\ub8f8 \ube4c\ub77c", None))
        self.officetel_check_box.setText(QCoreApplication.translate("Form", u"\uc624\ud53c\uc2a4\ud154", None))
        self.apart_check_box.setText(QCoreApplication.translate("Form", u"\uc544\ud30c\ud2b8", None))
        self.store_check_box.setText(QCoreApplication.translate("Form", u"\uc0c1\uac00", None))
        self.house_check_box.setText(QCoreApplication.translate("Form", u"\uc8fc\ud0dd", None))
        self.office_check_box.setText(QCoreApplication.translate("Form", u"\uc0ac\ubb34\uc2e4", None))
        self.building_check_box.setText(QCoreApplication.translate("Form", u"\uac74\ubb3c", None))
        self.factory_check_box.setText(QCoreApplication.translate("Form", u"\uacf5\uc7a5/\ucc3d\uace0", None))
        self.land_check_box.setText(QCoreApplication.translate("Form", u"\ud1a0\uc9c0", None))
        self.label_9.setText(QCoreApplication.translate("Form", u"\uc774\ubbf8\uc9c0 \ub2e4\uc6b4\ub85c\ub4dc \uc9c4\ud589\ub3c4", None))
        self.month_check_box.setText(QCoreApplication.translate("Form", u"\uc6d4\uc138", None))
        self.borrow_check_box.setText(QCoreApplication.translate("Form", u"\uc804\uc138", None))
        self.buy_check_box.setText(QCoreApplication.translate("Form", u"\ub9e4\ub9e4", None))
        self.short_check_box.setText(QCoreApplication.translate("Form", u"\ub2e8\uae30", None))
        self.region_input.setPlaceholderText(QCoreApplication.translate("Form", u"\uc9c0\uc5ed\uba85\uc744 \uac80\uc0c9 \ud6c4 \uc544\ub798\uc5d0\uc11c \uc120\ud0dd\ud574\uc8fc\uc138\uc694.", None))
        self.region_search_button.setText(QCoreApplication.translate("Form", u"\uac80\uc0c9", None))
        self.reset_button.setText(QCoreApplication.translate("Form", u"\ucd08\uae30\ud654", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"\uc9c0\uc5ed\uba85", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\uac70\ub798 \uc720\ud615", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\uc9c0\uc5ed \uc870\ud68c \uc9c4\ud589\ub3c4", None))
        self.label_8.setText(QCoreApplication.translate("Form", u"\uc218\uc9d1 \uc9c4\ud589\ub3c4 ", None))
        self.use_button.setText(QCoreApplication.translate("Form", u"\u2192", None))
        self.disable_button.setText(QCoreApplication.translate("Form", u"\u2190", None))
        self.excel_name.setPlaceholderText(QCoreApplication.translate("Form", u"\ubbf8\uc785\ub825 \uc2dc \ub2f9\uadfc\ub9c8\ucf13_\ubd80\ub3d9\uc0b0\uc815\ubcf4(\uc120\ud0dd\ud55c \uc635\uc158\uba85) \uc73c\ub85c \ud30c\uc77c\uba85\uc774 \uc800\uc7a5\ub429\ub2c8\ub2e4.", None))
        self.contents.setPlaceholderText(QCoreApplication.translate("Form", u"\uc791\uc5c5\uc911\uc778 \ub0b4\uc6a9\uc774 \ubcf4\uc5ec\uc9c8 \uacf5\uac04\uc785\ub2c8\ub2e4.", None))
        self.excel_save_button.setText(QCoreApplication.translate("Form", u"\uc5d1\uc140 \uc800\uc7a5", None))
        self.exit_button.setText(QCoreApplication.translate("Form", u"\uc885\ub8cc", None))
    # retranslateUi

