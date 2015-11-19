from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from classes import *
import gui_elements

class VendorDialog(QDialog):
    def __init__(self, mode, parent=None, vendor=None):
        super().__init__(parent)

        layout = QGridLayout()

        nameLbl = QLabel("Name:")
        addressLbl = QLabel("Address:")
        cityLbl = QLabel("City:")
        stateLbl = QLabel("State:")
        zipLbl = QLabel("ZIP:")
        phoneLbl = QLabel("Phone:")

        if mode == "View":
            self.nameText = QLabel(vendor.name)
            self.addressText = QLabel(vendor.address)
            self.cityText = QLabel(vendor.city)
            self.stateText = QLabel(vendor.state)
            self.zipText = QLabel(vendor.zip)
            self.phoneText = QLabel(vendor.phone)
        elif mode == "New":
            self.nameText = QLineEdit()
            self.addressText = QLineEdit()
            self.cityText = QLineEdit()
            self.stateText = QLineEdit()
            self.zipText = QLineEdit()
            self.phoneText = QLineEdit()
        else:
            self.nameText = QLineEdit()
            self.addressText = QLineEdit()
            self.cityText = QLineEdit()
            self.stateText = QLineEdit()
            self.zipText = QLineEdit()
            self.phoneText = QLineEdit()

        layout.addWidget(nameLbl, 0, 0)
        layout.addWidget(self.nameText, 0, 1)
        layout.addWidget(addressLbl, 1, 0)
        layout.addWidget(self.addressText, 1, 1)
        layout.addWidget(cityLbl, 2, 0)
        layout.addWidget(self.cityText, 2, 1)
        layout.addWidget(stateLbl, 3, 0)
        layout.addWidget(self.stateText, 3, 1)
        layout.addWidget(zipLbl, 4, 0)
        layout.addWidget(self.zipText,4, 1)
        layout.addWidget(phoneLbl, 5, 0)
        layout.addWidget(self.phoneText, 5, 1)
        nextRow = 6

        if mode == "View":
            invoicesWidget = gui_elements.InvoiceTreeWidget(vendor.invoices)
            invoicesWidget.setIndentation(0)
            invoicesWidget.setHeaderHidden(True)
            layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
            nextRow += 1

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        buttonLayout.addWidget(saveButton)

        if mode == "View":
            editButton = QPushButton("Edit")
            buttonLayout.addWidget(editButton)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout, nextRow, 0, 1, 2)
        self.setLayout(layout)

    def accept(self):
        QDialog.accept(self)

