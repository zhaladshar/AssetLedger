from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_elements import *
from classes import *


class APView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        layout = QVBoxLayout()

        self.vendorLabel = QLabel("Vendors: %d" % len(self.dataConnection.vendors))
        layout.addWidget(self.vendorLabel)

        # Piece together the vendor layout
        vendorLayout = QHBoxLayout()

        self.vendorDetail = VendorTreeWidget(self.dataConnection.vendors)
        self.vendorDetail.setIndentation(0)
        self.vendorDetail.setHeaderHidden(True)

        newVendor = QPushButton("New")
        newVendor.clicked.connect(self.showNewVendorDialog)
        viewVendor = QPushButton("View")
        deleteVendor = QPushButton("Delete")

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(newVendor)
        buttonLayout.addWidget(viewVendor)
        buttonLayout.addWidget(deleteVendor)
        buttonLayout.addStretch(1)

        vendorLayout.addWidget(self.vendorDetail)
        vendorLayout.addLayout(buttonLayout)

        layout.addLayout(vendorLayout)

        self.setLayout(layout)

    def showNewVendorDialog(self):
        dialog = VendorDialog("New", self)
        if dialog.exec_():
            newVendor = Vendor(dialog.nameText.text(),
                               dialog.addressText.text(),
                               dialog.cityText.text(),
                               dialog.stateText.text(),
                               dialog.zipText.text(),
                               dialog.phoneText.text())
            self.dataConnection.vendors[newVendor.idNum] = newVendor
            self.parent.dbCursor.execute("""INSERT INTO Vendors (Name, Address, City, State, ZIP, Phone) VALUES (?, ?, ?, ?, ?, ?)""",
                                  (newVendor.name, newVendor.address, newVendor.city, newVendor.state, newVendor.zip, newVendor.phone))
            self.parent.dbConnection.commit()

class VendorDialog(QDialog):
    def __init__(self, mode, parent=None):
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

        ######################
        ############# Add proposal and invoice boxes
        ######################

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        editButton = QPushButton("Edit")
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)

        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(editButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout, 6, 0, 2, 0)
        self.setLayout(layout)

    def accept(self):
        QDialog.accept(self)

