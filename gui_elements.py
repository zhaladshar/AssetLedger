from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *

class ClickableLabel(QLabel):
    released = pyqtSignal()

    def __init__(self, text):
        super().__init__(text)

    def mouseReleaseEvent(self, event):
        self.released.emit()

class CollapsableFrame(QFrame):
    def __init__(self, headerText):
        super().__init__()
        self.entries = []
        self.setStyleSheet("QFrame { border: 1px solid red }")
        self.setContentsMargins(-8,-8,-8,-8)

        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(0)
        self.bodyLayout = QVBoxLayout()
        self.body = QWidget()

        mainLayout = QVBoxLayout()

        headerWidget = QWidget()
        headerWidget.setStyleSheet("QWidget { background-color: red }")
        headerLbl = QLabel(headerText)
        headerLbl.setMaximumHeight(15)
        headerLbl.setMargin(0)
        self.caretLbl = ClickableLabel("â–²")
        self.caretLbl.setMaximumWidth(15)
        self.caretLbl.setStyleSheet("QLabel:hover { color: yellow }")
        self.caretLbl.released.connect(lambda: self.showHideBody())
        headerLayout.addWidget(headerLbl)
        headerLayout.addStretch(0)
        headerLayout.addWidget(self.caretLbl)
        headerWidget.setLayout(headerLayout)

        self.body.setLayout(self.bodyLayout)

        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(self.body)

        self.setLayout(mainLayout)

    def addEntry(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("QLabel { border: none }")

        self.entries.append(lbl)
        self.bodyLayout.addWidget(lbl)

    def changeEntry(self, index, newText):
        self.entries[index].setText(newText)

    def showHideBody(self):
        if self.body.isHidden() == True:
            self.body.show()
            self.caretLbl.setText("â–²")
        else:
            self.body.hide()
            self.caretLbl.setText("â–¼")

class ButtonToggleBoxItem(QPushButton):
        buttonPressed = pyqtSignal(str)

        def __init__(self, text):
                super().__init__()
                self.setCheckable(True)
                self.setChecked(False)
                self.setText(text)

        def mousePressEvent(self, event):
                self.buttonPressed.emit(self.text())
                event.accept()

class ButtonToggleBox(QWidget):
        selectionChanged = pyqtSignal(str)

        def __init__(self, layoutStyle):
                super().__init__()
                self.btnList = []
                if layoutStyle == "Vertical":
                    self.layout = QVBoxLayout()
                else:
                    self.layout = QHBoxLayout()
                self.layout.setSpacing(0)
                self.layout.addStretch(1)

        def addButton(self, button):
                button.setCheckable(True)
                button.setChecked(False)
                button.buttonPressed.connect(self.changeSelection)

                self.btnList.append(button)

                self.layout.takeAt(self.layout.count() - 1)
                self.layout.addWidget(button)
                self.layout.addStretch(1)

                newWidth = self.determineMinButtonWidth()
                for each in self.btnList:
                        each.setMaximumWidth(newWidth + 20)

        def addButtons(self, listToAdd):
            for item in listToAdd:
                button = ButtonToggleBoxItem(item)
                self.addButton(button)

        def determineMinButtonWidth(self):
                widths = []
                for each in self.btnList:
                        test = each.fontMetrics().boundingRect(each.text()).width()
                        widths.append(test)
                return max(widths)

        def changeSelection(self, btnText):
                for each in self.btnList:
                        if each.text() != btnText:
                                each.setChecked(False)
                        else:
                            if each.isChecked() == True:
                                each.setChecked(False)
                            else:
                                each.setChecked(True)
                self.selectionChanged.emit(btnText)

class VendorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, vendorItem, parent):
        super().__init__(parent)
        self.vendor = vendorItem
        self.main = QWidget()

        idLabel = QLabel(str(self.vendor.idNum))
        self.nameLabel = QLabel(self.vendor.name)
        self.bidsLabel = QLabel("Bids: %d / %d" % (len(self.vendor.proposals),
                                                   0))
        self.invoicesLabel = QLabel("Invoices: %d / %d" % (0,
                                                           len(self.vendor.invoices)))
        self.balanceLabel = QLabel(str(self.vendor.balance()))

        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.bidsLabel)
        layout.addWidget(self.invoicesLabel)
        layout.addWidget(self.balanceLabel)

        self.main.setLayout(layout)

    def refreshData(self):
        self.nameLabel = QLabel(self.vendor.name)
        self.bidsLabel = QLabel("Bids: %d / %d" % (len(self.vendor.proposals),
                                                   0))
        self.invoicesLabel = QLabel("Invoices: %d / %d" % (0,
                                                           len(self.vendor.invoices)))
        self.balanceLabel = QLabel(str(self.vendor.balance()))

class VendorTreeWidget(QTreeWidget):
    def __init__(self, vendorsDict):
        super().__init__()
        self.buildItems(self, vendorsDict)

    def buildItems(self, parent, vendorsDict):
        for vendorKey in vendorsDict:
            item = VendorTreeWidgetItem(vendorsDict[vendorKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for item in self.items():
            item.refreshData()

class VendorWidget(QWidget):
    def __init__(self, vendorsDict, parent):
        super().__init__()
        self.vendorsDict = vendorsDict
        self.parent = parent
        
        mainLayout = QVBoxLayout()

        self.vendorLabel = QLabel("Vendors: %d" % len(self.vendorsDict))
        mainLayout.addWidget(self.vendorLabel)

        # Piece together the vendor layout
        subLayout = QHBoxLayout()

        self.vendorTreeWidget = VendorTreeWidget(self.vendorsDict)
        self.vendorTreeWidget.setIndentation(0)
        self.vendorTreeWidget.setHeaderHidden(True)
        self.vendorTreeWidget.setMinimumWidth(500)
        self.vendorTreeWidget.setMaximumHeight(200)

        newVendorButton = QPushButton("New")
        newVendorButton.clicked.connect(self.showNewVendorDialog)
        viewVendorButton = QPushButton("View")
        viewVendorButton.clicked.connect(self.showViewVendorDialog)
        deleteVendorButton = QPushButton("Delete")
        deleteVendorButton.clicked.connect(self.deleteSelectedVendorFromList)

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(newVendorButton)
        buttonLayout.addWidget(viewVendorButton)
        buttonLayout.addWidget(deleteVendorButton)
        buttonLayout.addStretch(1)

        subLayout.addWidget(self.vendorTreeWidget)
        subLayout.addLayout(buttonLayout)

        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)

    def printOut(self):
        print(self.vendorTreeWidget.indexOfTopLevelItem(self.vendorTreeWidget.currentItem()))

    def showNewVendorDialog(self):
        dialog = VendorDialog("New", self)
        if dialog.exec_():
            # Create new vendor and add it to database and company data
            newVendor = Vendor(dialog.nameText.text(),
                               dialog.addressText.text(),
                               dialog.cityText.text(),
                               dialog.stateText.text(),
                               dialog.zipText.text(),
                               dialog.phoneText.text())
            self.vendorsDict[newVendor.idNum] = newVendor
            self.parent.parent.dbCursor.execute("""INSERT INTO Vendors (Name, Address, City, State, ZIP, Phone) VALUES (?, ?, ?, ?, ?, ?)""",
                                  (newVendor.name, newVendor.address, newVendor.city, newVendor.state, newVendor.zip, newVendor.phone))
            self.parent.parent.dbConnection.commit()

            # Make vendor into a VendorTreeWidgetItem and add it to VendorTree
            item = VendorTreeWidgetItem(newVendor, self.vendorTreeWidget)
            self.vendorTreeWidget.addItem(item)
            self.updateVendorCount()

    def showViewVendorDialog(self):
        idxToShow = self.vendorTreeWidget.indexFromItem(self.vendorTreeWidget.currentItem())
        item = self.vendorTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = VendorDialog("View", self, item.vendor)
            if dialog.exec_():
                print("Closed")
            
    def deleteSelectedVendorFromList(self):
        # Get item that was deleted from VendorTreeWidget
        idxToDelete = self.vendorTreeWidget.indexOfTopLevelItem(self.vendorTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.vendorTreeWidget.takeTopLevelItem(idxToDelete)

            # Delete item from database and update the vendors dictionary
            self.parent.parent.dbCursor.execute("DELETE FROM Vendors WHERE idNum=?", (item.vendor.idNum,))
            self.parent.parent.dbConnection.commit()
            self.vendorsDict.pop(item.vendor.idNum)
            self.updateVendorCount()

    def updateVendorCount(self):
        self.vendorLabel.setText("Vendors: %d" % len(self.vendorsDict))

class InvoiceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, invoiceItem, parent):
        super().__init__(parent)
        self.invoice = invoiceItem
        self.main = QWidget()

        idLabel = QLabel(str(self.invoice.idNum))
        vendorLabel = QLabel(self.invoice.vendor.name)
        invoiceDateLabel = QLabel(self.invoice.invoiceDate)
        dueDateLabel = QLabel(self.invoice.dueDate)
        invoiceAmountLabel = QLabel(str(self.invoice.amount))
        invoicePaidLabel = QLabel(str(self.invoice.paid()))
        invoiceBalanceLabel = QLabel(str(self.invoice.balance()))

        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(vendorLabel)
        layout.addWidget(invoiceDateLabel)
        layout.addWidget(dueDateLabel)
        layout.addWidget(invoiceAmountLabel)
        layout.addWidget(invoicePaidLabel)
        layout.addWidget(invoiceBalanceLabel)
        
        self.main.setLayout(layout)

    def refreshData(self):
        pass

class InvoiceTreeWidget(QTreeWidget):
    def __init__(self, invoicesDict):
        super().__init__()
        self.buildItems(self, invoicesDict)

    def buildItems(self, parent, invoicesDict):
        for invoiceKey in invoicesDict:
            item = InvoiceTreeWidgetItem(invoicesDict[invoiceKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for item in self.items():
            item.refreshData()

class InvoiceWidget(QWidget):
    def __init__(self, invoicesDict, parent):
        super().__init__()
        self.invoicesDict = invoicesDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openInvoicesLabel = QLabel("Open Invoices: %d" % len(self.invoicesDict.openInvoices()))
        mainLayout.addWidget(self.openInvoicesLabel)

        # Piece together the invoices layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.openInvoices())
        self.openInvoicesTreeWidget.setIndentation(0)
        self.openInvoicesTreeWidget.setHeaderHidden(True)
        self.openInvoicesTreeWidget.setMinimumWidth(500)
        self.openInvoicesTreeWidget.setMaximumHeight(100)
        
        self.paidInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.paidInvoices())
        self.paidInvoicesTreeWidget.setIndentation(0)
        self.paidInvoicesTreeWidget.setHeaderHidden(True)
        self.paidInvoicesTreeWidget.setMinimumWidth(500)
        self.paidInvoicesTreeWidget.setMaximumHeight(200)

        self.paidInvoicesLabel = QLabel("Paid Invoices: %d" % len(self.invoicesDict.paidInvoices()))

        treeWidgetsLayout.addWidget(self.openInvoicesTreeWidget)
        treeWidgetsLayout.addWidget(self.paidInvoicesLabel)
        treeWidgetsLayout.addWidget(self.paidInvoicesTreeWidget)

        buttonLayout = QVBoxLayout()
        newInvoiceButton = QPushButton("New")
        viewInvoiceButton = QPushButton("View")
        deleteInvoiceButton = QPushButton("Delete")

        buttonLayout.addWidget(newInvoiceButton)
        buttonLayout.addWidget(viewInvoiceButton)
        buttonLayout.addWidget(deleteInvoiceButton)
        buttonLayout.addStretch(1)

        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)
        
class APView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        layout = QVBoxLayout()

        self.vendorWidget = VendorWidget(self.dataConnection.vendors, self)
        self.invoiceWidget = InvoiceWidget(self.dataConnection.invoices, self)
        layout.addWidget(self.vendorWidget)
        layout.addWidget(self.invoiceWidget)
        layout.addStretch(1)

        self.setLayout(layout)
