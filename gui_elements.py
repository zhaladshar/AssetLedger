from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *
import re
from classes import *
import sys
import constants
        
class SaveViewCancelButtonWidget(QWidget):
    def __init__(self, mode):
        super().__init__()
        layout = QHBoxLayout()
        
        self.saveButton = QPushButton("Save")
        self.editButton = QPushButton("Edit")
        self.cancelButton = QPushButton("Cancel")

        layout.addWidget(self.saveButton)
        if mode == "View":
            layout.addWidget(self.editButton)
        layout.addWidget(self.cancelButton)
        
        self.setLayout(layout)
        
class GLPostingLineItem(QWidget):
    deleteRow = pyqtSignal(int)
    validateRow = pyqtSignal(int)
    
    def __init__(self, glAcctsList, rowNum, glAcct=None, debit=None, credit=None):
        super().__init__()
        self.row = rowNum
        
        if glAcct and (debit or credit):
            pass
        else:
            self.glBox = QComboBox()
            self.glBox.addItems(glAcctsList)
            self.debitBox = QLineEdit()
            self.creditBox = gui_elements.NewLineEdit()
            self.creditBox.lostFocus.connect(lambda: self.validateRow.emit(self.row))
            deleteButton = QPushButton("-")
            deleteButton.clicked.connect(lambda: self.deleteRow.emit(self.row))

        layout = QHBoxLayout()
        layout.addWidget(self.glBox)
        layout.addWidget(self.debitBox)
        layout.addWidget(self.creditBox)
        layout.addWidget(deleteButton)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def balanceType(self):
        if self.debitBox.text() != "":
            return constants.DEBIT
        elif self.creditBox.text() != "":
            return constants.CREDIT
        else:
            return "NONE"

    def balance(self):
        if self.debitBox.text() == "":
            debit = 0
        else:
            debit = float(self.debitBox.text())

        if self.creditBox.text() == "":
            credit = 0
        else:
            credit = float(self.creditBox.text())
        return abs(debit - credit)

class GLPostingsSection(QWidget):
    def __init__(self, glAcctsList, glPosting=None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.numEntries = 0
        self.glAcctsList = glAcctsList
        self.details = {}

        if glPosting:
            pass
        else:
            self.addLine()

        self.layout.setSpacing(0)
        self.setLayout(self.layout)

    def addLine(self, glAcct=None, debit=None, credit=None):
        if glAcct and debit and credit:
            pass
        else:
            newEntry = GLPostingLineItem(self.glAcctsList, self.numEntries)
            newEntry.validateRow.connect(self.validateRow)
            newEntry.deleteRow.connect(self.deleteRow)
            
        self.details[self.numEntries] = newEntry
        self.layout.addWidget(newEntry)
        self.numEntries += 1

    def validateRow(self, rowNum):
        item = self.details[rowNum]
        if item.debitBox.text() != "" or item.creditBox.text() != "":
            self.addLine()

    def deleteRow(self, rowNum):
        item = self.details.pop(rowNum)
        self.layout.removeWidget(item)
        item.deleteLater()

    def inBalance(self):
        # If credits = debits and credit are negative, the posting is in balance
        # if the balance == 0.
        balance = 0.0
        for key, entry in self.details.items():
            if entry.balanceType() == constants.DEBIT:
                balance += entry.balance()
            elif entry.balanceType() == constants.CREDIT:
                balance -= entry.balance()
        if balance == 0.0:
            return True
        else:
            return False
        
class NewTreeWidget(QTreeWidget):
    def __init__(self, headerList, widthList):
        super().__init__()
        self.setIndentation(0)
        self.setMinimumWidth(constants.TREE_WIDGET_MIN_WIDTH)
        self.setMaximumHeight(constants.TREE_WIDGET_MAX_HEIGHT)
        self.setSortingEnabled(True)
        self.setHeaderLabels(headerList)
        self.setColumnSizes(constants.TREE_WIDGET_MIN_WIDTH, widthList)

    def setColumnSizes(self, width, columnSizePercentList):
        index = 0
        for percent in columnSizePercentList:
            size = int(percent * width)
            self.header().resizeSection(index, size)
            index += 1
        
class ClickableLabel(QLabel):
    released = pyqtSignal()

    def __init__(self, text):
        super().__init__(text)

    def mouseReleaseEvent(self, event):
        self.released.emit()

class InvoicePaymentTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, invoicePaymentItem, parent):
        super().__init__(parent)
        self.invoicePayment = invoicePaymentItem
        self.setText(0, str(self.invoicePayment.idNum))
        self.setText(1, self.invoicePayment.datePaid)
        self.setText(2, str(self.invoicePayment.amountPaid))

    def refreshData(self):
        self.setText(1, self.invoicePayment.datePaid)
        self.setText(2, str(self.invoicePayment.amountPaid))

class InvoicePaymentTreeWidget(NewTreeWidget):
    def __init__(self, invoicePaymentsDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, invoicePaymentsDict)

    def buildItems(self, parent, invoicePaymentsDict):
        for invoicePaymentKey in invoicePaymentsDict:
            item = InvoicePaymentTreeWidgetItem(invoicePaymentsDict[invoicePaymentKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()
            
class StandardButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.newButton = QPushButton("New")
        self.viewButton = QPushButton("View")
        self.deleteButton = QPushButton("Delete")

        self.layout.addWidget(self.newButton)
        self.layout.addWidget(self.viewButton)
        self.layout.addWidget(self.deleteButton)
        self.layout.addStretch(1)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)

    def addSpacer(self):
        # Remove last element as it is a spacer.
        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
        self.layout.addSpacing(10)
        self.layout.addStretch(1)

    def addButton(self, button):
        # Remove last element as it is a spacer.
        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
        self.layout.addWidget(button)
        self.layout.addStretch(1)
        
class DateLineEdit(QLineEdit):
    def __init__(self, text=None):
        super().__init__(text)

    def focusOutEvent(self, event):
        self.setText(self.formatStringAsDate(self.text()))
        super().focusOutEvent(event)
        
    def formatStringAsDate(self, string):
        regex = re.fullmatch(r"[0-9]+", string)
        if regex and len(string) == 6:
            return string[0:2] + "/" + string[2:4] + "/20" + string[4:6]
        elif regex and len(string) == 8:
            return string[0:2] + "/" + string[2:4] + "/" + string[4:8]

        regex = re.fullmatch(r"([0-9]+)/([0-9]+)/([0-9]+)", string)
        if regex and len(regex.groups()[2]) == 2:
            return "{:>02}".format(regex.groups()[0]) + "/" + "{:>02}".format(regex.groups()[1]) + "/20" + regex.groups()[2]
        elif regex and len(regex.groups()[2]) == 4:
            return "{:>02}".format(regex.groups()[0]) + "/" + "{:>02}".format(regex.groups()[1]) + "/" + regex.groups()[2]
        else:
            return string
        
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

    def showAssetDict(self, checked):
        # Only do this if we are clicking on the item, not if it is being
        # unclicked.
        if checked == True:
            self.clear()
            
            self.selector.addItems(self.company.assets.currentAssets().sortedListOfKeysAndNames())
            self.selector.show()
            
            self.emitRdoBtnChange()

    def showProjectDict(self, checked):
        # Only do this if we are clicking on the item, not if it is being
        # unclicked.
        if checked == True:
            self.clear()
            
            self.selector.addItems(self.company.projects.projectsByStatus(constants.OPN_PROJECT_STATUS).sortedListOfKeysAndNames())
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
    
    def __init__(self, detailsDict=None, proposals=None):
        super().__init__()
        self.details = {}
        self.proposals = proposals
        
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
        
    def addProposals(self, proposals):
        self.proposals = proposals
        self.resetProposalBoxes()

    def makeProposalDetComboBox(self, proposalDet):
        proposalDetList = [""]

        if self.proposals:
            for proposal in self.proposals:
                for detailKey, detail in proposal.details.items():
                    proposalDetList.append("%4s - %s" % (detailKey, detail.description))
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
            if self.proposals:
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

class AssetHistoryTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, historyItem, parent):
        super().__init__(parent)
        self.history = historyItem

        self.setText(0, self.history.date)
        self.setText(1, self.history.text)
        if self.history.posNeg == constants.POSITIVE:
            self.setText(2, "{:,.2f}".format(self.history.amount))
        else:
            self.setText(2, "{:,.2f}".format(-1 * self.history.amount))

    def refreshData(self):
        self.setText(0, self.history.date)
        self.setText(1, self.history.text)
        if self.history.posNeg == constants.POSITIVE:
            self.setText(2, "{:,.2f}".format(self.history.amount))
        else:
            self.setText(2, "{:,.2f}".format(-1 * self.history.amount))

class AssetHistoryTreeWidget(NewTreeWidget):
    def __init__(self, historyDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, historyDict)
        self.setColumnCount(len(headerList))
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, historyDict):
        for historyKey in historyDict:
            item = AssetHistoryTreeWidgetItem(historyDict[historyKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

class VendorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, vendorItem, parent):
        super().__init__(parent)
        self.vendor = vendorItem

        self.setText(0, str(self.vendor.idNum))
        self.setText(1, self.vendor.name)
        self.setText(2, "%d / %d" % (len(self.vendor.proposals.proposalsByStatus("Open")),
                                     len(self.vendor.proposals)))
        self.setText(3, "%d / %d" % (self.vendor.openInvoiceCount(),
                                     len(self.vendor.invoices)))
        self.setText(4, "{:,.2f}".format(self.vendor.balance()))

    def refreshData(self):
        self.setText(1, self.vendor.name)
        self.setText(2, "%d / %d" % (len(self.vendor.proposals.proposalsByStatus("Open")),
                                     len(self.vendor.proposals)))
        self.setText(3, "%d / %d" % (self.vendor.openInvoiceCount(),
                                     len(self.vendor.invoices)))
        self.setText(4, "{:,.2f}".format(self.vendor.balance()))
        
class VendorTreeWidget(NewTreeWidget):
    def __init__(self, vendorsDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, vendorsDict)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)
        
    def buildItems(self, parent, vendorsDict):
        for vendorKey in vendorsDict:
            item = VendorTreeWidgetItem(vendorsDict[vendorKey], parent)
            self.addTopLevelItem(item)

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

        self.vendorTreeWidget = VendorTreeWidget(self.vendorsDict,
                                                 constants.VENDOR_HDR_LIST,
                                                 constants.VENDOR_HDR_WDTH)
        
        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewVendorDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewVendorDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedVendorFromList)

        subLayout.addWidget(self.vendorTreeWidget)
        subLayout.addWidget(buttonWidget)

        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)
        
    def stripAllButNumbers(self, string):
        if string == "":
            return None
        else:
            regex = re.match(r"\s*([0-9]+).*", string)
            return int(regex.groups()[0])

    def showNewVendorDialog(self):
        dialog = VendorDialog("New", self.parent.dataConnection.glAccounts, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            self.parent.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Vendors'")
            largestId = self.parent.parent.dbCursor.fetchone()
            if largestId != None:
                nextId = largestId[0] + 1
            else:
                nextId = 1
            GLNumber = self.stripAllButNumbers(dialog.glAccountsBox.currentText())

            # Create new vendor and add it to database and company data
            newVendor = Vendor(dialog.nameText.text(),
                               dialog.addressText.text(),
                               dialog.cityText.text(),
                               dialog.stateText.text(),
                               dialog.zipText.text(),
                               dialog.phoneText.text(),
                               nextId)
            newVendor.addGLAccount(self.parent.dataConnection.glAccounts[GLNumber])
            self.vendorsDict[newVendor.idNum] = newVendor
            self.parent.parent.dbCursor.execute("INSERT INTO Vendors (Name, Address, City, State, ZIP, Phone) VALUES (?, ?, ?, ?, ?, ?)",
                                  (newVendor.name, newVendor.address, newVendor.city, newVendor.state, newVendor.zip, newVendor.phone))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)", ("vendors", newVendor.idNum, "addGLAccount", "glAccounts", GLNumber))
            self.parent.parent.dbConnection.commit()

            # Make vendor into a VendorTreeWidgetItem and add it to VendorTree
            item = VendorTreeWidgetItem(newVendor, self.vendorTreeWidget)
            self.vendorTreeWidget.addTopLevelItem(item)
            self.updateVendorCount()

    def showViewVendorDialog(self):
        idxToShow = self.vendorTreeWidget.indexFromItem(self.vendorTreeWidget.currentItem())
        item = self.vendorTreeWidget.itemFromIndex(idxToShow)

        # Only display dialog if an item in the widget tree has been selected
        if item:
            dialog = VendorDialog("View", self.parent.dataConnection.glAccounts, self, item.vendor)
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

                    self.vendorsDict[item.vendor.idNum].name = dialog.nameText_edit.text()
                    self.vendorsDict[item.vendor.idNum].address = dialog.addressText_edit.text()
                    self.vendorsDict[item.vendor.idNum].city = dialog.cityText_edit.text()
                    self.vendorsDict[item.vendor.idNum].state = dialog.stateText_edit.text()
                    self.vendorsDict[item.vendor.idNum].zip = dialog.zipText_edit.text()
                    self.vendorsDict[item.vendor.idNum].phone = dialog.phoneText_edit.text()

                    if dialog.glAccountChanged == True:
                        newGLAccountNum = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
                        oldGLAccountNum = item.vendor.glAccount.idNum
                        item.vendor.addGLAccount(self.parent.dataConnection.glAccounts[newGLAccountNum])

                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='vendors' AND ObjectIdBeingLinked=? AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='glAccounts'",
                                                            (newGLAccountNum, oldGLAccountNum, item.vendor.idNum))
                    self.parent.parent.dbConnection.commit()
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
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='vendors' AND ObjectIdToAddLinkTo=?", (item.vendor.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='vendors' AND ObjectIdBeingLinked=?", (item.vendor.idNum,))
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

        self.setText(0, str(self.invoice.idNum))
        self.setText(1, self.invoice.vendor.name)
        self.setText(2, self.invoice.date)
        self.setText(3, self.invoice.dueDate)
        self.setText(4, "{:,.2f}".format(self.invoice.amount()))
        self.setText(5, "{:,.2f}".format(self.invoice.paid()))
        self.setText(6, "{:,.2f}".format(self.invoice.balance()))

    def refreshData(self):
        self.setText(1, self.invoice.vendor.name)
        self.setText(2, self.invoice.date)
        self.setText(3, self.invoice.dueDate)
        self.setText(4, "{:,.2f}".format(self.invoice.amount()))
        self.setText(5, "{:,.2f}".format(self.invoice.paid()))
        self.setText(6, "{:,.2f}".format(self.invoice.balance()))

class InvoiceTreeWidget(NewTreeWidget):
    balanceZero = pyqtSignal(int)
    balanceNotZero = pyqtSignal(int)
    
    def __init__(self, invoicesDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, invoicesDict)
        self.setColumnCount(7)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, invoicesDict):
        for invoiceKey in invoicesDict:
            item = InvoiceTreeWidgetItem(invoicesDict[invoiceKey], parent)
            self.addTopLevelItem(item)

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
    updateAssetTree = pyqtSignal()
    updateCompanyTree = pyqtSignal()
    postToGL = pyqtSignal(int, str, str, list)
    updateGLPost = pyqtSignal(object, int, str, str, list)
    updateGLDet = pyqtSignal(object, float, str, object)
    deleteGLPost = pyqtSignal(object)
    
    def __init__(self, invoicesDict, paymentTypesDict, invoicePaymentsDict, parent):
        super().__init__()
        self.invoicesDict = invoicesDict
        self.paymentTypesDict = paymentTypesDict
        self.invoicePaymentsDict = invoicePaymentsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openInvoicesLabel = QLabel("Open Invoices: %d" % len(self.invoicesDict.openInvoices()))
        mainLayout.addWidget(self.openInvoicesLabel)

        # Piece together the invoices layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.openInvoices().trueInvoices(), constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
        self.openInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openInvoicesTreeWidget.balanceZero.connect(self.moveOpenInvoiceToPaid)

        self.paidInvoicesTreeWidget = InvoiceTreeWidget(self.invoicesDict.paidInvoices().trueInvoices(), constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
        self.paidInvoicesTreeWidget.balanceNotZero.connect(self.movePaidInvoiceToOpen)
        self.paidInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        
        self.paidInvoicesLabel = QLabel("Paid Invoices: %d" % len(self.invoicesDict.paidInvoices()))

        treeWidgetsLayout.addWidget(self.openInvoicesTreeWidget)
        treeWidgetsLayout.addWidget(self.paidInvoicesLabel)
        treeWidgetsLayout.addWidget(self.paidInvoicesTreeWidget)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewInvoiceDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewInvoiceDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedInvoiceFromList)
        buttonWidget.addSpacer()
        
        payInvoiceButton = QPushButton("Pay...")
        payInvoiceButton.clicked.connect(self.payInvoice)
        buttonWidget.addButton(payInvoiceButton)

        paymentTypeButton = QPushButton("Pymt Types...")
        paymentTypeButton.clicked.connect(self.showPaymentTypeDialog)
        buttonWidget.addButton(paymentTypeButton)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def refreshOpenInvoiceTree(self):
        self.openInvoicesTreeWidget.refreshData()

    def refreshPaidInvoicesTreeWidget(self):
        self.paidInvoicesTreeWidget.refreshData()
    
    def payInvoice(self):
        idxToShow = self.openInvoicesTreeWidget.indexFromItem(self.openInvoicesTreeWidget.currentItem())
        item = self.openInvoicesTreeWidget.itemFromIndex(idxToShow)
        
        if item:
            dialog = InvoicePaymentDialog("New", self.paymentTypesDict, self, item.invoice)
            if dialog.exec_():
                nextId = self.nextIdNum("InvoicesPayments")
                paymentTypeId = self.stripAllButNumbers(dialog.paymentTypeBox.currentText())
                datePd = dialog.datePaidText.text()
                amtPd = float(dialog.amountText.text())
                
                # Create new payment and get necessary objects
                newPayment = InvoicePayment(datePd, amtPd, nextId)
                paymentType = self.paymentTypesDict[paymentTypeId]
                
                # Add to database and to data structure
                self.insertIntoDatabase("InvoicesPayments", "(DatePaid, AmountPaid)", "('" + newPayment.datePaid + "', " + str(newPayment.amountPaid) + ")")
                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoices', " + str(item.invoice.idNum) + ", 'addPayment', 'invoicesPayments', " + str(nextId) + ")")
                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoicesPayments', " + str(newPayment.idNum) + ", 'addInvoice', 'invoices', " + str(item.invoice.idNum) + ")")
                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoicesPayments', " + str(newPayment.idNum) + ", 'addPaymentType', 'paymentTypes', " + str(paymentTypeId) + ")")
                self.parent.parent.dbConnection.commit()
                
                newPayment.addInvoice(item.invoice)
                item.invoice.addPayment(newPayment)
                newPayment.addPaymentType(paymentType)
                self.invoicePaymentsDict[newPayment.idNum] = newPayment
                
                # Create GL posting for this payment
                companyId = newPayment.invoicePaid.company.idNum
                paymentTypeId = self.stripAllButNumbers(dialog.paymentTypeBox.currentText())
                description = constants.GL_POST_PYMT_DESC % (int(dialog.invoiceText.text()), item.invoice.vendor.idNum, datePd)
                details = []
                details.append((amtPd, "CR", paymentType.glAccount.idNum, newPayment, "invoicesPayments"))
                details.append((amtPd, "DR", item.invoice.vendor.glAccount.idNum, None, None))
                
                self.postToGL.emit(companyId, datePd, description, details)
                
                # Refresh AP info
                self.updateVendorTree.emit()
                self.refreshOpenInvoiceTree()
                self.updateInvoicesCount()
                
    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.paidInvoicesTreeWidget.setCurrentItem(self.paidInvoicesTreeWidget.invisibleRootItem())
        else:
            self.openInvoicesTreeWidget.setCurrentItem(self.openInvoicesTreeWidget.invisibleRootItem())

    def showPaymentTypeDialog(self):
        dialog = PaymentTypeDialog(self.parent.dataConnection.paymentTypes, self.parent.dataConnection.glAccounts, self)
        dialog.exec_()

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
        dialog = InvoiceDialog("New", None, self)
        if dialog.exec_():
            nextId = self.nextIdNum("Invoices")
            
            # Create new invoice
            newInvoice = Invoice(dialog.invoiceDateText.text(),
                                 dialog.dueDateText.text(),
                                 nextId)
            
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
                    self.insertIntoDatabase("InvoicesDetails", "(Description, Cost)", "('" + invoiceDetail.description + "', " + str(invoiceDetail.cost) + ")")
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
            
            # Add invoice<->vendor links
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            newInvoice.addVendor(self.parent.dataConnection.vendors[vendorId])
            self.parent.dataConnection.vendors[vendorId].addInvoice(newInvoice)
            
            # Add invoice<->project/asset links
            type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
            
            if dialog.assetProjSelector.assetSelected() == True:
                asset = self.parent.dataConnection.assets[type_Id]
                type_ = "assets"
                type_action = "addAsset"
                newInvoice.addAsset(asset)
                asset.addInvoice(newInvoice)

                # Create new cost element for asset
                costId = self.nextIdNum("AssetCosts")
                cost = AssetCost(newInvoice.amount(), costId)
                asset.addCost(cost)
                cost.addAsset(asset)
                cost.addInvoice(newInvoice)
                
                self.parent.dataConnection.assetCosts[costId] = cost
                self.parent.parent.dbCursor.execute("INSERT INTO AssetCosts (Cost) VALUES (?)", (newInvoice.amount(),))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('assets', ?, 'addCost', 'assetCosts', ?)", (asset.idNum, cost.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('assetCosts', ?, 'addAsset', 'assets', ?)", (cost.idNum, asset.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('assetCosts', ?, 'addInvoice', 'invoices', ?)", (cost.idNum, newInvoice.idNum))

                # Create history entry for asset
                histId = self.nextIdNum("AssetHistory")
                history = AssetHistory(newInvoice.date, constants.ASSET_HIST_INV % newInvoice.idNum, newInvoice.amount(), constants.POSITIVE, histId)
                history.addAsset(asset)
                asset.addHistory(history)
                history.addObject(cost)
                self.parent.dataConnection.assetsHistory[histId] = history
                self.parent.parent.dbCursor.execute("INSERT INTO AssetHistory (Date, Description, Dollars, PosNeg) VALUES (?, ?, ?, ?)",
                                                    (history.date, history.text, history.amount, history.posNeg))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assetsHistory', histId, 'addAsset', 'assets', asset.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assetsHistory', histId, 'addObject', 'assetCosts', cost.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assets', asset.idNum, 'addHistory', 'assetsHistory', histId))
            else:
                type_ = "projects"
                type_action = "addProject"
                newInvoice.addProject(self.parent.dataConnection.projects[type_Id])
                self.parent.dataConnection.projects[type_Id].addInvoice(newInvoice)
            
            # Add invoice<->company links
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            newInvoice.addCompany(self.parent.dataConnection.companies[companyId])
            self.parent.dataConnection.companies[companyId].addInvoice(newInvoice)
            
            # Add the invoice to the corporate data structure and update the
            # invoice and the link information to the database
            self.invoicesDict[newInvoice.idNum] = newInvoice
            
            self.parent.parent.dbCursor.execute("INSERT INTO Invoices (InvoiceDate, DueDate) VALUES (?, ?)",
                                  (newInvoice.date, newInvoice.dueDate))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addVendor', 'vendors', ?)", (nextId, vendorId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('vendors', ?, 'addInvoice', 'invoices', ?)", (vendorId, nextId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, ?, ?, ?)", (nextId, type_action, type_, type_Id))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, 'addInvoice', 'invoices', ?)", (type_, type_Id, nextId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('invoices', ?, 'addCompany', 'companies', ?)", (nextId, companyId))
            self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES ('companies', ?, 'addInvoice', 'invoices', ?)", (companyId, nextId))

            self.parent.parent.dbConnection.commit()
            
            # Make invoice into an InvoiceTreeWidgetItem and add it to VendorTree
            item = InvoiceTreeWidgetItem(newInvoice, self.openInvoicesTreeWidget)
            self.openInvoicesTreeWidget.addTopLevelItem(item)
            self.updateInvoicesCount()
            
            # Create GL posting.
            date = newInvoice.date
            description = constants.GL_POST_INV_DESC % (newInvoice.idNum, newInvoice.vendor.idNum, date)
            details = [(newInvoice.amount(), "CR", newInvoice.vendor.glAccount.idNum, newInvoice, "invoices")]
            if newInvoice.assetProj[0] == "projects":
                details.append((newInvoice.amount(), "DR", newInvoice.assetProj[1].glAccount.idNum, None, None))
            else:
                details.append((newInvoice.amount(), "DR", newInvoice.assetProj[1].assetType.assetGLAccount.idNum, None, None))
            
            self.postToGL.emit(companyId, date, description, details)
            
            # Update vendor tree widget to display new information based on
            # invoice just created
            self.updateVendorTree.emit()
            self.updateProjectTree.emit()
            self.updateAssetTree.emit()
            self.updateCompanyTree.emit()
            
    def showViewInvoiceDialog(self):
        needToUpdateGL = False
        
        # Determine which invoice tree (if any) has been selected
        idxToShow = self.openInvoicesTreeWidget.indexFromItem(self.openInvoicesTreeWidget.currentItem())
        item = self.openInvoicesTreeWidget.itemFromIndex(idxToShow)
        if item == None:
            idxToShow = self.paidInvoicesTreeWidget.indexFromItem(self.paidInvoicesTreeWidget.currentItem())
            item = self.paidInvoicesTreeWidget.itemFromIndex(idxToShow)

        # Only show dialog if an item has been selected
        if item:
            dialog = InvoiceDialog("View", self.paymentTypesDict, self, item.invoice)
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
                            type_ = "assets"
                            oldType = item.invoice.assetProj[1]

                            oldType.removeInvoice(item.invoice)
                            item.invoice.addAsset(self.parent.dataConnection.assets[newTypeId])
                            self.parent.dataConnection.assets[newTypeId].addInvoice(item.invoice)
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

                        # Need to transmit cost, history, and signal that GL entry needs to be updated
                        if dialog.assetProjSelector.assetSelected() == True:
                            cost = oldType.findCost(item.invoice)
                            oldType.removeCost(cost)
                            item.invoice.assetProj[1].addCost(cost)

                            history = oldType.findHistory(cost)
                            oldType.removeHistory(history)
                            item.invoice.assetProj[1].addHistory(history)

                            oldGL = oldType.assetType.assetGLAccount
                            newGL = item.invoice.assetProj[1].assetType.assetGLAccount
                            if oldGL != newGL:
                                needToUpdateGL = True
                            
                            self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetCosts' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='assets'",
                                                                (item.invoice.assetProj[1].idNum, cost.idNum))
                            self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='assets' AND ObjectBeingLinked='assetCosts' AND ObjectIdBeingLinked=?",
                                                                (item.invoice.assetProj[1].idNum, cost.idNum))
                            self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetsHistory' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='assets'",
                                                                (item.invoice.assetProj[1].idNum, history.idNum))
                            self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='assets' AND ObjectBeingLinked='assetsHistory' AND ObjectIdBeingLinked=?",
                                                                (item.invoice.assetProj[1].idNum, history.idNum))
                            
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

                        # If invoice of an asset, update the asset cost and
                        # update history element
                        if item.invoice.assetProj[0] == "assets":
                            cost = item.invoice.assetProj[1].findCost(item.invoice)
                            cost.cost = item.invoice.amount()
                            
                            history = item.invoice.assetProj[1].getHistoryByObject(item.invoice)
                            history.date = item.invoice.date
                            history.amount = item.invoice.amount()

                            self.parent.parent.dbCursor.execute("UPDATE AssetCosts SET Cost=? WHERE idNum=?",
                                                                (cost.cost, cost.idNum))
                            self.parent.parent.dbCursor.execute("UPDATE AssetHistory SET Date=?, Dollars=? WHERE idNum=?",
                                                                (history.date, history.amount, history.idNum))
                            
                    self.parent.parent.dbConnection.commit()

                    item.invoice.date = dialog.invoiceDateText_edit.text()
                    item.invoice.dueDate = dialog.dueDateText_edit.text()

                    if needToUpdateGL == True:
                        oldGLPost = item.invoice.glPosting.detailOf
                        glDetList = []
                        for detail in oldGLPost.details.values():
                            if detail.glAccount != item.invoice.vendor.glAccount:
                                glDetList.append((detail, item.invoice.amount(), detail.debitCredit, newGL))
                            else:
                                glDetList.append((detail, item.invoice.amount(), detail.debitCredit, item.invoice.vendor.glAccount))
                        
                        self.updateGLPost.emit(oldGLPost, oldGLPost.company.idNum, oldGLPost.date, oldGLPost.description, glDetList)

                    self.openInvoicesTreeWidget.refreshData()
                    self.paidInvoicesTreeWidget.refreshData()

                    self.updateVendorTree.emit()
                    self.updateProjectTree.emit()
                    self.updateAssetTree.emit()
                    self.updateCompanyTree.emit()
                    
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
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoices' AND ObjectIdToAddLinkTo=?)",
                                                (item.invoice.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectBeingLinked='invoices' AND ObjectIdBeingLinked=?)",
                                                (item.invoice.idNum,))
            
            # Delete invoice details and detail/proposal connections
            for detailKey in item.invoice.details:
                invoiceDetId = item.invoice.details[detailKey].idNum

                self.parent.parent.dbCursor.execute("DELETE FROM InvoicesDetails WHERE idNum=?", (invoiceDetId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='invoicesDetails' AND ObjectIdToAddLinkTo=?)", (invoiceDetId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectBeingLinked='invoicesDetails' AND ObjectIdBeingLinked=?)", (invoiceDetId,))

                invoiceDetail = self.parent.dataConnection.invoicesDetails.pop(invoiceDetId)
                if invoiceDetail.proposalDetail:
                    self.parent.dataConnection.proposalsDetails[invoiceDetail.proposalDetail.idNum].removeInvoiceDetail(invoiceDetail)
            
            # Remove invoice<->data connections
            self.parent.parent.dbConnection.commit()
            self.parent.dataConnection.vendors[item.invoice.vendor.idNum].removeInvoice(item.invoice)
            self.parent.dataConnection.companies[item.invoice.company.idNum].removeInvoice(item.invoice)
            
            if item.invoice.assetProj[0] == "assets":
                self.parent.dataConnection.assets[item.invoice.assetProj[1].idNum].removeInvoice(item.invoice)
            else:
                self.parent.dataConnection.projects[item.invoice.assetProj[1].idNum].removeInvoice(item.invoice)
            
            self.invoicesDict.pop(item.invoice.idNum)
            
            # Delete payments if invoice has any
            for paymentId, payment in item.invoice.payments.items():
                self.invoicePaymentsDict.pop(paymentId)
                self.parent.parent.dbCursor.execute("DELETE FROM InvoicesPayments WHERE idNum=?",
                                                    (paymentId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='invoicesPayments' AND ObjectIdBeingLinked=?",
                                                    (paymentId,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='invoicesPayments' AND ObjectIdToAddLinkTo=?",
                                                    (paymentId,))
                self.parent.parent.dbConnection.commit()
                glDet = payment.glPosting
                glPost = glDet.detailOf
                self.deleteGLPost.emit(glPost)
            
            # If invoice has an asset, zero the cost associated with this and
            # delete the history element
            if item.invoice.assetProj[0] == "assets":
                cost = item.invoice.assetProj[1].findCost(item.invoice)
                item.invoice.assetProj[1].removeCost(cost)

                history = item.invoice.assetProj[1].getHistoryByObject(cost)
                item.invoice.assetProj[1].removeHistory(history)

                self.parent.dataConnection.assetsHistory.pop(history.idNum)
                self.parent.dataConnection.assetCosts.pop(cost.idNum)
                self.parent.parent.dbCursor.execute("DELETE FROM AssetCosts WHERE idNum=?", (cost.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='assetCosts' AND ObjectIdToAddLinkTo=?", (cost.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='assetCosts' AND ObjectIdBeingLinked=?", (cost.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM AssetHistory WHERE idNum=?", (history.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='assetsHistory' AND ObjectIdToAddLinkTo=?", (history.idNum,))
                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='assetsHistory' AND ObjectIdBeingLinked=?", (history.idNum,))
            
            # Delete GL Postings
            glDet = item.invoice.glPosting
            glPost = glDet.detailOf
            
            self.deleteGLPost.emit(glPost)
            
            self.updateInvoicesCount()

            self.updateVendorTree.emit()
            self.updateProjectTree.emit()
            self.updateAssetTree.emit()
            self.updateCompanyTree.emit()

    def updateInvoicesCount(self):
        self.openInvoicesLabel.setText("Open Invoices: %d" % len(self.invoicesDict.openInvoices()))
        self.paidInvoicesLabel.setText("Paid Invoices: %d" % len(self.invoicesDict.paidInvoices()))

    def moveOpenInvoiceToPaid(self, idx):
        item = self.openInvoicesTreeWidget.takeTopLevelItem(idx)
        newItem = InvoiceTreeWidgetItem(item.invoice, self.paidInvoicesTreeWidget)
        self.paidInvoicesTreeWidget.addTopLevelItem(newItem)

    def movePaidInvoiceToOpen(self, idx):
        item = self.paidInvoicesTreeWidget.takeTopLevelItem(idx)
        newItem = InvoiceTreeWidgetItem(item.invoice, self.openInvoicesTreeWidget)
        self.openInvoicesTreeWidget.addTopLevelItem(newItem)

class APView(QWidget):
    updateProjectTree = pyqtSignal()
    updateAssetTree = pyqtSignal()
    updateCompanyTree = pyqtSignal()
    updateGLTree = pyqtSignal()
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        layout = QVBoxLayout()
        
        self.vendorWidget = VendorWidget(self.dataConnection.vendors, self)
        self.invoiceWidget = InvoiceWidget(self.dataConnection.invoices, self.dataConnection.paymentTypes, self.dataConnection.invoicesPayments, self)
        self.invoiceWidget.updateVendorTree.connect(self.updateVendorWidget)
        self.invoiceWidget.updateProjectTree.connect(self.emitUpdateProjectTree)
        self.invoiceWidget.updateAssetTree.connect(self.emitUpdateAssetTree)
        self.invoiceWidget.updateCompanyTree.connect(self.emitUpdateCompanyTree)
        self.invoiceWidget.postToGL.connect(self.postToGL)
        self.invoiceWidget.updateGLPost.connect(self.updateGLPost)
        self.invoiceWidget.updateGLDet.connect(self.updateGLDet)
        self.invoiceWidget.deleteGLPost.connect(self.deleteGLPost)
        
        layout.addWidget(self.vendorWidget)
        layout.addWidget(self.invoiceWidget)
        layout.addStretch(1)

        self.setLayout(layout)

    def nextIdNum(self, name):
        self.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.parent.dbCursor.fetchone()
        if largestId != None:
            return int(largestId[0]) + 1
        else:
            return 1
        
    def updateVendorWidget(self):
        self.vendorWidget.refreshVendorTree()

    def emitUpdateProjectTree(self):
        self.updateProjectTree.emit()

    def emitUpdateAssetTree(self):
        self.updateAssetTree.emit()

    def emitUpdateCompanyTree(self):
        self.updateCompanyTree.emit()

    def updateGLPost(self, glPost, companyId, postingDate, description, glDetList):
        glPost.description = description
        glPost.date = postingDate
        
        for glDet in glDetList:
            self.updateGLDet(glDet[0], glDet[1], glDet[2], glDet[3])
        
        self.parent.dbCursor.execute("UPDATE GLPostings SET Date=?, Description=? WHERE idNum=?",
                                     (postingDate, description, glPost.idNum))
        self.parent.dbConnection.commit()
        self.updateGLTree.emit()

    def updateGLDet(self, glDet, amtPd, debitCredit, glAccount):
        glDet.amount = amtPd
        glDet.debitCredit = debitCredit
        
        glDet.glAccount.removePosting(glDet)
        glDet.glAccount = glAccount
        glAccount.addPosting(glDet)
        
        self.parent.dbCursor.execute("UPDATE GLPostingsDetails SET Amount=?, DebitCredit=? WHERE idNum=?",
                                     (amtPd, debitCredit, glDet.idNum))
        self.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='glPostingsDetails' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='glAccounts'",
                                     (glAccount.idNum, glDet.idNum))
        self.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='glAccounts' AND ObjectIdToAddLinkTo=? AND ObjectBeingLinked='glPostingsDetails'",
                                     (glAccount.idNum, glDet.idNum))
        self.parent.dbConnection.commit()

    def deleteGLPost(self, GLPost):
        self.dataConnection.glPostings.pop(GLPost.idNum)
        self.dataConnection.companies[GLPost.company.idNum].removePosting(GLPost)
        self.parent.dbCursor.execute("DELETE FROM GLPostings WHERE idNum=?",
                                     (GLPost.idNum,))
        self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='glPostings' AND ObjectIdToAddLinkTo=?",
                                     (GLPost.idNum,))
        self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='glPostings' AND ObjectIdBeingLinked=?",
                                     (GLPost.idNum,))
        for glDetKey, glDet in GLPost.details.items():
            self.dataConnection.glPostingsDetails.pop(glDetKey)
            glAccount = glDet.glAccount
            glAccount.removePosting(glDet)
            self.parent.dbCursor.execute("DELETE FROM GLPostingsDetails WHERE idNum=?",
                                         (glDetKey,))
            self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='glPostingsDetails' AND ObjectIdToAddLinkTo=?",
                                         (glDetKey,))
            self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='glPostingsDetails' AND ObjectIdBeingLinked=?",
                                         (glDetKey,))

        self.parent.dbConnection.commit()
        self.updateGLTree.emit()

    def postToGL(self, companyNum, date, description, listOfDetails):
        glPostingIdNum = self.nextIdNum("GLPostings")
        glPostingDetailIdNum = self.nextIdNum("GLPostingsDetails")
        
        glPosting = GLPosting(date, description, glPostingIdNum)
        glPosting.addCompany(self.dataConnection.companies[companyNum])
        self.dataConnection.companies[companyNum].addPosting(glPosting)
        self.dataConnection.glPostings[glPosting.idNum] = glPosting
        self.parent.dbCursor.execute("INSERT INTO GLPostings (Date, Description) VALUES (?, ?)",
                                            (glPosting.date, glPosting.description))
        self.parent.dbCursor.execute("INSERT INTO Xref VALUES ('glPostings', ?, 'addCompany', 'companies', ?)",
                                     (glPosting.idNum, companyNum))
        self.parent.dbCursor.execute("INSERT INTO Xref VALUES ('companies', ?, 'addPosting', 'glPostings', ?)",
                                     (companyNum, glPosting.idNum))

        for detail in listOfDetails:
            glPostingDetail = GLPostingDetail(detail[0], detail[1], glPostingDetailIdNum)
            
            glPosting.addDetail(glPostingDetail)
            glPostingDetail.addDetailOf(glPosting)
            glPostingDetail.addGLAccount(self.dataConnection.glAccounts[detail[2]])
            glPostingDetail.glAccount.addPosting(glPostingDetail)

            if detail[3]:
                detail[3].addGLPosting(glPostingDetail)
                self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                             (detail[4], detail[3].idNum, "addGLPosting", "glPostingsDetails", glPostingDetail.idNum))
            
            self.dataConnection.glPostingsDetails[glPostingDetail.idNum] = glPostingDetail

            self.parent.dbCursor.execute("INSERT INTO GLPostingsDetails (Amount, DebitCredit) VALUES (?, ?)",
                                         (glPostingDetail.amount, glPostingDetail.debitCredit))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostings", glPosting.idNum, "addDetail", "glPostingsDetails", glPostingDetail.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostingsDetails", glPostingDetail.idNum, "addDetailOf", "glPostings", glPosting.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostingsDetails", glPostingDetail.idNum, "addGLAccount", "glAccounts", glPostingDetail.glAccount.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glAccounts", glPostingDetail.glAccount.idNum, "addPosting", "glPostingsDetails", glPostingDetail.idNum))
            
            self.parent.dbConnection.commit()

            glPostingDetailIdNum += 1
        self.updateGLTree.emit()
            
class ProposalTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, proposalItem, parent):
        super().__init__(parent)
        self.proposal = proposalItem

        self.setText(0, str(self.proposal.idNum))
        self.setText(1, self.proposal.vendor.name)
        self.setText(2, self.proposal.date)
        self.setText(3, self.proposal.proposalFor[1].description)
        self.setText(4, "{:,.2f}".format(self.proposal.totalCost()))

    def refreshData(self):
        self.setText(1, self.proposal.vendor.name)
        self.setText(2, self.proposal.date)
        self.setText(3, self.proposal.proposalFor[1].description)
        self.setText(4, "{:,.2f}".format(self.proposal.totalCost()))
        
class ProposalTreeWidget(NewTreeWidget):
    openProposal = pyqtSignal(int)
    rejectedProposal = pyqtSignal(int)
    acceptedProposal = pyqtSignal(int)
    
    def __init__(self, proposalsDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, proposalsDict)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)
        
    def buildItems(self, parent, proposalsDict):
        for proposalKey in proposalsDict:
            item = ProposalTreeWidgetItem(proposalsDict[proposalKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            # Need to use a try...except... method because if an item gets
            # moved from one location to another during this refresh, idx
            # will get an out of bounds error if any object other than the last
            # item in the list had its status changed (and hence was moved)
            try:
                self.topLevelItem(idx).refreshData()
    
                if self.topLevelItem(idx).proposal.status == constants.OPN_PROPOSAL_STATUS:
                    self.openProposal.emit(idx)
                elif self.topLevelItem(idx).proposal.status == constants.REJ_PROPOSAL_STATUS:
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

        self.openProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus(constants.OPN_PROPOSAL_STATUS), constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
        self.openProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openProposalsTreeWidget.rejectedProposal.connect(self.moveOpenToRejected)
        self.openProposalsTreeWidget.acceptedProposal.connect(self.moveOpenToAccepted)

        self.rejectedProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus(constants.REJ_PROPOSAL_STATUS), constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
        self.rejectedProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        self.rejectedProposalsTreeWidget.openProposal.connect(self.moveRejectedToOpen)
        self.rejectedProposalsTreeWidget.acceptedProposal.connect(self.moveRejectedToAccepted)
        
        self.acceptedProposalsTreeWidget = ProposalTreeWidget(self.proposalsDict.proposalsByStatus(constants.ACC_PROPOSAL_STATUS), constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
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

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewProposalDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewProposalDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedProposalFromList)
        buttonWidget.addSpacer()

        acceptProposalButton = QPushButton("Accept...")
        acceptProposalButton.clicked.connect(self.acceptProposal)
        rejectProposalButton = QPushButton("Reject...")
        rejectProposalButton.clicked.connect(self.rejectProposal)
        buttonWidget.addButton(acceptProposalButton)
        buttonWidget.addButton(rejectProposalButton)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def acceptProposal(self):
        idxToShow = self.openProposalsTreeWidget.indexFromItem(self.openProposalsTreeWidget.currentItem())
        item = self.openProposalsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = ChangeProposalStatusDialog(constants.ACC_PROPOSAL_STATUS, self)
            if dialog.exec_():
                item.proposal.accept()
                self.parent.parent.dbCursor.execute("UPDATE Proposals SET Status = ?, StatusReason = ? WHERE idNum = ?", (constants.ACC_PROPOSAL_STATUS, dialog.statusTxt.text(), str(item.proposal.idNum)))
                self.parent.parent.dbConnection.commit()
                
        self.openProposalsTreeWidget.refreshData()
        self.updateProposalsCount()
        self.updateVendorWidgetTree.emit()

    def rejectProposal(self):
        idxToShow = self.openProposalsTreeWidget.indexFromItem(self.openProposalsTreeWidget.currentItem())
        item = self.openProposalsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = ChangeProposalStatusDialog(constants.REJ_PROPOSAL_STATUS, self)
            if dialog.exec_():
                item.proposal.reject()
                self.parent.parent.dbCursor.execute("UPDATE Proposals SET Status = ?, StatusReason = ? WHERE idNum = ?", (constants.REJ_PROPOSAL_STATUS, dialog.statusTxt.text(), str(item.proposal.idNum)))
                self.parent.parent.dbConnection.commit()
                
        self.openProposalsTreeWidget.refreshData()
        self.updateProposalsCount()
        self.updateVendorWidgetTree.emit()

    def moveOpenToRejected(self, idx):
        item = self.openProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.rejectedProposalsTreeWidget)
        self.rejectedProposalsTreeWidget.addTopLevelItem(newItem)

    def moveOpenToAccepted(self, idx):
        item = self.openProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.acceptedProposalsTreeWidget)
        self.acceptedProposalsTreeWidget.addTopLevelItem(newItem)

    def moveRejectedToOpen(self, idx):
        item = self.rejectedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.openProposalsTreeWidget)
        self.openProposalsTreeWidget.addTopLevelItem(newItem)

    def moveRejectedToAccepted(self, idx):
        item = self.rejectedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.acceptedProposalsTreeWidget)
        self.acceptedProposalsTreeWidget.addTopLevelItem(newItem)

    def moveAcceptedToOpen(self, idx):
        item = self.acceptedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.openProposalsTreeWidget)
        self.openProposalsTreeWidget.addTopLevelItem(newItem)

    def moveAcceptedToRejected(self, idx):
        item = self.acceptedProposalsTreeWidget.takeTopLevelItem(idx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.rejectedProposalsTreeWidget)
        self.rejectedProposalsTreeWidget.addTopLevelItem(newItem)

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
                                   "",
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
            
            # Add proposal<->project/asset links
            type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
            if dialog.assetProjSelector.assetSelected() == True:
                type_ = "assets"
                type_action = "addAsset"
                newProposal.addAsset(self.parent.dataConnection.assets[type_Id])
                self.parent.dataConnection.assets[type_Id].addProposal(newProposal)
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
            item = ProposalTreeWidgetItem(newProposal, self.openProposalsTreeWidget)
            self.openProposalsTreeWidget.addTopLevelItem(item)
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
        
        self.setText(0, str(self.project.idNum))
        self.setText(1, self.project.description)
        self.setText(2, self.project.dateStart)
        self.setText(3, self.project.dateEnd)
        self.setText(4, "<Duration>")
        self.setText(5, "{:,.2f}".format(self.project.calculateCIP()))

    def refreshData(self):
        self.setText(1, self.project.description)
        self.setText(2, self.project.dateStart)
        self.setText(3, self.project.dateEnd)
        self.setText(4, "<Duration>")
        self.setText(5, "{:,.2f}".format(self.project.calculateCIP()))
        
class ProjectTreeWidget(NewTreeWidget):
    projectAbandoned = pyqtSignal(int)
    projectCompleted = pyqtSignal(int)
    
    def __init__(self, projectsDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, projectsDict)
        self.setColumnCount(6)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, projectsDict):
        for projectKey in projectsDict:
            item = ProjectTreeWidgetItem(projectsDict[projectKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            try:
                self.topLevelItem(idx).refreshData()

                if self.topLevelItem(idx).project.status() == constants.ABD_PROJECT_STATUS:
                    self.projectAbandoned.emit(idx)
                elif self.topLevelItem(idx).project.status() == constants.CMP_PROJECT_STATUS:
                    self.projectCompleted.emit(idx)
            except:
                pass

class ProjectWidget(QWidget):
    addAssetToAssetView = pyqtSignal(object)
    
    def __init__(self, projectsDict, parent):
        super().__init__()
        self.projectsDict = projectsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.openProjectsLabel = QLabel("%s: %d" % (constants.OPN_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.OPN_PROJECT_STATUS))))
        mainLayout.addWidget(self.openProjectsLabel)

        # Piece together the projects layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.openProjectsTreeWidget = ProjectTreeWidget(self.projectsDict.projectsByStatus(constants.OPN_PROJECT_STATUS), constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.openProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openProjectsTreeWidget.projectAbandoned.connect(self.moveOpenToAbandoned)

        self.abandonedProjectsTreeWidget = ProjectTreeWidget(self.projectsDict.projectsByStatus(constants.ABD_PROJECT_STATUS), constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.abandonedProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))

        self.completedProjectsTreeWidget = ProjectTreeWidget(self.projectsDict.projectsByStatus(constants.CMP_PROJECT_STATUS), constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.completedProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(3))

        self.abandonedProjectsLabel = QLabel("%s: %d" % (constants.ABD_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.ABD_PROJECT_STATUS))))
        self.completedProjectsLabel = QLabel("%s: %d" % (constants.CMP_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.CMP_PROJECT_STATUS))))

        treeWidgetsLayout.addWidget(self.openProjectsTreeWidget)
        treeWidgetsLayout.addWidget(self.abandonedProjectsLabel)
        treeWidgetsLayout.addWidget(self.abandonedProjectsTreeWidget)
        treeWidgetsLayout.addWidget(self.completedProjectsLabel)
        treeWidgetsLayout.addWidget(self.completedProjectsTreeWidget)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewProjectDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewProjectDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedProjectFromList)
        buttonWidget.addSpacer()

        completeProject = QPushButton("Complete...")
        completeProject.clicked.connect(self.completeProject)
        abandonProject = QPushButton("Abandon...")
        abandonProject.clicked.connect(self.abandonProject)
        buttonWidget.addButton(completeProject)
        buttonWidget.addButton(abandonProject)

        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def moveOpenToAbandoned(self, idx):
        item = self.openProjectsTreeWidget.takeTopLevelItem(idx)
        newItem = ProjectTreeWidgetItem(item.project, self.abandonedProjectsTreeWidget)
        self.abandonedProjectsTreeWidget.addTopLevelItem(newItem)
        
    def completeProject(self):
        idxToComplete = self.openProjectsTreeWidget.indexFromItem(self.openProjectsTreeWidget.currentItem())
        item = self.openProjectsTreeWidget.itemFromIndex(idxToComplete)

        if item:
            dialog = CloseProjectDialog(constants.CMP_PROJECT_STATUS, self)

            if dialog.exec_():
                assetId = self.nextIdNum("Assets")
                costId = self.nextIdNum("AssetCosts")
                histId = self.nextIdNum("AssetHistory")
                
                if dialog.inSvcChk.isChecked() == True:
                    inSvcDate = dialog.dateTxt.text()
                else:
                    inSvcDate = ""

                # Create new asset and cost
                newAsset = Asset(dialog.assetNameTxt.text(),
                                 dialog.dateTxt.text(),
                                 inSvcDate,
                                 "",
                                 None,
                                 float(dialog.usefulLifeTxt.text()),
                                 float(dialog.salvageValueText.text()),
                                 dialog.depMethodBox.currentText(),
                                 int(False),
                                 assetId)
                parentAssetTxt = dialog.childOfAssetBox.currentText()
                cost = AssetCost(item.project.calculateCIP(), costId)
                history = AssetHistory(dialog.dateTxt.text(),
                                       constants.ASSET_HIST_PROJ_COMP % item.project.idNum,
                                       cost.cost,
                                       constants.POSITIVE,
                                       histId)
                
                # Add assetType, company, fromProject, and cost data to asset
                assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
                newAsset.addAssetType(self.parent.dataConnection.assetTypes[assetTypeId])
                newAsset.addCompany(item.project.company)
                newAsset.addProject(item.project)
                newAsset.addCost(cost)
                newAsset.addHistory(history)
                
                if parentAssetTxt != "":
                    parentAssetId = self.stripAllButNumbers(parentAssetTxt)
                    parentAsset = self.parent.dataConnection.assets[parentAssetId]
                    newAsset.addSubAssetOf(parentAsset)
                    parentAsset.addSubAsset(newAsset)
                    
                # Add reverse data
                newAsset.company.addAsset(newAsset)
                self.parent.dataConnection.assets[assetId] = newAsset
                self.parent.dataConnection.assetCosts[costId] = cost
                self.parent.dataConnection.assetsHistory[histId] = history
                cost.addAsset(newAsset)
                history.addAsset(newAsset)
                history.addObject(cost)
                
                # Add completion information to project
                item.project.addAsset(newAsset)
                item.project.dateEnd = dialog.dateTxt.text()
                
                # Add to database
                self.insertIntoDatabase("Assets", "(idNum, Description, AcquireDate, InSvcDate, UsefulLife, SalvageAmount, DepreciationMethod, PartiallyDisposed)", "(" + str(newAsset.idNum) + ", '" + newAsset.description + "', '" + newAsset.acquireDate + "', '" + newAsset.inSvcDate + "', " + str(newAsset.usefulLife) + ", " + str(newAsset.salvageAmount) + ", '" + newAsset.depMethod + "', " + str(int(newAsset.partiallyDisposed)) + ")")
                self.insertIntoDatabase("Xref", "", "('assets', " + str(newAsset.idNum) + ", 'addAssetType', 'assetTypes', " + str(newAsset.assetType.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('assets', " + str(newAsset.idNum) + ", 'addCompany', 'companies', " + str(newAsset.company.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('assets', " + str(newAsset.idNum) + ", 'addProject', 'projects', " + str(newAsset.fromProject.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('companies', " + str(newAsset.company.idNum) + ", 'addAsset', 'assets', " + str(newAsset.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('projects', " + str(newAsset.fromProject.idNum) + ", 'addAsset', 'assets', " + str(newAsset.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('assets', " + str(newAsset.idNum) + ", 'addCost', 'assetCosts', " + str(cost.idNum) + ")")
                self.parent.parent.dbCursor.execute("INSERT INTO AssetHistory (Date, Description, Dollars, PosNeg) VALUES (?, ?, ?, ?)",
                                                    (history.date, history.text, history.amount, history.posNeg))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assetsHistory', histId, 'addAsset', 'assets', newAsset.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assetsHistory', histId, 'addObject', 'assetCosts', cost.idNum))
                self.parent.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                                    ('assets', newAsset.idNum, 'addHistory', 'assetsHistory', histId))
                self.parent.parent.dbCursor.execute("INSERT INTO AssetCosts (Cost) VALUES (?)",
                                                    (cost.cost,))

                self.parent.parent.dbCursor.execute("UPDATE Projects SET DateEnd=? WHERE idNum=?", (item.project.dateEnd, item.project.idNum))
                
                if parentAssetTxt != "":
                    self.insertIntoDatabase("Xref", "", "('assets', " + str(newAsset.idNum) + ", 'addSubAssetOf', 'assets', " + str(parentAsset.idNum) + ")")
                    self.insertIntoDatabase("Xref", "", "('assets', " + str(parentAsset.idNum) + ", 'addSubAsset', 'assets', " + str(newAsset.idNum) + ")")
                    
                self.parent.parent.dbConnection.commit()
                
                self.openProjectsTreeWidget.takeTopLevelItem(idxToComplete.row())                
                newItem = ProjectTreeWidgetItem(item.project, self.completedProjectsTreeWidget)
                self.completedProjectsTreeWidget.addTopLevelItem(newItem)
                
                self.addAssetToAssetView.emit(newAsset)
                self.refreshOpenProjectTree()
                self.updateProjectsCount()
                
    def abandonProject(self):
        idxToAbandon = self.openProjectsTreeWidget.indexFromItem(self.openProjectsTreeWidget.currentItem())
        item = self.openProjectsTreeWidget.itemFromIndex(idxToAbandon)

        if item:
            dialog = CloseProjectDialog(constants.ABD_PROJECT_STATUS, self)

            if dialog.exec_():
                item.project.dateEnd = dialog.dateTxt.text()
                item.project.notes = dialog.reasonTxt.text()
                
                self.parent.parent.dbCursor.execute("UPDATE Projects SET DateEnd=?, Notes=? WHERE idNum=?", (dialog.dateTxt.text(), dialog.reasonTxt.text(), item.project.idNum))
                self.parent.parent.dbConnection.commit()

        self.refreshOpenProjectTree()
        self.updateProjectsCount()

    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.abandonedProjectsTreeWidget.setCurrentItem(self.abandonedProjectsTreeWidget.invisibleRootItem())
            self.completedProjectsTreeWidget.setCurrentItem(self.completedProjectsTreeWidget.invisibleRootItem())
        elif but == 2:
            self.openProjectsTreeWidget.setCurrentItem(self.openProjectsTreeWidget.invisibleRootItem())
            self.completedProjectsTreeWidget.setCurrentItem(self.completedProjectsTreeWidget.invisibleRootItem())
        else:
            self.openProjectsTreeWidget.setCurrentItem(self.openProjectsTreeWidget.invisibleRootItem())
            self.abandonedProjectsTreeWidget.setCurrentItem(self.abandonedProjectsTreeWidget.invisibleRootItem())

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
        dialog = ProjectDialog("New", self.parent.dataConnection.glAccounts, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Projects")
            glAccountNum = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
            
            # Create project and add to database
            newProject = Project(dialog.descriptionText.text(),
                                 dialog.startDateText.text(),
                                 "",
                                 nextId)
            newProject.addGLAccount(self.parent.dataConnection.glAccounts[glAccountNum])
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            newProject.addCompany(self.parent.dataConnection.companies[companyId])
            self.parent.dataConnection.companies[companyId].addProject(newProject)
            self.projectsDict[newProject.idNum] = newProject
            
            self.insertIntoDatabase("Projects", "(Description, DateStart)", "('" + newProject.description + "', '" + newProject.dateStart + "')")
            self.insertIntoDatabase("Xref", "", "('projects', " + str(nextId) + ", 'addCompany', 'companies', " + str(companyId) + ")")
            self.insertIntoDatabase("Xref", "", "('companies', " + str(companyId) + ", 'addProject', 'projects', " + str(nextId) + ")")
            self.insertIntoDatabase("Xref", "", "('projects', " + str(nextId) + ", 'addGLAccount', 'glAccounts', " + str(glAccountNum) + ")")
            
            self.parent.parent.dbConnection.commit()
            
            # Make project into a ProjectTreeWidgetItem and add it to ProjectTree
            item = ProjectTreeWidgetItem(newProject, self.openProjectsTreeWidget)
            self.openProjectsTreeWidget.addTopLevelItem(item)
            self.updateProjectsCount()

    def showViewProjectDialog(self):
        # Determine which tree the project is in--if any.  If none, don't
        # display dialog
        idxToShow = self.openProjectsTreeWidget.indexFromItem(self.openProjectsTreeWidget.currentItem())
        item = self.openProjectsTreeWidget.itemFromIndex(idxToShow)

        if item == None:
            idxToShow = self.abandonedProjectsTreeWidget.indexFromItem(self.abandonedProjectsTreeWidget.currentItem())
            item = self.abandonedProjectsTreeWidget.itemFromIndex(idxToShow)

            if item == None:
                idxToShow = self.completedProjectsTreeWidget.indexFromItem(self.completedProjectsTreeWidget.currentItem())
                item = self.completedProjectsTreeWidget.itemFromIndex(idxToShow)
        
        if item:
            dialog = ProjectDialog("View", self.parent.dataConnection.glAccounts, self, item.project)
            
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

                    if dialog.glAccountChanged == True:
                        oldGLAccountNum = item.project.glAccount.idNum
                        newGLAccountNum = self.stripAllButNumbers(dialog.glAccountsBox.currentText())

                        item.project.addGLAccount(self.parent.dataConnection.glAccounts[newGLAccountNum])
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='projects' AND ObjectIdToAddLinkTo=? AND Method='addGLAccount' AND ObjectIdBeingLinked=?",
                                                            (newGLAccountNum, item.project.idNum, oldGLAccountNum))

                    self.parent.parent.dbConnection.commit()
                    
                    item.project.description = dialog.descriptionText_edit.text()
                    item.project.dateStart = dialog.startDateText_edit.text()
                    item.project.dateEnd = dialog.endDateText.text()
                    
                    self.openProjectsTreeWidget.refreshData()
                    
    def deleteSelectedProjectFromList(self):
        # Check to see if the item to delete is in the open project tree widget
        idxToDelete = self.openProjectsTreeWidget.indexOfTopLevelItem(self.openProjectsTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.openProjectsTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            idxToDelete = self.completedProjectsTreeWidget.indexOfTopLevelItem(self.completedProjectsTreeWidget.currentItem())
            if idxToDelete < 0:
                idxToDelete = self.abandonedProjectsTreeWidget.indexOfTopLevelItem(self.abandonedProjectsTreeWidget.currentItem())
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
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectToAddLinkTo='projects' AND ObjectIdToAddLinkTo=?)",
                                                (item.project.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE (ObjectIdBeingLinked=? AND ObjectBeingLinked='projects')",
                                                (item.project.idNum,))

            self.parent.dataConnection.companies[item.project.company.idNum].removeProject(item.project)
            self.projectsDict.pop(item.project.idNum)

            self.parent.parent.dbConnection.commit()
                
            self.updateProjectsCount()
            
    def updateProjectsCount(self):
        self.openProjectsLabel.setText("%s: %d" % (constants.OPN_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.OPN_PROJECT_STATUS))))
        self.abandonedProjectsLabel.setText("%s: %d" % (constants.ABD_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.ABD_PROJECT_STATUS))))
        self.completedProjectsLabel.setText("%s: %d" % (constants.CMP_PROJECT_STATUS, len(self.projectsDict.projectsByStatus(constants.CMP_PROJECT_STATUS))))

    def refreshOpenProjectTree(self):
        self.openProjectsTreeWidget.refreshData()
        
class ProjectView(QWidget):
    addAssetToAssetView = pyqtSignal(object)
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.projectWidget = ProjectWidget(self.dataConnection.projects, self)
        self.projectWidget.addAssetToAssetView.connect(self.emitAddAssetToAssetView)
        layout = QVBoxLayout()
        layout.addWidget(self.projectWidget)

        self.setLayout(layout)

    def emitAddAssetToAssetView(self, asset):
        self.addAssetToAssetView.emit(asset)

class CompanyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, companyItem, parent):
        super().__init__(parent)
        self.company = companyItem
        
        self.setText(0, str(self.company.idNum))
        self.setText(1, self.company.name)
        self.setText(2, self.company.shortName)
        self.setText(3, "{:,.2f}".format(self.company.assetsAmount()))
        self.setText(4, "{:,.2f}".format(self.company.CIPAmount()))
        
    def refreshData(self):
        self.setText(1, self.company.name)
        self.setText(2, self.company.shortName)
        self.setText(3, "{:,.2f}".format(self.company.assetsAmount()))
        self.setText(4, "{:,.2f}".format(self.company.CIPAmount()))
        
class CompanyTreeWidget(NewTreeWidget):
    def __init__(self, companiesDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, companiesDict)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, companiesDict):
        for companyKey in companiesDict:
            item = CompanyTreeWidgetItem(companiesDict[companyKey], parent)
            self.addTopLevelItem(item)

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

        self.companiesTreeWidget = CompanyTreeWidget(self.companiesDict, constants.COMPANY_HDR_LIST, constants.COMPANY_HDR_WDTH)

        treeWidgetsLayout.addWidget(self.companiesTreeWidget)
        treeWidgetsLayout.addStretch(1)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewCompanyDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewCompanyDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedCompanyFromList)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
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

    def refreshCompanyTree(self):
        self.companiesTreeWidget.refreshData()
        
    def showNewCompanyDialog(self):
        dialog = CompanyDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Companies")
            
            # Create company and add to database
            newCompany = Company(dialog.nameText.text(),
                                 dialog.shortNameText.text(),
                                 True,
                                 nextId)
            self.companiesDict[newCompany.idNum] = newCompany

            self.insertIntoDatabase("Companies", "(Name, ShortName, Active)", "('" + newCompany.name + "', '" + newCompany.shortName + "', 'Y')")
            
            self.parent.parent.dbConnection.commit()
            
            # Make company into a CompanyTreeWidgetItem and add it to CompanyTree
            item = CompanyTreeWidgetItem(newCompany, self.companiesTreeWidget)
            self.companiesTreeWidget.addTopLevelItem(item)
            self.updateCompaniesCount()

            self.addNewCompany.emit(newCompany.shortName)
            
    def showViewCompanyDialog(self):
        # Determine which tree the company is in--if any.  If none, don't
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

        self.setText(0, str(self.asset.idNum))
        self.setText(1, self.asset.description)
        self.setText(2, "{:,.2f}".format(self.asset.cost()))
        self.setText(3, "{:,.2f}".format(self.asset.depreciatedAmount()))
        self.setText(4, self.asset.acquireDate)
        self.setText(5, self.asset.inSvcDate)
        
    def refreshData(self):
        self.setText(1, self.asset.description)
        self.setText(2, "{:,.2f}".format(self.asset.cost()))
        self.setText(3, "{:,.2f}".format(self.asset.depreciatedAmount()))
        self.setText(4, self.asset.acquireDate)
        self.setText(5, self.asset.inSvcDate)

    def depth(self, asset):
        if asset.subAssetOf == None:
            return 0
        else:
            return 1 + self.depth(asset.subAssetOf)

    def assignChildren(self, listOfChildren, parent):
        for item in listOfChildren:
            newItem = AssetTreeWidgetItem(item.asset, parent)

            if item.childCount() > 0:
                self.assignChildren(item.takeChildren(), newItem)
        
class AssetTreeWidget(NewTreeWidget):
    disposeAsset = pyqtSignal(int)
    
    def __init__(self, assetsDict, headerList, widthList, inSvcFg=True):
        super().__init__(headerList, widthList)
        self.inSvcFg = inSvcFg
        self.itemsInTree = []
        self.buildItems(self, assetsDict)
        self.setColumnCount(6)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, assetsDict):
        # This function will check to make sure the asset's service status
        # matches that required by the TreeWidget and also that its idNum has not
        # already been added to the tree (this condition is caused when an asset
        # and its subasset have both been disposed; the flat dictionary passed
        # to the tree will end up adding the subasset when it adds the parent
        # item's subassets and then again when it reaches that item in the flat
        # dictionary).  If not, it will create the item, add it to the tree,
        # and then go through its subassets and add them if their statuses meet
        # the requirements.  Otherwise, it will cycle to the next
        for assetKey in assetsDict:
            item = parent
            
            if assetsDict[assetKey].inSvc() == self.inSvcFg:
                if assetKey not in self.itemsInTree:
                    item = AssetTreeWidgetItem(assetsDict[assetKey], parent)
                    self.addTopLevelItem(item)

                    if assetsDict[assetKey].subAssets:
                        self.buildChildren(item, assetsDict[assetKey].subAssets)

    def buildChildren(self, parent, assetsDict):
        for assetKey in assetsDict:
            item = parent

            if assetsDict[assetKey].inSvc() == self.inSvcFg:
                if assetKey not in self.itemsInTree:
                    item = AssetTreeWidgetItem(assetsDict[assetKey], parent)
                    parent.addChild(item)
                    self.itemsInTree.append(assetKey)

                    if assetsDict[assetKey].subAssets:
                        self.buildChildren(item, assetsDict[assetKey].subAssets)

    def refreshChildren(self, parentItem):
        for idx in range(parentItem.childCount()):
            parentItem.child(idx).refreshData()

            if parentItem.child(idx).asset.inSvc() != True:
                self.disposeAsset.emit(parentItem.child(idx).asset.idNum)
                
            if parentItem.child(idx).childCount() > 0:
                self.refreshChildren(parentItem.child(idx))

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            try:
                self.topLevelItem(idx).refreshData()

                if self.topLevelItem(idx).asset.inSvc() != True:
                    self.disposeAsset.emit(self.topLevelItem(idx).asset.idNum)
                    
                if self.topLevelItem(idx).childCount() > 0:
                    self.refreshChildren(self.topLevelItem(idx))
            except:
                pass
            
class AssetWidget(QWidget):
    def __init__(self, assetsDict, parent):
        super().__init__()
        self.assetsDict = assetsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.currentAssetsLabel = QLabel("Current Assets: %d / %.02f" % (len(self.assetsDict.currentAssets()), self.assetsDict.currentCost()))
        mainLayout.addWidget(self.currentAssetsLabel)

        # Piece together the companies layout
        subLayout = QHBoxLayout()
        assetWidgetsLayout = QVBoxLayout()

        self.currentAssetsTreeWidget = AssetTreeWidget(self.assetsDict.currentAssets(True), constants.ASSET_HDR_LIST, constants.ASSET_HDR_WDTH)
        self.currentAssetsTreeWidget.disposeAsset.connect(self.moveCurrentAssetToDisposed)
        self.currentAssetsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))

        self.disposedAssetsTreeWidget = AssetTreeWidget(self.assetsDict.disposedAssets(), constants.ASSET_HDR_LIST, constants.ASSET_HDR_WDTH, False)
        self.disposedAssetsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))

        self.disposedAssetsLabel = QLabel("Disposed Assets: %d / %.02f" % (len(self.assetsDict.disposedAssets()), self.assetsDict.disposedCost()))
        
        assetWidgetsLayout.addWidget(self.currentAssetsTreeWidget)
        assetWidgetsLayout.addWidget(self.disposedAssetsLabel)
        assetWidgetsLayout.addWidget(self.disposedAssetsTreeWidget)
        assetWidgetsLayout.addStretch(1)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewAssetDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewAssetDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedAssetFromList)
        buttonWidget.addSpacer()

        assetTypeBtn = QPushButton("Asset Types...")
        assetTypeBtn.clicked.connect(self.showAssetTypeDialog)
        impairBtn = QPushButton("Impair...")
        disposeBtn = QPushButton("Dispose...")
        disposeBtn.clicked.connect(self.disposeAsset)
        buttonWidget.addButton(assetTypeBtn)
        buttonWidget.addButton(impairBtn)
        buttonWidget.addButton(disposeBtn)

        subLayout.addLayout(assetWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def printdata(self):
        idx = self.currentAssetsTreeWidget.indexFromItem(self.currentAssetsTreeWidget.currentItem())

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
        self.currentAssetsLabel.setText("Current Assets: %d / %.02f" % (len(self.assetsDict.currentAssets()), self.assetsDict.currentCost()))
        self.disposedAssetsLabel.setText("Disposed Assets: %d / %.02f" % (len(self.assetsDict.disposedAssets()), self.assetsDict.disposedCost()))

    def showAssetTypeDialog(self):
        dialog = AssetTypeDialog(self.parent.dataConnection.assetTypes, self.parent.dataConnection.glAccounts, self)
        dialog.exec_()

    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.disposedAssetsTreeWidget.setCurrentItem(self.disposedAssetsTreeWidget.invisibleRootItem())
        else:
            self.currentAssetsTreeWidget.setCurrentItem(self.currentAssetsTreeWidget.invisibleRootItem())

    def moveCurrentAssetToDisposed(self, assetId):
        item = self.getItem(assetId)
        newItem = AssetTreeWidgetItem(item.asset, self.disposedAssetsTreeWidget)
        # If disposed asset has subassets, we must dispose of them and move them over to newItem
        if item.childCount() > 0:
            self.moveChildren(item, newItem)

        # If disposed asset already has a subasset that has been disposed, we want to merge the newly
        # disposed asset into the tree rather than create a new entry.  Otherwise, make it a top level
        # item in the disposed asset tree
        if item.asset.partiallyDisposed == True:
            pass
        else:
            self.disposedAssetsTreeWidget.addTopLevelItem(newItem)

        # Remove the top-most disposed item from the list.  If it is a subasset, we must remove it as
        # a child of its parent.  If it is not, we can remove it through the takeTopLevelItem() method.
        if item.asset.subAssetOf:
            parentItem = self.getParentItem(item.asset.idNum)
            for idx in range(parentItem.childCount()):
                if parentItem.child(idx).asset.idNum == item.asset.idNum:
                    childToTake = idx
            parentItem.takeChild(childToTake)
        else:
            idx = self.currentAssetsTreeWidget.indexOfTopLevelItem(item)
            self.currentAssetsTreeWidget.takeTopLevelItem(idx)
        
        # Make all asset disposal indicator changes
        item.asset.markDisposals(self.parent.parent.dbCursor, self.parent.parent.dbConnection)

    def moveChildren(self, oldParentItem, newParentItem):
        while oldParentItem.childCount() > 0:
            child = oldParentItem.takeChild(0)
            newChild = AssetTreeWidgetItem(child.asset, newParentItem)
            newParentItem.addChild(newChild)

            if child.childCount() > 0:
                self.moveChildren(child, newChild)
                
    def getItem(self, assetNum):
        iterator = QTreeWidgetItemIterator(self.currentAssetsTreeWidget)

        while iterator.value():
            if iterator.value().asset.idNum == assetNum:
                return iterator.value()

            iterator += 1
            
    def getParentItem(self, assetNum):
        iterator = QTreeWidgetItemIterator(self.currentAssetsTreeWidget)
        
        while iterator.value():
            if iterator.value().asset.subAssets:
                if assetNum in iterator.value().asset.subAssets.keys():
                    return iterator.value()
            
            iterator += 1

    def disposeChildAssets(self, parentItem, amt, date):
        for idx in range(parentItem.childCount()):
            self.parent.parent.dbCursor.execute("UPDATE Assets SET DisposeDate=?, DisposeAmount=? WHERE idNum=?", (date, amt, parentItem.child(idx).asset.idNum))
            parentItem.child(idx).asset.disposeDate = date
            parentItem.child(idx).asset.disposeAmount = amt

            if parentItem.child(idx).childCount() > 0:
                self.disposeChildAssets(parentItem.child(idx), amt, date)

    def disposeAsset(self):
        # Need to dispose not only given item, but also any child items it may have.
        idxToDispose = self.currentAssetsTreeWidget.indexFromItem(self.currentAssetsTreeWidget.currentItem())
        item = self.currentAssetsTreeWidget.itemFromIndex(idxToDispose)

        if item:
            dialog = DisposeAssetDialog(self)
            if dialog.exec_():
                self.parent.parent.dbCursor.execute("UPDATE Assets SET DisposeDate=?, DisposeAmount=? WHERE idNum=?", (dialog.dispDateTxt.text(), float(dialog.dispAmtTxt.text()), item.asset.idNum))
                item.asset.disposeDate = dialog.dispDateTxt.text()
                item.asset.disposeAmount = float(dialog.dispAmtTxt.text())

                if item.childCount() > 0:
                    self.disposeChildAssets(item, float(dialog.dispAmtTxt.text()), dialog.dispDateTxt.text())

                self.parent.parent.dbConnection.commit()
                self.refreshAssetTree()
                self.updateAssetsCount()

    def showNewAssetDialog(self):
        dialog = AssetDialog("New", self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Assets")
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())

            # Get and/or set some data elements
            assetType = self.parent.dataConnection.assetTypes[assetTypeId]
            if assetType.depreciable == True:
                usefulLife = float(dialog.usefulLifeText.text())
                depMethod = dialog.depMethodBox.currentText()
                salvageAmount = float(dialog.salvageValueText.text())
            else:
                usefulLife = None
                depMethod = None
                salvageAmount = None
                
            if dialog.childOfAssetBox.currentText() == "":
                subAssetOfId = None
            else:
                subAssetOfId = self.stripAllButNumbers(dialog.childOfAssetBox.currentText())
            
            # Create asset and add to database
            newAsset = Asset(dialog.descriptionText.text(),
                             dialog.dateAcquiredText.text(),
                             dialog.dateInSvcText.text(),
                             None,
                             None,
                             usefulLife,
                             salvageAmount,
                             depMethod,
                             False,
                             nextId)
            
            self.assetsDict[newAsset.idNum] = newAsset
            newAsset.addCompany(self.parent.dataConnection.companies[companyId])
            newAsset.addAssetType(assetType)
            self.parent.dataConnection.companies[companyId].addAsset(newAsset)
            
            self.parent.parent.dbCursor.execute("INSERT INTO Assets (Description, AcquireDate, InSvcDate, UsefulLife, SalvageAmount, DepreciationMethod, PartiallyDisposed) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                                (newAsset.description, newAsset.acquireDate, newAsset.inSvcDate, newAsset.usefulLife, newAsset.salvageAmount, newAsset.depMethod, int(newAsset.partiallyDisposed)))
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('companies', " + str(companyId) + ", 'addAsset', 'assets', " + str(nextId) + ")")
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(nextId) + ", 'addCompany', 'companies', " + str(companyId) + ")")
            self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(nextId) + ", 'addAssetType', 'assetTypes', " + str(assetTypeId) + ")")
            
            # Add subasset info, if it exists
            if subAssetOfId:
                newAsset.addSubAssetOf(self.parent.dataConnection.assets[subAssetOfId])
                self.parent.dataConnection.assets[subAssetOfId].addSubAsset(newAsset)
                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(nextId) + ", 'addSubAssetOf', 'assets', " + str(subAssetOfId) + ")")
                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(subAssetOfId) + ", 'addSubAsset', 'assets', " + str(nextId) + ")")

            self.parent.parent.dbConnection.commit()
            
            # Make asset into an AssetTreeWidgetItem and add it to AssetTree
            if subAssetOfId == None:
                item = AssetTreeWidgetItem(newAsset, self.currentAssetsTreeWidget)
            else:
                parentItem = self.getParentItem(subAssetOfId)
                item = AssetTreeWidgetItem(newAsset, parentItem)
            
            self.currentAssetsTreeWidget.addTopLevelItem(item)
            self.updateAssetsCount()
            
    def showViewAssetDialog(self):
        # Determine which tree the asset is in--if any.  If none, don't
        # display dialog
        idxToShow = self.currentAssetsTreeWidget.indexFromItem(self.currentAssetsTreeWidget.currentItem())
        item = self.currentAssetsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = AssetDialog("View", self, item.asset)
            dialog.setWindowTitle("View Asset")
            
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    sql = ("UPDATE Assets SET Description = '" + dialog.descriptionText_edit.text() +
                           "', AcquireDate = '" + dialog.dateAcquiredText_edit.text() +
                           "', InSvcDate = '" + dialog.dateInSvcText_edit.text() + 
                           "', UsefulLife = " + dialog.usefulLifeText_edit.text() +
                           ", SalvageAmount = " + str(dialog.salvageValueText_edit.text()) +
                           ", DepreciationMethod = '" + dialog.depMethodBox.currentText() + 
                           "' WHERE idNum = " + str(item.asset.idNum))
                    self.parent.parent.dbCursor.execute(sql)

                    item.asset.description = dialog.descriptionText_edit.text()
                    item.asset.acquireDate = dialog.dateAcquiredText_edit.text()
                    item.asset.inSvcDate = dialog.dateInSvcText_edit.text()
                    item.asset.usefulLife = dialog.usefulLifeText_edit.text()
                    item.asset.salvageAmount = float(dialog.salvageValueText_edit.text())
                    item.asset.depMethod = dialog.depMethodBox.currentText()

                    if dialog.companyChanged == True:
                        companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                        
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='companies' AND ObjectBeingLinked='assets' AND ObjectIdBeingLinked=?", (companyId, item.asset.idNum))
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectBeingLinked='companies' AND ObjectToAddLinkTo='assets' AND ObjectIdToAddLinkTo=?", (companyId, item.asset.idNum))
                        
                        item.asset.company.removeAsset(item.asset)
                        item.asset.addCompany(self.parent.dataConnection.companies[companyId])
                        item.asset.company.addAsset(item.asset)
                        
                    if dialog.assetTypeChanged == True:
                        assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
                        
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectBeingLinked='assetTypes' AND ObjectToAddLinkTo='assets' AND ObjectIdToAddLinkTo=?", (assetTypeId, item.asset.idNum))
                        
                        item.asset.addAssetType(self.parent.dataConnection.assetTypes[assetTypeId])

                    if dialog.parentAssetChanged == True:
                        # Check to see if the asset has been changed to be the
                        # child of a different asset or is now a top-level asset
                        if dialog.childOfAssetBox.currentText() == "":
                            # The case where an item is not a subasset, changed
                            # to a subasset, and then changed back to no subasset
                            # will flag the parentAssetChanged flag to be true
                            # even though there is no real change.  Need to make
                            # sure that item.asset.subAssetOf exists
                            if item.asset.subAssetOf:
                                oldParentItem = self.getParentItem(item.asset.idNum)
                                
                                item.asset.subAssetOf.removeSubAsset(item.asset)
                                item.asset.removeSubAssetOf()
                                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='assets' AND ObjectIdToAddLinkTo=? AND Method='addSubAssetOf'",
                                                                    (item.asset.idNum,))
                                self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='assets' AND ObjectIdBeingLinked=? AND Method='addSubAsset'",
                                                                    (item.asset.idNum,))
                                
                                oldItemIdx = oldParentItem.indexOfChild(item)
                                oldParentItem.takeChild(oldItemIdx)
                                newItem = AssetTreeWidgetItem(item.asset, self.currentAssetsTreeWidget)
                                self.currentAssetsTreeWidget.addItem(newItem)
                        else:
                            newParentAssetId = self.stripAllButNumbers(dialog.childOfAssetBox.currentText())
                            
                            # Make sure subAssetOf exists.  If it doesn't, some
                            # code will not be used.
                            if item.asset.subAssetOf:
                                oldParentItem = self.getParentItem(item.asset.idNum)
                                
                                item.asset.subAssetOf.removeSubAsset(item.asset)
                                item.asset.addSubAssetOf(self.parent.dataConnection.assets[newParentAssetId])
                                item.asset.subAssetOf.addSubAsset(item.asset)
                                
                                oldItemIdx = oldParentItem.indexOfChild(item)
                                oldParentItem.takeChild(oldItemIdx)
                                newParentItem = self.getParentItem(item.asset.idNum)
                                newItem = AssetTreeWidgetItem(item.asset, newParentItem)

                                # Move children of old item to newItem
                                newItem.assignChildren(item.takeChildren(), newItem)
                                
                                childrenIterator = QTreeWidgetItemIterator(newItem)
                                while childrenIterator.value():
                                    self.currentAssetsTreeWidget.addItem(childrenIterator.value())
                                    childrenIterator += 1
                                
                                self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assets' AND ObjectIdToAddLinkTo=? AND Method='addSubAssetOf' AND ObjectBeingLinked='assets'",
                                                                    (newParentAssetId, item.asset.idNum))
                                self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='assets' AND Method='addSubAsset' AND ObjectBeingLinked='assets' AND ObjectIdBeingLinked=?",
                                                                    (newParentAssetId, item.asset.idNum))
                            else:
                                # Changing from no parent asset to a parent
                                # asset.
                                item.asset.addSubAssetOf(self.parent.dataConnection.assets[newParentAssetId])
                                item.asset.subAssetOf.addSubAsset(item.asset)

                                oldItemIdx = self.currentAssetsTreeWidget.indexOfTopLevelItem(item)
                                self.currentAssetsTreeWidget.takeTopLevelItem(oldItemIdx)
                                parentItem = self.getParentItem(item.asset.idNum)
                                newItem = AssetTreeWidgetItem(item.asset, parentItem)
                                self.currentAssetsTreeWidget.addItem(newItem)

                                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(item.asset.idNum) + ", 'addSubAssetOf', 'assets', " + str(newParentAssetId) + ")")
                                self.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('assets', " + str(newParentAssetId) + ", 'addSubAsset', 'assets', " + str(item.asset.idNum) + ")")
                                
                    self.parent.parent.dbConnection.commit()
                    self.refreshAssetTree()

    def deleteSelectedAssetFromList(self):
        # Get the index of the item in the company list to delete
        idxToDelete = self.currentAssetsTreeWidget.indexOfTopLevelItem(self.currentAssetsTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.currentAssetsTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            item = None
        
        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM Assets WHERE idNum=?", (item.asset.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='assets' AND ObjectIdToAddLinkTo=?", (item.asset.idNum,))
            self.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='assets' AND ObjectIdBeingLinked=?", (item.asset.idNum,))
            
            self.assetsDict.pop(item.asset.idNum)
            item.asset.company.removeAsset(item.asset)
            self.parent.parent.dbConnection.commit()
            
            self.updateAssetsCount()

    def refreshAssetTree(self):
        self.currentAssetsTreeWidget.refreshData()
        
class AssetView(QWidget):
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.assetWidget = AssetWidget(self.dataConnection.assets, self)

        layout = QVBoxLayout()
        layout.addWidget(self.assetWidget)

        self.setLayout(layout)

class GLTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, glAccount, parent):
        super().__init__(parent)
        self.glAccount = glAccount
        
        self.setText(0, str(self.glAccount.idNum))
        self.setText(1, self.glAccount.description)
        self.setText(2, "{:,.2f}".format(self.glAccount.balance()))

        if self.glAccount.placeHolder == True:
            for n in range(3):
                font = self.font(n)
                font.setBold(True)
                self.setFont(n, font)

    def refreshData(self):
        self.setText(0, str(self.glAccount.idNum))
        self.setText(1, self.glAccount.description)
        self.setText(2, "{:,.2f}".format(self.glAccount.balance()))
        
class GLTreeWidget(NewTreeWidget):
    moveGLAcctXToYFromZ = pyqtSignal(int, int, int)
    
    def __init__(self, glAccountsDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, glAccountsDict)
        self.setColumnCount(3)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, glAccountsDict):
        tempDict = glAccountsDict.accountGroups()
        for glAccountKey in tempDict.sortedListOfKeys():
            item = GLTreeWidgetItem(tempDict[glAccountKey], parent)
            
            if item.glAccount.parentOf:
                for subAccountKey in item.glAccount.parentOf.sortedListOfKeys():
                    subItem = GLTreeWidgetItem(item.glAccount.parentOf[subAccountKey], item)
                    subItem.addChild(subItem)
            
            self.addTopLevelItem(item)

    def refreshChildren(self, parentItem):
        for idx in range(parentItem.childCount()):
            parentItem.child(idx).refreshData()

            if parentItem.child(idx).glAccount.childOf.idNum != parentItem.glAccount.idNum:
                self.moveGLAcctXToYFromZ.emit(parentItem.child(idx).glAccount.idNum, parentItem.child(idx).glAccount.childOf.idNum, parentItem.glAccount.idNum)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

            if self.topLevelItem(idx).childCount() > 0:
                self.refreshChildren(self.topLevelItem(idx))
            
class GLWidget(QWidget):
    displayGLAcct = pyqtSignal(int)
    
    def __init__(self, glAccountsDict, parent):
        super().__init__()
        self.glAccountsDict = glAccountsDict
        self.parent = parent

        mainLayout = QVBoxLayout()

        self.chartOfAccountsLabel = QLabel("Chart of Accounts")
        mainLayout.addWidget(self.chartOfAccountsLabel)

        # Piece together the GL layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.chartOfAccountsTreeWidget = GLTreeWidget(self.glAccountsDict, constants.GL_HDR_LIST, constants.GL_HDR_WDTH)
        self.chartOfAccountsTreeWidget.currentItemChanged.connect(self.displayGLDetails)
        self.chartOfAccountsTreeWidget.moveGLAcctXToYFromZ.connect(self.moveAcctXToGrpY)

        treeWidgetsLayout.addWidget(self.chartOfAccountsTreeWidget)
        treeWidgetsLayout.addStretch(1)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewGLAccountDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewGLAccountDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteGLAccount)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)
        
        self.setLayout(mainLayout)

    def displayGLDetails(self, newItem, oldItem):
        self.displayGLAcct.emit(newItem.glAccount.idNum)
        
    def moveAcctXToGrpY(self, acctId, newParentId, oldParentId):
        oldParentItem = self.getItem(oldParentId)
        newParentItem = self.getItem(newParentId)
        
        for idx in range(oldParentItem.childCount()):
            if oldParentItem.child(idx).glAccount.idNum == acctId:
                oldItem = oldParentItem.takeChild(idx)
                
        newItem = GLTreeWidgetItem(oldItem.glAccount, newParentItem)
        self.chartOfAccountsTreeWidget.addItem(newItem)

    def insertIntoDatabase(self, tblName, columns, values):
        sql = "INSERT INTO " + tblName + " " + columns + " VALUES " + values
        self.parent.parent.dbCursor.execute(sql)

    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def getParentItem(self, glNum):
        iterator = QTreeWidgetItemIterator(self.chartOfAccountsTreeWidget)
        
        while iterator.value():
            for childKey in iterator.value().glAccount.parentOf:
                if glNum == childKey:
                    return iterator.value()
            iterator += 1

    def getItem(self, glNum):
        for idx in range(self.chartOfAccountsTreeWidget.topLevelItemCount()):
            item = self.chartOfAccountsTreeWidget.topLevelItem(idx)
            if item.glAccount.placeHolder == True and item.glAccount.idNum == glNum:
                return item

    def showNewGLAccountDialog(self):
        dialog = GLAccountDialog("New", self)
        if dialog.exec_():
            if dialog.acctGrpChk.checkState() == Qt.Checked:
                placeHolder = 1
            else:
                placeHolder = 0
                parentAccount = self.stripAllButNumbers(dialog.acctGrpsBox.currentText())

            # Create new object and add links
            newGLAccount = GLAccount(dialog.descriptionText.text(),
                                     placeHolder,
                                     int(dialog.accountNumText.text()))
            if placeHolder == 0:
                newGLAccount.addParent(self.glAccountsDict[parentAccount])
                self.glAccountsDict[parentAccount].addChild(newGLAccount)
            
            # Add to database and corporate structure. If we are dealing
            # with a "live" GL account, we need to add Xref records to
            # the database.
            self.glAccountsDict[newGLAccount.idNum] = newGLAccount
            self.insertIntoDatabase("GLAccounts", "(idNum, Description, Placeholder)", "(" + str(newGLAccount.idNum) + ", '" + newGLAccount.description + "', " + str(placeHolder) + ")")
            if placeHolder == 0:
                self.insertIntoDatabase("Xref", "", "('glAccounts', " + str(parentAccount) + ", 'addChild', 'glAccounts', " + str(newGLAccount.idNum) + ")")
                self.insertIntoDatabase("Xref", "", "('glAccounts', " + str(newGLAccount.idNum) + ", 'addParent', 'glAccounts', " + str(parentAccount) + ")")
            self.parent.parent.dbConnection.commit()
            
            # Add GL to widget tree
            if placeHolder == 1:
                item = GLTreeWidgetItem(newGLAccount, self.chartOfAccountsTreeWidget)
                self.chartOfAccountsTreeWidget.addTopLevelItem(item)
            else:
                parentItem = self.getItem(parentAccount)
                item = GLTreeWidgetItem(newGLAccount, parentItem)
                parentItem.addChild(item)
            
    def showViewGLAccountDialog(self):
        idxToShow = self.chartOfAccountsTreeWidget.indexFromItem(self.chartOfAccountsTreeWidget.currentItem())
        item = self.chartOfAccountsTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = GLAccountDialog("View", self, item.glAccount)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    self.parent.parent.dbCursor.execute("UPDATE GLAccounts SET idNum=?, Description=? WHERE idNum=?", (dialog.accountNumText_edit.text(), dialog.descriptionText_edit.text(), item.glAccount.idNum))
                    self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='glAccounts' AND ObjectIdToAddLinkTo=?",
                                                        (dialog.accountNumText_edit.text(), item.glAccount.idNum))
                    self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectBeingLinked='glAccounts' AND ObjectIdBeingLinked=?",
                                                        (dialog.accountNumText_edit.text(), item.glAccount.idNum))
                    item.glAccount.idNum = int(dialog.accountNumText_edit.text())
                    item.glAccount.description = dialog.descriptionText_edit.text()

                    if dialog.accountGroupChanged == True:
                        newParent = self.stripAllButNumbers(dialog.acctGrpsBox.currentText())
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdToAddLinkTo=? WHERE ObjectToAddLinkTo='glAccounts' AND ObjectIdBeingLinked=? AND Method='addChild' AND ObjectBeingLinked='glAccounts'",
                                                            (newParent, item.glAccount.idNum))
                        self.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectBeingLinked='glAccounts' AND Method='addParent' AND ObjectToAddLinkTo='glAccounts' AND ObjectIdToAddLinkTo=?",
                                                            (newParent, item.glAccount.idNum))
                        item.glAccount.childOf.removeChild(item.glAccount)
                        item.glAccount.addParent(self.glAccountsDict[newParent])
                        item.glAccount.childOf.addChild(item.glAccount)

                    self.parent.parent.dbConnection.commit()
                    self.chartOfAccountsTreeWidget.refreshData()

    def deleteGLAccount(self):
        idxToDelete = self.chartOfAccountsTreeWidget.indexOfTopLevelItem(self.chartOfAccountsTreeWidget.currentItem())
        item = self.chartOfAccountsTreeWidget.takeTopLevelItem(idxToDelete)
        
        if item:
            self.parent.parent.dbCursor.execute("DELETE FROM GLAccounts WHERE idNum=?", (item.glAccount.idNum,))
            self.parent.parent.dbConnection.commit()
            self.glAccountsDict.pop(item.glAccount.idNum)

class GLPostingsTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, postingItem, parent):
        super().__init__(parent)
        self.glPosting = postingItem
        
        self.setText(0, self.glPosting.detailOf.date)
        self.setText(1, self.glPosting.detailOf.description)
        if self.glPosting.debitCredit == constants.DEBIT:
            self.setText(2, "{: ,.2f}".format(self.glPosting.amount))
        else:
            self.setText(2, "{:-,.2f}".format(-1 * self.glPosting.amount))
        
    def refreshData(self):
        self.setText(0, self.glPosting.detailOf.date)
        self.setText(1, self.glPosting.detailOf.description)
        self.setText(2, "{:,.2f}".format(self.glPosting.amount))
        
class GLPostingsTreeWidget(NewTreeWidget):
    def __init__(self, headerList, widthList):
        super().__init__(headerList, widthList)
        self.setColumnCount(3)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, glPostingsDetDict):
        for glKey in glPostingsDetDict:
            item = GLPostingsTreeWidgetItem(glPostingsDetDict[glKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

class GLPostingsWidget(QWidget):
    postToGL = pyqtSignal(int, str, str, list)
    updateGLPost = pyqtSignal(object, str, str)
    updateGLDet = pyqtSignal(object, float, str)
    deleteGLPost = pyqtSignal(object)
    
    def __init__(self, parent, companiesDict, glAcctsDict):
        super().__init__()
        mainLayout = QVBoxLayout()
        self.parent = parent
        self.companiesDict = companiesDict
        self.glAcctsDict = glAcctsDict

        self.glPostingsLabel = QLabel("Details")
        mainLayout.addWidget(self.glPostingsLabel)

        # Piece together the GL layout
        subLayout = QHBoxLayout()
        treeWidgetsLayout = QVBoxLayout()

        self.glPostingsTreeWidget = GLPostingsTreeWidget(constants.GL_POST_HDR_LIST, constants.GL_POST_HDR_WDTH)

        treeWidgetsLayout.addWidget(self.glPostingsTreeWidget)
        treeWidgetsLayout.addStretch(1)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewGLPostingDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewGLPostingDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteGLPostingAccount)
        
        subLayout.addLayout(treeWidgetsLayout)
        subLayout.addWidget(buttonWidget)
        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)

    def showDetail(self, glAcctNum, glPostingsDetDict):
        self.glPostingsTreeWidget.clear()
        self.glPostingsTreeWidget.buildItems(self.glPostingsTreeWidget, glPostingsDetDict)
        
    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        return int(regex.groups()[0])

    def showNewGLPostingDialog(self):
        dialog = NewGLPostingDialog("New", self.companiesDict, self.glAcctsDict)
        if dialog.exec_():
            companyNum = self.stripAllButNumbers(dialog.companyBox.currentText())
            date = dialog.dateText.text()
            description = dialog.memoText.text()
            details = []
            for detailKey, detail in dialog.postingsWidget.details.items():
                if detail.balanceType() != "NONE":
                    glAccountNum = self.stripAllButNumbers(detail.glBox.currentText())
                    details.append((detail.balance(), detail.balanceType(), glAccountNum, None, None))
            
            self.postToGL.emit(companyNum, date, description, details)
            
    def showViewGLPostingDialog(self):
        pass

    def deleteGLPostingAccount(self):
        idxToDelete = self.glPostingsTreeWidget.indexOfTopLevelItem(self.glPostingsTreeWidget.currentItem())

        if idxToDelete >= 0:
            item = self.glPostingsTreeWidget.takeTopLevelItem(idxToDelete)
        else:
            item = None
        
        if item:
            glDet = item.glPosting
            glPost = glDet.detailOf
            self.deleteGLPost.emit(glPost)
        
class GLView(QWidget):
    updateGLTree = pyqtSignal()
    
    def __init__(self, dataConnection, parent):
        super().__init__(parent)
        self.dataConnection = dataConnection
        self.parent = parent

        self.glWidget = GLWidget(self.dataConnection.glAccounts, self)
        self.glWidget.displayGLAcct.connect(self.displayGLDetails)
        self.glPostingsWidget = GLPostingsWidget(self, self.dataConnection.companies, self.dataConnection.glAccounts)
        self.glPostingsWidget.postToGL.connect(self.postToGL)
        self.glPostingsWidget.deleteGLPost.connect(self.deleteGLPost)

        layout = QVBoxLayout()
        layout.addWidget(self.glWidget)
        layout.addWidget(self.glPostingsWidget)

        self.setLayout(layout)

    def refreshGL(self):
        self.glWidget.chartOfAccountsTreeWidget.refreshData()

    def displayGLDetails(self, glAcctNum):
        self.glPostingsWidget.showDetail(glAcctNum, self.dataConnection.glAccounts[glAcctNum].postings)

    def nextIdNum(self, name):
        self.parent.dbCursor.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.parent.dbCursor.fetchone()
        if largestId != None:
            return largestId[0] + 1
        else:
            return 1

    def deleteGLPost(self, GLPost):
        self.dataConnection.glPostings.pop(GLPost.idNum)
        self.dataConnection.companies[GLPost.company.idNum].removePosting(GLPost)
        self.parent.dbCursor.execute("DELETE FROM GLPostings WHERE idNum=?",
                                     (GLPost.idNum,))
        self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='glPostings' AND ObjectIdToAddLinkTo=?",
                                     (GLPost.idNum,))
        self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='glPostings' AND ObjectIdBeingLinked=?",
                                     (GLPost.idNum,))
        for glDetKey, glDet in GLPost.details.items():
            self.dataConnection.glPostingsDetails.pop(glDetKey)
            glAccount = glDet.glAccount
            glAccount.removePosting(glDet)
            self.parent.dbCursor.execute("DELETE FROM GLPostingsDetails WHERE idNum=?",
                                         (glDetKey,))
            self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='glPostingsDetails' AND ObjectIdToAddLinkTo=?",
                                         (glDetKey,))
            self.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='glPostingsDetails' AND ObjectIdBeingLinked=?",
                                         (glDetKey,))

        self.parent.dbConnection.commit()
        self.updateGLTree.emit()
        
    def postToGL(self, companyNum, date, description, listOfDetails):
        glPostingIdNum = self.nextIdNum("GLPostings")
        glPostingDetailIdNum = self.nextIdNum("GLPostingsDetails")
        
        glPosting = GLPosting(date, description, glPostingIdNum)
        glPosting.addCompany(self.dataConnection.companies[companyNum])
        self.dataConnection.companies[companyNum].addPosting(glPosting)
        self.dataConnection.glPostings[glPosting.idNum] = glPosting
        self.parent.dbCursor.execute("INSERT INTO GLPostings (Date, Description) VALUES (?, ?)",
                                            (glPosting.date, glPosting.description))
        self.parent.dbCursor.execute("INSERT INTO Xref VALUES ('glPostings', ?, 'addCompany', 'companies', ?)",
                                     (glPosting.idNum, companyNum))
        self.parent.dbCursor.execute("INSERT INTO Xref VALUES ('companies', ?, 'addPosting', 'glPostings', ?)",
                                     (companyNum, glPosting.idNum))

        for detail in listOfDetails:
            glPostingDetail = GLPostingDetail(detail[0], detail[1], glPostingDetailIdNum)
            
            glPosting.addDetail(glPostingDetail)
            glPostingDetail.addDetailOf(glPosting)
            glPostingDetail.addGLAccount(self.dataConnection.glAccounts[detail[2]])
            glPostingDetail.glAccount.addPosting(glPostingDetail)

            if detail[3]:
                detail[3].addGLPosting(glPostingDetail)
                self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                             (detail[4], detail[3].idNum, "addGLPosting", "glPostingsDetails", glPostingDetail.idNum))
            
            self.dataConnection.glPostingsDetails[glPostingDetail.idNum] = glPostingDetail

            self.parent.dbCursor.execute("INSERT INTO GLPostingsDetails (Amount, DebitCredit) VALUES (?, ?)",
                                         (glPostingDetail.amount, glPostingDetail.debitCredit))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostings", glPosting.idNum, "addDetail", "glPostingsDetails", glPostingDetail.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostingsDetails", glPostingDetail.idNum, "addDetailOf", "glPostings", glPosting.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glPostingsDetails", glPostingDetail.idNum, "addGLAccount", "glAccounts", glPostingDetail.glAccount.idNum))
            self.parent.dbCursor.execute("INSERT INTO Xref VALUES (?, ?, ?, ?, ?)",
                                         ("glAccounts", glPostingDetail.glAccount.idNum, "addPosting", "glPostingsDetails", glPostingDetail.idNum))
            
            self.parent.dbConnection.commit()

            glPostingDetailIdNum += 1
        self.updateGLTree.emit()
