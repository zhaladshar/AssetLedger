from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *
import re
from classes import *
import sys

class NewLineEdit(QLineEdit):
    lostFocus = pyqtSignal()
    
    def __init__(self, text=None):
        super().__init__(text)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if event.lostFocus() == True:
            self.lostFocus.emit()
    
class AssetProjSelector(QGroupBox):
    rdoBtnChanged = pyqtSignal()
    selectorChanged = pyqtSignal()
    
    def __init__(self, company):
        super().__init__()
        self.company = company
        self.dontEmit = False

        self.buttonGroup = QButtonGroup()
        
        self.assetRdoBtn = QRadioButton("Asset")
        self.assetRdoBtn.toggled.connect(self.showAssetDict)
        self.assetRdoBtn.setEnabled(False)
        self.buttonGroup.addButton(self.assetRdoBtn)
        
        self.projRdoBtn = QRadioButton("Project")
        self.projRdoBtn.toggled.connect(self.showProjectDict)
        self.buttonGroup.addButton(self.projRdoBtn)
        
        self.selector = QComboBox()
        self.selector.currentIndexChanged.connect(self.emitSelectorChange)
        self.selector.hide()
        
        layout = QGridLayout()
        layout.addWidget(self.assetRdoBtn, 0, 0)
        layout.addWidget(self.projRdoBtn, 0, 1)
        layout.addWidget(self.selector, 1, 0, 1, 2)

        self.setLayout(layout)

    def showAssetDict(self):
        self.clear()
        newList = []
        for assetKey in self.company.assets.keys():
            newList.append(str("%4s" % assetKey) + " - " + self.company.assets[assetKey].description)
        
        self.selector.addItems(newList)
        self.selector.show()
        self.emitRdoBtnChange()

    def showProjectDict(self):
        self.clear()
        
        newList = []
        for projectKey in self.company.projects.keys():
            newList.append(str("%4s" % projectKey) + " - " + self.company.projects[projectKey].description)

        self.selector.addItems(newList)
        self.selector.show()
        self.emitRdoBtnChange()

    def dontEmitSignals(self, tf):
        self.dontEmit = tf
        
    def updateCompany(self, company):
        self.company = company

        self.buttonGroup.setExclusive(False)
        self.assetRdoBtn.setChecked(False)
        self.projRdoBtn.setChecked(False)
        self.buttonGroup.setExclusive(True)

    def emitSelectorChange(self, index):
        # Check for index > -1, because if index == -1, this means that the
        # selector was cleared and no signal should be emitted.  Otherwise,
        # this will cause the invoice dialog to try to use the currentText()
        # of the assetProjSelector to find a new proposal whose details will be
        # put in the detail/proposal crossreference section of the invoice
        # dialog.
        if index > -1:
            if self.dontEmit == False:
                self.selectorChanged.emit()
        
    def emitRdoBtnChange(self):
        if self.dontEmit == False:
            self.rdoBtnChanged.emit()

    def assetSelected(self):
        if self.assetRdoBtn.isChecked() == True:
            return True
        else:
            return False

    def projectSelected(self):
        if self.projRdoBtn.isChecked() == True:
            return True
        else:
            return False

    def clear(self):
        self.selector.clear()

class InvoiceDetailWidget(QWidget):
    detailsHaveChanged = pyqtSignal()
    
    def __init__(self, detailsDict=None, proposal=None):
        super().__init__()
        self.details = {}
        self.proposal = proposal
        
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        descLine = QLabel("Description")
        costLine = QLabel("Cost")
        propLine = QLabel("Proposal Element")

        self.gridLayout.addWidget(descLine, 0, 0)
        self.gridLayout.addWidget(costLine, 0, 1)
        self.gridLayout.addWidget(propLine, 0, 2, 1, 2)
        
        if detailsDict == None:
            self.addNewLine()
        else:
            for detailKey in detailsDict:
                # Need to check if detailsDict[detailKey].proposalDetail is
                # None. If so, that means invoice was attached to an asset or
                # project with no proposal.  Thus, a blank line should be used
                if detailsDict[detailKey].proposalDetail:
                    proposalDet = str("%4s - " % detailsDict[detailKey].proposalDetail.idNum) + detailsDict[detailKey].proposalDetail.description
                else:
                    proposalDet = ""
                self.addLine(detailsDict[detailKey].description, detailsDict[detailKey].cost, proposalDet, False, False, detailsDict[detailKey].idNum)
        
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)

    def resetProposalBoxes(self):
        for detailKey in self.details:
            rowToUse = self.details[detailKey][4]
            
            newProposalBox = self.makeProposalDetComboBox("")
            newProposalBox.currentIndexChanged.connect(lambda: self.validateInput(rowToUse))
            newProposalBox.currentIndexChanged.connect(self.emitChange)
            
            newDetail = (self.details[detailKey][0], self.details[detailKey][1],
                         self.details[detailKey][2], newProposalBox,
                         rowToUse)
            
            self.details[detailKey] = newDetail

            oldWidget = self.gridLayout.itemAtPosition(rowToUse, 2).widget()
            self.gridLayout.removeWidget(oldWidget)
            self.gridLayout.addWidget(newProposalBox, rowToUse, 2)
            oldWidget.deleteLater()
        
    def addProposal(self, proposal):
        self.proposal = proposal
        self.resetProposalBoxes()

    def makeProposalDetComboBox(self, proposalDet):
        proposalDetList = [""]

        if self.proposal:
            for detailKey in self.proposal.details:
                proposalDetList.append(str("%4s - " % detailKey) + self.proposal.details[detailKey].description)
        proposalBox = QComboBox()
        proposalBox.addItems(proposalDetList)
        proposalBox.setCurrentIndex(proposalBox.findText(proposalDet))

        return proposalBox
        
    def addLine(self, desc, cost, proposalDet, showDelBtn=False, editable=True, detailIdNum=0):
        rowToUse = self.gridLayout.rowCount()
        
        proposalBox = self.makeProposalDetComboBox(proposalDet)
        
        if editable == True:
            descLine = NewLineEdit(desc)
            descLine.textEdited.connect(self.emitChange)
            descLine.lostFocus.connect(lambda: self.validateInput(rowToUse))
            costLine = NewLineEdit(str(cost))
            costLine.textEdited.connect(self.emitChange)
            costLine.lostFocus.connect(lambda: self.validateInput(rowToUse))
            proposalBox.currentIndexChanged.connect(lambda: self.validateInput(rowToUse))
            proposalBox.currentIndexChanged.connect(self.emitChange)
        else:
            descLine = QLabel(desc)
            costLine = QLabel(str(cost))
            proposalBox.setEnabled(False)
            proposalBox.currentIndexChanged.connect(self.emitChange)

        deleteButton = QPushButton("-")
        deleteButton.clicked.connect(lambda: self.deleteLine(rowToUse))
        if showDelBtn == False:
            deleteButton.hide()
        else:
            deleteButton.show()
        
        self.gridLayout.addWidget(descLine, rowToUse, 0)
        self.gridLayout.addWidget(costLine, rowToUse, 1)
        self.gridLayout.addWidget(proposalBox, rowToUse, 2)
        self.gridLayout.addWidget(deleteButton, rowToUse, 3)
        
        self.details[rowToUse] = (detailIdNum, descLine, costLine, proposalBox, rowToUse)
        
    def addNewLine(self):
        self.addLine("", "", "")
        
    def deleteLine(self, row):
        self.details.pop(row)
        
        for n in range(4):
            widget = self.gridLayout.itemAtPosition(row, n).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        self.emitChange()

    def validateInput(self, row):
        if self.gridLayout.itemAtPosition(row, 0).widget().text() != "" and \
           self.gridLayout.itemAtPosition(row, 1).widget().text() != "":
            if self.proposal:
                if self.gridLayout.itemAtPosition(row, 2).widget().currentText() != "":
                    if row == self.gridLayout.rowCount() - 1:
                        self.addNewLine()
                        self.gridLayout.itemAtPosition(row + 1, 0).widget().setFocus()
                        self.gridLayout.itemAtPosition(row, 3).widget().show()
            else:
                if row == self.gridLayout.rowCount() - 1:
                    self.addNewLine()
                    self.gridLayout.itemAtPosition(row + 1, 0).widget().setFocus()
                    self.gridLayout.itemAtPosition(row, 3).widget().show()

    def makeEditable(self):
        for key in self.details:
            detailLine_edit = QLineEdit(self.details[key][1].text())
            detailLine_edit.textEdited.connect(self.emitChange)
            costLine_edit = QLineEdit(self.details[key][2].text())
            costLine_edit.textEdited.connect(self.emitChange)
            
            for n in range(2):
                oldWidget = self.gridLayout.itemAtPosition(key, n).widget()
                self.gridLayout.removeWidget(oldWidget)
                oldWidget.deleteLater()
            
            self.gridLayout.addWidget(detailLine_edit, key, 0)
            self.gridLayout.addWidget(costLine_edit, key, 1)

            self.gridLayout.itemAtPosition(key, 2).widget().setEnabled(True)
            self.gridLayout.itemAtPosition(key, 3).widget().show()

            self.details[key] = (self.details[key][0], detailLine_edit, costLine_edit, self.gridLayout.itemAtPosition(key, 2).widget(), self.details[key][4])

        self.addNewLine()

    def emitChange(self):
        self.detailsHaveChanged.emit()
        
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
        self.details.pop(row)
        
        for n in range(3):
            widget = self.gridLayout.itemAtPosition(row, n).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

        self.emitChange()

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

            for n in range(2):
                oldWidget = self.gridLayout.itemAtPosition(key, n).widget()
                self.gridLayout.removeWidget(oldWidget)
                oldWidget.deleteLater()
            
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

    def deleteButton(self, name):
        # Have to use a try statement because of spacer items in layout.
        # Trying to call widget() on a spacer item is killing the program.
        for idx in range(self.layout.count()):
            try:
                item = self.layout.itemAt(idx).widget()
                
                if item.text() == name:
                    self.layout.removeWidget(item)
                    item.deleteLater()
            except:
                pass

    def deleteButtons(self, listToDelete):
        for item in listToDelete:
            self.deleteButton(item)

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
        self.invoiceAmountLabel = QLabel(str(self.invoice.amount()))
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
        self.invoiceAmountLabel.setText(str(self.invoice.amount()))
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
    updateVendorTree = pyqtSignal()
    updateProjectTree = pyqtSignal()
    
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
        self.openInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openInvoicesTreeWidget.balanceZero.connect(self.moveOpenInvoiceToPaid)

        self.paidInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.paidInvoices())
        self.paidInvoicesTreeWidget.setIndentation(0)
        self.paidInvoicesTreeWidget.setHeaderHidden(True)
        self.paidInvoicesTreeWidget.setMinimumWidth(500)
        self.paidInvoicesTreeWidget.setMaximumHeight(200)
        self.paidInvoicesTreeWidget.balanceNotZero.connect(self.movePaidInvoiceToOpen)
        self.paidInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        
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

    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.paidInvoicesTreeWidget.setCurrentItem(self.paidInvoicesTreeWidget.invisibleRootItem())
        else:
            self.openInvoicesTreeWidget.setCurrentItem(self.openInvoicesTreeWidget.invisibleRootItem())

    def nextIdNum(self, name):
        self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.parent.parent.dbCursor.fetchone()
        if largestId != None:
            return int(largestId[0]) + 1
        else:
            return 1

    def stripAllButNumbers(self, string):
        if string == "":
            return None
        else:
            regex = re.match(r"\s*([0-9]+).*", string)
            return int(regex.groups()[0])

    def insertIntoDatabase(self, tblName, columns, values):
        sql = "INSERT INTO " + tblName + " " + columns + " VALUES " + values
        self.parent.parent.dbCursor.execute(sql)

    def showNewInvoiceDialog(self):
        dialog = InvoiceDialog("New", self)
        if dialog.exec_():
            nextId = self.nextIdNum("Invoices")

            # Create new invoice
            newInvoice = Invoice(dialog.invoiceDateText.text(),
                                 dialog.dueDateText.text(),
                                 nextId)
            
            # Add invoice<->vendor links
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            newInvoice.addVendor(self.parent.dataConnection.vendors[vendorId])
            self.parent.dataConnection.vendors[vendorId].addInvoice(newInvoice)
            
            # Add invoice<->project/asset links
            if dialog.assetProjSelector.assetSelected() == True:
                type_ = "assets"
                type_action = "addAsset"
            else:
                type_ = "projects"
                type_action = "addProject"
                type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
                newInvoice.addProject(self.parent.dataConnection.projects[type_Id])
                self.parent.dataConnection.projects[type_Id].addInvoice(newInvoice)

            # Add invoice<->company links
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            newInvoice.addCompany(self.parent.dataConnection.companies[companyId])
            self.parent.dataConnection.companies[companyId].addInvoice(newInvoice)

            # Create invoice detail items
            nextInvoiceDetId = self.nextIdNum("InvoicesDetails")
            
            for key in dialog.detailsWidget.details:
                if dialog.detailsWidget.details[key][2].text() == "":
                    invoiceDetail = None
                else:
                    invoiceDetail = InvoiceDetail(dialog.detailsWidget.details[key][1].text(), float(dialog.detailsWidget.details[key][2].text()), nextInvoiceDetId)
                    proposalDetId = self.stripAllButNumbers(dialog.detailsWidget.details[key][3].currentText())

                # Last item in the dialog is a blank line, so a blank invoice
                # detail will be created.  Ignore it.
                if invoiceDetail:
                    self.insertIntoDatabase("InvoicesDetails", "(Description, Cost)", "('" + invoiceDetail.description + "', '" + str(invoiceDetail.cost) + "')")
                    self.insertIntoDatabase("Xref", "", "('invoicesDetails', " + str(nextInvoiceDetId) + ", 'addDetailOf', 'invoices', " + str(nextId) + ")")
                    self.insertIntoDatabase("Xref", "", "('invoices', " + str(nextId) + ", 'addDetail', 'invoicesDetails', " + str(nextInvoiceDetId) + ")")

                    newInvoice.addDetail(invoiceDetail)
                    invoiceDetail.addDetailOf(newInvoice)
                    self.parent.dataConnection.invoicesDetails[invoiceDetail.idNum] = invoiceDetail

                    if proposalDetId:
                        self.insertIntoDatabase("Xref", "", "('invoicesDetails', " + str(nextInvoiceDetId) + ", 'addProposalDetail', 'proposalsDetails', " + str(proposalDetId) + ")")
                        self.insertIntoDatabase("Xref", "", "('proposalsDetails', " + str(proposalDetId) + ", 'addInvoiceDetail', 'invoicesDetails', " + str(nextInvoiceDetId) +")")
                        invoiceDetail.addProposalDetail(self.parent.dataConnection.proposalsDetails[proposalDetId])
                        self.parent.dataConnection.proposalsDetails[proposalDetId].addInvoiceDetail(invoiceDetail)

                    nextInvoiceDetId += 1
            
            # Add the invoice to the corporate data structure and update the
            # invoice and the link information to the database
            self.invoicesDict[newInvoice.idNum] = newInvoice
            
            self.parent.parent.dbCursor.execute("INSERT INTO Invoices (InvoiceDate, DueDate) VALUES (?, ?)",
                                  (newInvoice.invoiceDate, newInvoice.dueDate))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addVendor', 'vendors', ?)", (nextId, vendorId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('vendors', ?, 'addInvoice', 'invoices', ?)", (vendorId, nextId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, ?, ?, ?)", (nextId, type_action, type_, type_Id))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, 'addInvoice', 'invoices', ?)", (type_, type_Id, nextId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addCompany', 'companies', ?)", (nextId, companyId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('companies', ?, 'addInvoice', 'invoices', ?)", (companyId, nextId))

            self.parent.parent.dbConnection.commit()

            # Make invoice into an InvoiceTreeWidgetItem and add it to VendorTree
            item = InvoiceTreeWidgetItem(newInvoice, self.openInvoicesTreeWidget)
            self.openInvoicesTreeWidget.addItem(item)
            self.updateInvoicesCount()

            # Update vendor tree widget to display new information based on
            # invoice just created
            self.updateVendorTree.emit()
            self.updateProjectTree.emit()

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
                    listOfInvPropDetailKeysFromItem = list(item.invoice.details.keys())

                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Invoices SET InvoiceDate = '" + dialog.invoiceDateText_edit.text() +
                          "', DueDate = '" + dialog.dueDateText_edit.text() +
                          "' WHERE idNum = " + str(item.invoice.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    if dialog.companyChanged == True:
                        newCompanyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                        
                        # Change company<->invoice links in Xref tabel
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'invoices' AND" +
                               " ObjectIdToAddLinkTo = " + str(item.invoice.idNum) + " AND" +
                               " ObjectBeingLinked = 'companies'")
                        self.parent.parent.dbCursor.execute(sql)

                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'companies' AND" +
                               " ObjectIdBeingLinked = " + str(item.invoice.idNum) + " AND" +
                               " ObjectBeingLinked = 'invoices'")
                        self.parent.parent.dbCursor.execute(sql)

                        # Change company<->invoice links in dataConnection
                        self.parent.dataConnection.companies[item.invoice.company.idNum].removeInvoice(item.invoice)
                        item.invoice.addCompany(self.parent.dataConnection.companies[newCompanyId])
                        self.parent.dataConnection.companies[newCompanyId].addInvoice(item.invoice)

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

                    if dialog.projectAssetChanged == True:
                        newTypeId = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
                        
                        if dialog.assetProjSelector.assetSelected() == True:
                            pass
                        else:
                            type_ = "projects"
                            oldType = item.invoice.assetProj[1]
                            
                            oldType.removeInvoice(item.invoice)
                            item.invoice.addProject(self.parent.dataConnection.projects[newTypeId])
                            self.parent.dataConnection.projects[newTypeId].addInvoice(item.invoice)
                        
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo=? " +
                               "AND ObjectBeingLinked='invoices' AND ObjectIdBeingLinked=?",
                               (newTypeId, type_, item.invoice.idNum))
                        
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectBeingLinked=? "
                               "AND ObjectToAddLinkTo='invoices' AND ObjectIdToAddLinkTo=?",
                               (newTypeId, type_, item.invoice.idNum))
                        
                    if dialog.invoicePropDetailsChanged == True:
                        # Generate list of invoice/proposal detail entries to
                        # compare with original.  Delete from database any
                        # entries in original that aren't in the new list
                        # generated.
                        listOfInvPropDetailKeysFromDialog = []
                        
                        for key in dialog.detailsWidget.details:
                            listOfInvPropDetailKeysFromDialog.append(dialog.detailsWidget.details[key][0])
                        
                        for oldKey in listOfInvPropDetailKeysFromItem:
                            if oldKey not in listOfInvPropDetailKeysFromDialog:
                                invoiceDetail = self.parent.dataConnection.invoicesDetails.pop(oldKey)
                                invoiceDetail.detailOf.removeDetail(invoiceDetail)
                                
                                self.parent.parent.dbCursor.execute("DELETE FROM InvoicesDetails WHERE idNum=?", (invoiceDetail.idNum,))
                                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo = 'invoicesDetails' AND ObjectIdToAddLinkTo=?", (invoiceDetail.idNum,))
                                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked = 'invoicesDetails' AND ObjectIdBeingLinked=?", (invoiceDetail.idNum,))

                                if invoiceDetail.proposalDetail:
                                    proposalDetail = invoiceDetail.proposalDetail
                                    proposalDetail.removeInvoiceDetail(invoiceDetail)

                        # If the details of the proposal have changed, update as well
                        # If dialog.detailsWidget.details[key][0] > 0 then that means
                        # we changed a currently existing detail.  If it equals 0, this
                        # is a newly added detail and so it must be created and added
                        # to database.
                        for key in dialog.detailsWidget.details:
                            if dialog.detailsWidget.details[key][0] > 0:
                                proposalDetId = self.stripAllButNumbers(dialog.detailsWidget.details[key][3].currentText())
                                
                                sql = ("UPDATE InvoicesDetails SET Description = '" + dialog.detailsWidget.details[key][1].text() +
                                       "', Cost = " + dialog.detailsWidget.details[key][2].text() +
                                       " WHERE idNum = " + str(dialog.detailsWidget.details[key][0]))
                                self.parent.parent.dbCursor.execute(sql)
                                
                                self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='invoicesDetails' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposalsDetails'",
                                                                    (proposalDetId, dialog.detailsWidget.details[key][0]))
                                self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='proposalsDetails' AND ObjectBeingLinked='invoicesDetails' AND ObjectIdBeingLinked=?",
                                                                    (proposalDetId, dialog.detailsWidget.details[key][0]))
                                
                                item.invoice.details[dialog.detailsWidget.details[key][0]].description = dialog.detailsWidget.details[key][1].text()
                                item.invoice.details[dialog.detailsWidget.details[key][0]].cost = float(dialog.detailsWidget.details[key][2].text())
                                
                                if item.invoice.details[dialog.detailsWidget.details[key][0]].proposalDetail:
                                    oldProposalDetail = item.invoice.details[dialog.detailsWidget.details[key][0]].proposalDetail
                                    oldProposalDetail.removeInvoiceDetail(item.invoice.details[dialog.detailsWidget.details[key][0]])
                                    newProposalDetail = self.parent.dataConnection.proposalsDetails[proposalDetId]
                                    
                                    item.invoice.details[dialog.detailsWidget.details[key][0]].addProposalDetail(newProposalDetail)
                                    newProposalDetail.addInvoiceDetail(item.invoice.details[dialog.detailsWidget.details[key][0]])
                            else:
                                # Make sure description is not blank - if so, this
                                # is the usual blank line at the end of the widget
                                if dialog.detailsWidget.details[key][1].text() != "":
                                    nextInvoiceDetId = self.nextIdNum("InvoicesDetails")
                                    proposalDetId = self.stripAllButNumbers(dialog.detailsWidget.details[key][3].currentText())
                                    
                                    self.parent.parent.dbCursor.execute("INSERT INTO InvoicesDetails (Description, Cost) VALUES (?, ?)",
                                                                        (dialog.detailsWidget.details[key][1].text(), dialog.detailsWidget.details[key][2].text()))
                                    self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoicesDetails', ?, 'addDetailOf', 'invoices', ?)", (nextInvoiceDetId, item.invoice.idNum))
                                    self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addDetail', 'invoicesDetails', ?)", (item.invoice.idNum, nextInvoiceDetId))
                                    
                                    newInvoiceDetail = InvoiceDetail(dialog.detailsWidget.details[key][1].text(), float(dialog.detailsWidget.details[key][2].text()), nextInvoiceDetId)
                                    newInvoiceDetail.addDetailOf(item.invoice)
                                    item.invoice.addDetail(newInvoiceDetail)
                                    
                                    if proposalDetId:
                                        self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoicesDetails', ?, 'addProposalDetail', 'proposalsDetails', ?)", (nextInvoiceDetId, proposalDetId))
                                        self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('proposalsDetails', ?, 'addInvoiceDetail', 'invoicesDetails', ?)", (proposalDetId, nextInvoiceDetId))
                                        newInvoiceDetail.addProposalDetail(self.parent.dataConnection.proposalsDetails[proposalDetId])
                                        self.parent.dataConnection.proposalsDetails[proposalDetId].addInvoiceDetail(newInvoiceDetail)
                                    
                                    self.parent.dataConnection.invoicesDetails[newInvoiceDetail.idNum] = newInvoiceDetail
                        
                    self.parent.parent.dbConnection.commit()

                    item.invoice.invoiceDate = dialog.invoiceDateText_edit.text()
                    item.invoice.dueDate = dialog.dueDateText_edit.text()

                    self.openInvoicesTreeWidget.refreshData()
                    self.paidInvoicesTreeWidget.refreshData()

                    self.updateVendorTree.emit()
                    self.updateProjectTree.emit()
                    
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
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoices' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked=? AND ObjectIdBeingLinked=?)",
                                                (item.invoice.idNum, item.invoice.assetProj[0], item.invoice.assetProj[1].idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo=? AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='invoices' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.assetProj[0], item.invoice.assetProj[1].idNum, item.invoice.idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoices' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='companies' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.idNum, item.invoice.company.idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='companies' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='invoices' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.company.idNum, item.invoice.idNum))

            # Delete invoice details and detail/proposal connections
            for detailKey in item.invoice.details:
                invoiceDetId = item.invoice.details[detailKey].idNum

                self.parent.parent.dbCursor.execute("DELETE FROM InvoicesDetails WHERE idNum=?", (invoiceDetId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoicesDetails' AND ObjectIdToAddLinkTo=?)", (invoiceDetId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectBeingLinked='invoicesDetails' AND ObjectIdBeingLinked=?)", (invoiceDetId,))

                invoiceDetail = self.parent.dataConnection.invoicesDetails.pop(invoiceDetId)
                self.parent.dataConnection.proposalsDetails[invoiceDetail.proposalDetail.idNum].removeInvoiceDetail(invoiceDetail)
            
            self.parent.parent.dbConnection.commit()
            self.parent.dataConnection.vendors[item.invoice.vendor.idNum].removeInvoice(item.invoice)
            self.parent.dataConnection.companies[item.invoice.company.idNum].removeInvoice(item.invoice)
            
            if item.invoice.assetProj[0] == "assets":
                self.parent.dataConnection.assets[item.invoice.assetProj[1].idNum].removeInvoice(item.invoice)
            else:
                self.parent.dataConnection.projects[item.invoice.assetProj[1].idNum].removeInvoice(item.invoice)
                
            self.invoicesDict.pop(item.invoice.idNum)
            self.updateInvoicesCount()

            self.updateVendorTree.emit()
            self.updateProjectTree.emit()
        
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
    updateProjectTree = pyqtSignal()
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        layout = QVBoxLayout()
        
        self.vendorWidget = VendorWidget(self.dataConnection.vendors, self)
        self.invoiceWidget = InvoiceWidget(self.dataConnection.invoices, self)
        self.invoiceWidget.updateVendorTree.connect(self.updateVendorWidget)
        self.invoiceWidget.updateProjectTree.connect(self.emitUpdateProjectTree)
        
        layout.addWidget(self.vendorWidget)
        layout.addWidget(self.invoiceWidget)
        layout.addStretch(1)

        self.setLayout(layout)

    def updateVendorWidget(self):
        self.vendorWidget.refreshVendorTree()

    def emitUpdateProjectTree(self):
        self.updateProjectTree.emit()

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
            self.proposalsDict[newProposal.idNum] = newProposal
            
            # Add company<->proposal link
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            newProposal.addCompany(self.parent.dataConnection.companies[companyId])
            self.parent.dataConnection.companies[companyId].addProposal(newProposal)
            
            # Add vendor<->proposal link
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            newProposal.addVendor(self.parent.dataConnection.vendors[vendorId])
            self.parent.dataConnection.vendors[vendorId].addProposal(newProposal)
            
            # Add invoice<->project/asset links
            type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
            if dialog.assetProjSelector.assetSelected() == True:
                type_ = "assets"
                type_action = "addAsset"
            else:
                type_ = "projects"
                type_action = "addProject"
                newProposal.addProject(self.parent.dataConnection.projects[type_Id])
                self.parent.dataConnection.projects[type_Id].addProposal(newProposal)
            
            # Add to database
            self.insertIntoDatabase("Proposals", "(ProposalDate, Status)", "('" + newProposal.date + "', '" + newProposal.status + "')")
            self.insertIntoDatabase("Xref", "", "('proposals', " + str(nextId) + ", 'addCompany', 'companies', " + str(companyId) + ")")
            self.insertIntoDatabase("Xref", "", "('companies', " + str(companyId) + ", 'addProposal', 'proposals', " + str(nextId) + ")")
            self.insertIntoDatabase("Xref", "", "('proposals', " + str(nextId) + ", 'addVendor', 'vendors', " + str(vendorId) + ")")
            self.insertIntoDatabase("Xref", "", "('vendors', " + str(vendorId) + ", 'addProposal', 'proposals', " + str(nextId) + ")")
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('proposals', ?, ?, ?, ?)", (nextId, type_action, type_, type_Id))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, 'addProposal', 'proposals', ?)", (type_, type_Id, nextId))
            
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
                    listOfKeysFromItem = list(item.proposal.details.keys())
                    
                    # Commit changes to database
                    sql = ("UPDATE Proposals SET ProposalDate = '" + dialog.dateText_edit.text() +
                           "', Status = '" + dialog.statusBox.currentText() + 
                           "' WHERE idNum = " + str(item.proposal.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    # If the details of the proposal have changed, update as well
                    # If dialog.detailsWidget.details[key][0] > 0 then that means
                    # we changed a currently existing detail.  If it equals 0, this
                    # is a newly added detail and so it must be created and added
                    # to database.
                    for key in dialog.detailsWidget.details:
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

                    # Compare entries in original details dictionary
                    # (item.proposals.details) to what is in the
                    # details widget of the dialog.  Delete any items
                    # that are in the former but not the latter.
                    listOfPropDetailsFromDialog = []
                    
                    for dialogKey in dialog.detailsWidget.details:
                        listOfPropDetailsFromDialog.append(dialog.detailsWidget.details[dialogKey][0])

                    for key in listOfKeysFromItem:
                        if key not in listOfPropDetailsFromDialog:
                            self.parent.parent.dbCursor.execute("DELETE FROM ProposalsDetails WHERE idNum=?", (item.proposal.details[key].idNum,))
                            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposalsDetails' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposals' AND ObjectIdBeingLinked=?)",
                                                                (key, item.proposal.idNum))
                            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposals' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='proposalsDetails' AND ObjectIdBeingLinked=?)",
                                                                (item.proposal.idNum, key))
                            item.proposal.details.pop(key)
                            self.parent.dataConnection.proposalsDetails.pop(key)

                    if dialog.vendorChanged == True:
                        newVendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())

                        # Change vendor<->proposal links in Xref table
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

                        # Change vendor<->proposal links in dataConnection
                        self.parent.dataConnection.vendors[item.proposal.vendor.idNum].removeProposal(item.proposal)
                        item.proposal.addVendor(self.parent.dataConnection.vendors[newVendorId])
                        self.parent.dataConnection.vendors[newVendorId].addProposal(item.proposal)

                    if dialog.companyChanged == True:
                        newCompanyId = self.stripAllButNumbers(dialog.companyBox.currentText())

                        # Change company<->proposal links in Xref table
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'proposals' AND" +
                               " ObjectIdToAddLinkTo = " + str(item.proposal.idNum) + " AND" +
                               " ObjectBeingLinked = 'companies'")
                        self.parent.parent.dbCursor.execute(sql)

                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'companies' AND" +
                               " ObjectBeingLinked = 'proposals' AND" +
                               " ObjectIdBeingLinked = " + str(item.proposal.idNum))
                        self.parent.parent.dbCursor.execute(sql)

                        # Change company<->proposal links in dataConnection
                        self.parent.dataConnection.companies[item.proposal.company.idNum].removeProposal(item.proposal)
                        item.proposal.addCompany(self.parent.dataConnection.companies[newCompanyId])
                        self.parent.dataConnection.companies[newCompanyId].addProposal(item.proposal)

                    if dialog.projectAssetChanged == True:
                        # Change project/asset<->proposal links in database
                        type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
                        if dialog.assetProjSelector.assetSelected() == True:
                            pass
                        else:
                            type_ = "projects"
                            self.parent.dataConnection.projects[item.proposal.proposalFor[1].idNum].removeProposal(item.proposal)
                            item.proposal.addProject(self.parent.dataConnection.projects[type_Id])
                            self.parent.dataConnection.projects[type_Id].addProposal(item.proposal)
                        
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(type_Id) +
                               " WHERE ObjectToAddLinkTo = 'proposals' AND" +
                               " ObjectIdToAddLinkTo = " + str(item.proposal.idNum) + " AND" +
                               " ObjectBeingLinked = '" + type_ + "'")
                        self.parent.parent.dbCursor.execute(sql)
                        
                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(type_Id) +
                               " WHERE ObjectToAddLinkTo = '" + type_ + "' AND" +
                               " ObjectBeingLinked = 'proposals' AND" +
                               " ObjectIdBeingLinked = " + str(item.proposal.idNum))
                        self.parent.parent.dbCursor.execute(sql)

                    self.parent.parent.dbConnection.commit()

                    item.proposal.date = dialog.dateText_edit.text()
                    item.proposal.status = dialog.statusBox.currentText()

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
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='proposals' AND ObjectIdToAddLinkTo=?)", (item.proposal.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectBeingLinked='proposals' AND ObjectIdBeingLinked=?)", (item.proposal.idNum,))

            self.parent.dataConnection.vendors[item.proposal.vendor.idNum].removeProposal(item.proposal)
            self.parent.dataConnection.companies[item.proposal.company.idNum].removeProposal(item.proposal)
            
            if item.proposal.proposalFor[0] == "assets":
                self.parent.dataConnection.assets[item.proposal.proposalFor[1].idNum].removeProposal(item.proposal)
            else:
                self.parent.dataConnection.projects[item.proposal.proposalFor[1].idNum].removeProposal(item.proposal)
            
            proposal = self.proposalsDict.pop(item.proposal.idNum)
            for key in proposal.details.keys():
                proposalDet = proposal.details[key]
                self.parent.parent.dbCursor.execute("DELETE FROM ProposalsDetails WHERE idNum=?", (proposalDet.idNum,))
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

class ProjectTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, projectItem, parent):
        super().__init__(parent)
        self.project = projectItem
        self.main = QWidget()
        
        idLabel = QLabel(str(self.project.idNum))
        self.descLabel = QLabel(self.project.description)
        self.startDateLabel = QLabel(self.project.dateStart)
        self.endDateLabel = QLabel(self.project.dateEnd)
        self.durationLabel = QLabel("<Duration>")
        self.CIPLabel = QLabel("CIP: %.02f" % self.project.calculateCIP())
        
        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.descLabel)
        layout.addWidget(self.startDateLabel)
        layout.addWidget(self.endDateLabel)
        layout.addWidget(self.durationLabel)
        layout.addWidget(self.CIPLabel)
        
        self.main.setLayout(layout)

    def refreshData(self):
        self.descLabel.setText(self.project.description)
        self.startDateLabel.setText(self.project.dateStart)
        self.endDateLabel.setText(self.project.dateEnd)
        self.durationLabel.setText("<Duration>")
        self.CIPLabel.setText("CIP: %.02f" % self.project.calculateCIP())

class ProjectTreeWidget(QTreeWidget):
    def __init__(self, projectsDict):
        super().__init__()
        self.buildItems(self, projectsDict)

    def buildItems(self, parent, projectsDict):
        for projectKey in projectsDict:
            item = ProjectTreeWidgetItem(projectsDict[projectKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

class ProjectWidget(QWidget):
    updateVendorWidgetTree = pyqtSignal()
    
    def __init__(self, projectsDict, parent):
        super().__init__()
        self.projectsDict = projectsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openProjectsLabel = QLabel("Open: %d" % len(self.projectsDict.projectsByStatus("Open")))
        mainLayout.addWidget(self.openProjectsLabel)

        # Piece together the projects layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openProjectsTreeWidget = ProjectTreeWidget(self.projectsDict.projectsByStatus("Open"))
        self.openProjectsTreeWidget.setIndentation(0)
        self.openProjectsTreeWidget.setHeaderHidden(True)
        self.openProjectsTreeWidget.setMinimumWidth(500)
        self.openProjectsTreeWidget.setMaximumHeight(100)
        #self.openProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))

        self.closedProjectsTreeWidget = ProjectTreeWidget(self.projectsDict.projectsByStatus("Closed"))
        self.closedProjectsTreeWidget.setIndentation(0)
        self.closedProjectsTreeWidget.setHeaderHidden(True)
        self.closedProjectsTreeWidget.setMinimumWidth(500)
        self.closedProjectsTreeWidget.setMaximumHeight(100)
        #self.closedProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))

        self.closedProjectsLabel = QLabel("Closed: %d" % len(self.projectsDict.projectsByStatus("Closed")))

        treeWidgetsLayout.addWidget(self.openProjectsTreeWidget)
        treeWidgetsLayout.addWidget(self.closedProjectsLabel)
        treeWidgetsLayout.addWidget(self.closedProjectsTreeWidget)

        buttonLayout = QVBoxLayout()
        newButton = QPushButton("New")
        newButton.clicked.connect(self.showNewProjectDialog)
        viewButton = QPushButton("View")
        viewButton.clicked.connect(self.showViewProjectDialog)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteSelectedProjectFromList)
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(viewButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addStretch(1)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def nextIdNum(self, name):
        self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.parent.parent.dbCursor.fetchone()
        if largestId != None:
            return largestId[0] + 1
        else:
            return 1

    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def insertIntoDatabase(self, tblName, columns, values):
        sql = "INSERT INTO " + tblName + " " + columns + " VALUES " + values
        self.parent.parent.dbCursor.execute(sql)

    def showNewProjectDialog(self):
        dialog = ProjectDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Projects")
            
            # Create proposal and add to database
            newProject = Project(dialog.descriptionText.text(),
                                 dialog.startDateText.text(),
                                 nextId)
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            newProject.addCompany(self.parent.dataConnection.companies[companyId])
            self.parent.dataConnection.companies[companyId].addProject(newProject)
            self.projectsDict[newProject.idNum] = newProject

            self.insertIntoDatabase("Projects", "(Description, DateStart)", "('" + newProject.description + "', '" + newProject.dateStart + "')")
            self.insertIntoDatabase("Xref", "", "('projects', " + str(nextId) + ", 'addCompany', 'companies', " + str(companyId) + ")")
            self.insertIntoDatabase("Xref", "", "('companies', " + str(companyId) + ", 'addProject', 'projects', " + str(nextId) + ")")            
            
            self.parent.parent.dbConnection.commit()
            
            # Make project into a ProjectTreeWidgetItem and add it to ProjectTree
            item = ProjectTreeWidgetItem(newProject, self.openProjectsTreeWidget)
            self.openProjectsTreeWidget.addItem(item)
            self.updateProjectsCount()

    def showViewProjectDialog(self):
        # Determine which tree the proposal is in--if any.  If none, don't
        # display dialog
        idxToShow = self.openProjectsTreeWidget.indexFromItem(self.openProjectsTreeWidget.currentItem())
        item = self.openProjectsTreeWidget.itemFromIndex(idxToShow)

        if item == None:
            idxToShow = self.closedProjectsTreeWidget.indexFromItem(self.closedProjectsTreeWidget.currentItem())
            item = self.closedProjectsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = ProjectDialog("View", self, item.project)
            
            dialog.setWindowTitle("View Project")
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Projects SET Description = '" + dialog.descriptionText_edit.text() +
                           "', DateStart = '" + dialog.startDateText_edit.text() +
                           "', DateEnd = '" + dialog.endDateText.text() + 
                           "' WHERE idNum = " + str(item.project.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    if dialog.companyChanged == True:
                        newCompanyId = self.stripAllButNumbers(dialog.companyBox.currentText())

                        # Change company<->project links in Xref table
                        sql = ("UPDATE Xref SET ObjectIdBeingLinked = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'projects' AND" + 
                               " ObjectIdToAddLinkTo = " + str(item.project.idNum) + " AND" +
                               " ObjectBeingLinked = 'companies'")
                        self.parent.parent.dbCursor.execute(sql)

                        sql = ("UPDATE Xref SET ObjectIdToAddLinkTo = " + str(newCompanyId) +
                               " WHERE ObjectToAddLinkTo = 'companies' AND" +
                               " ObjectBeingLinked = 'projects' AND" +
                               " ObjectIdBeingLinked = " + str(item.project.idNum))
                        self.parent.parent.dbCursor.execute(sql)

                        # Change company<->project links in dataConnection
                        self.parent.dataConnection.companies[item.project.company.idNum].removeProject(item.project)
                        item.project.addCompany(self.parent.dataConnection.companies[newCompanyId])
                        self.parent.dataConnection.companies[newCompanyId].addProject(item.project)

                    self.parent.parent.dbConnection.commit()

                    item.project.description = dialog.descriptionText_edit.text()
                    item.project.dateStart = dialog.startDateText_edit.text()
                    item.project.dateEnd = dialog.endDateText.text()

                    self.openProjectsTreeWidget.refreshData()
                    self.closedProjectsTreeWidget.refreshData()

    def deleteSelectedProjectFromList(self):
        # Check to see if the item to delete is in the open project tree widget
        idxToDelete = self.openProjectsTreeWidget.indexOfTopLevelItem(self.openProjectsTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.openProjectsTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            idxToDelete = self.closedProjectsTreeWidget.indexOfTopLevelItem(self.closedProjectsTreeWidget.currentItem())
            item = None
            
            if idxToDelete >= 0:
                # Selected item not in open project tree widget--cannot delete
                # because it could be converted to an asset.
                deleteError = QMessageBox()
                deleteError.setWindowTitle("Can't Delete")
                deleteError.setText("Cannot delete a closed project")
                deleteError.exec_()
        
        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Projects WHERE idNum=?", (item.project.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='projects' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='companies' AND ObjectIdBeingLinked=?)",
                                                (item.project.idNum, item.project.company.idNum))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='companies' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='projects' AND ObjectIdBeingLinked=?)",
                                                (item.project.company.idNum, item.project.idNum))

            self.parent.dataConnection.companies[item.project.company.idNum].removeProject(item.project)
            self.projectsDict.pop(item.project.idNum)

            self.parent.parent.dbConnection.commit()
                
            self.updateProjectsCount()
            
    def updateProjectsCount(self):
        self.openProjectsLabel.setText("Open: %d" % len(self.projectsDict.projectsByStatus("Open")))
        self.closedProjectsLabel.setText("Closed: %d" % len(self.projectsDict.projectsByStatus("Closed")))

    def refreshProjectTree(self):
        self.openProjectsTreeWidget.refreshData()
        
class ProjectView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.projectWidget = ProjectWidget(self.dataConnection.projects, self)
        layout = QVBoxLayout()
        layout.addWidget(self.projectWidget)

        self.setLayout(layout)

class CompanyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, companyItem, parent):
        super().__init__(parent)
        self.company = companyItem
        self.main = QWidget()
        
        idLabel = QLabel(str(self.company.idNum))
        self.nameLabel = QLabel(self.company.name)
        self.shortNameLabel = QLabel(self.company.shortName)
        self.assetsAmountLabel = QLabel("Assets: %.02f" % self.company.assetsAmount())
        self.CIPLabel = QLabel("CIP: %.02f" % self.company.CIPAmount())
        
        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.shortNameLabel)
        layout.addWidget(self.assetsAmountLabel)
        layout.addWidget(self.CIPLabel)
        
        self.main.setLayout(layout)

    def refreshData(self):
        self.nameLabel.setText(self.company.name)
        self.shortNameLabel.setText(self.company.shortName)
        self.assetsAmountLabel.setText("Assets: %.02f" % self.company.assetsAmount())
        self.CIPLabel.setText("CIP: %.02f" % self.company.CIPAmount())
        
class CompanyTreeWidget(QTreeWidget):
    def __init__(self, companiesDict):
        super().__init__()
        self.buildItems(self, companiesDict)

    def buildItems(self, parent, companiesDict):
        for companyKey in companiesDict:
            item = CompanyTreeWidgetItem(companiesDict[companyKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()
            
class CompanyWidget(QWidget):
    addNewCompany = pyqtSignal(str)
    deleteCompany = pyqtSignal(str)
    
    def __init__(self, companiesDict, parent):
        super().__init__()
        self.companiesDict = companiesDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.companiesLabel = QLabel("Companies: %d" % len(self.companiesDict))
        mainLayout.addWidget(self.companiesLabel)

        # Piece together the companies layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.companiesTreeWidget = CompanyTreeWidget(self.companiesDict)
        self.companiesTreeWidget.setIndentation(0)
        self.companiesTreeWidget.setHeaderHidden(True)
        self.companiesTreeWidget.setMinimumWidth(500)
        self.companiesTreeWidget.setMaximumHeight(100)

        treeWidgetsLayout.addWidget(self.companiesTreeWidget)
        treeWidgetsLayout.addStretch(1)

        buttonLayout = QVBoxLayout()
        newButton = QPushButton("New")
        newButton.clicked.connect(self.showNewCompanyDialog)
        viewButton = QPushButton("View")
        viewButton.clicked.connect(self.showViewCompanyDialog)
        deleteButton = QPushButton("Delete")
        deleteButton.clicked.connect(self.deleteSelectedCompanyFromList)
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(viewButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addStretch(1)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

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

    def updateCompaniesCount(self):
        self.companiesLabel.setText("Companies: %d" % len(self.companiesDict))

    def showNewCompanyDialog(self):
        dialog = CompanyDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Companies")
            
            # Create proposal and add to database
            newCompany = Company(dialog.nameText.text(),
                                 dialog.shortNameText.text(),
                                 True,
                                 nextId)
            self.companiesDict[newCompany.idNum] = newCompany

            self.insertIntoDatabase("Companies", "(Name, ShortName, Active)", "('" + newCompany.name + "', '" + newCompany.shortName + "', 'Y')")
            
            self.parent.parent.dbConnection.commit()
            
            # Make project into a ProjectTreeWidgetItem and add it to ProjectTree
            item = CompanyTreeWidgetItem(newCompany, self.companiesTreeWidget)
            self.companiesTreeWidget.addItem(item)
            self.updateCompaniesCount()

            self.addNewCompany.emit(newCompany.shortName)
            
    def showViewCompanyDialog(self):
        # Determine which tree the proposal is in--if any.  If none, don't
        # display dialog
        idxToShow = self.companiesTreeWidget.indexFromItem(self.companiesTreeWidget.currentItem())
        item = self.companiesTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = CompanyDialog("View", self, item.company)
            dialog.setWindowTitle("View Company")
            
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    if item.company.active == True:
                        active = "Y"
                    else:
                        active = "N"
                        
                    sql = ("UPDATE Companies SET Name = '" + dialog.nameText_edit.text() +
                           "', ShortName = '" + dialog.shortNameText_edit.text() +
                           "', Active = '" + active + 
                           "' WHERE idNum = " + str(item.company.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    self.parent.parent.dbConnection.commit()

                    item.company.name = dialog.nameText_edit.text()
                    item.company.shortName = dialog.shortNameText_edit.text()
                    #item.company.active = dialog.endDateText.text()
                    
                    self.companiesTreeWidget.refreshData()

    def deleteSelectedCompanyFromList(self):
        # Get the index of the item in the company list to delete
        idxToDelete = self.companiesTreeWidget.indexOfTopLevelItem(self.companiesTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.companiesTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            item = None
        
        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Companies WHERE idNum=?", (item.company.idNum,))
            self.companiesDict.pop(item.company.idNum)
            self.parent.parent.dbConnection.commit()
            self.updateCompaniesCount()

        self.deleteCompany.emit(item.company.shortName)

class CompanyView(QWidget):
    addNewCompany = pyqtSignal(str)
    deleteCompany = pyqtSignal(str)
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.companyWidget = CompanyWidget(self.dataConnection.companies, self)
        self.companyWidget.addNewCompany.connect(self.emitAddNewCompany)
        self.companyWidget.deleteCompany.connect(self.emitDeleteCompany)

        layout = QVBoxLayout()
        layout.addWidget(self.companyWidget)

        self.setLayout(layout)

    def emitAddNewCompany(self, shortName):
        self.addNewCompany.emit(shortName)

    def emitDeleteCompany(self, shortName):
        self.deleteCompany.emit(shortName)

class AssetTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, assetItem, parent):
        super().__init__(parent)
        self.asset = assetItem
        self.main = QWidget()
        
        idLabel = QLabel(str(self.asset.idNum))
        self.descLabel = QLabel(self.asset.description)
        self.costLabel = QLabel(str(self.asset.cost()))
        self.depAmtLabel = QLabel(str(self.asset.depreciatedAmount()))
        self.botDateLabel = QLabel(self.asset.acquireDate)
        self.inSvcDateLabel = QLabel(self.asset.inSvcDate)
        
        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.descLabel)
        layout.addWidget(self.costLabel)
        layout.addWidget(self.depAmtLabel)
        layout.addWidget(self.botDateLabel)
        layout.addWidget(self.inSvcDateLabel)
        
        self.main.setLayout(layout)

    def refreshData(self):
        self.descLabel.setText(self.asset.description)
        self.costLabel.setText(self.asset.cost())
        self.depAmtLabel.setText(self.asset.depreciatedAmount())
        self.botDateLabel.setText(self.asset.acquireDate)
        self.inSvcDateLabel.setText(self.asset.inSvcDate)
        
class AssetTreeWidget(QTreeWidget):
    def __init__(self, assetsDict):
        super().__init__()
        self.buildItems(self, assetsDict)

    def buildItems(self, parent, assetsDict):
        for assetKey in assetsDict:
            item = AssetTreeWidgetItem(assetsDict[assetKey], parent)
            self.addItem(item)

    def addItem(self, widgetItem):
        self.setItemWidget(widgetItem, 0, widgetItem.main)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()
            
class AssetWidget(QWidget):
    def __init__(self, assetsDict, parent):
        super().__init__()
        self.assetsDict = assetsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.currentAssetsLabel = QLabel("Assets: %d / %.02f" % (len(self.assetsDict.currentAssets()), self.assetsDict.currentCost()))
        mainLayout.addWidget(self.currentAssetsLabel)

        # Piece together the companies layout
        subLayout = QHBoxLayout()
        assetWidgetsLayout = QVBoxLayout()

        self.currentAssetsTreeWidget = AssetTreeWidget(self.assetsDict.currentAssets())
        self.currentAssetsTreeWidget.setIndentation(0)
        self.currentAssetsTreeWidget.setHeaderHidden(True)
        self.currentAssetsTreeWidget.setMinimumWidth(500)
        self.currentAssetsTreeWidget.setMaximumHeight(100)

        self.disposedAssetsTreeWidget = AssetTreeWidget(self.assetsDict.disposedAssets())
        self.disposedAssetsTreeWidget.setIndentation(0)
        self.disposedAssetsTreeWidget.setHeaderHidden(True)
        self.disposedAssetsTreeWidget.setMinimumWidth(500)
        self.disposedAssetsTreeWidget.setMaximumHeight(100)

        self.disposedAssetsLabel = QLabel("Assets: %d / %.02f" % (len(self.assetsDict.disposedAssets()), self.assetsDict.disposedCost()))
        
        assetWidgetsLayout.addWidget(self.currentAssetsTreeWidget)
        assetWidgetsLayout.addWidget(self.disposedAssetsLabel)
        assetWidgetsLayout.addWidget(self.disposedAssetsTreeWidget)
        assetWidgetsLayout.addStretch(1)

        buttonLayout = QVBoxLayout()
        newButton = QPushButton("New")
        newButton.clicked.connect(self.showNewAssetDialog)
        viewButton = QPushButton("View")
        #viewButton.clicked.connect(self.showViewAssetDialog)
        deleteButton = QPushButton("Delete")
        #deleteButton.clicked.connect(self.deleteSelectedAssetFromList)
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(viewButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addStretch(1)
        
        subLayout.addLayout(assetWidgetsLayout)
        subLayout.addLayout(buttonLayout)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

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

    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def updateAssetsCount(self):
        self.currentAssetsLabel.setText("Assets: %d / %.02f" % (len(self.assetsDict.currentAssets()), self.assetsDict.currentCost()))

    def showNewAssetDialog(self):
        dialog = AssetDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Assets")
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
            
            # Create proposal and add to database
            newAsset = Asset(dialog.descriptionText.text(),
                             dialog.dateAcquiredText.text(),
                             dialog.dateInSvcText.text(),
                             "",
                             dialog.usefulLifeText.text(),
                             nextId)
            self.assetsDict[newAsset.idNum] = newAsset
            newAsset.addCompany(self.parent.dataConnection.companies[companyId])
            newAsset.addAssetType(self.parent.dataConnection.assetTypes[assetTypeId])
            self.parent.dataConnection.companies[companyId].addAsset(newAsset)
            
            self.insertIntoDatabase("Assets", "(Description, AcquireDate, InSvcDate, DisposeDate, UsefulLife)", "('" + newAsset.description + "', '" + newAsset.acquireDate + "', '" + newAsset.inSvcDate + "', '" + newAsset.disposeDate + "', '" + newAsset.usefulLife + "')")
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('companies', " + str(companyId) + ", 'addAsset', 'assets', " + str(nextId) + ")")
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(nextId) + ", 'addCompany', 'companies', " + str(companyId) + ")")
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(nextId) + ", 'addAssetType', 'assetTypes', " + str(assetTypeId) + ")")
            
            self.parent.parent.dbConnection.commit()
            
            # Make project into a ProjectTreeWidgetItem and add it to ProjectTree
            item = AssetTreeWidgetItem(newAsset, self.currentAssetsTreeWidget)
            self.currentAssetsTreeWidget.addItem(item)
            self.updateAssetsCount()
            
    def showViewCompanyDialog(self):
        # Determine which tree the proposal is in--if any.  If none, don't
        # display dialog
        idxToShow = self.companiesTreeWidget.indexFromItem(self.companiesTreeWidget.currentItem())
        item = self.companiesTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = CompanyDialog("View", self, item.company)
            dialog.setWindowTitle("View Company")
            
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    if item.company.active == True:
                        active = "Y"
                    else:
                        active = "N"
                        
                    sql = ("UPDATE Companies SET Name = '" + dialog.nameText_edit.text() +
                           "', ShortName = '" + dialog.shortNameText_edit.text() +
                           "', Active = '" + active + 
                           "' WHERE idNum = " + str(item.company.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    self.parent.parent.dbConnection.commit()

                    item.company.name = dialog.nameText_edit.text()
                    item.company.shortName = dialog.shortNameText_edit.text()
                    #item.company.active = dialog.endDateText.text()
                    
                    self.companiesTreeWidget.refreshData()

    def deleteSelectedCompanyFromList(self):
        # Get the index of the item in the company list to delete
        idxToDelete = self.companiesTreeWidget.indexOfTopLevelItem(self.companiesTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.companiesTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            item = None
        
        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Companies WHERE idNum=?", (item.company.idNum,))
            self.companiesDict.pop(item.company.idNum)
            self.parent.parent.dbConnection.commit()
            self.updateCompaniesCount()

        self.deleteCompany.emit(item.company.shortName)
        
class AssetView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.assetWidget = AssetWidget(self.dataConnection.assets, self)

        layout = QVBoxLayout()
        layout.addWidget(self.assetWidget)

        self.setLayout(layout)
