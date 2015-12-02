from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *
import re
from classes import *

class ProposalDetailWidget(QWidget):
    detailsHaveChanged = pyqtSignal()
    
    def __init__(self, detailsDict=None):
        super().__init__()
        self.details = {}
        
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        detailLine = QLabel("Detail")
        costLine = QLabel("Cost")

        self.gridLayout.addWidget(detailLine, 0, 0)
        self.gridLayout.addWidget(costLine, 0, 1, 1, 2)
        
        if detailsDict == None:
            self.addNewLine()
        else:
            for detail in detailsDict.keys():
                self.addLine(detailsDict[detail].description, detailsDict[detail].cost, False, False, detailsDict[detail].idNum)

        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)

    def addLine(self, detail, cost, showDelBtn=False, editable=True, detailIdNum=0):
        rowToUse = self.gridLayout.rowCount()

        if editable == True:
            detailLine = QLineEdit(detail)
            costLine = QLineEdit(str(cost))
            costLine.editingFinished.connect(lambda: self.validateInput(rowToUse))
            costLine.textEdited.connect(self.emitChange)
        else:
            detailLine = QLabel(detail)
            costLine = QLabel(str(cost))

        deleteButton = QPushButton("-")
        deleteButton.clicked.connect(lambda: self.deleteLine(rowToUse))
        if showDelBtn == False:
            deleteButton.hide()
        else:
            deleteButton.show()

        self.gridLayout.addWidget(detailLine, rowToUse, 0)
        self.gridLayout.addWidget(costLine, rowToUse, 1)
        self.gridLayout.addWidget(deleteButton, rowToUse, 2)

        self.details[rowToUse] = (detailIdNum, detailLine, costLine)

    def addNewLine(self):
        self.addLine("", "")

    def deleteLine(self, row):
        print(row)
        print(self.gridLayout.itemAtPosition(row, 1))
        print(self.details.pop(row))

        for n in range(3):
            item = self.gridLayout.itemAtPosition(row, n).widget()
            self.gridLayout.removeWidget(self.gridLayout.itemAtPosition(row, n).widget())
            item.deleteLater()

    def validateInput(self, row):
        if self.gridLayout.itemAtPosition(row, 0).widget().text() != "" and \
           self.gridLayout.itemAtPosition(row, 1).widget().text() != "":
            if row == self.gridLayout.rowCount() - 1:
                self.addNewLine()
                self.gridLayout.itemAtPosition(row + 1, 0).widget().setFocus()
                self.gridLayout.itemAtPosition(row, 2).widget().show()

    def makeEditable(self):
        for key in self.details.keys():
            detailLine_edit = QLineEdit(self.details[key][1].text())
            detailLine_edit.textEdited.connect(self.emitChange)
            costLine_edit = QLineEdit(self.details[key][2].text())
            costLine_edit.textEdited.connect(self.emitChange)

            self.gridLayout.addWidget(detailLine_edit, key, 0)
            self.gridLayout.addWidget(costLine_edit, key, 1)
            
            self.gridLayout.itemAtPosition(key, 2).widget().show()

            self.details[key] = (self.details[key][0], detailLine_edit, costLine_edit)

        self.addNewLine()

    def emitChange(self):
        self.detailsHaveChanged.emit()
    
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
        self.bidsLabel = QLabel("Bids: %d / %d" % (len(self.vendor.proposals.proposalsByStatus("Open")),
                                                   len(self.vendor.proposals)))
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
        self.bidsLabel.setText("Bids: %d / %d" % (len(self.vendor.proposals.proposalsByStatus("Open")),
                                                   len(self.vendor.proposals)))
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

class ProposalTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, proposalItem, parent, suppressClickableLabels):
        super().__init__(parent)
        self.proposal = proposalItem
        self.suppressClickableLabels = suppressClickableLabels
        self.main = QWidget()

        idLabel = QLabel(str(self.proposal.idNum))
        self.vendorLabel = QLabel(self.proposal.vendor.name)
        self.dateLabel = QLabel(self.proposal.date)
        self.description = QLabel("") # Put asset/project desc here
        self.proposalAmountLabel = QLabel(str(self.proposal.totalCost()))
        self.acceptProposal = ClickableLabel("✔")
        self.acceptProposal.setStyleSheet("QLabel { color: black } QLabel:hover { color: green }")
        self.rejectProposal = ClickableLabel("✘")
        self.rejectProposal.setStyleSheet("QLabel { color: black } QLabel:hover { color: red }")

        if self.suppressClickableLabels == True:
            self.acceptProposal.hide()
            self.rejectProposal.hide()

        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.vendorLabel)
        layout.addWidget(self.dateLabel)
        layout.addWidget(self.description)
        layout.addWidget(self.proposalAmountLabel)
        layout.addWidget(self.acceptProposal)
        layout.addWidget(self.rejectProposal)

        self.main.setLayout(layout)

    def refreshData(self):
        self.vendorLabel.setText(self.proposal.vendor.name)
        self.dateLabel.setText(self.proposal.date)
        self.proposalAmountLabel.setText(str(self.proposal.totalCost()))
    
class ProposalTreeWidget(QTreeWidget):
    openProposal = pyqtSignal(int)
    rejectedProposal = pyqtSignal(int)
    acceptedProposal = pyqtSignal(int)
    
    def __init__(self, proposalsDict, suppressClickableLabels=False):
        super().__init__()
        self.suppressClickableLabels = suppressClickableLabels
        self.buildItems(self, proposalsDict)

    def buildItems(self, parent, proposalsDict):
        for proposalKey in proposalsDict:
            item = ProposalTreeWidgetItem(proposalsDict[proposalKey], parent, self.suppressClickableLabels)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            # Need to use a try...except... method because if an item gets
            # moved from one location to another during this refresh, idx
            # will get an out of bounds error if any object other than the last
            # item in the list had its status changed (and hence was moved)
            try:
                self.topLevelItem(idx).refreshData()
    
                if self.topLevelItem(idx).proposal.status == "Open":
                    self.openProposal.emit(idx)
                elif self.topLevelItem(idx).proposal.status == "Rejected":
                    self.rejectedProposal.emit(idx)
                else:
                    self.acceptedProposal.emit(idx)
            except:
                pass
    
class ProposalWidget(QWidget):
    updateVendorWidgetTree = pyqtSignal()
    
    def __init__(self, proposalsDict, parent):
        super().__init__(parent)
        self.proposalsDict = proposalsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openProposalsLabel = QLabel("Open: %d" % len(self.proposalsDict.proposalsByStatus("Open")))
        mainLayout.addWidget(self.openProposalsLabel)

        # Piece together the proposals layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus("Open"))
        self.openProposalsTreeWidget.setIndentation(0)
        self.openProposalsTreeWidget.setHeaderHidden(True)
        self.openProposalsTreeWidget.setMinimumWidth(500)
        self.openProposalsTreeWidget.setMaximumHeight(100)
        self.openProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openProposalsTreeWidget.rejectedProposal.connect(self.moveOpenToRejected)
        self.openProposalsTreeWidget.acceptedProposal.connect(self.moveOpenToAccepted)

        self.rejectedProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus("Rejected"))
        self.rejectedProposalsTreeWidget.setIndentation(0)
        self.rejectedProposalsTreeWidget.setHeaderHidden(True)
        self.rejectedProposalsTreeWidget.setMinimumWidth(500)
        self.rejectedProposalsTreeWidget.setMaximumHeight(100)
        self.rejectedProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        self.rejectedProposalsTreeWidget.openProposal.connect(self.moveRejectedToOpen)
        self.rejectedProposalsTreeWidget.acceptedProposal.connect(self.moveRejectedToAccepted)
        
        self.acceptedProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus("Accepted"))
        self.acceptedProposalsTreeWidget.setIndentation(0)
        self.acceptedProposalsTreeWidget.setHeaderHidden(True)
        self.acceptedProposalsTreeWidget.setMinimumWidth(500)
        self.acceptedProposalsTreeWidget.setMaximumHeight(100)
        self.acceptedProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(3))
        self.acceptedProposalsTreeWidget.openProposal.connect(self.moveAcceptedToOpen)
        self.acceptedProposalsTreeWidget.rejectedProposal.connect(self.moveAcceptedToRejected)

        self.rejectedProposalsLabel = QLabel("Rejected: %d" % len(self.proposalsDict.proposalsByStatus("Rejected")))
        self.acceptedProposalsLabel = QLabel("Accepted: %d" % len(self.proposalsDict.proposalsByStatus("Accepted")))

        treeWidgetsLayout.addWidget(self.openProposalsTreeWidget)
        treeWidgetsLayout.addWidget(self.rejectedProposalsLabel)
        treeWidgetsLayout.addWidget(self.rejectedProposalsTreeWidget)
        treeWidgetsLayout.addWidget(self.acceptedProposalsLabel)
        treeWidgetsLayout.addWidget(self.acceptedProposalsTreeWidget)

        buttonLayout = QVBoxLayout()
        newButton = QPushButton("New")
        newButton.clicked.connect(self.showNewProposalDialog)
        viewButton = QPushButton("View")
        viewButton.clicked.connect(self.showViewProposalDialog)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteSelectedProposalFromList)
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(viewButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addStretch(1)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def moveOpenToRejected(self, idx):
        item = self.openProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.rejectedProposalsTreeWidget, True)
        self.rejectedProposalsTreeWidget.addItem(newItem)

    def moveOpenToAccepted(self, idx):
        item = self.openProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.acceptedProposalsTreeWidget, True)
        self.acceptedProposalsTreeWidget.addItem(newItem)

    def moveRejectedToOpen(self, idx):
        item = self.rejectedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.openProposalsTreeWidget, False)
        self.openProposalsTreeWidget.addItem(newItem)

    def moveRejectedToAccepted(self, idx):
        item = self.rejectedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.acceptedProposalsTreeWidget, True)
        self.acceptedProposalsTreeWidget.addItem(newItem)

    def moveAcceptedToOpen(self, idx):
        item = self.acceptedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.openProposalsTreeWidget, False)
        self.openProposalsTreeWidget.addItem(newItem)

    def moveAcceptedToRejected(self, idx):
        item = self.acceptedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.rejectedProposalsTreeWidget, True)
        self.rejectedProposalsTreeWidget.addItem(newItem)

    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.rejectedProposalsTreeWidget.setCurrentItem(self.rejectedProposalsTreeWidget.invisibleRootItem())
            self.acceptedProposalsTreeWidget.setCurrentItem(self.acceptedProposalsTreeWidget.invisibleRootItem())
        elif but == 2:
            self.openProposalsTreeWidget.setCurrentItem(self.openProposalsTreeWidget.invisibleRootItem())
            self.acceptedProposalsTreeWidget.setCurrentItem(self.acceptedProposalsTreeWidget.invisibleRootItem())
        else:
            self.openProposalsTreeWidget.setCurrentItem(self.openProposalsTreeWidget.invisibleRootItem())
            self.rejectedProposalsTreeWidget.setCurrentItem(self.rejectedProposalsTreeWidget.invisibleRootItem())

    def nextIdNum(self, name):
        self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.parent.parent.dbCursor.fetchone()
        if largestId != None:
            return largestId[0] + 1
        else:
            return 1

    def insertIntoDatabase(self, tblName, columns, values):
        sql = "INSERT INTO " + tblName + " " + columns + " VALUES " + values
        self.parent.parent.dbCursor.execute(sql)
                
    def showNewProposalDialog(self):
        dialog = ProposalDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Proposals")
            
            # Create proposal and add to database
            newProposal = Proposal(dialog.dateText.text(),
                                   "Open",
                                   nextId)
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            newProposal.addVendor(self.parent.dataConnection.vendors[vendorId])
            self.parent.dataConnection.vendors[vendorId].addProposal(newProposal)
            self.proposalsDict[newProposal.idNum] = newProposal

            self.insertIntoDatabase("Proposals", "(ProposalDate, Status)", "('" + newProposal.date + "', '" + newProposal.status + "')")
            self.insertIntoDatabase("Xref", "", "('proposals', " + str(nextId) + ", 'addVendor', 'vendors', " + str(vendorId) + ")")
            self.insertIntoDatabase("Xref", "", "('vendors', " + str(vendorId) + ", 'addProposal', 'proposals', " + str(nextId) + ")")

            # Create proposal details and add to database
            nextProposalDetId = self.nextIdNum("ProposalsDetails")
                
            for key in dialog.detailsWidget.details.keys():
                if dialog.detailsWidget.details[key][2].text() == "":
                    proposalDetail = None
                else:
                    proposalDetail = ProposalDetail(dialog.detailsWidget.details[key][1].text(), float(dialog.detailsWidget.details[key][2].text()), nextProposalDetId)

                # Last item in the dialog is a blank line, so a blank proposal
                # detail will be created.  Ignore it.
                if proposalDetail:
                    self.insertIntoDatabase("ProposalsDetails", "(Description, Cost)", "('" + proposalDetail.description + "', '" + str(proposalDetail.cost) + "')")
                    self.insertIntoDatabase("Xref", "", "('proposalsDetails', " + str(nextProposalDetId) + ", 'addDetailOf', 'proposals', " + str(nextId) + ")")
                    self.insertIntoDatabase("Xref", "", "('proposals', " + str(nextId) + ", 'addDetail', 'proposalsDetails', " + str(nextProposalDetId) + ")")

                    newProposal.addDetail(proposalDetail)
                    proposalDetail.addDetailOf(newProposal)
                    self.parent.dataConnection.proposalsDetails[proposalDetail.idNum] = proposalDetail

                    nextProposalDetId += 1

            self.parent.parent.dbConnection.commit()

            # Make proposal into a ProposalTreeWidgetItem and add it to ProposalTree
            item = ProposalTreeWidgetItem(newProposal, self.openProposalsTreeWidget, False)
            self.openProposalsTreeWidget.addItem(item)
            self.updateProposalsCount()
            self.updateVendorWidgetTree.emit()

    def showViewProposalDialog(self):
        # Determine which tree the proposal is in--if any.  If none, don't
        # display dialog
        idxToShow = self.openProposalsTreeWidget.indexFromItem(self.openProposalsTreeWidget.currentItem())
        item = self.openProposalsTreeWidget.itemFromIndex(idxToShow)

        if item == None:
            idxToShow = self.rejectedProposalsTreeWidget.indexFromItem(self.rejectedProposalsTreeWidget.currentItem())
            item = self.rejectedProposalsTreeWidget.itemFromIndex(idxToShow)

            if item == None:
                idxToShow = self.acceptedProposalsTreeWidget.indexFromItem(self.acceptedProposalsTreeWidget.currentItem())
                item = self.acceptedProposalsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = ProposalDialog("View", self, item.proposal)
            dialog.setWindowTitle("View Proposal")
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Proposals SET ProposalDate = '" + dialog.dateText_edit.text() +
                           "', Status = '" + dialog.statusBox.currentText() + 
                           "' WHERE idNum = " + str(item.proposal.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    # If the details of the proposal have changed, update as well
                    # If dialog.detailsWidget.details[key][0] > 0 then that means
                    # we changed a currently existing detail.  If it equals 0, this
                    # is a newly added detail and so it must be created and added
                    # to database.
                    for key in dialog.detailsWidget.details.keys():
                        if dialog.detailsWidget.details[key][0] > 0:
                            sql = ("UPDATE ProposalsDetails SET Description = '" + dialog.detailsWidget.details[key][1].text() +
                                   "', Cost = " + dialog.detailsWidget.details[key][2].text() +
                                   " WHERE idNum = " + str(dialog.detailsWidget.details[key][0]))
                            self.parent.parent.dbCursor.execute(sql)
                            
                            item.proposal.details[dialog.detailsWidget.details[key][0]].description = dialog.detailsWidget.details[key][1].text()
                            item.proposal.details[dialog.detailsWidget.details[key][0]].cost = float(dialog.detailsWidget.details[key][2].text())
                        else:
                            # Make sure description is not blank - if so, this
                            # is the usual blank line at the end of the widget
                            if dialog.detailsWidget.details[key][1].text() != "":
                                nextProposalDetId = self.nextIdNum("ProposalsDetails")
                                
                                self.parent.parent.dbCursor.execute("INSERT INTO ProposalsDetails (Description, Cost) VALUES (?, ?)",
                                                                    (dialog.detailsWidget.details[key][1].text(), dialog.detailsWidget.details[key][2].text()))
                                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('proposalsDetails', ?, 'addDetailOf', 'proposals', ?)", (nextProposalDetId, item.proposal.idNum))
                                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('proposals', ?, 'addDetail', 'proposalsDetails', ?)", (item.proposal.idNum, nextProposalDetId))
                                
                                newProposalDetail = ProposalDetail(dialog.detailsWidget.details[key][1].text(), float(dialog.detailsWidget.details[key][2].text()), nextProposalDetId)
                                newProposalDetail.addDetailOf(item.proposal)
                                item.proposal.addDetail(newProposalDetail)

                                self.parent.dataConnection.proposalsDetails[newProposalDetail.idNum] = newProposalDetail

                    if dialog.vendorChanged == True:
                        newVendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())

                        # Change vendor<->invoice links in Xref table
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(newVendorId) +
                               " WHERE ObjectToAddLinkTo = 'proposals' AND" + 
                               " ObjectIdToAddLinkTo = " + str(item.proposal.idNum) + " AND" +
                               " ObjectBeingLinked = 'vendors'")
                        self.parent.parent.dbCursor.execute(sql)

                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(newVendorId) +
                               " WHERE ObjectToAddLinkTo = 'vendors' AND" +
                               " ObjectBeingLinked = 'proposals' AND" +
                               " ObjectIdBeingLinked = " + str(item.proposal.idNum))
                        self.parent.parent.dbCursor.execute(sql)

                        # Change vendor<->invoice links in dataConnection
                        self.parent.dataConnection.vendors[item.proposal.vendor.idNum].removeProposal(item.proposal)
                        self.proposalsDict[item.proposal.idNum].addVendor(self.parent.dataConnection.vendors[newVendorId])
                        self.parent.dataConnection.vendors[newVendorId].addProposal(item.proposal)

                    self.parent.parent.dbConnection.commit()

                    self.proposalsDict[item.proposal.idNum].date = dialog.dateText_edit.text()
                    self.proposalsDict[item.proposal.idNum].status = dialog.statusBox.currentText()

                    self.openProposalsTreeWidget.refreshData()
                    self.rejectedProposalsTreeWidget.refreshData()
                    self.acceptedProposalsTreeWidget.refreshData()
                    self.updateVendorWidgetTree.emit()
                
    def deleteSelectedProposalFromList(self):
        # Check to see if the item to delete is in the open proposal tree widget
        idxToDelete = self.openProposalsTreeWidget.indexOfTopLevelItem(self.openProposalsTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.openProposalsTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            # Selected item not in open proposals tree widget--check if in
            # rejected proposals tree widget
            idxToDelete = self.rejectedProposalsTreeWidget.indexOfTopLevelItem(self.rejectedProposalsTreeWidget.currentItem())

            if idxToDelete >= 0:
                item = self.paidInvoicesTreeWidget.takeTopLevelItem(idxToDelete)
            else:
                item = None

                idxToDelete = self.acceptedProposalsTreeWidget.indexOfTopLevelItem(self.acceptedProposalsTreeWidget.currentItem())

                if idxToDelete >= 0:
                    # Selected item in accepted proposal tree widget--throw up error
                    deleteError = QMessageBox()
                    deleteError.setWindowTitle("Can't Delete")
                    deleteError.setText("Cannot delete an accepted proposal")
                    deleteError.exec_()

        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Proposals WHERE idNum=?", (item.proposal.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposals' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='vendors' AND ObjectIdBeingLinked=?)",
                                                (item.proposal.idNum, item.proposal.vendor.idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='vendors' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposals' AND ObjectIdBeingLinked=?)",
                                                (item.proposal.vendor.idNum, item.proposal.idNum))

            self.parent.dataConnection.vendors[item.proposal.vendor.idNum].removeProposal(item.proposal)
            proposal = self.proposalsDict.pop(item.proposal.idNum)

            for key in proposal.details.keys():
                proposalDet = proposal.details[key]

                self.parent.parent.dbCursor.execute("DELETE FROM ProposalsDetails WHERE idNum=?", (proposalDet.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposalsDetails' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposals' AND ObjectIdBeingLinked=?)",
                                                    (proposalDet.idNum, proposal.idNum))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposals' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposalsDetails' AND ObjectIdBeingLinked=?)",
                                                    (proposal.idNum, proposalDet.idNum))
                self.parent.dataConnection.proposalsDetails.pop(proposalDet.idNum)

            self.parent.parent.dbConnection.commit()
                
            self.updateProposalsCount()
            self.updateVendorWidgetTree.emit()

    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def updateProposalsCount(self):
        self.openProposalsLabel.setText("Open: %d" % len(self.proposalsDict.proposalsByStatus("Open")))
        self.rejectedProposalsLabel.setText("Rejected: %d" % len(self.proposalsDict.proposalsByStatus("Rejected")))
        self.acceptedProposalsLabel.setText("Accepted: %d" % len(self.proposalsDict.proposalsByStatus("Accepted")))
    
class ProposalView(QWidget):
    updateVendorWidgetTree = pyqtSignal()
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.proposalWidget = ProposalWidget(self.dataConnection.proposals, self)
        self.proposalWidget.updateVendorWidgetTree.connect(self.emitVendorWidgetUpdate)
        layout = QVBoxLayout()
        layout.addWidget(self.proposalWidget)

        self.setLayout(layout)

    def emitVendorWidgetUpdate(self):
        self.updateVendorWidgetTree.emit()
