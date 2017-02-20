from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui_dialogs import *
import re
import sys
import constants
import functions
from classes import *

class ObjectWidget(QWidget):
    def __init__(self, parent, dbConn, dbCur):
        super().__init__()
        self.parent = parent
        self.dbConn = dbConn
        self.dbCur = dbCur
    
    def stripAllButNumbers(self, string):
        regex = re.match(r"\s*([0-9]+).*", string)
        if regex:
            return int(regex.groups()[0])
        else:
            return None
    
    def nextIdNum(self, name):
        self.dbCur.execute("SELECT seq FROM sqlite_sequence WHERE name = '" + name + "'")
        largestId = self.dbCur.fetchone()
        if largestId:
            return int(largestId[0]) + 1
        else:
            return 1
    
    def insertIntoDatabase(self, tblName, columns, values):
        if columns:
            columnsStr = " " + str(columns).replace("'", "")
        else:
            columnsStr = ""
            
        valuesStr = "("
        for n in range(len(values)):
            valuesStr += "?, "
        valuesStr = valuesStr[:-2] + ")"
        
        sql = "INSERT INTO %s%s VALUES %s" % (tblName, columnsStr, valuesStr)
        self.dbCur.execute(sql, values)

    def updateDatabase(self, tblName, columnValuesDict, whereDict):
        listOfPassedValues = []
        sql = "UPDATE %s SET " % tblName
        
        for column, value in columnValuesDict.items():
            sql += "%s=?, " % column
            listOfPassedValues.append(value)
        sql = sql[:-2]
        
        sql += " WHERE "
        for column, value in whereDict.items():
            sql += "%s=? AND " % column
            listOfPassedValues.append(value)
        sql = sql[:-5]
        
        self.dbCur.execute(sql, tuple(listOfPassedValues))

    def deleteFromDatabase(self, tblName, whereDict):
        listOfPassedValues = []
        sql = "DELETE FROM %s WHERE " % tblName

        for column, value in whereDict.items():
            sql += "%s=? AND " % column
            listOfPassedValues.append(value)
        sql = sql[:-5]
        
        self.dbCur.execute(sql, tuple(listOfPassedValues))
        
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

class DeleteButton(QPushButton):
    def __init__(self):
        super().__init__("-")
        self.setFixedWidth(30)

class CIPAllocationDetailExpenseItem(QWidget):
    def __init__(self, parent, dbCur):
        super().__init__(parent)
        
        # Create major GUI elements
        expenseAcctLbl = QLabel("Expense Acct:")
        self.glBox = QComboBox()
        glAccounts = functions.GetListOfGLAccounts(dbCur)
        self.glBox.addItems(glAccounts)
        
        # Add GUI elements to layout
        layout = QHBoxLayout()
        layout.addWidget(expenseAcctLbl)
        layout.addWidget(self.glBox)
        layout.setContentsMargins(0, 1, 0, 1)
        
        self.setLayout(layout)
        
class CIPAllocationDetailItem(QWidget):
    validity = pyqtSignal(bool)
    delete = pyqtSignal(object)
    
    def __init__(self, parent, dbCur, costAmt=""):
        super().__init__(parent)
        self.valid = False
        
        # Create major GUI elements
        self.assetTxt = QLineEdit()
        self.costTxt = QLineEdit(str(round(float(costAmt), 2)))
        self.expenseChk = QCheckBox()
        self.deleteBtn = DeleteButton()
        self.expenseDetailWidget = CIPAllocationDetailExpenseItem(self, dbCur)
        
        # Add GUI functionality
        self.assetTxt.setFixedWidth(133)
        self.assetTxt.editingFinished.connect(self.validate)
        self.costTxt.setFixedWidth(60)
        self.costTxt.editingFinished.connect(self.validate)
        self.expenseChk.stateChanged.connect(self.showHideExpenseGL)
        self.deleteBtn.released.connect(self.deleteLine)
        self.expenseDetailWidget.hide()
        
        # Add GUI elements to layout
        layout = QVBoxLayout()
        
        layoutRow1 = QHBoxLayout()
        layoutRow1.addWidget(self.assetTxt)
        layoutRow1.addWidget(self.costTxt)
        layoutRow1.addWidget(self.expenseChk)
        layoutRow1.addWidget(self.deleteBtn)
        layoutRow1.setContentsMargins(0, 1, 0, 1)

        layout.addLayout(layoutRow1)
        layout.addWidget(self.expenseDetailWidget)
        layout.setContentsMargins(0, 1, 0, 1)

        self.setLayout(layout)

    def deleteLine(self):
        self.delete.emit(self)

    def hasBlanks(self):
        if self.assetTxt.text() == "" or self.costTxt.text() == "":
            return True

    def validate(self):
        self.valid = True
        if self.assetTxt.text() != "" and self.costTxt.text() != "":
            try:
                float(self.costTxt.text())
            except:
                self.valid = False
        else:
            self.valid = False
        self.validity.emit(self.valid)

    def showHideExpenseGL(self):
        if self.expenseChk.isChecked() == True:
            self.expenseDetailWidget.show()
        else:
            self.expenseDetailWidget.hide()
        
class CIPAllocationDetailWidget(QWidget):
    validity = pyqtSignal(bool)
    
    def __init__(self, parent, cipAmt, dbCur):
        super().__init__(parent)
        self.cipAmt = cipAmt
        self.dbCur = dbCur
        
        self.layout = QVBoxLayout()
        self.subLayout = QVBoxLayout()

        # Create header
        headerLayout = QHBoxLayout()
        
        hdrAssetLbl = QLabel("Asset Desc")
        hdrAssetLbl.setFixedWidth(133)
        hdrAssetLbl.setAlignment(Qt.AlignCenter)
        self.hdrAmtLbl = QLabel("Cost")
        self.hdrAmtLbl.setFixedWidth(60)
        self.hdrAmtLbl.setAlignment(Qt.AlignCenter)
        hdrExpLbl = QLabel("Exp")
        hdrExpLbl.setFixedWidth(30)
        hdrExpLbl.setAlignment(Qt.AlignCenter)
        
        headerLayout.addWidget(hdrAssetLbl)
        headerLayout.addWidget(self.hdrAmtLbl)
        headerLayout.addWidget(hdrExpLbl)
        headerLayout.addSpacing(30)
        headerLayout.addStretch(1)
        headerLayout.setContentsMargins(0, 1, 0, 1)
        
        # Create first blank line
        self.newLine(cipAmt)
        
        # Assemble layout
        self.subLayout.setSpacing(0)
        
        self.layout.addLayout(headerLayout)
        self.layout.addLayout(self.subLayout)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

    def allocatedCIP(self):
        allocCIP = 0.0

        for n in range(self.subLayout.count()):
            costTxt = self.subLayout.itemAt(n).widget().costTxt.text()
            allocCIP += float(costTxt)
        return allocCIP
    
    def newLine(self, cipAmt):
        detItem = CIPAllocationDetailItem(self, self.dbCur, cipAmt)
        detItem.validity.connect(self.validateDetails)
        detItem.delete.connect(self.deleteLine)
        
        self.subLayout.addWidget(detItem)
        
    def validateDetails(self):
        detailsValid = True
        for n in range(self.subLayout.count()):
            if self.subLayout.itemAt(n).widget().valid == False:
                detailsValid = False
        
        if detailsValid == True:
            cipAmt = round(self.cipAmt - self.allocatedCIP(), 2)
        
            if cipAmt > 0.0:
                self.newLine(cipAmt)
                self.validity.emit(False)
            else:
                self.validity.emit(True)
        else:
            self.validity.emit(False)
            
    def deleteLine(self, objToDel):
        index = self.subLayout.indexOf(objToDel)
        layoutItem = self.subLayout.takeAt(index)
        widget = layoutItem.widget()
        widget.close()
        del widget
        
class DepAssetTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, assetItem, parent):
        super().__init__(parent)
        self.asset = assetItem

        self.setText(0, str(self.asset.idNum))
        self.setText(1, self.asset.description)

    def refreshData(self):
        self.setText(0, str(self.asset.idNum))
        self.setText(1, self.asset.description)

class DepAssetTreeWidget(NewTreeWidget):
    def __init__(self, assetDict, headerList, widthList):
        super().__init__(headerList, widthList)
        self.buildItems(self, assetDict)
        self.setColumnCount(len(headerList))
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, assetDict):
        for assetKey in assetDict:
            item = DepAssetTreeWidgetItem(assetDict[assetKey], parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

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

    def disableSave(self):
        self.saveButton.setEnabled(False)

    def enableSave(self):
        self.saveButton.setEnabled(True)
        
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
                
class ClickableLabel(QLabel):
    released = pyqtSignal()

    def __init__(self, text):
        super().__init__(text)

    def mouseReleaseEvent(self, event):
        self.released.emit()

class InvoicePaymentTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, pymtId, dbCur, parent):
        super().__init__(parent)
        self.invoicePayment = pymtId
        self.refreshData(dbCur)

    def refreshData(self, dbCur):
        dbCur.execute("""SELECT DatePaid, AmountPaid FROM InvoicesPayments
                         WHERE idNum=?""", (self.invoicePayment,))
        datePd, amtPd = dbCur.fetchone()
        self.setText(0, str(self.invoicePayment))
        self.setText(1, datePd)
        self.setText(2, str(amtPd))

class InvoicePaymentTreeWidget(NewTreeWidget):
    def __init__(self, dbCur, invoice, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.invoice = invoice
        self.buildItems(self)
        
    def buildItems(self, parent):
        self.dbCursor.execute("""SELECT idNum FROM InvoicesPayments
                                 WHERE InvoiceId=?""", (self.invoice,))
        results = self.dbCursor.fetchall()
        for idNum in results:
            item = InvoicePaymentTreeWidgetItem(idNum[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData(self.dbCursor)
            
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
    
    def __init__(self, company, dbCur):
        super().__init__()
        self.company = company
        self.dbCur = dbCur
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
            oldEmit = self.dontEmit

            self.dontEmitSignals(True)
            self.dbCur.execute("""SELECT idNum, Description FROM Assets
                                  WHERE CompanyId=?""",
                               (self.company,))
            for idNum, desc in self.dbCur:
                self.selector.addItem(constants.ID_DESC % (idNum, desc))
            self.selector.show()
            self.dontEmitSignals(oldEmit)
            
            self.emitRdoBtnChange()

    def showProjectDict(self, checked):
        # Only do this if we are clicking on the item, not if it is being
        # unclicked.
        if checked == True:
            self.clear()
            oldEmit = self.dontEmit

            self.dontEmitSignals(True)
            self.dbCur.execute("""SELECT idNum, Description FROM Projects
                                  WHERE CompanyId=?""",
                               (self.company,))
            for idNum, desc in self.dbCur:
                self.selector.addItem(constants.ID_DESC % (idNum, desc))
            self.selector.show()
            self.dontEmitSignals(oldEmit)
            
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
    
    def __init__(self, dbCur, invoiceNum=None, proposals=None):
        super().__init__()
        self.details = {}
        self.proposals = proposals
        self.dbCur = dbCur
        
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        descLine = QLabel("Description")
        costLine = QLabel("Cost")
        propLine = QLabel("Proposal Element")
        
        self.gridLayout.addWidget(descLine, 0, 0)
        self.gridLayout.addWidget(costLine, 0, 1)
        self.gridLayout.addWidget(propLine, 0, 2, 1, 2)
        
        dbCur.execute("""SELECT Description, Cost, ProposalDetId, idNum
                         FROM InvoicesDetails WHERE InvoiceId=?""",
                      (invoiceNum,))
        invoiceDetails = dbCur.fetchall()
        
        if not invoiceDetails:
            self.addNewLine()
        else:
            for desc, cost, propDetail, idNum in invoiceDetails:
                self.addLine(desc, cost, propDetail, dbCur, False, False, idNum)
        
        self.layout.addLayout(self.gridLayout)
        self.layout.addStretch(1)
        
        self.setLayout(self.layout)

    def resetProposalBoxes(self):
        for detailKey in self.details:
            rowToUse = self.details[detailKey][4]
            
            newProposalBox = self.makeProposalDetComboBox(self.dbCur, None)
            
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

    def makeProposalDetComboBox(self, dbCur, proposalDet):
        proposalDetList = [""]
        proposalBox = QComboBox()
        results = None
        
        if proposalDet:
            dbCur.execute("""SELECT idNum, Description FROM ProposalsDetails
                             WHERE ProposalId IN
                             (SELECT ProposalId FROM ProposalsDetails
                             WHERE idNum=?)""", (proposalDet,))
            results = dbCur.fetchall()
        elif self.proposals:
            if len(self.proposals) == 1:
                proposals = str(tuple(self.proposals)).replace(",", "")
            else:
                proposals = str(tuple(self.proposals))
            sql = """SELECT idNum, Description FROM ProposalsDetails
                     WHERE ProposalId IN %s""" % proposals
            dbCur.execute(sql)
            results = dbCur.fetchall()
            
        if results:
            for idNum, desc in results:
                if idNum == proposalDet:
                    proposalDesc = desc
                    
                proposalDetList.append(constants.ID_DESC % (idNum, desc))
            proposalBox.addItems(proposalDetList)

            if proposalDet:
                proposalBox.setCurrentIndex(proposalBox.findText(constants.ID_DESC % (proposalDet, proposalDesc)))

        return proposalBox
        
    def addLine(self, desc, cost, proposalDet, dbCur, showDelBtn=False, editable=True, detailIdNum=0):
        rowToUse = self.gridLayout.rowCount()
        
        proposalBox = self.makeProposalDetComboBox(dbCur, proposalDet)
        
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
        self.addLine("", "", "", self.dbCur)
        
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
    
    def __init__(self, dbCur, proposalId=None):
        super().__init__()
        self.details = {}
        
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        detailLine = QLabel("Detail")
        costLine = QLabel("Cost")

        self.gridLayout.addWidget(detailLine, 0, 0)
        self.gridLayout.addWidget(costLine, 0, 1, 1, 2)

        dbCur.execute("""SELECT idNum, Description, Cost FROM ProposalsDetails
                         WHERE ProposalId=?""", (proposalId,))
        details = dbCur.fetchall()
        if not details:
            self.addNewLine()
        else:
            for idNum, desc, cost in details:
                self.addLine(desc, cost, False, False, idNum)

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
    def __init__(self, historyItem, dbCur, parent):
        super().__init__(parent)
        self.history = historyItem
        self.refreshData(dbCur)

    def refreshData(self, dbCur):
        dbCur.execute("""SELECT Date, Description, Dollars, PosNeg
                         FROM AssetHistory WHERE idNum=?""", (self.history,))
        date, desc, cost, posNeg = dbCur.fetchone()
        
        self.setText(0, date)
        self.setText(1, desc)
        if posNeg == constants.POSITIVE:
            self.setText(2, "{:,.2f}".format(cost))
        else:
            self.setText(2, "{:,.2f}".format(-1 * cost))

class AssetHistoryTreeWidget(NewTreeWidget):
    def __init__(self, dbCur, headerList, widthList, assetId):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.asset = assetId
        self.buildItems(self)
        self.setColumnCount(len(headerList))
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent):
        self.dbCursor.execute("""SELECT idNum FROM AssetHistory
                                 WHERE AssetId=?""", (self.asset,))
        histories = self.dbCursor.fetchall()
        for history in histories:
            item = AssetHistoryTreeWidgetItem(history[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData()

class VendorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, vendorId, dbCur, parent):
        super().__init__(parent)
        self.vendor = vendorId
        self.refreshData(dbCur)
        
    def refreshData(self, dbCur):
        dbCur.execute("SELECT Name FROM Vendors WHERE idNum=?", (self.vendor,))
        name = dbCur.fetchone()[0]

        dbCur.execute("SELECT Count(idNum) FROM Proposals WHERE VendorId=?",
                      (self.vendor,))
        propCount = dbCur.fetchone()[0]

        dbCur.execute("""SELECT Count(idNum) FROM Proposals
                         WHERE VendorId=? AND Status=?""",
                      (self.vendor, constants.OPN_PROPOSAL_STATUS))
        openPropCount = dbCur.fetchone()[0]
        
        openInvoices = 0
        invoiceCount = 0
        balance = 0.0
        dbCur.execute("SELECT idNum FROM Invoices WHERE VendorId=?",
                      (self.vendor,))
        invoices = dbCur.fetchall()
        for invoice in invoices:
            dbCur.execute("""SELECT Sum(Cost) FROM InvoicesDetails
                             WHERE InvoiceId=?""", (invoice[0],))
            invoiceTtl = dbCur.fetchone()[0]

            dbCur.execute("""SELECT Sum(AmountPaid) FROM InvoicesPayments
                             WHERE InvoiceId=?""", (invoice[0],))
            invoicePymts = dbCur.fetchone()[0]
            if not invoicePymts:
                invoicePymts = 0.0

            if invoiceTtl - invoicePymts != 0:
                openInvoices += 1
            balance += invoiceTtl - invoicePymts
        
        self.setText(0, str(self.vendor))
        self.setText(1, name)
        self.setText(2, "%d / %d" % (openPropCount, propCount))
        self.setText(3, "%d / %d" % (openInvoices, len(invoices)))
        self.setText(4, "{:,.2f}".format(balance))
        
class VendorTreeWidget(NewTreeWidget):
    def __init__(self, dbCur, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.buildItems(self, dbCur)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)
        
    def buildItems(self, parent, dbCur):
        dbCur.execute("SELECT idNum FROM Vendors")
        results = dbCur.fetchall()
        for idNum in results:
            item = VendorTreeWidgetItem(idNum[0], dbCur, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData(self.dbCursor)

class VendorWidget(ObjectWidget):
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()

        self.vendorLabel = QLabel()
        mainLayout.addWidget(self.vendorLabel, 0, 0)

        # Piece together the vendor layout
        self.vendorTreeWidget = VendorTreeWidget(self.dbCur,
                                                 constants.VENDOR_HDR_LIST,
                                                 constants.VENDOR_HDR_WDTH)
        
        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewVendorDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewVendorDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedVendorFromList)

        mainLayout.addWidget(self.vendorTreeWidget, 1, 0)
        mainLayout.addWidget(buttonWidget, 1, 1)
        
        self.setLayout(mainLayout)
        self.updateVendorCount()
        
    def showNewVendorDialog(self):
        dialog = VendorDialog("New", self.dbCur, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Vendors")
            GLNumber = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
            
            vendTblCols = ("Name", "Address", "City", "State",
                           "ZIP", "Phone", "GLAccount")
            vendTblVals = (dialog.nameText.text(),
                           dialog.addressText.text(),
                           dialog.cityText.text(),
                           dialog.stateText.text(),
                           dialog.zipText.text(),
                           dialog.phoneText.text(),
                           GLNumber)
            self.insertIntoDatabase("Vendors", vendTblCols, vendTblVals)
            
            self.dbConn.commit()
            
            # Make vendor into a VendorTreeWidgetItem and add it to VendorTree
            item = VendorTreeWidgetItem(nextId, self.dbCur,
                                        self.vendorTreeWidget)
            self.vendorTreeWidget.addTopLevelItem(item)
            self.updateVendorCount()

    def showViewVendorDialog(self):
        item = self.vendorTreeWidget.currentItem()
        
        # Only display dialog if an item in the widget tree has been selected
        if item:
            dialog = VendorDialog("View", self.dbCur, self, item.vendor)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    vendId = item.vendor
                    glAccountNum = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
                    
                    colValDict = {"Name": dialog.nameText.text(),
                                  "Address": dialog.addressText.text(),
                                  "City": dialog.cityText.text(),
                                  "State": dialog.stateText.text(),
                                  "ZIP": dialog.zipText.text(),
                                  "Phone": dialog.phoneText.text(),
                                  "GLAccount": glAccountNum}
                    whereDict = {"idNum": vendId}
                    self.updateDatabase("Vendors", colValDict, whereDict)
                    
                    self.dbConn.commit()
                    self.vendorTreeWidget.refreshData()

    def deleteSelectedVendorFromList(self):
        # Get item that was deleted from VendorTreeWidget
        item = self.vendorTreeWidget.currentItem()
        
        if item:
            self.dbCur.execute("""SELECT Invoices.idNum FROM Invoices
                                  WHERE Invoices.VendorId=?
                                  UNION
                                  SELECT Proposals.idNum FROM Proposals
                                  WHERE Proposals.VendorId=?""",
                               (item.vendor, item.vendor))
            
            # Only delete vendor if it has no invoices or proposals
            # linked to it.
            if self.dbCur.fetchall():
                deleteError = QMessageBox()
                deleteError.setWindowTitle("Can't delete")
                deleteError.setText("Cannot delete a vendor that has issued invoices or bids.  Delete those first.")
                deleteError.exec_()
            else:
            # Delete item from database and update the vendors dictionary
                idxToDelete = self.vendorTreeWidget.indexOfTopLevelItem(item)
                self.vendorTreeWidget.takeTopLevelItem(idxToDelete)
                
                whereDict = {"idNum": item.vendor}
                self.deleteFromDatabase("Vendors", whereDict)
                self.dbConn.commit()
            
                self.updateVendorCount()

    def updateVendorCount(self):
        self.vendorLabel.setText("Vendors: %d" %
                                 self.vendorTreeWidget.topLevelItemCount())
        
    def refreshVendorTree(self):
        self.vendorTreeWidget.refreshData()
        
class InvoiceTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, invoiceId, dbCur, parent):
        super().__init__(parent)
        self.invoice = invoiceId
        self.refreshData(dbCur)
    
    def refreshData(self, dbCur):
        invoiceAmt = 0.0
        paymentAmt = 0.0

        dbCur.execute("""SELECT Invoices.InvoiceDate, Invoices.DueDate,
                                Vendors.Name
                         FROM Invoices
                         LEFT JOIN Vendors ON Invoices.VendorId = Vendors.idNum
                         WHERE Invoices.idNum=?""", (self.invoice,))
        invoiceDate, dueDate, vendorName = dbCur.fetchone()

        dbCur.execute("SELECT Cost FROM InvoicesDetails WHERE InvoiceId=?",
                      (self.invoice,))
        for cost in dbCur:
            invoiceAmt += cost[0]

        dbCur.execute("""SELECT AmountPaid FROM InvoicesPayments
                         WHERE InvoiceId=?""", (self.invoice,))
        for payment in dbCur:
            paymentAmt += payment[0]
        
        self.setText(0, str(self.invoice))
        self.setText(1, vendorName)
        self.setText(2, invoiceDate)
        self.setText(3, dueDate)
        self.setText(4, "{:,.2f}".format(invoiceAmt))
        self.setText(5, "{:,.2f}".format(paymentAmt))
        self.setText(6, "{:,.2f}".format(invoiceAmt - paymentAmt))

class InvoiceTreeWidget(NewTreeWidget):
    moveItem = pyqtSignal(int, str, str)
    
    def __init__(self, dbCursor, status, headerList, widthList, restriction=None):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCursor
        self.status = status
        self.buildItems(self, restriction)
        self.setColumnCount(7)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, restriction):
        sql = "SELECT idNum FROM Invoices"
        if restriction:
            params = tuple(restriction.split("."))
            if params[0] == "VendorId":
                sql += " WHERE VendorId=?"
                params = (params[1],)
            else:
                sql += """ JOIN InvoicesObjects
                           ON Invoices.idNum = InvoicesObjects.InvoiceId
                           WHERE ObjectType=? AND ObjectId=?"""
            self.dbCursor.execute(sql, params)
        else:
            self.dbCursor.execute(sql)
            
        results = self.dbCursor.fetchall()
        for idNum in results:
            balance = functions.CalculateInvoiceBalance(self.dbCursor, idNum[0])
                
            if self.status == constants.INV_OPEN_STATUS and balance != 0.0:
                item = InvoiceTreeWidgetItem(idNum[0], self.dbCursor, parent)
                self.addTopLevelItem(item)
            elif self.status == constants.INV_PAID_STATUS and balance == 0.0:
                item = InvoiceTreeWidgetItem(idNum[0], self.dbCursor, parent)
                self.addTopLevelItem(item)
            elif self.status == None:
                item = InvoiceTreeWidgetItem(idNum[0], self.dbCursor, parent)
                self.addTopLevelItem(item)
                
    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            try:
                item = self.topLevelItem(idx)
                item.refreshData(self.dbCursor)

                balance = float(item.text(6).replace(",", ""))
                if self.status == constants.INV_OPEN_STATUS and balance == 0.0:
                    self.moveItem.emit(idx,
                                       constants.INV_OPEN_STATUS,
                                       constants.INV_PAID_STATUS)
                elif self.status == constants.INV_PAID_STATUS and balance != 0.0:
                    self.moveItem.emit(idx,
                                       constants.INV_PAID_STATUS,
                                       constants.INV_OPEN_STATUS)
            except:
                pass

class InvoiceWidget(ObjectWidget):
    updateVendorTree = pyqtSignal()
    updateProjectTree = pyqtSignal()
    updateAssetTree = pyqtSignal()
    updateCompanyTree = pyqtSignal()
    postToGL = pyqtSignal(int, object, str, str, list)
    updateGLPost = pyqtSignal(object, int, object, str, list)
    updateGLDet = pyqtSignal(object, float, str, object)
    deleteGLPost = pyqtSignal(object)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()
        
        # Piece together the invoices layout
        self.openInvoicesTreeWidget = InvoiceTreeWidget(self.dbCur, constants.INV_OPEN_STATUS, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
        self.openInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openInvoicesTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)

        self.paidInvoicesTreeWidget = InvoiceTreeWidget(self.dbCur, constants.INV_PAID_STATUS, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
        self.paidInvoicesTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        self.paidInvoicesTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)
        
        self.openInvoicesLabel = QLabel()
        self.paidInvoicesLabel = QLabel()
        
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
        
        mainLayout.addWidget(self.openInvoicesLabel, 0, 0)
        mainLayout.addWidget(self.openInvoicesTreeWidget, 1, 0)
        mainLayout.addWidget(self.paidInvoicesLabel, 2, 0)
        mainLayout.addWidget(self.paidInvoicesTreeWidget, 3, 0)
        mainLayout.addWidget(buttonWidget, 1, 1, 3, 1)
        
        self.setLayout(mainLayout)
        self.updateInvoicesCount()

    def refreshOpenInvoiceTree(self):
        self.openInvoicesTreeWidget.refreshData()

    def refreshPaidInvoicesTreeWidget(self):
        self.paidInvoicesTreeWidget.refreshData()
    
    def payInvoice(self):
        idxToShow = self.openInvoicesTreeWidget.indexFromItem(self.openInvoicesTreeWidget.currentItem())
        item = self.openInvoicesTreeWidget.itemFromIndex(idxToShow)
        
        if item:
            dialog = InvoicePaymentDialog("New", self.dbCur, self, item.invoice)
            if dialog.exec_():
                nextId = self.nextIdNum("InvoicesPayments")
                paymentTypeId = self.stripAllButNumbers(dialog.paymentTypeBox.currentText())
                datePd = dialog.datePaidText.text()
                amtPd = float(dialog.amountText.text())
                
                # Add to database and to data structure
                columns = ("DatePaid", "AmountPaid", "InvoiceId",
                           "PaymentTypeId")
                values = (datePd, amtPd, item.invoice, paymentTypeId)
                self.insertIntoDatabase("InvoicesPayments", columns, values)
                self.dbConn.commit()
                
                # Create GL posting for this payment
                self.dbCur.execute("""SELECT Invoices.CompanyId, Invoices.VendorId,
                                             Vendors.GLAccount, PaymentTypes.GLAccount
                                      FROM Invoices
                                      JOIN Vendors
                                      ON Invoices.VendorId = Vendors.idNum
                                      JOIN InvoicesPayments
                                      ON Invoices.idNum = InvoicesPayments.InvoiceID
                                      JOIN PaymentTypes
                                      ON PaymentTypes.idNum = InvoicesPayments.PaymentTypeId
                                      WHERE Invoices.idNum=? AND InvoicesPayments.idNum=?""",
                                   (item.invoice, nextId))
                companyId, vendorId, vendGLAcct, pymtGLAccount = self.dbCur.fetchone()
                reference = ".".join(["InvoicesPayments", str(nextId)])
                
                description = constants.GL_POST_PYMT_DESC % (item.invoice, vendorId, str(datePd))
                details = [(amtPd, "CR", pymtGLAccount),
                           (amtPd, "DR", vendGLAcct)]
                self.postToGL.emit(companyId, datePd, description,
                                   reference, details)
                
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
        dialog = PaymentTypeDialog(self.dbCur, self)
        dialog.exec_()

    def createCostHistory(self, invDate, invoiceId, cost, assetId):
        reference = ".".join(["Invoices", str(invoiceId)])
        
        columns = ("Cost", "Date", "AssetId", "Reference")
        values = (cost, invDate, assetId, reference)
        self.insertIntoDatabase("AssetCosts", columns, values)

    def createAssetHistory(self, invDate, invoiceId, cost, assetId):
        reference = ".".join(["Invoices", str(invoiceId)])
        
        columns = ("Date", "Description", "Dollars", "PosNeg",
                   "AssetId", "Reference")
        values = (invDate, constants.ASSET_HIST_INV % invoiceId, cost,
                  constants.POSITIVE, assetId, reference)
        self.insertIntoDatabase("AssetHistory", columns, values)
                
    def showNewInvoiceDialog(self):
        dialog = InvoiceDialog("New", self.dbCur, self)
        if dialog.exec_():
            nextId = self.nextIdNum("Invoices")
            invoiceCost = 0.0
            
            # Create new invoice
            invoiceDate = dialog.invoiceDateText.text()
            dueDate = dialog.dueDateText.text()
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            
            # Create invoice detail items
            for row, detTuple in dialog.detailsWidget.details.items():
                detId, detLine, costLine, propBox, rowToUse = detTuple
                
                if costLine.text() == "":
                    invoiceDetail = None
                else:
                    invoiceDetail = 1
                    proposalDetId = self.stripAllButNumbers(propBox.currentText())
                
                # Last item in the dialog is a blank line, so a blank invoice
                # detail will be created.  Ignore it.
                if invoiceDetail:
                    cost = float(costLine.text())
                    invoiceCost += cost
                    columns = ("InvoiceId", "Description", "Cost",
                               "ProposalDetId")
                    values = (nextId,
                              detLine.text(),
                              cost,
                              proposalDetId)
                    self.insertIntoDatabase("InvoicesDetails", columns, values)
            
            # Add invoice<->project/asset links
            type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
            
            if dialog.assetProjSelector.assetSelected() == True:
                type_ = "assets"
                
                # Create new cost element for asset
                self.createCostHistory(invoiceDate,
                                       nextId,
                                       invoiceCost,
                                       type_Id)
                
                # Create history entry for asset
                self.createAssetHistory(invoiceDate,
                                        nextId,
                                        invoiceCost,
                                        type_Id)
            else:
                type_ = "projects"
            
            # Add the invoice to the corporate data structure and update the
            # invoice and the link information to the database
            columns = ("InvoiceDate", "DueDate", "CompanyId", "VendorId")
            values = (invoiceDate, dueDate, companyId, vendorId)
            self.insertIntoDatabase("Invoices", columns, values)
            
            columns = ("InvoiceId", "ObjectType", "ObjectId")
            values = (nextId, type_, type_Id)
            self.insertIntoDatabase("InvoicesObjects", columns, values)
            
            self.dbConn.commit()
            
            # Make invoice into an InvoiceTreeWidgetItem and add it to VendorTree
            item = InvoiceTreeWidgetItem(nextId,
                                         self.dbCur,
                                         self.openInvoicesTreeWidget)
            self.openInvoicesTreeWidget.addTopLevelItem(item)
            self.updateInvoicesCount()
            
            # Create GL posting
            self.dbCur.execute("SELECT GLAccount FROM Vendors WHERE idNum=?",
                               (vendorId,))
            vendorGLAccount = self.dbCur.fetchone()[0]
            description = constants.GL_POST_INV_DESC % (nextId, vendorId, invoiceDate)
            reference = ".".join(["Invoices", str(nextId)])
            if type_ == "projects":
                self.dbCur.execute("""SELECT GLAccount FROM Projects
                                    WHERE idNum=?""", (type_Id,))
            else:
                self.dbCur.execute("""SELECT AssetTypes.AssetGL
                                      FROM Assets
                                      LEFT JOIN AssetTypes
                                      ON Assets.AssetTypeId = AssetTypes.idNum
                                      WHERE Assets.idNum=?""", (type_Id,))
            glAcct = self.dbCur.fetchone()[0]
            details = [(invoiceCost, "CR", vendorGLAccount),
                       (invoiceCost, "DR", glAcct)]
            self.postToGL.emit(companyId, invoiceDate, description, reference, details)
            
            # Update vendor tree widget to display new information based on
            # invoice just created
            self.updateVendorTree.emit()
            self.updateProjectTree.emit()
##            self.updateAssetTree.emit()
            self.updateCompanyTree.emit()
            
    def showViewInvoiceDialog(self):
        needToUpdateGL = False
        
        # Determine which invoice tree (if any) has been selected
        item = self.openInvoicesTreeWidget.currentItem()
        if not item:
            item = self.paidInvoicesTreeWidget.currentItem()

        # Only show dialog if an item has been selected
        if item:
            dialog = InvoiceDialog("View", self.dbCur, self, item.invoice)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    invDate = dialog.invoiceDateText_edit.text()
                    dueDate = dialog.dueDateText_edit.text()
                    companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                    vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())

                    colValDict = {"InvoiceDate": invDate,
                                  "DueDate": dueDate,
                                  "CompanyId": companyId,
                                  "VendorId": vendorId}
                    whereDict = {"idNum": item.invoice}
                    self.updateDatabase("Invoices", colValDict, whereDict)
                    
                    self.dbCur.execute("""SELECT idNum FROM InvoicesDetails
                                          WHERE InvoiceId=?""", (item.invoice,))
                    listOfDetailsInDB = self.dbCur.fetchall()
                    listOfDetailsInWidget = []
                    for row in dialog.detailsWidget.details.keys():
                        detailId = dialog.detailsWidget.details[row][0]
                        listOfDetailsInWidget.append(detailId)
                    for detail in listOfDetailsInDB:
                        if detail[0] not in listOfDetailsInWidget:
                            whereDict = {"idNum": detail[0],
                                         "InvoiceId": item.invoice}
                            self.deleteFromDatabase("InvoicesDetails",
                                                    whereDict)

                    # If the details of the proposal have changed, update as
                    # well. If dialog.detailsWidget.details[key][0] > 0 then
                    # that means we changed a currently existing detail.  If
                    # it equals 0, this is a newly added detail and so it must
                    # be created and added to database.
                    for row, detTuple in dialog.detailsWidget.details.items():
                        detId, detLine, costLine, propBox, rowToUse = detTuple
                        propDetId = self.stripAllButNumbers(propBox.currentText())
                        if dialog.detailsWidget.details[row][0] > 0:
                            colValDict = {"Description": detLine.text(),
                                          "Cost": costLine.text(),
                                          "ProposalDetId": propDetId}
                            whereDict = {"idNum": detId}
                            self.updateDatabase("InvoicesDetails",
                                                colValDict,
                                                whereDict)
                        else:
                            # Make sure description is not blank - if so, this
                            # is the usual blank line at the end of the widget
                            if detLine.text() != "":
                                columns = ("InvoiceId", "Description", "Cost",
                                           "ProposalDetId")
                                values = (item.invoice, detLine.text(),
                                          costLine.text(), propDetId)
                                self.insertIntoDatabase("InvoicesDetails",
                                                        columns,
                                                        values)
                    
                    # Make any changes to which object the invoice is allocated
                    # to.  If an asset, cascade this change down through the
                    # asset info.
                    newTypeId = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
                    if dialog.assetProjSelector.assetSelected() == True:
                        newType = "assets"

                        self.dbCur.execute("""SELECT AssetGL FROM AssetTypes
                                              JOIN Assets
                                              ON Assets.AssetTypeId = AssetTypes.idNum
                                              WHERE Assets.idNum=?""",
                                           (newTypeId,))
                    else:
                        newType = "projects"

                        self.dbCur.execute("""SELECT GLAccount FROM Projects
                                              WHERE idNum=?""", (newTypeId,))
                    newDebitGLAcct = self.dbCur.fetchone()[0]
                        
                    self.dbCur.execute("""SELECT ObjectType, ObjectId
                                          FROM InvoicesObjects
                                          WHERE InvoiceId=?""", (item.invoice,))
                    oldType, oldTypeId = self.dbCur.fetchone()
                    self.dbCur.execute("""SELECT Sum(Cost) FROM InvoicesDetails
                                          WHERE InvoiceId=?""", (item.invoice,))
                    cost = self.dbCur.fetchone()[0]
                    reference = ".".join(["Invoices", str(item.invoice)])
                    
                    if oldType != newType:
                        if newType == "assets":
                            self.createCostHistory(invDate,
                                                   item.invoice,
                                                   cost,
                                                   newTypeId)
                            self.createAssetHistory(invDate,
                                                    item.invoice,
                                                    cost,
                                                    newTypeId)
                        else:
                            whereDict = {"Reference": reference}
                            self.deleteFromDatabase("AssetCosts", whereDict)
                            self.deleteFromDatabase("AssetHistory", whereDict)
                    else:
                        if newType == "assets":
                            colValDict = {"Cost": cost,
                                          "Date": invDate,
                                          "AssetId": newTypeId}
                            whereDict = {"Reference": reference}
                            self.updateDatabase("AssetCosts",
                                                colValDict,
                                                whereDict)

                            colValDict = {"Date": invDate,
                                          "Dollars": cost,
                                          "AssetId": newTypeId}
                            self.updateDatabase("AssetHistory",
                                                colValDict,
                                                whereDict)
                            
                    colValDict = {"ObjectType": newType,
                                  "ObjectId": newTypeId}
                    whereDict = {"InvoiceId": item.invoice}
                    self.updateDatabase("InvoicesObjects",
                                        colValDict,
                                        whereDict)

                    # Update GL Posting
                    self.dbCur.execute("""SELECT GLAccount FROM Vendors
                                          WHERE idNum=?""", (vendorId,))
                    vendGLAcct = self.dbCur.fetchone()[0]
                    
                    colValDict = {"Date": invDate, "CompanyId": companyId}
                    whereDict = {"Reference": reference}
                    self.updateDatabase("GLPostings", colValDict, whereDict)

                    self.dbCur.execute("""SELECT GLPostingsDetails.idNum,
                                                 DebitCredit
                                          FROM GLPostingsDetails JOIN GLPostings
                                          ON GLPostings.idNum = GLPostingsDetails.GLPostingId
                                          WHERE Reference=?""", (reference,))
                    glPostDetIds = self.dbCur.fetchall()
                    for glPostDetId, drCr in glPostDetIds:
                        whereDict = {"idNum": glPostDetId}
                        if drCr == constants.DEBIT:
                            colValDict = {"GLAccount": newDebitGLAcct,
                                          "Amount": cost}
                        else:
                            colValDict = {"GLAccount": vendGLAcct,
                                          "Amount": cost}
                        self.updateDatabase("GLPostingsDetails",
                                            colValDict,
                                            whereDict)

                    self.dbConn.commit()

                    self.openInvoicesTreeWidget.refreshData()
                    self.paidInvoicesTreeWidget.refreshData()

                    self.updateVendorTree.emit()
                    self.updateProjectTree.emit()
##                    self.updateAssetTree.emit()
                    self.updateCompanyTree.emit()
                    
    def deleteSelectedInvoiceFromList(self):
        # Check to see if the item to delete is in the open invoices tree widget
        item = self.openInvoicesTreeWidget.currentItem()

        if not item:
            # Selected item not in open invoices tree widget--delete from paid
            # invoices tree widget
            item = self.paidInvoicesTreeWidget.currentItem()
            treeWidget = self.paidInvoicesTreeWidget
        else:
            treeWidget = self.openInvoicesTreeWidget

        if item:
            reference = ".".join(["Invoices", str(item.invoice)])
            self.dbCur.execute("SELECT idNum FROM GLPostings WHERE Reference=?",
                               (reference,))
            glPostingId = self.dbCur.fetchone()[0]

            # Delete asset and gl posting information of invoice
            whereDict = {"Reference": reference}
            self.deleteFromDatabase("AssetCosts", whereDict)
            self.deleteFromDatabase("AssetHistory", whereDict)
            self.deleteFromDatabase("GLPostings", whereDict)

            whereDict = {"GLPostingId": glPostingId}
            self.deleteFromDatabase("GLPostingsDetails", whereDict)

            # Delete invoice, invoice payments, gl postings of those payments,
            # and gl details of those postings
            self.dbCur.execute("""SELECT idNum FROM InvoicesPayments
                                  WHERE InvoiceId=?""",
                               (item.invoice,))
            payments = self.dbCur.fetchall()
            for payment in payments:
                reference = ".".join(["InvoicesPayments", str(payment[0])])
                self.dbCur.execute("""SELECT idNum FROM GLPostings
                                      WHERE Reference=?""",
                                   (reference,))
                postings = self.dbCur.fetchall()
                for posting in postings:
                    whereDict = {"GLPostingId": posting[0]}
                    self.deleteFromDatabase("GLPostingsDetails", whereDict)
                whereDict = {"Reference", reference}
                self.deleteFromDatabase("GLPostings", whereDict)

            whereDict = {"idNum": item.invoice}
            self.deleteFromDatabase("Invoices", whereDict)

            whereDict = {"InvoiceId": item.invoice}
            self.deleteFromDatabase("InvoicesPayments", whereDict)
            self.deleteFromDatabase("InvoicesDetails", whereDict)
            self.deleteFromDatabase("InvoicesObjects", whereDict)

            # Delete item from invoices tree widget
            idxToDelete = treeWidget.indexOfTopLevelItem(item)
            treeWidget.takeTopLevelItem(idxToDelete)
            
            self.dbConn.commit()
            self.updateInvoicesCount()
            
            self.updateVendorTree.emit()
            self.updateProjectTree.emit()
##            self.updateAssetTree.emit()
            self.updateCompanyTree.emit()

    def updateInvoicesCount(self):
        self.openInvoicesLabel.setText("Open Invoices: %d" % self.openInvoicesTreeWidget.topLevelItemCount())
        self.paidInvoicesLabel.setText("Paid Invoices: %d" % self.paidInvoicesTreeWidget.topLevelItemCount())

    def moveFromTreeXToTreeY(self, fromIdx, fromTree, toTree):
        list_ = [fromTree, toTree]
        for n in range(len(list_)):
            if list_[n] == constants.INV_OPEN_STATUS:
                list_[n] = self.openInvoicesTreeWidget
            elif list_[n] == constants.INV_PAID_STATUS:
                list_[n] = self.paidInvoicesTreeWidget
        
        item = list_[0].takeTopLevelItem(fromIdx)
        newItem = InvoiceTreeWidgetItem(item.invoice, self.dbCur, list_[1])
        list_[1].addTopLevelItem(newItem)

class APView(ObjectWidget):
    updateProjectTree = pyqtSignal()
    updateAssetTree = pyqtSignal()
    updateCompanyTree = pyqtSignal()
    updateGLTree = pyqtSignal()
    
    def __init__(self, parent, dbConnection, dbCursor):
        super().__init__(parent, dbConnection, dbCursor)
        layout = QVBoxLayout()
        
        self.vendorWidget = VendorWidget(self, dbConnection, dbCursor)
        self.invoiceWidget = InvoiceWidget(self, dbConnection, dbCursor)
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
                                     (str(postingDate), description, glPost.idNum))
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

    def postToGL(self, companyNum, date, description, reference, listOfDetails):
        glPostingIdNum = self.nextIdNum("GLPostings")
        glPostingDetailIdNum = self.nextIdNum("GLPostingsDetails")
        
        glPosting = GLPosting(date, description, companyNum, glPostingIdNum)
        
        columns = ("Date", "Description", "CompanyId", "Reference")
        values = (str(date), description, companyNum, reference)
        self.insertIntoDatabase("GLPostings", columns, values)

        columnValDict = {"GLPostingId": glPostingIdNum}
        whereDict = {"idNum": reference.split(".")[1]}
        self.updateDatabase(reference.split(".")[0], columnValDict, whereDict)
        
        for amount, drCr, glAcct in listOfDetails:
            glPostingDetail = GLPostingDetail(amount, drCr, glAcct, glPostingIdNum, glPostingDetailIdNum)

            columns = ("GLPostingId", "GLAccount", "Amount", "DebitCredit")
            values = (glPostingIdNum, glAcct, amount, drCr)
            self.insertIntoDatabase("GLPostingsDetails", columns, values)
            
            self.parent.dbConnection.commit()

            glPostingDetailIdNum += 1
        self.updateGLTree.emit()
            
class ProposalTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, proposalId, dbCur, parent):
        super().__init__(parent)
        self.proposal = proposalId
        self.refreshData(dbCur)
        
    def refreshData(self, dbCur):
        dbCur.execute("""SELECT ProposalDate, Status, ObjectType, ObjectId, Name
                         FROM Proposals LEFT JOIN ProposalsObjects
                         ON Proposals.idNum = ProposalsObjects.ProposalId
                         LEFT JOIN Vendors
                         ON Proposals.VendorId = Vendors.idNum
                         WHERE Proposals.idNum=?""", (self.proposal,))
        propDate, status, objectType, objectId, vendName = dbCur.fetchone()
        self.status = status
        
        if objectType == "projects":
            dbCur.execute("SELECT Description FROM Projects WHERE idNum=?",
                          (objectId,))
        else:
            dbCur.execute("SELECT Description FROM Assets WHERE idNum=?",
                          (objectId,))
        desc = dbCur.fetchone()[0]
        proposalCost = functions.CalculateProposalCost(dbCur, self.proposal)
        
        self.setText(0, str(self.proposal))
        self.setText(1, vendName)
        self.setText(2, propDate)
        self.setText(3, desc)
        self.setText(4, "{:,.2f}".format(proposalCost))
        
class ProposalTreeWidget(NewTreeWidget):
    moveItem = pyqtSignal(int, str, str)
    
    def __init__(self, dbCur, status, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.status = status
        self.buildItems(self)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)
        
    def buildItems(self, parent):
        self.dbCursor.execute("SELECT idNum FROM Proposals WHERE Status=?",
                              (self.status,))
        results = self.dbCursor.fetchall()
        for idNum in results:
            item = ProposalTreeWidgetItem(idNum[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            # Need to use a try...except... method because if an item gets
            # moved from one location to another during this refresh, idx
            # will get an out of bounds error if any object other than the last
            # item in the list had its status changed (and hence was moved)
            try:
                item = self.topLevelItem(idx)
                item.refreshData(self.dbCursor)
                
                if item.status != self.status:
                    self.moveItem.emit(idx, self.status, item.status)
            except:
                pass
    
class ProposalWidget(ObjectWidget):
    updateVendorWidgetTree = pyqtSignal()
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()
        
        # Piece together the proposals layout
        self.openProposalsLabel = QLabel()
        self.rejectedProposalsLabel = QLabel()
        self.acceptedProposalsLabel = QLabel()
        
        self.openProposalsTreeWidget = ProposalTreeWidget(dbCur, constants.OPN_PROPOSAL_STATUS, constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
        self.openProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openProposalsTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)

        self.rejectedProposalsTreeWidget = ProposalTreeWidget(dbCur, constants.REJ_PROPOSAL_STATUS, constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
        self.rejectedProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        self.rejectedProposalsTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)
        
        self.acceptedProposalsTreeWidget = ProposalTreeWidget(dbCur, constants.ACC_PROPOSAL_STATUS, constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
        self.acceptedProposalsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(3))
        self.acceptedProposalsTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)
        
        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewProposalDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewProposalDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedProposalFromList)
        buttonWidget.addSpacer()
        
        acceptProposalButton = QPushButton("Accept...")
        acceptProposalButton.clicked.connect(lambda: self.changeProposalStatus(constants.ACC_PROPOSAL_STATUS))
        rejectProposalButton = QPushButton("Reject...")
        rejectProposalButton.clicked.connect(lambda: self.changeProposalStatus(constants.REJ_PROPOSAL_STATUS))
        buttonWidget.addButton(acceptProposalButton)
        buttonWidget.addButton(rejectProposalButton)
        
        mainLayout.addWidget(self.openProposalsLabel, 0, 0)
        mainLayout.addWidget(self.openProposalsTreeWidget, 1, 0)
        mainLayout.addWidget(self.rejectedProposalsLabel, 2, 0)
        mainLayout.addWidget(self.rejectedProposalsTreeWidget, 3, 0)
        mainLayout.addWidget(self.acceptedProposalsLabel, 4, 0)
        mainLayout.addWidget(self.acceptedProposalsTreeWidget, 5, 0)
        mainLayout.addWidget(buttonWidget, 1, 1, 5, 1)
        
        self.setLayout(mainLayout)
        self.updateProposalsCount()

    def changeProposalStatus(self, status):
        item = self.openProposalsTreeWidget.currentItem()
        
        if item:
            dialog = ChangeProposalStatusDialog(status, self)
            if dialog.exec_():
                colValDict = {"Status": status,
                              "StatusReason": dialog.statusTxt.text()}
                whereDict = {"idNum": item.proposal}
                self.updateDatabase("Proposals", colValDict, whereDict)
            self.dbConn.commit()
                
        self.openProposalsTreeWidget.refreshData()
        self.updateProposalsCount()
        self.updateVendorWidgetTree.emit()

    def moveFromTreeXToTreeY(self, fromIdx, fromTree, toTree):
        list_ = [fromTree, toTree]
        for n in range(len(list_)):
            if list_[n] == constants.OPN_PROPOSAL_STATUS:
                list_[n] = self.openProposalsTreeWidget
            elif list_[n] == constants.REJ_PROPOSAL_STATUS:
                list_[n] = self.rejectedProposalsTreeWidget
            elif list_[n] == constants.ACC_PROPOSAL_STATUS:
                list_[n] = self.acceptedProposalsTreeWidget
        
        item = list_[0].takeTopLevelItem(fromIdx)
        newItem = ProposalTreeWidgetItem(item.proposal, self.dbCur, list_[1])
        list_[1].addTopLevelItem(newItem)

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
    
    def showNewProposalDialog(self):
        dialog = ProposalDialog("New", self.dbCur, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Proposals")
            
            # Create proposal and add to database
            date = dialog.dateText.text()
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
            
            # Add proposal<->project/asset links
            type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
            if dialog.assetProjSelector.assetSelected() == True:
                type_ = "assets"
            else:
                type_ = "projects"
            
            # Add to database
            columns = ("ProposalDate", "Status", "CompanyId", "VendorId")
            values = (date, constants.OPN_PROPOSAL_STATUS, companyId,
                      vendorId)
            self.insertIntoDatabase("Proposals", columns, values)
            
            columns = ("ProposalId", "ObjectType", "ObjectId")
            values = (nextId, type_, type_Id)
            self.insertIntoDatabase("ProposalsObjects", columns, values)
            
            # Create proposal details and add to database
            nextProposalDetId = self.nextIdNum("ProposalsDetails")
            columns = ("ProposalId", "Description", "Cost")
            
            for row, detTuple in dialog.detailsWidget.details.items():
                detIdNum, detLine, costLine = detTuple
                if costLine.text() == "":
                    proposalDetail = None
                else:
                    proposalDetail = 1

                # Last item in the dialog is a blank line, so a blank proposal
                # detail will be created.  Ignore it.
                if proposalDetail:
                    values = (nextId, detLine.text(), costLine.text())
                    self.insertIntoDatabase("ProposalsDetails", columns, values)
            
            self.dbConn.commit()

            # Make proposal into a ProposalTreeWidgetItem and add it to ProposalTree
            item = ProposalTreeWidgetItem(nextId, self.dbCur, self.openProposalsTreeWidget)
            self.openProposalsTreeWidget.addTopLevelItem(item)
            self.updateProposalsCount()
            self.updateVendorWidgetTree.emit()
            
    def showViewProposalDialog(self):
        # Determine which tree the proposal is in--if any.  If none, don't
        # display dialog
        item = self.openProposalsTreeWidget.currentItem()
        
        if not item:
            item = self.rejectedProposalsTreeWidget.currentItem()

            if not item:
                item = self.acceptedProposalsTreeWidget.currentItem()
                treeWidget = self.acceptedProposalsTreeWidget
            else:
                treeWidget = self.rejectedProposalsTreeWidget
        else:
            treeWidget = self.openProposalsTreeWidget
            
        if item:
            dialog = ProposalDialog("View", self.dbCur, self, item.proposal)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database
                    companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                    vendorId = self.stripAllButNumbers(dialog.vendorBox.currentText())
                    type_Id = self.stripAllButNumbers(dialog.assetProjSelector.selector.currentText())
                    if dialog.assetProjSelector.assetSelected() == True:
                        type_ = "assets"
                    else:
                        type_ = "projects"
                    colValDict = {"ProposalDate": dialog.dateText_edit.text(),
                                  "Status": dialog.statusBox.currentText(),
                                  "CompanyId": companyId,
                                  "VendorId": vendorId}
                    whereDict = {"idNum": item.proposal}
                    self.updateDatabase("Proposals", colValDict, whereDict)

                    colValDict = {"ObjectType": type_,
                                  "ObjectId": type_Id}
                    whereDict = {"ProposalId": item.proposal}
                    self.updateDatabase("ProposalsObjects",
                                        colValDict,
                                        whereDict)
                    
                    # Get list of current details in DB and compare to list
                    # in detailsWidget.  If an item is the the DB list but
                    # not the widget list it must be deleted from the DB
                    self.dbCur.execute("""SELECT idNum FROM ProposalsDetails
                                          WHERE ProposalId=?""", (item.proposal,))
                    listOfDetailsInDB = self.dbCur.fetchall()
                    listOfDetailsInWidget = []
                    for row in dialog.detailsWidget.details.keys():
                        detailId = dialog.detailsWidget.details[row][0]
                        listOfDetailsInWidget.append(detailId)
                    for detail in listOfDetailsInDB:
                        if detail[0] not in listOfDetailsInWidget:
                            whereDict = {"idNum": detail[0],
                                         "ProposalId": item.proposal}
                            self.deleteFromDatabase("ProposalsDetails",
                                                    whereDict)
                        
                    # If the details of the proposal have changed, update as
                    # well. If dialog.detailsWidget.details[key][0] > 0 then
                    # that means we changed a currently existing detail.  If
                    # it equals 0, this is a newly added detail and so it must
                    # be created and added to database.
                    for row, detTuple in dialog.detailsWidget.details.items():
                        detId, detLine, costLine = detTuple
                        if dialog.detailsWidget.details[row][0] > 0:
                            colValDict = {"Description": detLine.text(),
                                          "Cost": costLine.text()}
                            whereDict = {"idNum": detId}
                            self.updateDatabase("ProposalsDetails",
                                                colValDict,
                                                whereDict)
                        else:
                            # Make sure description is not blank - if so, this
                            # is the usual blank line at the end of the widget
                            if detLine.text() != "":
                                columns = ("ProposalId", "Description", "Cost")
                                values = (item.proposal, detLine.text(),
                                          costLine.text())
                                self.insertIntoDatabase("ProposalsDetails",
                                                        columns,
                                                        values)
                    
                    self.dbConn.commit()

                    self.openProposalsTreeWidget.refreshData()
                    self.rejectedProposalsTreeWidget.refreshData()
                    self.acceptedProposalsTreeWidget.refreshData()
                    self.updateVendorWidgetTree.emit()
                
    def deleteSelectedProposalFromList(self):
        # Check to see if the item to delete is in the open proposal tree widget
        item = self.openProposalsTreeWidget.currentItem()
        
        if not item:
            item = self.rejectedProposalsTreeWidget.currentItem()
            
            if not item:
                item = self.acceptedProposalsTreeWidget.currentItem()
                treeWidget = self.acceptedProposalsTreeWidget
            else:
                treeWidget = self.rejectedProposalsTreeWidget
        else:
            treeWidget = self.openProposalsTreeWidget
            
        if item:
            whereDict = {"idNum": item.proposal}
            self.deleteFromDatabase("Proposals", whereDict)
            
            whereDict = {"ProposalId": item.proposal}
            self.deleteFromDatabase("ProposalsDetails", whereDict)
            self.deleteFromDatabase("ProposalsObjects", whereDict)
            
            self.dbConn.commit()

            idxToDelete = treeWidget.indexOfTopLevelItem(item)
            treeWidget.takeTopLevelItem(idxToDelete)
            
            self.updateProposalsCount()
            self.updateVendorWidgetTree.emit()
    
    def updateProposalsCount(self):
        self.openProposalsLabel.setText("Open: %d" % self.openProposalsTreeWidget.topLevelItemCount())
        self.rejectedProposalsLabel.setText("Rejected: %d" % self.rejectedProposalsTreeWidget.topLevelItemCount())
        self.acceptedProposalsLabel.setText("Accepted: %d" % self.acceptedProposalsTreeWidget.topLevelItemCount())
    
class ProposalView(QWidget):
    updateVendorWidgetTree = pyqtSignal()
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent)
        self.parent = parent

        self.proposalWidget = ProposalWidget(self, dbConn, dbCur)
        self.proposalWidget.updateVendorWidgetTree.connect(self.emitVendorWidgetUpdate)
        layout = QVBoxLayout()
        layout.addWidget(self.proposalWidget)
        
        self.setLayout(layout)

    def emitVendorWidgetUpdate(self):
        self.updateVendorWidgetTree.emit()

class ProjectTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, projectId, dbCur, parent):
        super().__init__(parent)
        self.project = projectId
        self.refreshData(dbCur)

    def refreshData(self, dbCur):
        dbCur.execute("""SELECT Description, DateStart, DateEnd FROM Projects
                         WHERE idNum=?""", (self.project,))
        desc, dateStart, dateEnd = dbCur.fetchone()

        cip = functions.CalculateCIP(dbCur, self.project)
        
        self.setText(0, str(self.project))
        self.setText(1, desc)
        self.setText(2, dateStart)
        self.setText(3, dateEnd)
        self.setText(4, "<Duration>")
        self.setText(5, "{:,.2f}".format(cip))
        
class ProjectTreeWidget(NewTreeWidget):
    moveItem = pyqtSignal(int, str, str)
    
    def __init__(self, dbCur, status, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.status = status
        self.buildItems(self)
        self.setColumnCount(6)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent):
        self.dbCursor.execute("SELECT idNum FROM Projects WHERE Status=?",
                              (self.status,))
        results = self.dbCursor.fetchall()
        for idNum in results:
            item = ProjectTreeWidgetItem(idNum[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            try:
                item = self.topLevelItem(idx)
                item.refreshData(self.dbCursor)
                
                if item.status != self.status:
                    self.moveItem.emit(idx, self.status, item.status)
            except:
                pass

class ProjectWidget(ObjectWidget):
    addAssetToAssetView = pyqtSignal(int)
    postToGL = pyqtSignal(int, object, str, str, list)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()

        # Piece together the projects layout
        self.openProjectsLabel = QLabel()
        self.abandonedProjectsLabel = QLabel()
        self.completedProjectsLabel = QLabel()

        self.openProjectsTreeWidget = ProjectTreeWidget(dbCur, constants.OPN_PROJECT_STATUS, constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.openProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))
        self.openProjectsTreeWidget.moveItem.connect(self.moveFromTreeXToTreeY)
        
        self.abandonedProjectsTreeWidget = ProjectTreeWidget(dbCur, constants.ABD_PROJECT_STATUS, constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.abandonedProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        
        self.completedProjectsTreeWidget = ProjectTreeWidget(dbCur, constants.CMP_PROJECT_STATUS, constants.PROJECT_HDR_LIST, constants.PROJECT_HDR_WDTH)
        self.completedProjectsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(3))

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

        mainLayout.addWidget(self.openProjectsLabel, 0, 0)
        mainLayout.addWidget(self.openProjectsTreeWidget, 1, 0)
        mainLayout.addWidget(self.abandonedProjectsLabel, 2, 0)
        mainLayout.addWidget(self.abandonedProjectsTreeWidget, 3, 0)
        mainLayout.addWidget(self.completedProjectsLabel, 4, 0)
        mainLayout.addWidget(self.completedProjectsTreeWidget, 5, 0)
        mainLayout.addWidget(buttonWidget, 1, 1, 5, 1)
        
        self.setLayout(mainLayout)
        self.updateProjectsCount()

    def moveFromTreeXToTreeY(self, fromIdx, fromTree, toTree):
        list_ = [fromTree, toTree]
        for n in range(len(list_)):
            if list_[n] == constants.OPN_PROJECT_STATUS:
                list_[n] = self.openProjectsTreeWidget
            elif list_[n] == constants.ABD_PROJECT_STATUS:
                list_[n] = self.abandonedProjectsTreeWidget
            elif list_[n] == constants.CMP_PROJECT_STATUS:
                list_[n] = self.completedProjectsTreeWidget
        
        item = list_[0].takeTopLevelItem(fromIdx)
        newItem = ProjectTreeWidgetItem(item.project, self.dbCur, list_[1])
        list_[1].addTopLevelItem(newItem)

    def completeProject(self):
        item = self.openProjectsTreeWidget.currentItem()

        if item:
            preDialog = CIPAllocationDialog(item.project, self.dbCur)
            if preDialog.exec_():
                entryCount = preDialog.details.subLayout.count()
                
                self.dbCur.execute("""SELECT CompanyId, GLAccount
                                      FROM Projects
                                      WHERE idNum=?""", (item.project,))
                companyId, projGLAcct = self.dbCur.fetchone()
                cipAmt = functions.CalculateCIP(self.dbCur, item.project)
                acqDate = preDialog.closeDateTxt.text()
                glDict = {}
                closureItems = []
                
                for n in range(entryCount):
                    widgetItem = preDialog.details.subLayout.itemAt(n).widget()
                    assetName = widgetItem.assetTxt.text()
                    assetCost = round(float(widgetItem.costTxt.text()), 2)
                    expenseFg = widgetItem.expenseChk.checkState()
                    
                    if expenseFg == 0:
                        dialog = CloseProjectDialog(constants.CMP_PROJECT_STATUS, self.dbCur, self, assetName, acqDate)
                        if dialog.exec_():
                            assetId = self.nextIdNum("Assets")
                            costId = self.nextIdNum("AssetCosts")
                            histId = self.nextIdNum("AssetHistory")
                            dateEnd = dialog.dateTxt.text()
                            description = dialog.assetNameTxt.text()
                            assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
                            parentAssetId = self.stripAllButNumbers(dialog.childOfAssetBox.currentText())
                            
                            if dialog.inSvcChk.isChecked() == True:
                                inSvcDate = dateEnd
                            else:
                                inSvcDate = None
                            
                            reference = ".".join(["Projects", str(item.project)])
                            
                            self.dbCur.execute("""SELECT Depreciable, AssetGL
                                                  FROM AssetTypes
                                                  WHERE idNum=?""", (assetTypeId,))
                            depreciable, assetGL = self.dbCur.fetchone()
                            
                            if bool(depreciable) == True:
                                usefulLife = float(dialog.usefulLifeTxt.text())
                                salvageValue = float(dialog.salvageValueText.text())
                                depMethod = dialog.depMethodBox.currentText()
                            else:
                                usefulLife = None
                                salvageValue = None
                                depMethod = None
                            
                            # Add to database
                            colValDict = {"DateEnd": dateEnd,
                                          "Status": constants.CMP_PROJECT_STATUS}
                            whereDict = {"idNum": item.project}
                            self.updateDatabase("Projects", colValDict, whereDict)
                            
                            columns = ("Description", "AcquireDate", "InSvcDate",
                                       "UsefulLife", "SalvageAmount",
                                       "DepreciationMethod", "PartiallyDisposed",
                                       "CompanyId", "AssetTypeId", "ParentAssetId")
                            values = (description, dateEnd, inSvcDate,
                                      usefulLife, salvageValue, depMethod, 0,
                                      companyId, assetTypeId, parentAssetId)
                            self.insertIntoDatabase("Assets", columns, values)
                            
                            columns = ("Date", "Description", "Dollars", "PosNeg",
                                       "AssetId", "Reference")
                            values = (dateEnd,
                                      constants.ASSET_HIST_PROJ_COMP % item.project,
                                      assetCost, constants.POSITIVE, assetId,
                                      reference)
                            self.insertIntoDatabase("AssetHistory", columns, values)
                            
                            columns = ("Cost", "Date", "AssetId", "Reference")
                            values = (assetCost, dateEnd, assetId, reference)
                            self.insertIntoDatabase("AssetCosts", columns, values)
                            
                            self.addAssetToAssetView.emit(assetId)

                            # Add info to GL dict
                            if assetGL in glDict.keys():
                                glDict[assetGL] += assetCost
                            else:
                                glDict[assetGL] = assetCost
                    else:
                        assetGL = widgetItem.expenseDetailWidget.glBox.currentText()
                        assetGL = self.stripAllButNumbers(assetGL)
                        if assetGL in glDict.keys():
                            glDict[assetGL] += assetCost
                        else:
                            glDict[assetGL] = assetCost
                    
                    closureItems.append((assetName, assetGL, assetCost))
                
                # Insert closure items
                columns = ("ProjectId", "Description", "GLAccount", "Cost")
                for assetName, assetGL, assetCost in closureItems:
                    values = (item.project, assetName, assetGL, assetCost)
                    self.insertIntoDatabase("ProjectClosureItems",
                                            columns,
                                            values)
                # Create GL entry
                description = constants.GL_POST_PROJ_COMP % (item.project,)
                details = [(cipAmt, "CR", projGLAcct)]
                for glAcct, amount in glDict.items():
                    details.append((amount, "DR", glAcct))
                self.postToGL.emit(companyId, dateEnd, description,
                                   reference, details)
                
                self.dbConn.commit()
                idxToTake = self.openProjectsTreeWidget.indexOfTopLevelItem(item)
                self.openProjectsTreeWidget.takeTopLevelItem(idxToTake)
                newItem = ProjectTreeWidgetItem(item.project,
                                                self.dbCur,
                                                self.completedProjectsTreeWidget)
                self.completedProjectsTreeWidget.addTopLevelItem(newItem)
                self.refreshOpenProjectTree()
                self.updateProjectsCount()
                
    def abandonProject(self):
        item = self.openProjectsTreeWidget.currentItem()

        if item:
            dialog = CloseProjectDialog(constants.ABD_PROJECT_STATUS,
                                        self.dbCur,
                                        self)

            if dialog.exec_():
                dateEnd = dialog.dateTxt.text()
                notes = dialog.reasonTxt.text()
                expGLAcct = self.stripAllButNumbers(dialog.glBox.currentText())
                cipAmt = functions.CalculateCIP(self.dbCur, item.project)
                reference = ".".join(["Projects", str(item.project)])
                
                self.dbCur.execute("SELECT CompanyId, GLAccount FROM Projects WHERE idNum=?",
                                   (item.project,))
                compId, projectGLAcct = self.dbCur.fetchone()[0]
                
                colValDict = {"DateEnd": dateEnd,
                              "Status": constants.ABD_PROJECT_STATUS,
                              "Notes": notes}
                whereDict = {"idNum": item.project}
                self.updateDatabase("Projects", colValDict, whereDict)

                # Post to GL
                description = constants.GL_POST_PROJ_ABD % (item.project, notes)
                details = [(cipAmt, "CR", projectGLAcct),
                           (cipAmt, "DR", expGLAcct)]
                self.postToGL.emit(compId, dateEnd, description, reference,
                                   details)
                
                self.dbConn.commit()

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

    def showNewProjectDialog(self):
        dialog = ProjectDialog("New", self.dbCur, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Projects")
            date = classes.NewDate(dialog.startDateText.text())
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            glAccountNum = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
            
            # Create project and add to database
            newProject = Project(dialog.descriptionText.text(),
                                 date,
                                 "",
                                 nextId,
                                 "")

            columns = ("Description", "DateStart", "Status", "CompanyId",
                       "GLAccount")
            values = (newProject.description, str(date),
                      constants.OPN_PROJECT_STATUS, companyId, glAccountNum)
            self.insertIntoDatabase("Projects", columns, values)
            
            self.dbConn.commit()
            
            # Make project into a ProjectTreeWidgetItem and add it to ProjectTree
            item = ProjectTreeWidgetItem(nextId, self.dbCur, self.openProjectsTreeWidget)
            self.openProjectsTreeWidget.addTopLevelItem(item)
            self.updateProjectsCount()

    def showViewProjectDialog(self):
        # Determine which tree the project is in--if any.  If none, don't
        # display dialog
        item = self.openProjectsTreeWidget.currentItem()

        if not item:
            item = self.abandonedProjectsTreeWidget.currentItem()

            if not item:
                item = self.completedProjectsTreeWidget.currentItem()
        
        if item:
            dialog = ProjectDialog("View", self.dbCur, self, item.project)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    dateStart = classes.NewDate(dialog.startDateText_edit.text())
                    companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                    glAccount = self.stripAllButNumbers(dialog.glAccountsBox.currentText())
                    if dialog.endDateText.text() == "" or dialog.endDateText.text() == None:
                        dateEnd = None
                        status = constants.OPN_PROJECT_STATUS
                    else:
                        dateEnd = dialog.endDateText.text()
                        status = constants.CMP_PROJECT_STATUS
                    
                    # Commit changes to database and to vendor entry
                    colValDict = {"Description": dialog.descriptionText_edit.text(),
                                  "DateStart": str(dateStart),
                                  "DateEnd": dateEnd,
                                  "Status": status,
                                  "CompanyId": companyId,
                                  "GLAccount": glAccount}
                    whereDict = {"idNum": item.project}
                    self.updateDatabase("Projects", colValDict, whereDict)
                    
                    self.dbConn.commit()
                    self.openProjectsTreeWidget.refreshData()
                    
    def deleteSelectedProjectFromList(self):
        # Check to see if the item to delete is in the open project tree widget
        item = self.openProjectsTreeWidget.currentItem()
        treeWidget = self.openProjectsTreeWidget
        idxToDelete = self.openProjectsTreeWidget.indexOfTopLevelItem(self.openProjectsTreeWidget.currentItem())

        if not item:
            item = self.completedProjectsTreeWidget.currentItem()

            if not item:
                item = self.abandonedProjectsTreeWidget.currentItem()
                treeWidget = self.abandonedProjectsTreeWidget
            else:
                item = None
                deleteError = QMessageBox()
                deleteError.setWindowTitle("Can't Delete")
                deleteError.setText("Cannot delete a closed project")
                deleteError.exec_()
        
        if item:
            whereDict = {"idNum": item.project}
            self.deleteFromDatabase("Projects", whereDict)
            
            self.dbConn.commit()
                
            self.updateProjectsCount()
            
    def updateProjectsCount(self):
        self.openProjectsLabel.setText("%s: %d" % (constants.OPN_PROJECT_STATUS, self.openProjectsTreeWidget.topLevelItemCount()))
        self.abandonedProjectsLabel.setText("%s: %d" % (constants.ABD_PROJECT_STATUS, self.abandonedProjectsTreeWidget.topLevelItemCount()))
        self.completedProjectsLabel.setText("%s: %d" % (constants.CMP_PROJECT_STATUS, self.completedProjectsTreeWidget.topLevelItemCount()))

    def refreshOpenProjectTree(self):
        self.openProjectsTreeWidget.refreshData()
        
class ProjectView(ObjectWidget):
    addAssetToAssetView = pyqtSignal(int)
    updateGLTree = pyqtSignal()
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        self.parent = parent

        self.projectWidget = ProjectWidget(self, dbConn, dbCur)
        self.projectWidget.addAssetToAssetView.connect(self.emitAddAssetToAssetView)
        self.projectWidget.postToGL.connect(self.postToGL)
        layout = QVBoxLayout()
        layout.addWidget(self.projectWidget)

        self.setLayout(layout)

    def postToGL(self, companyId, dateEnd, description, reference, details):
        glPostingIdNum = self.nextIdNum("GLPostings")
        glPostingDetailIdNum = self.nextIdNum("GLPostingsDetails")
        
        columns = ("Date", "Description", "CompanyId", "Reference")
        values = (dateEnd, description, companyId, reference)
        self.insertIntoDatabase("GLPostings", columns, values)
        
        columnValDict = {"GLPostingId": glPostingIdNum}
        whereDict = {"idNum": reference.split(".")[1]}
        self.updateDatabase(reference.split(".")[0], columnValDict, whereDict)
        
        for amount, drCr, glAcct in details:
            columns = ("GLPostingId", "GLAccount", "Amount", "DebitCredit")
            values = (glPostingIdNum, glAcct, amount, drCr)
            self.insertIntoDatabase("GLPostingsDetails", columns, values)
            
            self.dbConn.commit()
            glPostingDetailIdNum += 1
        self.updateGLTree.emit()
        
    def emitAddAssetToAssetView(self, assetId):
        self.addAssetToAssetView.emit(assetId)

class CompanyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, idNum, dbCur, parent):
        super().__init__(parent)
        self.company = idNum
        self.refreshData(dbCur)
        
    def refreshData(self, dbCur):
        dbCur.execute("""SELECT Name, ShortName FROM Companies
                         WHERE idNum=?""", (self.company,))
        name, shortName = dbCur.fetchone()

        cipAmt = 0.0
        dbCur.execute("SELECT idNum FROM Projects WHERE CompanyId=?",
                      (self.company,))
        results = dbCur.fetchall()
        for projectId in results:
            cipAmt += functions.CalculateCIP(dbCur, projectId[0])
        self.setText(0, str(self.company))
        self.setText(1, name)
        self.setText(2, shortName)
##        self.setText(3, "{:,.2f}".format(self.company.assetsAmount()))
        self.setText(4, "{:,.2f}".format(cipAmt))
        
class CompanyTreeWidget(NewTreeWidget):
    def __init__(self, dbCur, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.buildItems(self)
        self.setColumnCount(5)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent):
        self.dbCursor.execute("SELECT idNum FROM Companies")
        results = self.dbCursor.fetchall()
        for idNum in results:
            item = CompanyTreeWidgetItem(idNum[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData(self.dbCursor)
            
class CompanyWidget(ObjectWidget):
    addNewCompany = pyqtSignal(str)
    deleteCompany = pyqtSignal(str)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()
        
        # Piece together the companies layout
        self.companiesLabel = QLabel()
        self.companiesTreeWidget = CompanyTreeWidget(dbCur, constants.COMPANY_HDR_LIST, constants.COMPANY_HDR_WDTH)
        
        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewCompanyDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewCompanyDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteSelectedCompanyFromList)
        
        mainLayout.addWidget(self.companiesLabel, 0, 0)
        mainLayout.addWidget(self.companiesTreeWidget, 1, 0)
        mainLayout.addWidget(buttonWidget, 1, 1)
        mainLayout.setRowStretch(2, 1)
        
        self.setLayout(mainLayout)
        self.updateCompaniesCount()
        
    def updateCompaniesCount(self):
        self.companiesLabel.setText("Companies: %d" % self.companiesTreeWidget.topLevelItemCount())
    
    def refreshCompanyTree(self):
        self.companiesTreeWidget.refreshData()
        
    def showNewCompanyDialog(self):
        dialog = CompanyDialog("New", self.dbCur, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Companies")
            
            # Create company and add to database
            newCompany = Company(dialog.nameText.text(),
                                 dialog.shortNameText.text(),
                                 True,
                                 nextId)

            columns = ("Name", "ShortName", "Active")
            values = (newCompany.name, newCompany.shortName,
                      int(newCompany.active))
            self.insertIntoDatabase("Companies", columns, values)
            
            self.dbConn.commit()
            
            # Make company into a CompanyTreeWidgetItem and add it to CompanyTree
            item = CompanyTreeWidgetItem(nextId, self.dbCur, self.companiesTreeWidget)
            self.companiesTreeWidget.addTopLevelItem(item)
            self.updateCompaniesCount()
            self.addNewCompany.emit(newCompany.shortName)
            
    def showViewCompanyDialog(self):
        # Determine which tree the company is in--if any.  If none, don't
        # display dialog
        idxToShow = self.companiesTreeWidget.indexFromItem(self.companiesTreeWidget.currentItem())
        item = self.companiesTreeWidget.itemFromIndex(idxToShow)

        if item:
            dialog = CompanyDialog("View", self.dbCur, self, item.company)
            
            if dialog.exec_():
                if dialog.hasChanges == True:
                    # Commit changes to database and to vendor entry
                    columnValues = {"Name": dialog.nameText_edit.text(),
                                    "ShortName": dialog.shortNameText_edit.text(),
                                    "Active": dialog.activeChk.checkState()}
                    whereDict = {"idNum": item.company}
                    self.updateDatabase("Companies", columnValues, whereDict)
                    self.dbConn.commit()
                    
                    self.companiesTreeWidget.refreshData()

    def deleteSelectedCompanyFromList(self):
        # Get the index of the item in the company list to delete
        item = self.companiesTreeWidget.currentItem()
        
        if item:
            whereDict = {"idNum": item.company}
            self.deleteFromDatabase("Companies", whereDict)
            self.dbConn.commit()
            
            idxToDelete = self.companiesTreeWidget.indexOfTopLevelItem(item)
            self.companiesTreeWidget.takeTopLevelItem(idxToDelete)
            self.updateCompaniesCount()
            
        self.deleteCompany.emit(item.text(2))

class CompanyView(ObjectWidget):
    addNewCompany = pyqtSignal(str)
    deleteCompany = pyqtSignal(str)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        
        self.companyWidget = CompanyWidget(self, dbConn, dbCur)
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
    def __init__(self, assetId, dbCur, parent):
        super().__init__(parent)
        self.asset = assetId
        self.refreshData(dbCur)
        
    def refreshData(self, dbCur):
        dbCur.execute("""SELECT Description, AcquireDate, InSvcDate
                         FROM Assets WHERE idNum=?""", (self.asset,))
        desc, acqDate, svcDate = dbCur.fetchone()

        cost = functions.CalculateAssetCost(dbCur, self.asset)
        self.setText(0, str(self.asset))
        self.setText(1, desc)
        self.setText(2, "{:,.2f}".format(cost))
##        self.setText(3, "{:,.2f}".format(self.asset.depreciatedAmount()))
        self.setText(4, acqDate)
        self.setText(5, svcDate)

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
    
    def __init__(self, dbCur, headerList, widthList, notDisposed=True):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.disposedFg = not notDisposed
        self.buildItems(self)
        self.setColumnCount(6)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent):
        if self.disposedFg == True:
            self.dbCursor.execute("""SELECT idNum, DisposeDate
                                     FROM Assets
                                     WHERE ParentAssetId IS NULL
                                     OR ParentAssetId IN
                                        (SELECT idNum FROM Assets
                                        WHERE DisposeDate IS NULL)""")
        else:
            self.dbCursor.execute("""SELECT idNum, DisposeDate FROM Assets
                                     WHERE ParentAssetId IS NULL""")
        assetIds = self.dbCursor.fetchall()
        for assetId, dispDate in assetIds:
            if bool(dispDate) == self.disposedFg:
                item = AssetTreeWidgetItem(assetId, self.dbCursor, parent)
                self.addTopLevelItem(item)

                self.dbCursor.execute("""SELECT idNum, DisposeDate
                                         FROM Assets
                                         WHERE ParentAssetId=?""",
                                      (assetId,))
                childAssets = self.dbCursor.fetchall()
                for childId, dispDate in childAssets:
                    self.buildChildren(item, childId, dispDate)

    def buildChildren(self, parent, childAssetId, dispDate):
        if bool(dispDate) == self.disposedFg:
            item = AssetTreeWidgetItem(childAssetId, self.dbCursor, parent)
            parent.addChild(item)

            self.dbCursor.execute("""SELECT idNum, DisposeDate
                                     FROM Assets
                                     WHERE ParentAssetId=?""",
                                  (childAssetId,))
            childAssets = self.dbCursor.fetchall()
            for childId, dispDate in childAssets:
                self.buildChildren(item, childId, dispDate)

    def refreshChildren(self, parentItem):
        for idx in range(parentItem.childCount()):
            parentItem.child(idx).refreshData(self.dbCursor)
            childAssetId = parentItem.child(idx).asset
            
            if functions.AssetIsDisposed(self.dbCursor, childAssetId):
                self.disposeAsset.emit(childAssetId)
                
            if parentItem.child(idx).childCount() > 0:
                self.refreshChildren(parentItem.child(idx))

    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            try:
                self.topLevelItem(idx).refreshData(self.dbCursor)
                assetId = self.topLevelItem(idx).asset
                
                if functions.AssetIsDisposed(self.dbCursor, assetId):
                    self.disposeAsset.emit(assetId)
                    
                if self.topLevelItem(idx).childCount() > 0:
                    self.refreshChildren(self.topLevelItem(idx))
            except:
                pass
            
class AssetWidget(ObjectWidget):
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()

        # Piece together the companies layout
        self.currentAssetsLabel = QLabel()
        self.disposedAssetsLabel = QLabel()
        
        self.currentAssetsTreeWidget = AssetTreeWidget(dbCur, constants.ASSET_HDR_LIST, constants.ASSET_HDR_WDTH)
        self.currentAssetsTreeWidget.disposeAsset.connect(self.moveCurrentAssetToDisposed)
        self.currentAssetsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(1))

        self.disposedAssetsTreeWidget = AssetTreeWidget(dbCur, constants.ASSET_HDR_LIST, constants.ASSET_HDR_WDTH, False)
        self.disposedAssetsTreeWidget.itemClicked.connect(lambda: self.removeSelectionsFromAllBut(2))
        
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
        depreciateBtn = QPushButton("Depreciate...")
        depreciateBtn.clicked.connect(self.openDepreciationWindow)
        buttonWidget.addButton(assetTypeBtn)
        buttonWidget.addButton(impairBtn)
        buttonWidget.addButton(disposeBtn)
        buttonWidget.addButton(depreciateBtn)
        
        mainLayout.addWidget(self.currentAssetsLabel, 0, 0)
        mainLayout.addWidget(self.currentAssetsTreeWidget, 1, 0)
        mainLayout.addWidget(self.disposedAssetsLabel, 2, 0)
        mainLayout.addWidget(self.disposedAssetsTreeWidget, 3, 0)
        mainLayout.addWidget(buttonWidget, 1, 1, 3, 1)
        mainLayout.setRowStretch(4, 1)
        
        self.setLayout(mainLayout)
        self.updateAssetsCount()

    def openDepreciationWindow(self):
        dialog = DepreciationDialog(self.assetsDict, self.parent.dataConnection.companies)
        dialog.exec_()
    
    def updateAssetsCount(self):
        self.currentAssetsLabel.setText("Current Assets: %d / .02f" % self.currentAssetsTreeWidget.topLevelItemCount())
        self.disposedAssetsLabel.setText("Disposed Assets: %d / .02f" % self.disposedAssetsTreeWidget.topLevelItemCount())

    def showAssetTypeDialog(self):
        dialog = AssetTypeDialog(self.dbCur, self)
        dialog.exec_()

    def removeSelectionsFromAllBut(self, but):
        if but == 1:
            self.disposedAssetsTreeWidget.setCurrentItem(self.disposedAssetsTreeWidget.invisibleRootItem())
        else:
            self.currentAssetsTreeWidget.setCurrentItem(self.currentAssetsTreeWidget.invisibleRootItem())

    def moveCurrentAssetToDisposed(self, assetId):
        item = self.getItem(assetId)
        newItem = AssetTreeWidgetItem(item.asset,
                                      self.dbCur,
                                      self.disposedAssetsTreeWidget)
        
        # If disposed asset has subassets, we must dispose of them and move them
        # over to newItem
        if item.childCount() > 0:
            self.moveChildren(item, newItem)
        
        # If disposed asset already has a subasset that has been disposed, we
        # want to merge the newly disposed asset into the tree rather than
        # create a new entry. Otherwise, make it a top level item in the
        # disposed asset tree.
        self.dbCur.execute("""SELECT PartiallyDisposed, ParentAssetId
                              FROM Assets
                              WHERE idNum=?""", (assetId,))
        partiallyDisposed, parentAssetId = self.dbCur.fetchone()
        if bool(partiallyDisposed) == True:
            self.dbCur.execute("""SELECT idNum FROM Assets
                                  WHERE DisposeDate IS NOT NULL AND
                                        ParentAssetId=?""",
                               (assetId,))
            for idNum in self.dbCur:
                oldItem = self.getItem(idNum[0], self.disposedAssetsTreeWidget)
                idx = self.disposedAssetsTreeWidget.indexOfTopLevelItem(oldItem)
                self.disposedAssetsTreeWidget.takeTopLevelItem(idx)

                newChildItem = AssetTreeWidgetItem(oldItem.asset,
                                                   self.dbCur,
                                                   newItem)
                self.moveChildren(oldItem, newChildItem)
                
                newItem.addChild(newChildItem)
                
        self.disposedAssetsTreeWidget.addTopLevelItem(newItem)
        
        # Remove the top-most disposed item from the list.  If it is a subasset,
        # we must remove it as a child of its parent.  If it is not, we can
        # remove it through the takeTopLevelItem() method.
        if parentAssetId:
            parentItem = item.parent()
            childToTake = parentItem.indexOfChild(item)
            parentItem.takeChild(childToTake)
        else:
            idx = self.currentAssetsTreeWidget.indexOfTopLevelItem(item)
            self.currentAssetsTreeWidget.takeTopLevelItem(idx)
        
        # Make all asset disposal indicator changes
        functions.MarkPartialDisposals(self.dbCur, parentAssetId)
        self.dbConn.commit()
        
    def moveChildren(self, oldParentItem, newParentItem):
        while oldParentItem.childCount() > 0:
            child = oldParentItem.takeChild(0)
            newChild = AssetTreeWidgetItem(child.asset,
                                           self.dbCur,
                                           newParentItem)
            newParentItem.addChild(newChild)

            if child.childCount() > 0:
                self.moveChildren(child, newChild)
                
    def getItem(self, assetNum, treeWidget=None):
        if not treeWidget:
            treeWidget = self.currentAssetsTreeWidget
            
        iterator = QTreeWidgetItemIterator(treeWidget)
        while iterator.value():
            if iterator.value().asset == assetNum:
                return iterator.value()

            iterator += 1
    
    def disposeChildAssets(self, parentItem, amt, date):
        for idx in range(parentItem.childCount()):
            colValDict = {"DisposeDate": date,
                          "DisposeAmount": amt}
            whereDict = {"idNum": parentItem.child(idx).asset}
            self.updateDatabase("Assets", colValDict, whereDict)
            
            if parentItem.child(idx).childCount() > 0:
                self.disposeChildAssets(parentItem.child(idx), amt, date)

    def disposeAsset(self):
        # Need to dispose not only given item, but also any child items it may have.
        item = self.currentAssetsTreeWidget.currentItem()

        if item:
            dialog = DisposeAssetDialog(self)
            if dialog.exec_():
                dispDate = dialog.dispDateTxt.text()
                dispAmt = float(dialog.dispAmtTxt.text())
                colValDict = {"DisposeDate": dispDate,
                              "DisposeAmount": dispAmt}
                whereDict = {"idNum": item.asset}
                self.updateDatabase("Assets", colValDict, whereDict)
                
                if item.childCount() > 0:
                    self.disposeChildAssets(item, dispAmt, dispDate)
                
                self.dbConn.commit()
                self.refreshAssetTree()
                self.updateAssetsCount()

    def showNewAssetDialog(self):
        dialog = AssetDialog("New", self.dbCur, self)
        if dialog.exec_():
            # Find current largest id and increment by one
            nextId = self.nextIdNum("Assets")
            companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
            assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
            description = dialog.descriptionText.text()
            self.dbCur.execute("""SELECT Depreciable FROM AssetTypes
                                  WHERE idNum=?""",
                               (assetTypeId,))
            depreciable = bool(self.dbCur.fetchone()[0])
            
            # Get and/or set some data elements
            dateAcq = dialog.dateAcquiredText.text()
            if dialog.dateInSvcText.text() == "":
                dateInSvc = None
            else:
                dateInSvc = dialog.dateInSvcText.text()
            
            if depreciable:
                usefulLife = float(dialog.usefulLifeText.text())
                depMethod = dialog.depMethodBox.currentText()
                salvageAmount = float(dialog.salvageValueText.text())
            else:
                usefulLife = None
                depMethod = None
                salvageAmount = None
            
            if dialog.childOfAssetBox.currentText() == "":
                parentAssetId = None
            else:
                parentAssetId = self.stripAllButNumbers(dialog.childOfAssetBox.currentText())
            
            columns = ("Description", "AcquireDate", "InSvcDate", "UsefulLife",
                       "SalvageAmount", "DepreciationMethod",
                       "PartiallyDisposed", "CompanyId", "AssetTypeId",
                       "ParentAssetId")
            values = (description, dateAcq, dateInSvc, usefulLife,
                      salvageAmount, depMethod, 0, companyId, assetTypeId,
                      parentAssetId)
            self.insertIntoDatabase("Assets", columns, values)
            
            self.dbConn.commit()
            
            # Make asset into an AssetTreeWidgetItem and add it to AssetTree
            if parentAssetId == None:
                item = AssetTreeWidgetItem(nextId, self.dbCur, self.currentAssetsTreeWidget)
                self.currentAssetsTreeWidget.addTopLevelItem(item)
            else:
                parentItem = self.getItem(parentAssetId)
                item = AssetTreeWidgetItem(nextId, self.dbCur, parentItem)
                parentItem.addChild(item)
            
            self.updateAssetsCount()
            
    def showViewAssetDialog(self):
        item = self.currentAssetsTreeWidget.currentItem()

        if item:
            dialog = AssetDialog("View", self.dbCur, self, item.asset)
            
            if dialog.exec_():
                if dialog.hasChanges == True:
                    companyId = self.stripAllButNumbers(dialog.companyBox.currentText())
                    desc = dialog.descriptionText.text()
                    assetTypeId = self.stripAllButNumbers(dialog.assetTypeBox.currentText())
                    parentAssetId = self.stripAllButNumbers(dialog.childOfAssetBox.currentText())
                    if parentAssetId == "":
                        parentAssetId = None
                    dateAcq = dialog.dateAcquiredText.text()
                    dateInSvc = dialog.dateInSvcText.text()
                    usefulLife = dialog.usefulLifeText.text()
                    if usefulLife:
                        depMethod = None
                        salvageValue = None
                    else:
                        usefulLife = float(usefulLife)
                        depMethod = dialog.depMethodBox.currentText()
                        salvageValue = float(dialog.salvageValueText.text())
                    
                    # Commit changes to database and to vendor entry
                    colValDict = {"Description": desc,
                                  "AcquireDate": dateAcq,
                                  "InSvcDate": dateInSvc,
                                  "UsefulLife": usefulLife,
                                  "SalvageAmount": salvageValue,
                                  "DepreciationMethod": depMethod,
                                  "CompanyId": companyId,
                                  "AssetTypeId": assetTypeId, 
                                  "ParentAssetId": parentAssetId}
                    whereDict = {"idNum": item.asset}
                    self.updateDatabase("Assets", colValDict, whereDict)
                    
                    self.dbConn.commit()
                    self.refreshAssetTree()

    def deleteSelectedAssetFromList(self):
        # Get the index of the item in the company list to delete
        item = self.currentAssetsTreeWidget.currentItem()
        
        if item:
            self.dbCur.execute("""SELECT ProposalId FROM ProposalsObjects
                                  WHERE ObjectType=? AND ObjectId=?
                                  UNION
                                  SELECT InvoiceId FROM InvoicesObjects
                                  WHERE ObjectType=? AND ObjectId=?""",
                               ("assets", item.asset, "assets", item.asset))
            results = self.dbCur.fetchall()
            if results:
                deleteError = QMessageBox()
                deleteError.setWindowTitle("Can't delete")
                deleteError.setText("Cannot delete an asset that has proposals or invoices.")
                deleteError.exec_()
            else:
                whereDict = {"idNum": item.asset}
                self.deleteFromDatabase("Assets", whereDict)
                self.dbConn.commit()
                
                if item.parent():
                    parentItem = item.parent()
                    idxToDelete = parentItem.indexOfChild(item)
                    parentItem.takeChild(idxToDelete)
                else:
                    idxToDelete = self.currentAssetsTreeWidget.indexOfTopLevelItem(item)
                    self.currentAssetsTreeWidget.takeTopLevelItem(idxToDelete)
                
                self.updateAssetsCount()

    def refreshAssetTree(self):
        self.currentAssetsTreeWidget.refreshData()
        
class AssetView(QWidget):
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent)
        self.parent = parent

        self.assetWidget = AssetWidget(self, dbConn, dbCur)

        layout = QVBoxLayout()
        layout.addWidget(self.assetWidget)

        self.setLayout(layout)

class GLTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, glAccount, dbCur, parent):
        super().__init__(parent)
        self.glAccount = glAccount

        dbCur.execute("""SELECT Description, Placeholder FROM GLAccounts
                         WHERE idNum=?""", (glAccount,))
        description, placeHolder = dbCur.fetchone()
        self.description = description
        self.placeHolder = bool(placeHolder)
        
        self.setText(0, str(self.glAccount))
        self.setText(1, description)
        self.setText(2, "{:,.2f}".format(self.balance(dbCur)))

        if placeHolder == True:
            for n in range(3):
                font = self.font(n)
                font.setBold(True)
                self.setFont(n, font)

    def balance(self, dbCur):
        balance = 0.0
        dbCur.execute("""SELECT Amount, DebitCredit FROM GLPostingsDetails
                         WHERE GLAccount=?""", (self.glAccount,))
        for amount, drCr in dbCur:
            if drCr == constants.DEBIT:
                balance += amount
            else:
                balance -= amount
        return balance

    def balanceOfGroup(self):
        balance = 0.0
        for n in range(self.childCount()):
            child = self.child(n)
            textBalance = child.text(2).replace(",", "")
            balance += round(float(textBalance), 2)
        return balance

    def refreshData(self, dbCur):
        self.setText(0, str(self.glAccount))
        self.setText(1, self.description)
        if self.placeHolder == True:
            self.setText(2, "{:,.2f}".format(self.balanceOfGroup()))
        else:
            self.setText(2, "{:,.2f}".format(self.balance(dbCur)))
        
class GLTreeWidget(NewTreeWidget):
    def __init__(self, dbCursor, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCursor
        self.buildItems(self)
        self.setColumnCount(3)
        self.sortItems(0, Qt.AscendingOrder)
        self.refreshData()

    def buildItems(self, parent):
        self.dbCursor.execute("""SELECT idNum FROM GLAccounts
                                 WHERE Placeholder=1""")
        acctGrps = self.dbCursor.fetchall()
        for glId in acctGrps:
            item = GLTreeWidgetItem(glId[0], self.dbCursor, parent)

            self.dbCursor.execute("""SELECT idNum FROM GLAccounts
                                     WHERE ParentGL=?""", (glId[0],))
            children = self.dbCursor.fetchall()
            for idNum in children:
                subItem = GLTreeWidgetItem(idNum[0], self.dbCursor, item)
                item.addChild(subItem)
            
            self.addTopLevelItem(item)

    def refreshChildren(self, parentItem, dbCur):
        for idx in range(parentItem.childCount()):
            parentItem.child(idx).refreshData(dbCur)
    
    def refreshData(self):
        for idx in range(self.topLevelItemCount()):
            if self.topLevelItem(idx).childCount() > 0:
                self.refreshChildren(self.topLevelItem(idx), self.dbCursor)

            self.topLevelItem(idx).refreshData(self.dbCursor)
            
class GLWidget(ObjectWidget):
    displayGLAcct = pyqtSignal(int)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()

        # Piece together the GL layout
        self.chartOfAccountsLabel = QLabel("Chart of Accounts")
        
        self.chartOfAccountsTreeWidget = GLTreeWidget(dbCur, constants.GL_HDR_LIST, constants.GL_HDR_WDTH)
        self.chartOfAccountsTreeWidget.currentItemChanged.connect(self.displayGLDetails)
        
        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewGLAccountDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewGLAccountDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteGLAccount)
        
        mainLayout.addWidget(self.chartOfAccountsLabel, 0, 0)
        mainLayout.addWidget(self.chartOfAccountsTreeWidget, 1, 0)
        mainLayout.addWidget(buttonWidget, 1, 1)
        mainLayout.setRowStretch(2, 1)
        
        self.setLayout(mainLayout)

    def displayGLDetails(self, newItem, oldItem):
        self.displayGLAcct.emit(newItem.glAccount)
        
    def moveAcctXToGrpY(self, acctId, newParentId, oldParentId):
        oldParentItem = self.getItem(oldParentId)
        newParentItem = self.getItem(newParentId)
        
        for idx in range(oldParentItem.childCount()):
            if oldParentItem.child(idx).glAccount == acctId:
                oldItem = oldParentItem.takeChild(idx)
                
        newItem = GLTreeWidgetItem(oldItem.glAccount, newParentItem)
        self.chartOfAccountsTreeWidget.addItem(newItem)

    def getItem(self, glNum):
        iterator = QTreeWidgetItemIterator(self.chartOfAccountsTreeWidget)
        
        while iterator.value():
            if iterator.value().glAccount == glNum:
                return iterator.value()
            iterator += 1
    
    def showNewGLAccountDialog(self):
        dialog = GLAccountDialog("New", self.dbCur, self)
        if dialog.exec_():
            acctNum = int(dialog.accountNumText.text())
            desc = dialog.descriptionText.text()
            if dialog.acctGrpChk.checkState() == Qt.Checked:
                placeHolder = 1
                parentAccount = None
            else:
                placeHolder = 0
                parentAccount = self.stripAllButNumbers(dialog.acctGrpsBox.currentText())
            
            # Create new object and add links
            newGLAccount = GLAccount(dialog.descriptionText.text(),
                                     placeHolder,
                                     int(dialog.accountNumText.text()))
            
            # Add to database and corporate structure. If we are dealing
            # with a "live" GL account, we need to add Xref records to
            # the database.
            columns = ("idNum", "Description", "Placeholder", "ParentGL")
            values = (acctNum, desc, placeHolder, parentAccount)
            self.insertIntoDatabase("GLAccounts", columns, values)
            self.dbConn.commit()
            
            # Add GL to widget tree
            if placeHolder == 1:
                item = GLTreeWidgetItem(acctNum, self.dbCur, self.chartOfAccountsTreeWidget)
                self.chartOfAccountsTreeWidget.addTopLevelItem(item)
            else:
                parentItem = self.getItem(parentAccount)
                item = GLTreeWidgetItem(acctNum, self.dbCur, parentItem)
                parentItem.addChild(item)
            
    def showViewGLAccountDialog(self):
        item = self.chartOfAccountsTreeWidget.currentItem()

        if item:
            dialog = GLAccountDialog("View", self.dbCur, self, item.glAccount)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    newGLNum = int(dialog.accountNumText_edit.text())
                    desc = dialog.descriptionText_edit.text()
                    if dialog.acctGrpChk.checkState() == Qt.Checked:
                        placeholder = 1
                        parentGL = None
                    else:
                        placeholder = 0
                        parentGL = self.stripAllButNumbers(dialog.acctGrpsBox.currentText())
                    
                    colValDict = {"idNum": newGLNum,
                                  "Description": desc,
                                  "Placeholder": placeholder,
                                  "ParentGL": parentGL}
                    whereDict = {"idNum": item.glAccount}
                    self.updateDatabase("GLAccounts", colValDict, whereDict)
                    
                    if item.placeHolder == True and bool(placeholder) == False:
                        idxToDelete = self.chartOfAccountsTreeWidget.indexFromToplLevelItem(item)
                        self.chartOfAccountsTreeWidget.takeTopLevelItem(idxToDelete)
                        parentItem = self.getItem(parentGL)
                        newItem = GLTreeWidgetItem(newGLNum, self.dbCur, parentItem)
                        parentItem.addChild(newItem)
                    elif item.placeHolder == False and bool(placeholder) == True:
                        parentItem = item.parent()

                        idxToDelete = parentItem.indexOfChild(item)
                        parentItem.takeChild(idxToDelete)

                        newItem = GLTreeWidgetItem(newGLNum, self.dbCur, self.chartOfAccountsTreeWidget)
                        self.chartOfAccountsTreeWidget.addTopLevelItem(newItem)
                    elif item.placeHolder == True and bool(placeholder) == True:
                        pass
                    else:
                        oldParentItem = item.parent()
                        newParentItem = self.getItem(parentGL)

                        idxToDelete = oldParentItem.indexOfChild(item)
                        oldParentItem.takeChild(idxToDelete)
                        newItem = GLTreeWidgetItem(newGLNum, self.dbCur, newParentItem)
                        newParentItem.addChild(newItem)
                        
                    self.dbConn.commit()
                    self.chartOfAccountsTreeWidget.refreshData()

    def deleteGLAccount(self):
        item = self.chartOfAccountsTreeWidget.currentItem()
        
        if item:
            whereDict = {"idNum": item.glAccount}
            self.deleteFromDatabase("GLAccounts", whereDict)
            self.dbConn.commit()

            if item.placeHolder == True:
                idxToDelete = self.chartOfAccountsTreeWidget.indexOfTopLevelItem(item)
                self.chartOfAccountsTreeWidget.takeTopLevelItem(idxToDelete)
            else:
                idxToDelete = item.parent().indexOfChild(item)
                item.parent().takeChild(idxToDelete)

class GLPostingsTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, glPostingDet, dbCur, parent):
        super().__init__(parent)
        self.glPostingDet = glPostingDet
        self.refreshData(dbCur)
        
    def refreshData(self, dbCur):
        dbCur.execute("""SELECT Date, Description, Amount, DebitCredit
                         FROM GLPostings JOIN GLPostingsDetails
                         ON GLPostingsDetails.GLPostingId = GLPostings.idNum
                         WHERE GLPostingsDetails.idNum=?""", (self.glPostingDet,))
        date, desc, amt, drCr = dbCur.fetchone()
        
        self.setText(0, date)
        self.setText(1, desc)
        if drCr == constants.DEBIT:
            self.setText(2, "{: ,.2f}".format(amt))
        else:
            self.setText(2, "{:-,.2f}".format(-1 * amt))
        
class GLPostingsTreeWidget(NewTreeWidget):
    def __init__(self, dbCur, headerList, widthList):
        super().__init__(headerList, widthList)
        self.dbCursor = dbCur
        self.setColumnCount(3)
        self.sortItems(0, Qt.AscendingOrder)

    def buildItems(self, parent, glAcct):
        self.dbCursor.execute("""SELECT idNum FROM GLPostingsDetails
                                 WHERE GLAccount=?""", (glAcct,))
        results = self.dbCursor.fetchall()
        
        for idNum in results:
            item = GLPostingsTreeWidgetItem(idNum[0], self.dbCursor, parent)
            self.addTopLevelItem(item)

    def refreshData(self, dbCur):
        for idx in range(self.topLevelItemCount()):
            self.topLevelItem(idx).refreshData(dbCur)

class GLPostingsWidget(ObjectWidget):
    postToGL = pyqtSignal(int, object, str, list)
    updateGLPost = pyqtSignal(object, str, str)
    updateGLDet = pyqtSignal(object, float, str)
    deleteGLPost = pyqtSignal(object)
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent, dbConn, dbCur)
        mainLayout = QGridLayout()

        # Piece together the GL layout
        self.glPostingsLabel = QLabel("Details")
        self.glPostingsTreeWidget = GLPostingsTreeWidget(dbCur, constants.GL_POST_HDR_LIST, constants.GL_POST_HDR_WDTH)

        buttonWidget = StandardButtonWidget()
        buttonWidget.newButton.clicked.connect(self.showNewGLPostingDialog)
        buttonWidget.viewButton.clicked.connect(self.showViewGLPostingDialog)
        buttonWidget.deleteButton.clicked.connect(self.deleteGLPostingAccount)
        
        mainLayout.addWidget(self.glPostingsLabel, 0, 0)
        mainLayout.addWidget(self.glPostingsTreeWidget, 1, 0)
        mainLayout.addWidget(buttonWidget, 1, 1)
        mainLayout.setRowStretch(2, 1)

        self.setLayout(mainLayout)

    def showDetail(self, glAcctNum):
        self.glPostingsTreeWidget.clear()
        self.glPostingsTreeWidget.buildItems(self.glPostingsTreeWidget, glAcctNum)
        
    def showNewGLPostingDialog(self):
        dialog = NewGLPostingDialog("New", self.companiesDict, self.glAcctsDict)
        if dialog.exec_():
            companyNum = self.stripAllButNumbers(dialog.companyBox.currentText())
            date = classes.NewDate(dialog.dateText.text())
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
    
    def __init__(self, parent, dbConn, dbCur):
        super().__init__(parent)
        self.glWidget = GLWidget(self, dbConn, dbCur)
        self.glWidget.displayGLAcct.connect(self.displayGLDetails)
        self.glPostingsWidget = GLPostingsWidget(self, dbConn, dbCur)
##        self.glPostingsWidget.postToGL.connect(self.postToGL)
##        self.glPostingsWidget.deleteGLPost.connect(self.deleteGLPost)

        layout = QVBoxLayout()
        layout.addWidget(self.glWidget)
        layout.addWidget(self.glPostingsWidget)

        self.setLayout(layout)

    def refreshGL(self):
        self.glWidget.chartOfAccountsTreeWidget.refreshData()

    def displayGLDetails(self, glAcctNum):
        self.glPostingsWidget.showDetail(glAcctNum)

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
                                            (str(glPosting.date), glPosting.description))
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
