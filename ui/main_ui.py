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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QProgressBar,
    QPushButton, QRadioButton, QSizePolicy, QTextBrowser,
    QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(833, 635)
        self.gridLayout_3 = QGridLayout(Form)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
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

        self.label_running = QLabel(Form)
        self.label_running.setObjectName(u"label_running")

        self.verticalLayout_3.addWidget(self.label_running)


        self.gridLayout_3.addLayout(self.verticalLayout_3, 3, 0, 1, 1)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_5 = QLabel(Form)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_2.addWidget(self.label_5, 7, 0, 1, 1)

        self.label_7 = QLabel(Form)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setStyleSheet(u"font-weight: bold;")

        self.gridLayout_2.addWidget(self.label_7, 6, 2, 1, 1)

        self.label_2 = QLabel(Form)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_6 = QLabel(Form)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 11, 0, 1, 1)

        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(799, 1))
        self.frame.setStyleSheet(u"background-color: #808080;")
        self.frame.setFrameShape(QFrame.HLine)
        self.frame.setFrameShadow(QFrame.Raised)

        self.gridLayout_2.addWidget(self.frame, 5, 0, 1, 3)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 10, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.category1_list_widget = QListWidget(Form)
        self.category1_list_widget.setObjectName(u"category1_list_widget")

        self.horizontalLayout_2.addWidget(self.category1_list_widget)

        self.category2_list_widget = QListWidget(Form)
        self.category2_list_widget.setObjectName(u"category2_list_widget")
        self.category2_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.horizontalLayout_2.addWidget(self.category2_list_widget)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.use_button = QPushButton(Form)
        self.use_button.setObjectName(u"use_button")

        self.verticalLayout_7.addWidget(self.use_button)

        self.disable_button = QPushButton(Form)
        self.disable_button.setObjectName(u"disable_button")

        self.verticalLayout_7.addWidget(self.disable_button)


        self.horizontalLayout_2.addLayout(self.verticalLayout_7)

        self.selected_category_list_widget = QListWidget(Form)
        self.selected_category_list_widget.setObjectName(u"selected_category_list_widget")
        self.selected_category_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.horizontalLayout_2.addWidget(self.selected_category_list_widget)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 7, 2, 1, 1)

        self.excel_name = QLineEdit(Form)
        self.excel_name.setObjectName(u"excel_name")

        self.gridLayout_2.addWidget(self.excel_name, 10, 2, 1, 1)

        self.musinsa_category_type_label = QLabel(Form)
        self.musinsa_category_type_label.setObjectName(u"musinsa_category_type_label")

        self.gridLayout_2.addWidget(self.musinsa_category_type_label, 1, 0, 1, 1)

        self.progress_bar = QProgressBar(Form)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(0)

        self.gridLayout_2.addWidget(self.progress_bar, 11, 2, 1, 1)

        self.musinsa_category_type_sale_check = QCheckBox(Form)
        self.musinsa_category_type_sale_check.setObjectName(u"musinsa_category_type_sale_check")

        self.gridLayout_2.addWidget(self.musinsa_category_type_sale_check, 2, 2, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.count_input = QLineEdit(Form)
        self.count_input.setObjectName(u"count_input")

        self.horizontalLayout.addWidget(self.count_input)

        self.reset_button = QPushButton(Form)
        self.reset_button.setObjectName(u"reset_button")

        self.horizontalLayout.addWidget(self.reset_button)

        self.stop_button = QPushButton(Form)
        self.stop_button.setObjectName(u"stop_button")

        self.horizontalLayout.addWidget(self.stop_button)


        self.gridLayout_2.addLayout(self.horizontalLayout, 3, 2, 1, 1)

        self.sale_label = QLabel(Form)
        self.sale_label.setObjectName(u"sale_label")

        self.gridLayout_2.addWidget(self.sale_label, 2, 0, 1, 1)

        self.frame_2 = QFrame(Form)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 1))
        self.frame_2.setStyleSheet(u"background-color: #808080;")
        self.frame_2.setFrameShape(QFrame.HLine)
        self.frame_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.frame_2, 8, 0, 1, 3)

        self.label_3 = QLabel(Form)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.musinsa_male_radio_group = QGroupBox(Form)
        self.musinsa_male_radio_group.setObjectName(u"musinsa_male_radio_group")
        self.horizontalLayout_4 = QHBoxLayout(self.musinsa_male_radio_group)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.musinsa_category_type_male_radio = QRadioButton(self.musinsa_male_radio_group)
        self.musinsa_category_type_male_radio.setObjectName(u"musinsa_category_type_male_radio")
        self.musinsa_category_type_male_radio.setChecked(True)

        self.horizontalLayout_4.addWidget(self.musinsa_category_type_male_radio)

        self.musinsa_category_type_female_radio = QRadioButton(self.musinsa_male_radio_group)
        self.musinsa_category_type_female_radio.setObjectName(u"musinsa_category_type_female_radio")

        self.horizontalLayout_4.addWidget(self.musinsa_category_type_female_radio)


        self.gridLayout_2.addWidget(self.musinsa_male_radio_group, 1, 2, 1, 1)

        self.type_group = QGroupBox(Form)
        self.type_group.setObjectName(u"type_group")
        self.horizontalLayout_7 = QHBoxLayout(self.type_group)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.musinsa_radio_button = QRadioButton(self.type_group)
        self.musinsa_radio_button.setObjectName(u"musinsa_radio_button")
        self.musinsa_radio_button.setChecked(True)

        self.horizontalLayout_7.addWidget(self.musinsa_radio_button)

        self.ably_radio_button = QRadioButton(self.type_group)
        self.ably_radio_button.setObjectName(u"ably_radio_button")

        self.horizontalLayout_7.addWidget(self.ably_radio_button)


        self.gridLayout_2.addWidget(self.type_group, 0, 2, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 0, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.contents.setPlaceholderText(QCoreApplication.translate("Form", u"\uc791\uc5c5\uc911\uc778 \ub0b4\uc6a9\uc774 \ubcf4\uc5ec\uc9c8 \uacf5\uac04\uc785\ub2c8\ub2e4.", None))
        self.excel_save_button.setText(QCoreApplication.translate("Form", u"\uc5d1\uc140 \uc800\uc7a5", None))
        self.exit_button.setText(QCoreApplication.translate("Form", u"\uc885\ub8cc", None))
        self.label_running.setText("")
        self.label_5.setText(QCoreApplication.translate("Form", u"\uce74\ud14c\uace0\ub9ac", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"* \uc870\ud68c\ud560 \uce74\ud14c\uace0\ub9ac\ub97c \uc120\ud0dd \ud6c4 \ud654\uc0b4\ud45c\ub97c \ub20c\ub7ec\uc8fc\uc138\uc694.", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\uac80\uc0c9\uac74\uc218", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\uc870\ud68c \uc9c4\ud589\ub3c4", None))
        self.label.setText(QCoreApplication.translate("Form", u"\ud30c\uc77c\uba85", None))
        self.use_button.setText(QCoreApplication.translate("Form", u"\u2192", None))
        self.disable_button.setText(QCoreApplication.translate("Form", u"\u2190", None))
        self.excel_name.setPlaceholderText(QCoreApplication.translate("Form", u"\ubbf8\uc785\ub825 \uc2dc \ub79c\ub364\ud55c \uac12\uc73c\ub85c \ud30c\uc77c\uba85\uc774 \uc800\uc7a5\ub429\ub2c8\ub2e4.", None))
        self.musinsa_category_type_label.setText(QCoreApplication.translate("Form", u"\ubb34\uc2e0\uc0ac \uad6c\ubd84", None))
        self.musinsa_category_type_sale_check.setText(QCoreApplication.translate("Form", u"\uc138\uc77c", None))
        self.count_input.setPlaceholderText(QCoreApplication.translate("Form", u"\uac80\uc0c9\ud560 \uac74\uc218\ub97c \uc785\ub825\ud574\uc8fc\uc138\uc694.", None))
        self.reset_button.setText(QCoreApplication.translate("Form", u"\ucd08\uae30\ud654", None))
        self.stop_button.setText(QCoreApplication.translate("Form", u"\uc911\uc9c0", None))
        self.sale_label.setText(QCoreApplication.translate("Form", u"\uc138\uc77c\uc5ec\ubd80", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\uad6c\ubd84", None))
        self.musinsa_category_type_male_radio.setText(QCoreApplication.translate("Form", u"\ub0a8\uc790", None))
        self.musinsa_category_type_female_radio.setText(QCoreApplication.translate("Form", u"\uc5ec\uc790", None))
        self.musinsa_radio_button.setText(QCoreApplication.translate("Form", u"\ubb34\uc2e0\uc0ac", None))
        self.ably_radio_button.setText(QCoreApplication.translate("Form", u"\uc5d0\uc774\ube14\ub9ac", None))
    # retranslateUi

