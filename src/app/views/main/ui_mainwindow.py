from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtGui import (
    QCursor,
    QIcon,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from app.config import resource_path


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        MainWindow.setMinimumSize(QSize(1280, 720))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.sidebar = QFrame(self.centralwidget)
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumSize(QSize(200, 0))
        self.sidebar.setMaximumSize(QSize(200, 16777215))
        self.sidebar.setFrameShape(QFrame.StyledPanel)
        self.sidebar.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.sidebar)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 25, -1, -1)
        self.label_2 = QLabel(self.sidebar)
        self.label_2.setObjectName("label_2")
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_2)

        self.verticalSpacer_2 = QSpacerItem(
            20, 114, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.pushButton = QPushButton(self.sidebar)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton.setLayoutDirection(Qt.LeftToRight)
        icon = QIcon()
        icon.addFile(
            str(resource_path("icons", "analista-de-datos.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton.setIcon(icon)

        self.verticalLayout_2.addWidget(self.pushButton)

        self.pushButton_3 = QPushButton(self.sidebar)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_3.setStyleSheet("")
        icon1 = QIcon()
        icon1.addFile(
            str(resource_path("icons", "tabla.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_3.setIcon(icon1)

        self.verticalLayout_2.addWidget(self.pushButton_3)

        self.pushButton_8 = QPushButton(self.sidebar)
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_8.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_8.setStyleSheet("")
        icon55 = QIcon()
        icon55.addFile(
            str(resource_path("icons", "pizza.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_8.setIcon(icon55)

        self.verticalLayout_2.addWidget(self.pushButton_8)

        self.pushButton_5 = QPushButton(self.sidebar)
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_5.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_5.setStyleSheet("")
        icon3 = QIcon()
        icon3.addFile(
            str(resource_path("icons", "informe.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_5.setIcon(icon3)

        self.verticalLayout_2.addWidget(self.pushButton_5)

        self.pushButton_6 = QPushButton(self.sidebar)
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_6.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_6.setStyleSheet("")
        icon4 = QIcon()
        icon4.addFile(
            str(resource_path("icons", "dolar.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_6.setIcon(icon4)

        self.verticalLayout_2.addWidget(self.pushButton_6)

        self.pushButton_7 = QPushButton(self.sidebar)
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_7.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_7.setStyleSheet("")
        icon5 = QIcon()
        icon5.addFile(
            str(resource_path("icons", "agregar-usuario.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_7.setIcon(icon5)

        self.verticalLayout_2.addWidget(self.pushButton_7)

        self.verticalSpacer_3 = QSpacerItem(
            20, 115, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.pushButton_9 = QPushButton(self.sidebar)
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_9.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pushButton_9.setStyleSheet("")
        icon6 = QIcon()
        icon6.addFile(
            str(resource_path("icons", "cerrar-sesion.png")),
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.pushButton_9.setIcon(icon6)

        self.verticalLayout_2.addWidget(self.pushButton_9)

        self.horizontalLayout.addWidget(self.sidebar)

        self.main = QFrame(self.centralwidget)
        self.main.setObjectName("main")
        self.main.setFrameShape(QFrame.StyledPanel)
        self.main.setFrameShadow(QFrame.Raised)

        self.horizontalLayout.addWidget(self.main)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("MainWindow", "Mesas", None)
        )
        self.pushButton.setText(
            QCoreApplication.translate("MainWindow", "Dashboard", None)
        )
        self.pushButton_3.setText(
            QCoreApplication.translate("MainWindow", "Mesas", None)
        )
        self.pushButton_8.setText(
            QCoreApplication.translate("MainWindow", "Inventario", None)
        )
        self.pushButton_5.setText(
            QCoreApplication.translate("MainWindow", "Reportes", None)
        )
        self.pushButton_6.setText(
            QCoreApplication.translate("MainWindow", "Tasa del Dia", None)
        )
        self.pushButton_7.setText(
            QCoreApplication.translate("MainWindow", "Usuarios", None)
        )
        self.pushButton_9.setText(
            QCoreApplication.translate(
                "MainWindow", "Cerrar Sesi\u00f3n", None
            )
        )

    # retranslateUi
