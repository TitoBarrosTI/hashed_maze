# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_window_hashed_maze.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QGridLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(424, 229)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.frame = QFrame(Dialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.edtPWD = QLineEdit(self.frame)
        self.edtPWD.setObjectName(u"edtPWD")
        self.edtPWD.setGeometry(QRect(49, 68, 251, 21))
        self.edtPWD.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.edtPWD.setEchoMode(QLineEdit.EchoMode.Password)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(49, 47, 141, 16))
        self.lblMsg = QLabel(self.frame)
        self.lblMsg.setObjectName(u"lblMsg")
        self.lblMsg.setGeometry(QRect(49, 97, 331, 16))
        self.lblIconPad = QLabel(self.frame)
        self.lblIconPad.setObjectName(u"lblIconPad")
        self.lblIconPad.setGeometry(QRect(330, 10, 41, 41))
        self.lblIconPad.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btnShowPWD = QPushButton(self.frame)
        self.btnShowPWD.setObjectName(u"btnShowPWD")
        self.btnShowPWD.setGeometry(QRect(303, 67, 23, 24))
        self.lblWarning = QLabel(self.frame)
        self.lblWarning.setObjectName(u"lblWarning")
        self.lblWarning.setGeometry(QRect(49, 119, 341, 41))
        self.lblWarning.setStyleSheet(u"lblWarning{\n"
"	color: rgb(255, 255, 0)\n"
"	visibility:hidden;\n"
"}")
        self.lblWarning.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.btnBox = QDialogButtonBox(Dialog)
        self.btnBox.setObjectName(u"btnBox")
        self.btnBox.setOrientation(Qt.Orientation.Horizontal)
        self.btnBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.btnBox, 1, 0, 1, 1)


        self.retranslateUi(Dialog)
        self.btnBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Login | Hashed Maze", None))
        self.edtPWD.setText("")
        self.label.setText(QCoreApplication.translate("Dialog", u"Master password:", None))
        self.lblMsg.setText(QCoreApplication.translate("Dialog", u"...", None))
        self.lblIconPad.setText(QCoreApplication.translate("Dialog", u"ICON", None))
#if QT_CONFIG(tooltip)
        self.btnShowPWD.setToolTip(QCoreApplication.translate("Dialog", u"<html><head/><body><p>show/hide password</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.btnShowPWD.setText("")
        self.lblWarning.setText(QCoreApplication.translate("Dialog", u"The database will be wiped after three unsuccessful attempts", None))
    # retranslateUi

