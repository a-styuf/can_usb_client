# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'can_usb_bridge_client_widget.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1352, 702)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(820, 550))
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.scrollArea.setLineWidth(1)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.scrollArea.setObjectName("scrollArea")
        self.unitsSArea = QtWidgets.QWidget()
        self.unitsSArea.setGeometry(QtCore.QRect(0, 0, 801, 690))
        self.unitsSArea.setObjectName("unitsSArea")
        self.scrollArea.setWidget(self.unitsSArea)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(5)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.dltUnitNumSBox = QtWidgets.QSpinBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dltUnitNumSBox.sizePolicy().hasHeightForWidth())
        self.dltUnitNumSBox.setSizePolicy(sizePolicy)
        self.dltUnitNumSBox.setMinimumSize(QtCore.QSize(0, 30))
        self.dltUnitNumSBox.setObjectName("dltUnitNumSBox")
        self.gridLayout_2.addWidget(self.dltUnitNumSBox, 1, 1, 1, 1)
        self.dltAllUnitsPButt = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dltAllUnitsPButt.sizePolicy().hasHeightForWidth())
        self.dltAllUnitsPButt.setSizePolicy(sizePolicy)
        self.dltAllUnitsPButt.setMinimumSize(QtCore.QSize(130, 30))
        self.dltAllUnitsPButt.setObjectName("dltAllUnitsPButt")
        self.gridLayout_2.addWidget(self.dltAllUnitsPButt, 2, 0, 1, 2)
        self.saveCfgPButt = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveCfgPButt.sizePolicy().hasHeightForWidth())
        self.saveCfgPButt.setSizePolicy(sizePolicy)
        self.saveCfgPButt.setMinimumSize(QtCore.QSize(130, 30))
        self.saveCfgPButt.setObjectName("saveCfgPButt")
        self.gridLayout_2.addWidget(self.saveCfgPButt, 5, 0, 1, 2)
        self.line_9 = QtWidgets.QFrame(Form)
        self.line_9.setMinimumSize(QtCore.QSize(0, 10))
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.gridLayout_2.addWidget(self.line_9, 3, 0, 1, 2)
        self.dltUnitPButt = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dltUnitPButt.sizePolicy().hasHeightForWidth())
        self.dltUnitPButt.setSizePolicy(sizePolicy)
        self.dltUnitPButt.setMinimumSize(QtCore.QSize(60, 30))
        self.dltUnitPButt.setObjectName("dltUnitPButt")
        self.gridLayout_2.addWidget(self.dltUnitPButt, 1, 0, 1, 1)
        self.addUnitPButton = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addUnitPButton.sizePolicy().hasHeightForWidth())
        self.addUnitPButton.setSizePolicy(sizePolicy)
        self.addUnitPButton.setMinimumSize(QtCore.QSize(200, 30))
        self.addUnitPButton.setObjectName("addUnitPButton")
        self.gridLayout_2.addWidget(self.addUnitPButton, 0, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(190, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 15, 0, 1, 2)
        self.loadCfgPButt = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadCfgPButt.sizePolicy().hasHeightForWidth())
        self.loadCfgPButt.setSizePolicy(sizePolicy)
        self.loadCfgPButt.setMinimumSize(QtCore.QSize(130, 30))
        self.loadCfgPButt.setObjectName("loadCfgPButt")
        self.gridLayout_2.addWidget(self.loadCfgPButt, 4, 0, 1, 2)
        self.cycleStartPButton = QtWidgets.QPushButton(Form)
        self.cycleStartPButton.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleStartPButton.setObjectName("cycleStartPButton")
        self.gridLayout_2.addWidget(self.cycleStartPButton, 8, 0, 1, 2)
        self.line_10 = QtWidgets.QFrame(Form)
        self.line_10.setMinimumSize(QtCore.QSize(0, 10))
        self.line_10.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.gridLayout_2.addWidget(self.line_10, 6, 0, 1, 2)
        self.cycleElapsedTimeEdit = QtWidgets.QTimeEdit(Form)
        self.cycleElapsedTimeEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleElapsedTimeEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.cycleElapsedTimeEdit.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.cycleElapsedTimeEdit.setObjectName("cycleElapsedTimeEdit")
        self.gridLayout_2.addWidget(self.cycleElapsedTimeEdit, 12, 1, 1, 1)
        self.cycleIntervalSBox_3 = QtWidgets.QDoubleSpinBox(Form)
        self.cycleIntervalSBox_3.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleIntervalSBox_3.setDecimals(1)
        self.cycleIntervalSBox_3.setMinimum(0.7)
        self.cycleIntervalSBox_3.setMaximum(100000.0)
        self.cycleIntervalSBox_3.setSingleStep(0.1)
        self.cycleIntervalSBox_3.setProperty("value", 0.7)
        self.cycleIntervalSBox_3.setObjectName("cycleIntervalSBox_3")
        self.gridLayout_2.addWidget(self.cycleIntervalSBox_3, 10, 1, 1, 1)
        self.cycleIntervalLabel_3 = QtWidgets.QLabel(Form)
        self.cycleIntervalLabel_3.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleIntervalLabel_3.setObjectName("cycleIntervalLabel_3")
        self.gridLayout_2.addWidget(self.cycleIntervalLabel_3, 10, 0, 1, 1)
        self.cycleNumLabel_3 = QtWidgets.QLabel(Form)
        self.cycleNumLabel_3.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleNumLabel_3.setObjectName("cycleNumLabel_3")
        self.gridLayout_2.addWidget(self.cycleNumLabel_3, 11, 0, 1, 1)
        self.cycleStopPButton = QtWidgets.QPushButton(Form)
        self.cycleStopPButton.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleStopPButton.setObjectName("cycleStopPButton")
        self.gridLayout_2.addWidget(self.cycleStopPButton, 14, 0, 1, 2)
        self.cycleFullTimeLabel_3 = QtWidgets.QLabel(Form)
        self.cycleFullTimeLabel_3.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleFullTimeLabel_3.setObjectName("cycleFullTimeLabel_3")
        self.gridLayout_2.addWidget(self.cycleFullTimeLabel_3, 12, 0, 1, 1)
        self.cycleNumSBox_3 = QtWidgets.QSpinBox(Form)
        self.cycleNumSBox_3.setMinimumSize(QtCore.QSize(0, 30))
        self.cycleNumSBox_3.setMinimum(1)
        self.cycleNumSBox_3.setMaximum(100000)
        self.cycleNumSBox_3.setProperty("value", 100)
        self.cycleNumSBox_3.setObjectName("cycleNumSBox_3")
        self.gridLayout_2.addWidget(self.cycleNumSBox_3, 11, 1, 1, 1)
        self.cyclePrBar = QtWidgets.QProgressBar(Form)
        self.cyclePrBar.setMinimumSize(QtCore.QSize(0, 30))
        self.cyclePrBar.setProperty("value", 0)
        self.cyclePrBar.setObjectName("cyclePrBar")
        self.gridLayout_2.addWidget(self.cyclePrBar, 13, 0, 1, 2)
        self.connectionPButton = QtWidgets.QPushButton(Form)
        self.connectionPButton.setEnabled(True)
        self.connectionPButton.setFlat(False)
        self.connectionPButton.setObjectName("connectionPButton")
        self.gridLayout_2.addWidget(self.connectionPButton, 16, 0, 1, 2)
        self.devIDLEdit = QtWidgets.QLineEdit(Form)
        self.devIDLEdit.setEnabled(True)
        self.devIDLEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.devIDLEdit.setText("")
        self.devIDLEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.devIDLEdit.setObjectName("devIDLEdit")
        self.gridLayout_2.addWidget(self.devIDLEdit, 17, 0, 1, 2)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 1, 1, 1)
        self.dataTWidget = QtWidgets.QTableWidget(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataTWidget.sizePolicy().hasHeightForWidth())
        self.dataTWidget.setSizePolicy(sizePolicy)
        self.dataTWidget.setMinimumSize(QtCore.QSize(250, 0))
        self.dataTWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.dataTWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.dataTWidget.setWordWrap(False)
        self.dataTWidget.setRowCount(20)
        self.dataTWidget.setObjectName("dataTWidget")
        self.dataTWidget.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        item.setText("Имя")
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.dataTWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignVCenter)
        font = QtGui.QFont()
        font.setPointSize(7)
        item.setFont(font)
        self.dataTWidget.setHorizontalHeaderItem(1, item)
        self.dataTWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.dataTWidget.horizontalHeader().setDefaultSectionSize(0)
        self.dataTWidget.horizontalHeader().setMinimumSectionSize(150)
        self.dataTWidget.horizontalHeader().setStretchLastSection(True)
        self.dataTWidget.verticalHeader().setDefaultSectionSize(30)
        self.dataTWidget.verticalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.dataTWidget, 0, 2, 1, 1)
        self.gridLayout.setColumnMinimumWidth(2, 1)
        self.gridLayout.setColumnStretch(2, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.dltAllUnitsPButt.setText(_translate("Form", "Удалить все"))
        self.saveCfgPButt.setText(_translate("Form", "Сохранить"))
        self.dltUnitPButt.setText(_translate("Form", "Удалить"))
        self.addUnitPButton.setText(_translate("Form", "Добавить"))
        self.loadCfgPButt.setText(_translate("Form", "Загрузить"))
        self.cycleStartPButton.setText(_translate("Form", "Запуск циклического опроса"))
        self.cycleElapsedTimeEdit.setDisplayFormat(_translate("Form", "H:mm:ss"))
        self.cycleIntervalLabel_3.setText(_translate("Form", "Интервал, с"))
        self.cycleNumLabel_3.setText(_translate("Form", "Количество, шт"))
        self.cycleStopPButton.setText(_translate("Form", "Оставновить цикл"))
        self.cycleFullTimeLabel_3.setText(_translate("Form", "Осталось , c"))
        self.connectionPButton.setText(_translate("Form", "Подключение"))
        self.devIDLEdit.setPlaceholderText(_translate("Form", "USB-CAN device ID"))
        item = self.dataTWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Значение"))
