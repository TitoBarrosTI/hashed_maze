# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'master_pass_hashed_maze.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QProgressBar, QPushButton,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(876, 692)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 565))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(50, 130, 151, 16))
        self.edtMasterPass = QLineEdit(self.frame)
        self.edtMasterPass.setObjectName(u"edtMasterPass")
        self.edtMasterPass.setGeometry(QRect(50, 150, 342, 21))
        self.edtMasterPass.setEchoMode(QLineEdit.EchoMode.Password)
        self.btnAddMasterPass = QPushButton(self.frame)
        self.btnAddMasterPass.setObjectName(u"btnAddMasterPass")
        self.btnAddMasterPass.setGeometry(QRect(294, 180, 97, 24))
        self.lblCaptionOpenTextFile_3 = QLabel(self.frame)
        self.lblCaptionOpenTextFile_3.setObjectName(u"lblCaptionOpenTextFile_3")
        self.lblCaptionOpenTextFile_3.setGeometry(QRect(30, 39, 281, 22))
        self.lblCaptionOpenTextFile_3.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.lblIconUUID = QLabel(self.frame)
        self.lblIconUUID.setObjectName(u"lblIconUUID")
        self.lblIconUUID.setGeometry(QRect(765, 20, 80, 81))
        self.line_4 = QFrame(self.frame)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setGeometry(QRect(20, 60, 571, 16))
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)
        self.lblMsg = QLabel(self.frame)
        self.lblMsg.setObjectName(u"lblMsg")
        self.lblMsg.setGeometry(QRect(56, 182, 232, 16))
        self.pBar = QProgressBar(self.frame)
        self.pBar.setObjectName(u"pBar")
        self.pBar.setGeometry(QRect(430, 150, 118, 23))
        self.pBar.setMaximum(0)
        self.pBar.setValue(-1)
        self.lblInstructions = QLabel(self.frame)
        self.lblInstructions.setObjectName(u"lblInstructions")
        self.lblInstructions.setGeometry(QRect(40, 230, 441, 240))
        self.lblInstructions.setTextFormat(Qt.TextFormat.RichText)
        self.lblInstructions.setWordWrap(False)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(40, 520, 101, 20))
        self.label_2.setStyleSheet(u"")
        self.btnShowPWD = QPushButton(self.frame)
        self.btnShowPWD.setObjectName(u"btnShowPWD")
        self.btnShowPWD.setGeometry(QRect(397, 149, 23, 24))
        self.btnShowPWD.setCheckable(False)
        self.btnShowPWD.setFlat(False)
        self.lblCFGDatabaseDirectory = QLabel(self.frame)
        self.lblCFGDatabaseDirectory.setObjectName(u"lblCFGDatabaseDirectory")
        self.lblCFGDatabaseDirectory.setGeometry(QRect(40, 536, 801, 16))
        self.lblCFGDatabaseDirectory.setStyleSheet(u"QLabel{\n"
"	color:rgb(20, 182, 71)\n"
"}")

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.btnOk = QPushButton(Form)
        self.btnOk.setObjectName(u"btnOk")
        self.btnOk.setStyleSheet(u"QPushButton {\n"
"    padding: 0 32px;\n"
"}")

        self.horizontalLayout_2.addWidget(self.btnOk)


        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Register password - Hashed Maze", None))
        self.label.setText(QCoreApplication.translate("Form", u"Master password:", None))
        self.btnAddMasterPass.setText(QCoreApplication.translate("Form", u"save password", None))
        self.lblCaptionOpenTextFile_3.setText(QCoreApplication.translate("Form", u"Generate your vault master password.", None))
        self.lblIconUUID.setText(QCoreApplication.translate("Form", u"ICON", None))
        self.lblMsg.setText(QCoreApplication.translate("Form", u"...", None))
        self.lblInstructions.setText(QCoreApplication.translate("Form", u"<html><head/><body><p>&lt;b&gt;Create a strong password&lt;/b&gt;&lt;br/&gt;&lt;br/&gt;</p><p>Use at least 12 characters \u2014 longer passwords are more secure.&lt;br/&gt;&lt;br/&gt;</p><p>Avoid common patterns like 123456 or qwerty.&lt;br/&gt;&lt;br/&gt;</p><p>Don't use personal details like your name or birth date.&lt;br/&gt;&lt;br/&gt;</p><p>A good strategy is to combine random words or create a memorable phrase.&lt;br/&gt;&lt;br/&gt;</p><p>Try mixing uppercase letters, lowercase letters, numbers, and symbols.&lt;br/&gt;&lt;br/&gt;</p><p>Avoid reusing passwords across different accounts.&lt;br/&gt;&lt;br/&gt;</p><p>Keep your password private and change it if you think it's been exposed.</p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"database directory:", None))
#if QT_CONFIG(tooltip)
        self.btnShowPWD.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>show/hide password</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnShowPWD.setText("")
        self.lblCFGDatabaseDirectory.setText(QCoreApplication.translate("Form", u"database directory:", None))
        self.btnOk.setText(QCoreApplication.translate("Form", u"OK", None))
    # retranslateUi

