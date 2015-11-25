from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *
import re

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
        self.caretLbl = ClickableLabel("ÃƒÂ¢Ã¢â‚¬â€œÃ‚Â²")
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
            self.caretLbl.setText("ÃƒÂ¢Ã¢â‚¬â€œÃ‚Â²")
        else:
            self.body.hide()
            self.caretLbl.setText("ÃƒÂ¢Ã¢â‚¬â€œÃ‚Â¼")

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
        self.invoicesLabel = QLabel("Invoices: %d / %d" % (self.vendor.openInvoiceCount(),
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
        self.nameLabel.setText(self.vendor.name)
        self.bidsLabel.setText("Bids: %d / %d" % (len(self.vendor.proposals),
                                                   0))
        self.invoicesLabel.setText("Invoices: %d / %d" % (self.vendor.openInvoiceCount(),
                                                           len(self.vendor.invoices)))
        self.balanceLabel.setText(str(self.vendor.balance()))

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
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

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
            # Find current largest id and increment by one
            self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Vendors'")
            largestId = self.parent.parent.dbCursor.fetchone()
            if largestId != None:
                nextId = largestId[0] + 1
            else:
                nextId = 1

            # Create new vendor and add it to database and company data
            newVendor = Vendor(dialog.nameText.text(),
                               dialog.addressText.text(),
                               dialog.cityText.text(),
                               dialog.stateText.text(),
                               dialog.zipText.text(),
                               dialog.phoneText.text(),
                               nextId)
            self.vendorsDict[newVendor.idNum] = newVendor
            self.parent.parent.dbCursor.execute("INSERT INTO Vendors (Name, Address, City, State, ZIP, Phone) VALUES (?, ?, ?, ?, ?, ?)",
                                  (newVendor.name, newVendor.address, newVendor.city, newVendor.state, newVendor.zip, newVendor.phone))
            self.parent.parent.dbConnection.commit()

            # Make vendor into a VendorTreeWidgetItem and add it to VendorTree
            item = VendorTreeWidgetItem(newVendor, self.vendorTreeWidget)
            self.vendorTreeWidget.addItem(item)
            self.updateVendorCount()

    def showViewVendorDialog(self):
        idxToShow = self.vendorTreeWidget.indexFromItem(self.vendorTreeWidget.currentItem())
        item = self.vendorTreeWidget.itemFromIndex(idxToShow)

        # Only display dialog if an item in the widget tree has been selected
        if item:
            dialog = VendorDialog("View", self, item.vendor)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Vendors SET Name = '" + dialog.nameText_edit.text() +
                          "', Address = '" + dialog.addressText_edit.text() +
                          "', City = '" + dialog.cityText_edit.text() +
                          "', State = '" + dialog.stateText_edit.text() +
                          "', ZIP = '" + dialog.zipText_edit.text() +
                          "', Phone = '" + dialog.phoneText_edit.text() +
                          "' WHERE idNum = " + str(item.vendor.idNum))

                    self.parent.parent.dbCursor.execute(sql)
                    self.parent.parent.dbConnection.commit()

                    self.vendorsDict[item.vendor.idNum].name = dialog.nameText_edit.text()
                    self.vendorsDict[item.vendor.idNum].address = dialog.addressText_edit.text()
                    self.vendorsDict[item.vendor.idNum].city = dialog.cityText_edit.text()
                    self.vendorsDict[item.vendor.idNum].state = dialog.stateText_edit.text()
                    self.vendorsDict[item.vendor.idNum].zip = dialog.zipText_edit.text()
                    self.vendorsDict[item.vendor.idNum].phone = dialog.phoneText_edit.text()

                    self.vendorTreeWidget.refreshData()

    def deleteSelectedVendorFromList(self):
        # Get item that was deleted from VendorTreeWidget
        idxToDelete = self.vendorTreeWidget.indexOfTopLevelItem(self.vendorTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.vendorTreeWidget.topLevelItem(idxToDelete)

            # Only delete vendor if it has no invoices or proposals linked to it
            if item.vendor.invoices or item.vendor.proposals:
                deleteError = QMessageBox()
                deleteError.setWindowTitle("Can't delete")
                deleteError.setText("Cannot delete a vendor that has issued invoices or bids.  Delete those first.")
                deleteError.exec_()
            else:
                # Delete item from database and update the vendors dictionary
                self.vendorTreeWidget.takeTopLevelItem(idxToDelete)
                self.parent.parent.dbCursor.execute("DELETE FROM Vendors WHERE idNum=?", (item.vendor.idNum,))
                self.parent.parent.dbConnection.commit()
                self.vendorsDict.pop(item.vendor.idNum)
                self.updateVendorCount()

    def updateVendorCount(self):
        self.vendorLabel.setText("Vendors: %d" % len(self.vendorsDict))

    def refreshVendorTree(self):
        self.vendorTreeWidget.refreshData()
        
class InvoiceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, invoiceItem, parent):
        super().__init__(parent)
        self.invoice = invoiceItem
        self.main = QWidget()

        idLabel = QLabel(str(self.invoice.idNum))
        self.vendorLabel = QLabel(self.invoice.vendor.name)
        self.invoiceDateLabel = QLabel(self.invoice.invoiceDate)
        self.dueDateLabel = QLabel(self.invoice.dueDate)
        self.invoiceAmountLabel = QLabel(str(self.invoice.amount))
        self.invoicePaidLabel = QLabel(str(self.invoice.paid()))
        self.invoiceBalanceLabel = QLabel(str(self.invoice.balance()))
        self.payInvoiceLabel = ClickableLabel("$")
        self.payInvoiceLabel.setStyleSheet("QLabel { color: black } QLabel:hover { color: green }")

        if self.invoice.balance() == 0:
            self.payInvoiceLabel.setText("")

        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.vendorLabel)
        layout.addWidget(self.invoiceDateLabel)
        layout.addWidget(self.dueDateLabel)
        layout.addWidget(self.invoiceAmountLabel)
        layout.addWidget(self.invoicePaidLabel)
        layout.addWidget(self.invoiceBalanceLabel)
        layout.addWidget(self.payInvoiceLabel)

        self.main.setLayout(layout)

    def refreshData(self):
        self.vendorLabel.setText(self.invoice.vendor.name)
        self.invoiceDateLabel.setText(self.invoice.invoiceDate)
        self.dueDateLabel.setText(self.invoice.dueDate)
        self.invoiceAmountLabel.setText(str(self.invoice.amount))
        self.invoicePaidLabel.setText(str(self.invoice.paid()))
        self.invoiceBalanceLabel.setText(str(self.invoice.balance()))

class InvoiceTreeWidget(QTreeWidget):
    balanceZero = pyqtSignal(int)
    balanceNotZero = pyqtSignal(int)
    
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
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

            if self.topLevelItem(idx).invoice.balance() == 0:
                self.balanceZero.emit(idx)
            else:
                self.balanceNotZero.emit(idx)

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
        self.openInvoicesTreeWidget.balanceZero.connect(self.moveOpenInvoiceToPaid)

        self.paidInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.paidInvoices())
        self.paidInvoicesTreeWidget.setIndentation(0)
        self.paidInvoicesTreeWidget.setHeaderHidden(True)
        self.paidInvoicesTreeWidget.setMinimumWidth(500)
        self.paidInvoicesTreeWidget.setMaximumHeight(200)
        self.paidInvoicesTreeWidget.balanceNotZero.connect(self.movePaidInvoiceToOpen)

        self.paidInvoicesLabel = QLabel("Paid Invoices: %d" % len(self.invoicesDict.paidInvoices()))

        treeWidgetsLayout.addWidget(self.openInvoicesTreeWidget)
        treeWidgetsLayout.addWidget(self.paidInvoicesLabel)
        treeWidgetsLayout.addWidget(self.paidInvoicesTreeWidget)

        buttonLayout = QVBoxLayout()
        newInvoiceButton = QPushButton("New")
        newInvoiceButton.clicked.connect(self.showNewInvoiceDialog)
        viewInvoiceButton = QPushButton("View")
        viewInvoiceButton.clicked.connect(self.showViewInvoiceDialog)
        deleteInvoiceButton = QPushButton("Delete")
        deleteInvoiceButton.clicked.connect(self.deleteSelectedInvoiceFromList)

        buttonLayout.addWidget(newInvoiceButton)
        buttonLayout.addWidget(viewInvoiceButton)
        buttonLayout.addWidget(deleteInvoiceButton)
        buttonLayout.addStretch(1)

        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)

    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def showNewInvoiceDialog(self):
        dialog = InvoiceDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Invoices'")
            largestId = self.parent.parent.dbCursor.fetchone()
            if largestId != None:
                nextId = largestId[0] + 1
            else:
                nextId = 1

            # Create new invoice and add invoice<-->vendor links
            # Then add the invoice to the corporate data structure and
            # update the invoice and the link information to the database
            newInvoice = Invoice(dialog.invoiceDateText.text(),
                                 dialog.dueDateText.text(),
                                 float(dialog.amountText.text()),
                                 nextId)
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            newInvoice.addVendor(self.parent.dataConnection.vendors[vendorId])
            self.parent.dataConnection.vendors[vendorId].addInvoice(newInvoice)
            self.invoicesDict[newInvoice.idNum] = newInvoice
            self.parent.parent.dbCursor.execute("INSERT INTO Invoices (InvoiceDate, DueDate, Amount) VALUES (?, ?, ?)",
                                  (newInvoice.invoiceDate, newInvoice.dueDate, newInvoice.amount))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addVendor', 'vendors', ?)", (nextId, vendorId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('vendors', ?, 'addInvoice', 'invoices', ?)", (vendorId, nextId))
            self.parent.parent.dbConnection.commit()

            # Make invoice into an InvoiceTreeWidgetItem and add it to VendorTree
            item = InvoiceTreeWidgetItem(newInvoice, self.openInvoicesTreeWidget)
            self.openInvoicesTreeWidget.addItem(item)
            self.updateInvoicesCount()

            # Update vendor tree widget to display new information based on
            # invoice just created
            self.parent.vendorWidget.refreshVendorTree()

    def showViewInvoiceDialog(self):
        # Determine which invoice tree (if any) has been selected
        idxToShow = self.openInvoicesTreeWidget.indexFromItem(self.openInvoicesTreeWidget.currentItem())
        item = self.openInvoicesTreeWidget.itemFromIndex(idxToShow)
        if item == None:
            idxToShow = self.paidInvoicesTreeWidget.indexFromItem(self.paidInvoicesTreeWidget.currentItem())
            item = self.paidInvoicesTreeWidget.itemFromIndex(idxToShow)

        # Only show dialog if an item has been selected
        if item:
            dialog = InvoiceDialog("View", self, item.invoice)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Invoices SET InvoiceDate = '" + dialog.invoiceDateText_edit.text() +
                          "', DueDate = '" + dialog.dueDateText_edit.text() +
                          "', Amount = '" + dialog.amountText_edit.text() +
                          "' WHERE idNum = " + str(item.invoice.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    if dialog.vendorChanged == True:
                        newVendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())

                        # Change vendor<->invoice links in Xref table
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(newVendorId) +
                               " WHERE ObjectToAddLinkTo = 'invoices' AND" + 
                               " ObjectIdToAddLinkTo = " + str(item.invoice.idNum) + " AND" +
                               " ObjectBeingLinked = 'vendors'")
                        self.parent.parent.dbCursor.execute(sql)

                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(newVendorId) +
                               " WHERE ObjectToAddLinkTo = 'vendors' AND" +
                               " ObjectBeingLinked = 'invoices' AND" +
                               " ObjectIdBeingLinked = " + str(item.invoice.idNum))
                        self.parent.parent.dbCursor.execute(sql)

                        # Change vendor<->invoice links in dataConnection
                        self.parent.dataConnection.vendors[item.invoice.vendor.idNum].removeInvoice(item.invoice)
                        self.invoicesDict[item.invoice.idNum].addVendor(self.parent.dataConnection.vendors[newVendorId])
                        self.parent.dataConnection.vendors[newVendorId].addInvoice(item.invoice)

                    self.parent.parent.dbConnection.commit()

                    self.invoicesDict[item.invoice.idNum].invoiceDate = dialog.invoiceDateText_edit.text()
                    self.invoicesDict[item.invoice.idNum].dueDate = dialog.dueDateText_edit.text()
                    self.invoicesDict[item.invoice.idNum].amount = float(dialog.amountText_edit.text())

                    self.openInvoicesTreeWidget.refreshData()
                    self.paidInvoicesTreeWidget.refreshData()
                    self.parent.vendorWidget.refreshVendorTree()
                    
    def deleteSelectedInvoiceFromList(self):
        # Check to see if the item to delete is in the open invoices tree widget
        idxToDelete = self.openInvoicesTreeWidget.indexOfTopLevelItem(self.openInvoicesTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.openInvoicesTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            # Selected item not in open invoices tree widget--delete from paid
            # invoices tree widget
            idxToDelete = self.paidInvoicesTreeWidget.indexOfTopLevelItem(self.paidInvoicesTreeWidget.currentItem())
            item = self.paidInvoicesTreeWidget.takeTopLevelItem(idxToDelete)

        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Invoices WHERE idNum=?", (item.invoice.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoices' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='vendors' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.idNum, item.invoice.vendor.idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='vendors' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='invoices' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.vendor.idNum, item.invoice.idNum))
            self.parent.parent.dbConnection.commit()
            self.parent.dataConnection.vendors[item.invoice.vendor.idNum].removeInvoice(item.invoice)
            self.invoicesDict.pop(item.invoice.idNum)
            self.updateInvoicesCount()
            self.parent.vendorWidget.refreshVendorTree()
        
    def updateInvoicesCount(self):
        self.openInvoicesLabel.setText("Open Invoices: %d" % len(self.invoicesDict.openInvoices()))
        self.paidInvoicesLabel.setText("Paid Invoices: %d" % len(self.invoicesDict.paidInvoices()))

    def moveOpenInvoiceToPaid(self, idx):
        item = self.openInvoicesTreeWidget.takeTopLevelItem(idx)
        newItem = InvoiceTreeWidgetItem(item.invoice, self.paidInvoicesTreeWidget)
        self.paidInvoicesTreeWidget.addItem(newItem)

    def movePaidInvoiceToOpen(self, idx):
        item = self.paidInvoicesTreeWidget.takeTopLevelItem(idx)
        newItem = InvoiceTreeWidgetItem(item.invoice, self.openInvoicesTreeWidget)
        self.openInvoicesTreeWidget.addItem(newItem)

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

class ProposalTreeWidget(QTreeWidget):
    def __init__(self, proposalsDict):
        super().__init__()
        self.buildItems(self, proposalsDict)

    def buildItems(self, parent, proposalsDict):
        for proposalKey in proposalsDict:
            item = InvoiceTreeWidgetItem(proposalsDict[invoiceKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()
    
class ProposalWidget(QWidget):
    def __init__(self, proposalsDict, parent):
        super().__init__(parent)
        self.proposalsDict = proposalsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openProposalsLabel = QLabel("Open: %d" % len(self.proposalsDict))
        mainLayout.addWidget(self.openProposalsLabel)

        # Piece together the proposals layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict)

class ProposalView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self = ProposalWidget(self.dataConnection.proposals, self)
