from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from classes import *
import gui_elements

class VendorDialog(QDialog):
    def __init__(self, mode, parent=None, vendor=None):
        super().__init__(parent)
        self.vendor = vendor
        self.hasChanges = False

        self.layout = QGridLayout()

        nameLbl = QLabel("Name:")
        nameLbl.setStyleSheet("QLabel { background-color: red }")
        addressLbl = QLabel("Address:")
        addressLbl.setStyleSheet("QLabel { background-color: red }")
        cityLbl = QLabel("City:")
        cityLbl.setStyleSheet("QLabel { background-color: red }")
        stateLbl = QLabel("State:")
        stateLbl.setStyleSheet("QLabel { background-color: red }")
        zipLbl = QLabel("ZIP:")
        zipLbl.setStyleSheet("QLabel { background-color: red }")
        phoneLbl = QLabel("Phone:")
        phoneLbl.setStyleSheet("QLabel { background-color: red }")

        if mode == "View":
            self.nameText = QLabel(self.vendor.name)
            self.addressText = QLabel(self.vendor.address)
            self.cityText = QLabel(self.vendor.city)
            self.stateText = QLabel(self.vendor.state)
            self.zipText = QLabel(self.vendor.zip)
            self.phoneText = QLabel(self.vendor.phone)
        else:
            self.nameText = QLineEdit()
            self.addressText = QLineEdit()
            self.cityText = QLineEdit()
            self.stateText = QLineEdit()
            self.zipText = QLineEdit()
            self.phoneText = QLineEdit()

        self.layout.addWidget(nameLbl, 0, 0)
        self.layout.addWidget(self.nameText, 0, 1)
        self.layout.addWidget(addressLbl, 1, 0)
        self.layout.addWidget(self.addressText, 1, 1)
        self.layout.addWidget(cityLbl, 2, 0)
        self.layout.addWidget(self.cityText, 2, 1)
        self.layout.addWidget(stateLbl, 3, 0)
        self.layout.addWidget(self.stateText, 3, 1)
        self.layout.addWidget(zipLbl, 4, 0)
        self.layout.addWidget(self.zipText,4, 1)
        self.layout.addWidget(phoneLbl, 5, 0)
        self.layout.addWidget(self.phoneText, 5, 1)
        nextRow = 6

        if mode == "View":
            invoicesWidget = gui_elements.InvoiceTreeWidget(vendor.invoices)
            invoicesWidget.setIndentation(0)
            invoicesWidget.setHeaderHidden(True)
            self.layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
            nextRow += 1

            ######################
            ##### Add proposal section
            ######################

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        buttonLayout.addWidget(saveButton)

        if mode == "View":
            editButton = QPushButton("Edit")
            editButton.clicked.connect(self.makeLabelsEditable)
            buttonLayout.addWidget(editButton)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        self.layout.addLayout(buttonLayout, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

    def makeLabelsEditable(self):
        self.nameText_edit = QLineEdit(self.nameText.text())
        self.nameText_edit.textEdited.connect(self.changed)
        self.addressText_edit = QLineEdit(self.addressText.text())
        self.addressText_edit.textEdited.connect(self.changed)
        self.cityText_edit = QLineEdit(self.cityText.text())
        self.cityText_edit.textEdited.connect(self.changed)
        self.stateText_edit = QLineEdit(self.stateText.text())
        self.stateText_edit.textEdited.connect(self.changed)
        self.zipText_edit = QLineEdit(self.zipText.text())
        self.zipText_edit.textEdited.connect(self.changed)
        self.phoneText_edit = QLineEdit(self.phoneText.text())
        self.phoneText_edit.textEdited.connect(self.changed)

        self.layout.addWidget(self.nameText_edit, 0, 1)
        self.layout.addWidget(self.addressText_edit, 1, 1)
        self.layout.addWidget(self.cityText_edit, 2, 1)
        self.layout.addWidget(self.stateText_edit, 3, 1)
        self.layout.addWidget(self.zipText_edit, 4, 1)
        self.layout.addWidget(self.phoneText_edit, 5, 1)

    def changed(self):
        self.hasChanges = True

    def accept(self):
        QDialog.accept(self)

class InvoiceDialog(QDialog):
    def __init__(self, mode, parent=None, invoice=None):
        super().__init__(parent)
        self.hasChanges = False
        self.vendorChanged = False
        self.mode = mode

        self.layout = QGridLayout()

        vendorLbl = QLabel("Vendor:")
        invoiceDateLbl = QLabel("Invoice Date:")
        dueDateLabel = QLabel("Due Date:")
        amountLabel = QLabel("Amount:")

        self.vendorBox = QComboBox()
        vendorList = []
        for vendor in parent.parent.dataConnection.vendors.values():
            vendorList.append(str("%4s" % vendor.idNum) + " - " + vendor.name)
        self.vendorBox.addItems(vendorList)

        if self.mode == "View":
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(str("%4s" % invoice.vendor.idNum) + " - " + invoice.vendor.name))
            self.vendorBox.setEnabled(False)
            self.currentVendor = self.vendorBox.currentIndex()
            self.invoiceDateText = QLabel(invoice.invoiceDate)
            self.dueDateText = QLabel(invoice.dueDate)
            self.amountText = QLabel(str(invoice.amount))

        else:
            self.invoiceDateText = QLineEdit()
            self.dueDateText = QLineEdit()
            self.amountText = QLineEdit()

        self.layout.addWidget(vendorLbl, 0, 0)
        self.layout.addWidget(self.vendorBox, 0, 1)
        self.layout.addWidget(invoiceDateLbl, 1, 0)
        self.layout.addWidget(self.invoiceDateText, 1, 1)
        self.layout.addWidget(dueDateLabel, 2, 0)
        self.layout.addWidget(self.dueDateText, 2, 1)
        self.layout.addWidget(amountLabel, 3, 0)
        self.layout.addWidget(self.amountText, 3, 1)

        buttonLayout = QHBoxLayout()

        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        buttonLayout.addWidget(saveButton)

        if self.mode == "View":
            editButton = QPushButton("Edit")
            editButton.clicked.connect(self.makeLabelsEditable)
            buttonLayout.addWidget(editButton)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        ########################
        #### Add payment history for View mode
        ########################

        self.layout.addLayout(buttonLayout, 4, 0, 1, 2)
        self.setLayout(self.layout)

    def makeLabelsEditable(self):
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.changed)
        self.invoiceDateText_edit = QLineEdit(self.invoiceDateText.text())
        self.invoiceDateText_edit.textEdited.connect(self.changed)
        self.dueDateText_edit = QLineEdit(self.dueDateText.text())
        self.dueDateText_edit.textEdited.connect(self.changed)
        self.amountText_edit = QLineEdit(self.amountText.text())
        self.amountText_edit.textEdited.connect(self.changed)

        self.layout.addWidget(self.invoiceDateText_edit, 1, 1)
        self.layout.addWidget(self.dueDateText_edit, 2, 1)
        self.layout.addWidget(self.amountText_edit, 3, 1)

    def changed(self):
        self.hasChanges = True

    def accept(self):
        if self.mode == "View":
            if self.currentVendor != self.vendorBox.currentIndex():
                self.vendorChanged = True
        QDialog.accept(self)
