from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import constants
import gui_elements
import classes
import functions

class DepreciationDialog(QDialog):
    def __init__(self, assetsDict, companyDict):
        super().__init__()
        self.assetsDict = assetsDict
        self.companyDict = companyDict

        # Create major interface elements
        companyLbl = QLabel("Company:")
        #assetLbl = QLabel("Asset:")
        costLbl = QLabel("Cost:")
        accumDepLbl = QLabel("Accum. Dep.:")
        depMethLbl = QLabel("Dep. Method:")
        usefulLifeLbl = QLabel("Lifespan:")
        salvageLbl = QLabel("Salvage Amt.:")
        
        self.assetTreeWidget = gui_elements.DepAssetTreeWidget(self.assetsDict, constants.DEP_ASSET_HDR_LIST, constants.DEP_ASSET_HDR_WDTH)
        self.assetTreeWidget.setMinimumWidth(200)
        self.assetTreeWidget.setColumnSizes(200, constants.DEP_ASSET_HDR_WDTH)
        self.companyBox = QComboBox()
        self.companyBox.addItem("<All>")
        self.companyBox.addItems(self.companyDict.sortedListOfKeysAndNames())
        self.costTxt = QLineEdit()
        self.accumDepTxt = QLineEdit()
        self.depMethodBox = QComboBox()
        self.usefulLifeTxt = QLineEdit()
        self.salvageAmtTxt = QLineEdit()
        self.depHistoryWidget = gui_elements.DepHistoryWidget()
        
        # Assemble layout
        layout = QGridLayout()
        layout.addWidget(self.assetTreeWidget, 0, 0, 7, 1)
        layout.addWidget(companyLbl, 0, 1)
        layout.addWidget(self.companyBox, 0, 2)
        layout.addWidget(costLbl, 1, 1)
        layout.addWidget(self.costTxt, 1, 2)
        layout.addWidget(accumDepLbl, 2, 1)
        layout.addWidget(self.accumDepTxt, 2, 2)
        layout.addWidget(depMethLbl, 3, 1)
        layout.addWidget(self.depMethodBox, 3, 2)
        layout.addWidget(usefulLifeLbl, 4, 1)
        layout.addWidget(self.usefulLifeTxt, 4, 2)
        layout.addWidget(salvageLbl, 5, 1)
        layout.addWidget(self.salvageAmtTxt, 5, 2)
        layout.addWidget(self.depHistoryWidget, 6, 1, 1, 2)
        
        self.setLayout(layout)
        
class VendorDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, vendor=None):
        super().__init__(parent)
        self.vendor = vendor
        self.hasChanges = False
        
        self.layout = QGridLayout()

        nameLbl = QLabel("Name:")
        addressLbl = QLabel("Address:")
        cityLbl = QLabel("City:")
        stateLbl = QLabel("State:")
        zipLbl = QLabel("ZIP:")
        phoneLbl = QLabel("Phone:")
        glAccountLbl = QLabel("GL Account:")
        
        self.glAccountsBox = QComboBox()
        dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                         WHERE Placeholder=0""")
        for idNum, desc in dbCur:
            self.glAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
        
        if mode == "View":
            dbCur.execute("SELECT * FROM Vendors WHERE idNum=?", (vendor,))
            idNum, name, address, city, state, zip_, phone, glAcct = dbCur.fetchone()
            self.nameText = QLineEdit(name)
            self.addressText = QLineEdit(address)
            self.cityText = QLineEdit(city)
            self.stateText = QLineEdit(state)
            self.zipText = QLineEdit(zip_)
            self.phoneText = QLineEdit(phone)

            self.nameText.setEnabled(False)
            self.addressText.setEnabled(False)
            self.cityText.setEnabled(False)
            self.stateText.setEnabled(False)
            self.zipText.setEnabled(False)
            self.phoneText.setEnabled(False)
            
            dbCur.execute("SELECT Description FROM GLAccounts WHERE idNum=?",
                          (glAcct,))
            glDesc = dbCur.fetchone()[0]
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(constants.ID_DESC % (glAcct, glDesc)))
            self.glAccountsBox.setEnabled(False)
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
        self.layout.addWidget(glAccountLbl, 6, 0)
        self.layout.addWidget(self.glAccountsBox, 6, 1)
        nextRow = 7
        
        if mode == "View":
            restriction = ".".join(["VendorId", str(vendor)])
            invoicesWidget = gui_elements.InvoiceTreeWidget(dbCur, None, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH, restriction)
            self.layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
            nextRow += 1
            
##            proposalsWidget = gui_elements.ProposalTreeWidget(self.vendor.proposals, constants.PROPOSAL_HDR_LIST, constants.PROPOSAL_HDR_WDTH)
##            self.layout.addWidget(proposalsWidget, nextRow, 0, 1, 2)
##            nextRow += 1
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Vendor")
        else:
            self.setWindowTitle("New Vendor")
    
    def makeLabelsEditable(self):
        self.nameText.setEnabled(True)
        self.addressText.setEnabled(True)
        self.cityText.setEnabled(True)
        self.stateText.setEnabled(True)
        self.zipText.setEnabled(True)
        self.phoneText.setEnabled(True)

        self.nameText.textEdited.connect(self.changed)
        self.addressText.textEdited.connect(self.changed)
        self.cityText.textEdited.connect(self.changed)
        self.stateText.textEdited.connect(self.changed)
        self.zipText.textEdited.connect(self.changed)
        self.phoneText.textEdited.connect(self.changed)
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.changed)
        
    def changed(self):
        self.hasChanges = True

class InvoiceDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, invoice=None):
        super().__init__(parent)
        self.parent = parent
        self.invoice = invoice
        self.dbCur = dbCur
        self.hasChanges = False
        self.mode = mode
        
        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        vendorLbl = QLabel("Vendor:")
        invoiceDateLbl = QLabel("Invoice Date:")
        dueDateLabel = QLabel("Due Date:")
        
        self.companyBox = QComboBox()
        dbCur.execute("SELECT idNum, ShortName FROM Companies")
        for idNum, name in dbCur:
            self.companyBox.addItem(constants.ID_DESC % (idNum, name))
        self.companyBox.currentIndexChanged.connect(self.updateAssetProjSelector)
        
        self.vendorBox = QComboBox()
        dbCur.execute("SELECT idNum, Name FROM Vendors")
        for idNum, name in dbCur:
            self.vendorBox.addItem(constants.ID_DESC % (idNum, name))
        
        companyId = parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector = gui_elements.AssetProjSelector(companyId, dbCur)
        self.assetProjSelector.rdoBtnChanged.connect(self.updateDetailInvoiceWidget)
        self.assetProjSelector.selectorChanged.connect(self.updateDetailInvoiceWidget)
        
        if self.mode == "View":
            dbCur.execute("""SELECT Vendors.idNum, Vendors.Name,
                                    Companies.idNum, Companies.ShortName
                             FROM Invoices
                             LEFT JOIN Companies
                             ON Invoices.CompanyId = Companies.idNum
                             LEFT JOIN Vendors
                             ON Invoices.VendorId = Vendors.idNum
                             WHERE Invoices.idNum=?""",
                          (invoice,))
            vendId, vendName, companyId, companyName = dbCur.fetchone()
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (companyId, companyName)))
            self.companyBox.setEnabled(False)
            
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(constants.ID_DESC % (vendId, vendName)))
            self.vendorBox.setEnabled(False)
            
            self.assetProjSelector.updateCompany(companyId)
            
            dbCur.execute("""SELECT ObjectType, ObjectId FROM InvoicesObjects
                             WHERE InvoiceId=?""", (invoice,))
            objectType, objectId = dbCur.fetchone()
            
            if objectType == "assets":
                # Need to disable signals, otherwise checking the radio button
                # will cause a myriad of signals to be passed and will crash
                # the program.
                dbCur.execute("SELECT Description FROM Assets WHERE idNum=?",
                              (objectId,))
                desc = dbCur.fetchone()[0]
                self.assetProjSelector.dontEmitSignals(True)
                self.assetProjSelector.assetRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(constants.ID_DESC % (objectId, desc)))
                self.assetProjSelector.dontEmitSignals(False)
            else:
                dbCur.execute("SELECT Description FROM Projects WHERE idNum=?",
                              (objectId,))
                desc = dbCur.fetchone()[0]
                self.assetProjSelector.dontEmitSignals(True)
                self.assetProjSelector.projRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(constants.ID_DESC % (objectId, desc)))
                self.assetProjSelector.dontEmitSignals(False)
                
            self.assetProjSelector.setEnabled(False)
            self.assetProjSelector.show()
            
            dbCur.execute("""SELECT InvoiceDate, DueDate FROM Invoices
                             WHERE idNum=?""", (invoice,))
            invoiceDate, dueDate = dbCur.fetchone()
            self.invoiceDateText = QLabel(invoiceDate)
            self.dueDateText = QLabel(dueDate)
        else:
            self.invoiceDateText = gui_elements.DateLineEdit()
            self.dueDateText = gui_elements.DateLineEdit()
        
        self.layout.addWidget(companyLbl, 0, 0)
        self.layout.addWidget(self.companyBox, 0, 1)
        self.layout.addWidget(self.assetProjSelector, 1, 0, 1, 2)
        self.layout.addWidget(vendorLbl, 2, 0)
        self.layout.addWidget(self.vendorBox, 2, 1)
        self.layout.addWidget(invoiceDateLbl, 3, 0)
        self.layout.addWidget(self.invoiceDateText, 3, 1)
        self.layout.addWidget(dueDateLabel, 4, 0)
        self.layout.addWidget(self.dueDateText, 4, 1)
        
        if self.mode == "View":
            proposals = self.getAcceptedProposalsOfAssetProject()
            self.detailsWidget = gui_elements.InvoiceDetailWidget(dbCur, invoice, proposals)
        else:
            self.detailsWidget = gui_elements.InvoiceDetailWidget(dbCur)
        self.layout.addWidget(self.detailsWidget, 5, 0, 1, 2)
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        nextRow = 6
        if self.mode == "View":
            subLayout = QHBoxLayout()
            
            self.paymentHistory = gui_elements.InvoicePaymentTreeWidget(dbCur, invoice, constants.INVOICE_PYMT_HDR_LIST, constants.INVOICE_PYMT_HDR_WDTH)
            self.paymentHistory.setCurrentItem(self.paymentHistory.invisibleRootItem())
            
            paymentButtonLayout = gui_elements.StandardButtonWidget()
            paymentButtonLayout.newButton.clicked.connect(self.newPayment)
            paymentButtonLayout.viewButton.clicked.connect(self.viewPayment)
            paymentButtonLayout.deleteButton.clicked.connect(self.deletePayment)
            
            subLayout.addWidget(self.paymentHistory)
            subLayout.addWidget(paymentButtonLayout)
            
            self.layout.addLayout(subLayout, nextRow, 0, 1, 2)
            nextRow += 1
        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Invoice")
        else:
            self.setWindowTitle("New Invoice")
            
    def newPayment(self):
        dialog = InvoicePaymentDialog("New", self.dbCur, self, self.invoice)
        if dialog.exec_():
            nextId = self.parent.nextIdNum("InvoicesPayments")
            paymentTypeId = self.parent.stripAllButNumbers(dialog.paymentTypeBox.currentText())
            datePd = classes.NewDate(dialog.datePaidText.text())
            amtPd = float(dialog.amountText.text())

            # Create new payment and get necessary objects
            newPayment = classes.InvoicePayment(datePd, amtPd, nextId)
            
            # Add to database and to data structure
            columns = ("DatePaid", "AmountPaid", "InvoiceId", "PaymentTypeId")
            values = (str(datePd), amtPd, self.invoice, paymentTypeId)
            self.parent.insertIntoDatabase("InvoicesPayments", columns, values)
            self.parent.dbConn.commit()
            
            # Create GL posting
            reference = ".".join(["InvoicesPayments", str(nextId)])
            self.dbCur.execute("""SELECT PaymentTypes.GLAccount,
                                         Vendors.GLAccount, Vendors.idNum,
                                         Invoices.CompanyId
                                  FROM InvoicesPayments
                                  JOIN Invoices ON InvoicesPayments.InvoiceId = Invoices.idNum
                                  JOIN Vendors ON Vendors.idNum = Invoices.VendorId
                                  JOIN PaymentTypes ON InvoicesPayments.PaymentTypeId = PaymentTypes.idNum
                                  WHERE InvoicesPayments.idNum=?""", (nextId,))
            pymtGL, vendGL, vendId, compId = self.dbCur.fetchone()
            description = constants.GL_POST_PYMT_DESC % (self.invoice, vendId, str(datePd))
            details = [(amtPd, "CR", pymtGL),
                       (amtPd, "DR", vendGL)]
            self.parent.postToGL.emit(compId, datePd, description, reference,
                                      details)
            
            # Add entry to payment tree
            item = gui_elements.InvoicePaymentTreeWidgetItem(newPayment.idNum,
                                                             self.dbCur,
                                                             self.paymentHistory)
            self.paymentHistory.addTopLevelItem(item)
            
            # Refresh AP info
            self.parent.updateVendorTree.emit()
            self.parent.refreshOpenInvoiceTree()
            
    def viewPayment(self):
        item = self.paymentHistory.currentItem()

        if item:
            dialog = InvoicePaymentDialog("View", self.dbCur, self, self.invoice, item.invoicePayment)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    newAmtPaid = float(dialog.amountText.text())
                    newDatePaid = classes.NewDate(dialog.datePaidText.text())
                    
                    # Change values in data structure and database
                    colValDict = {"DatePaid": str(newDatePaid),
                                  "AmountPaid": newAmtPaid}
                    whereDict = {"idNum": item.invoicePayment}
                    
                    self.parent.updateDatabase("InvoicesPayments",
                                               colValDict,
                                               whereDict)
                    
                    # Update GL post
                    reference = ".".join(["InvoicesPayments",
                                          str(item.invoicePayment)])
                    colValDict = {"Date": str(newDatePaid)}
                    whereDict = {"Reference": reference}
                    self.parent.updateDatabase("GLPostings",
                                               colValDict,
                                               whereDict)
                    
                    self.dbCur.execute("""SELECT GLPostingsDetails.idNum,
                                                 DebitCredit
                                          FROM GLPostingsDetails JOIN GLPostings
                                          ON GLPostings.idNum = GLPostingsDetails.GLPostingId
                                          WHERE Reference=?""", (reference,))
                    glPostDetIds = self.dbCur.fetchall()
                    for glPostDetId, drCr in glPostDetIds:
                        colValDict = {"Amount": newAmtPaid}
                        whereDict = {"idNum": glPostDetId}
                        self.parent.updateDatabase("GLPostingsDetails",
                                                   colValDict,
                                                   whereDict)
                    self.parent.dbConn.commit()
                    self.parent.parent.updateGLTree.emit()
                    
                    # Refresh data
                    self.paymentHistory.refreshData()
                    self.parent.refreshOpenInvoiceTree()
                    self.parent.refreshPaidInvoicesTreeWidget()
                    self.parent.updateVendorTree.emit()

    def deletePayment(self):
        item = self.paymentHistory.currentItem()
        
        if item:
            # Delete payment from database
            self.dbCur.execute("""SELECT GLPostingId FROM InvoicesPayments
                                  WHERE idNum=?""", (item.invoicePayment,))
            glPostingId = self.dbCur.fetchone()[0]
            
            whereDict = {"idNum": item.invoicePayment}
            self.parent.deleteFromDatabase("InvoicesPayments", whereDict)
            
            whereDict = {"idNum": glPostingId}
            self.parent.deleteFromDatabase("GLPostings", whereDict)
            
            whereDict = {"GLPostingId": glPostingId}
            self.parent.deleteFromDatabase("GLPostingsDetails", whereDict)
            
            self.parent.dbConn.commit()
            
            # Refresh data
            self.parent.refreshOpenInvoiceTree()
            self.parent.refreshPaidInvoicesTreeWidget()
            self.parent.updateVendorTree.emit()

            # Remove payment from tree widget
            idxToDelete = self.paymentHistory.indexOfTopLevelItem(item)
            self.paymentHistory.takeTopLevelItem(idxToDelete)
    
    def getAcceptedProposalsOfAssetProject(self):
        listOfAcceptedProposals = []
        selection = self.assetProjSelector.selector.currentText()
        selectionId = self.parent.stripAllButNumbers(selection)
        
        if selectionId:
            if self.assetProjSelector.assetSelected() == True:
                type_ = 'assets'
            else:
                type_ = 'projects'
            
            self.dbCur.execute("""SELECT Proposals.idNum FROM Proposals
                                  LEFT JOIN ProposalsObjects
                                  ON Proposals.idNum = ProposalsObjects.ProposalId
                                  WHERE Status=? AND ObjectType=?
                                        AND ObjectId=?""",
                               (constants.ACC_PROPOSAL_STATUS, type_,
                                selectionId))
            
            for idNum in self.dbCur:
                listOfAcceptedProposals.append(idNum[0])
            
        return listOfAcceptedProposals

    def updateDetailInvoiceWidget(self):
        proposals = self.getAcceptedProposalsOfAssetProject()
        self.detailsWidget.addProposals(proposals)

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.vendorBox.setEnabled(True)
        self.assetProjSelector.setEnabled(True)
        self.invoiceDateText_edit = gui_elements.DateLineEdit(self.invoiceDateText.text())
        self.invoiceDateText_edit.textEdited.connect(self.changed)
        self.dueDateText_edit = gui_elements.DateLineEdit(self.dueDateText.text())
        self.dueDateText_edit.textEdited.connect(self.changed)
        self.detailsWidget.makeEditable()
        self.detailsWidget.detailsHaveChanged.connect(self.changed)
        
        self.layout.addWidget(self.invoiceDateText_edit, 3, 1)
        self.layout.addWidget(self.dueDateText_edit, 4, 1)

    def updateAssetProjSelector(self):
        companyId = self.parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector.updateCompany(companyId)
        self.assetProjSelector.clear()

    def changed(self):
        self.hasChanges = True

class ProposalDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, proposal=None):
        super().__init__(parent)
        self.parent = parent
        self.hasChanges = False
        self.mode = mode

        self.layout = QGridLayout()

        companyLbl = QLabel("Company:")
        vendorLbl = QLabel("Vendor:")
        statusLbl = QLabel("Status:")
        dateLbl = QLabel("Date:")
        
        self.companyBox = QComboBox()
        dbCur.execute("SELECT idNum, ShortName FROM Companies")
        for idNum, shortName in dbCur:
            self.companyBox.addItem(constants.ID_DESC % (idNum, shortName))
        self.companyBox.currentIndexChanged.connect(self.updateAssetProjSelector)
        
        self.vendorBox = QComboBox()
        dbCur.execute("SELECT idNum, Name FROM Vendors")
        for idNum, name in dbCur:
            self.vendorBox.addItem(constants.ID_DESC % (idNum, name))

        self.statusBox = QComboBox()
        self.statusBox.addItems(constants.PROPOSAL_STATUSES)
        
        companyId = parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector = gui_elements.AssetProjSelector(companyId, dbCur)
        
        if self.mode == "View":
            dbCur.execute("""SELECT Companies.idNum, ShortName, Vendors.idNum,
                                    Vendors.Name, ProposalDate, Status,
                                    ObjectType, ObjectId
                             FROM Proposals
                             LEFT JOIN Companies
                             ON Proposals.CompanyId = Companies.idNum
                             LEFT JOIN Vendors
                             ON Proposals.VendorId = Vendors.idNum
                             LEFT JOIN ProposalsObjects
                             ON Proposals.idNum = ProposalsObjects.ProposalId
                             WHERE Proposals.idNum=?""", (proposal,))
            compId, shortName, vendId, vendName, propDate, status, type_, typeId = dbCur.fetchone()
            
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (compId, shortName)))
            self.companyBox.setEnabled(False)
            
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(constants.ID_DESC % (vendId, vendName)))
            self.vendorBox.setEnabled(False)
            
            self.statusBox.setCurrentIndex(self.statusBox.findText(status))
            self.statusBox.setEnabled(False)

            self.assetProjSelector.updateCompany(compId)
            
            if type_ == "assets":
                dbCur.execute("SELECT Description FROM Assets WHERE idNum=?",
                              (typeId,))
                desc = dbCur.fetchone()[0]
                self.assetProjSelector.assetRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(constants.ID_DESC % (typeId, desc)))
            else:
                dbCur.execute("SELECT Description FROM Projects WHERE idNum=?",
                              (typeId,))
                desc = dbCur.fetchone()[0]
                self.assetProjSelector.projRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(constants.ID_DESC % (typeId, desc)))
            self.assetProjSelector.setEnabled(False)
            self.assetProjSelector.show()
            
            self.dateText = QLabel(propDate)
        else:
            self.dateText = gui_elements.DateLineEdit()

        self.layout.addWidget(companyLbl, 0, 0)
        self.layout.addWidget(self.companyBox, 0, 1)
        self.layout.addWidget(self.assetProjSelector, 1, 0, 1, 2)
        self.layout.addWidget(vendorLbl, 2, 0)
        self.layout.addWidget(self.vendorBox, 2, 1)
        nextRow = 3

        if self.mode == "View":
            self.layout.addWidget(statusLbl, nextRow, 0)
            self.layout.addWidget(self.statusBox, nextRow, 1)
            nextRow += 1
            
        self.layout.addWidget(dateLbl, nextRow, 0)
        self.layout.addWidget(self.dateText, nextRow, 1)
        nextRow += 1
        
        if self.mode == "View":
            self.detailsWidget = gui_elements.ProposalDetailWidget(dbCur, proposal)
        else:
            self.detailsWidget = gui_elements.ProposalDetailWidget(dbCur)
        self.layout.addWidget(self.detailsWidget, nextRow, 0, 1, 2)
        nextRow += 1
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Proposal")
        else:
            self.setWindowTitle("New Proposal")

    def accept(self):
        QDialog.accept(self)

    def changed(self):
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.changed)
        
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.changed)
        
        self.assetProjSelector.setEnabled(True)
        self.assetProjSelector.rdoBtnChanged.connect(self.changed)
        self.assetProjSelector.selectorChanged.connect(self.changed)
        
        self.statusBox.setEnabled(True)
        self.statusBox.currentIndexChanged.connect(self.changed)
        
        self.dateText_edit = gui_elements.DateLineEdit(self.dateText.text())
        self.dateText_edit.textEdited.connect(self.changed)
        self.layout.addWidget(self.dateText_edit, 4, 1)
        
        self.detailsWidget.makeEditable()
        self.detailsWidget.detailsHaveChanged.connect(self.changed)
        
    def updateAssetProjSelector(self):
        companyId = self.parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector.updateCompany(companyId)
        self.assetProjSelector.clear()
        
class ProjectDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self.hasChanges = False
        
        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        startDateLbl = QLabel("Start Date:")
        self.endDateLbl = QLabel("End Date:")
        statusLbl = QLabel("Status:")
        statusReasonLbl = QLabel("Reason:")
        glAccountLbl = QLabel("GL Account:")
        
        self.companyBox = QComboBox()
        dbCur.execute("SELECT idNum, ShortName FROM Companies")
        for idNum, shortName in dbCur:
            self.companyBox.addItem(constants.ID_DESC % (idNum, shortName))
        
        self.glAccountsBox = QComboBox()
        dbCur.execute("SELECT idNum, Description FROM GLAccounts")
        for idNum, desc in dbCur:
            self.glAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
        
        if mode == "View":
            dbCur.execute("""SELECT Projects.Description, DateStart, DateEnd,
                                    Status, Notes, GLAccount,
                                    GLAccounts.Description, CompanyId,
                                    ShortName
                             FROM Projects
                             JOIN Companies
                             ON Projects.CompanyId = Companies.idNum
                             JOIN GLAccounts
                             ON Projects.GLAccount = GLAccounts.idNum
                             WHERE Projects.idNum=?""", (project,))
            desc, dtStart, dtEnd, status, notes, glAcct, glDesc, companyId, shortName = dbCur.fetchone()
            
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (companyId, shortName)))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(desc)
            self.startDateText = QLabel(dtStart)
            self.endDateText = gui_elements.DateLineEdit(dtEnd)
            self.statusBox = QComboBox()
            self.statusBox.addItems(constants.PROJECT_STATUSES)
            self.statusBox.setCurrentIndex(self.statusBox.findText(status))
            self.statusBox.setEnabled(False)
            self.statusReasonText = QLabel(notes)
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(constants.ID_DESC % (glAcct, glDesc)))
            self.glAccountsBox.setEnabled(False)
            self.invoicesTreeWidget = gui_elements.InvoiceTreeWidget(dbCur, None, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH, "projects.%d" % project)
        else:
            self.descriptionText = QLineEdit()
            self.startDateText = gui_elements.DateLineEdit()
            self.endDateText = gui_elements.DateLineEdit()
        
        self.layout.addWidget(companyLbl, 0, 0)
        self.layout.addWidget(self.companyBox, 0, 1)
        self.layout.addWidget(descriptionLbl, 1, 0)
        self.layout.addWidget(self.descriptionText, 1, 1)
        self.layout.addWidget(startDateLbl, 2, 0)
        self.layout.addWidget(self.startDateText, 2, 1)
        self.layout.addWidget(self.endDateLbl, 3, 0)
        self.layout.addWidget(self.endDateText, 3, 1)
        self.layout.addWidget(glAccountLbl, 4, 0)
        self.layout.addWidget(self.glAccountsBox, 4, 1)
        nextRow = 5
        
        if mode == "View":
            self.layout.addWidget(statusLbl, nextRow, 0)
            self.layout.addWidget(self.statusBox, nextRow, 1)
            nextRow += 1
            
            self.layout.addWidget(statusReasonLbl, nextRow, 0)
            self.layout.addWidget(self.statusReasonText, nextRow, 1)
            nextRow += 1
            
            subLayout = QHBoxLayout()

            buttonWidget = gui_elements.StandardButtonWidget()
            buttonWidget.newButton.clicked.connect(self.newInvoice)
            buttonWidget.viewButton.clicked.connect(self.viewInvoice)
            buttonWidget.deleteButton.clicked.connect(self.deleteInvoice)
            
            subLayout.addWidget(self.invoicesTreeWidget)
            subLayout.addWidget(buttonWidget)
            self.layout.addLayout(subLayout, nextRow, 0, 1, 2)
            nextRow += 1

        self.endDateLbl.hide()
        self.endDateText.hide()

        buttonLayout = QHBoxLayout()
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Project")
        else:
            self.setWindowTitle("New Project")

    def newInvoice(self):
        pass

    def viewInvoice(self):
        pass

    def deleteInvoice(self):
        pass
    
    def changed(self):
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.changed)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.startDateText_edit = gui_elements.DateLineEdit(self.startDateText.text())
        self.startDateText_edit.textEdited.connect(self.changed)
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.changed)

        self.endDateText.textEdited.connect(self.changed)

        self.layout.addWidget(self.descriptionText_edit, 1, 1)
        self.layout.addWidget(self.startDateText_edit, 2, 1)

class CompanyDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, company=None):
        super().__init__(parent)
        self.hasChanges = False

        self.layout = QGridLayout()
        
        nameLbl = QLabel("Name:")
        shortNameLbl = QLabel("Short Name:")
        
        if mode == "View":
            activeLbl = QLabel("Active:")
            self.activeChk = QCheckBox()
            self.activeChk.setEnabled(False)
            
            dbCur.execute("""SELECT Name, ShortName, Active
                            FROM Companies WHERE idNum=?""",
                          (company,))
            name, shortName, active = dbCur.fetchone()
            self.nameText = QLabel(name)
            self.shortNameText = QLabel(shortName)
            self.activeChk.setCheckState(active)
        else:
            self.nameText = QLineEdit()
            self.shortNameText = QLineEdit()
        
        self.layout.addWidget(nameLbl, 0, 0)
        self.layout.addWidget(self.nameText, 0, 1)
        self.layout.addWidget(shortNameLbl, 1, 0)
        self.layout.addWidget(self.shortNameText, 1, 1)
        nextRow = 2

        if mode == "View":
            self.layout.addWidget(activeLbl, nextRow, 0)
            self.layout.addWidget(self.activeChk, nextRow, 1)
            nextRow += 1

        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Company")
        else:
            self.setWindowTitle("New Company")
        
    def changed(self):
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.nameText_edit = QLineEdit(self.nameText.text())
        self.nameText_edit.textEdited.connect(self.changed)
        
        self.shortNameText_edit = QLineEdit(self.shortNameText.text())
        self.shortNameText_edit.textEdited.connect(self.changed)

        self.activeChk.setEnabled(True)
        self.activeChk.stateChanged.connect(self.changed)
        
        self.layout.addWidget(self.nameText_edit, 0, 1)
        self.layout.addWidget(self.shortNameText_edit, 1, 1)

class AssetDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, asset=None):
        super().__init__(parent)
        self.parent = parent
        self.dbCur = dbCur
        self.hasChanges = False
        
        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        assetTypeLbl = QLabel("Asset Type:")
        childOfLbl = QLabel("Child of:")
        dateAcquiredLbl = QLabel("Date Acquired:")
        dateInSvcLbl = QLabel("Date in Service:")
        self.usefulLifeLbl = QLabel("Useful Life:")
        self.depMethodLbl = QLabel("Depreciation Method:")
        self.salvageValueLbl = QLabel("Salvage Amount:")
        costLbl = QLabel("Cost:")
        
        self.companyBox = QComboBox()
        dbCur.execute("SELECT idNum, ShortName FROM Companies")
        for idNum, shortName in dbCur:
            self.companyBox.addItem(constants.ID_DESC % (idNum, shortName))
        
        self.assetTypeBox = QComboBox()
        dbCur.execute("SELECT idNum, AssetType FROM AssetTypes")
        for idNum, desc in dbCur:
            self.assetTypeBox.addItem(constants.ID_DESC % (idNum, desc))
        
        self.childOfAssetBox = QComboBox()
        self.childOfAssetBox.addItem("")
        dbCur.execute("SELECT idNum, Description FROM Assets")
        for idNum, desc in dbCur:
            self.childOfAssetBox.addItem(constants.ID_DESC % (idNum, desc))
        
        self.depMethodBox = QComboBox()
        self.depMethodBox.addItems(constants.DEP_METHODS)
        
        if mode == "View":
            dbCur.execute("""SELECT a.CompanyId, ShortName, a.AssetTypeId,
                                    AssetType, a.Description,
                                    a.ParentAssetId, b.Description,
                                    a.AcquireDate, a.InSvcDate,
                                    a.UsefulLife, a.SalvageAmount,
                                    a.DepreciationMethod, Depreciable
                             FROM Assets a JOIN AssetTypes
                             ON AssetTypes.idNum = a.AssetTypeId
                             LEFT JOIN Assets b
                             ON a.ParentAssetId = b.idNum
                             JOIN Companies
                             ON a.CompanyId = Companies.idNum
                             WHERE a.idNum=?""", (asset,))
            compId, compName, assetTypeId, assetTypeDesc, desc, parentId, parentDesc, acqDate, inSvcDate, usefulLife, salvAmt, depMethod, dep = dbCur.fetchone()
            assetCost = functions.CalculateAssetCost(dbCur, asset)
            
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (compId, compName)))
            self.descriptionText = QLineEdit(desc)
            self.assetTypeBox.setCurrentIndex(self.assetTypeBox.findText(constants.ID_DESC % (assetTypeId, assetTypeDesc)))
            if not parentId:
                subAssetOfText = ""
            else:
                subAssetOfText = constants.ID_DESC % (parentId, parentDesc)
            self.childOfAssetBox.setCurrentIndex(self.childOfAssetBox.findText(subAssetOfText))
            self.dateAcquiredText = gui_elements.DateLineEdit(acqDate)
            self.dateInSvcText = gui_elements.DateLineEdit(inSvcDate)
            self.usefulLifeText = QLineEdit(str(usefulLife))
            self.depMethodBox.setCurrentIndex(self.depMethodBox.findText(depMethod))
            self.salvageValueText = QLineEdit(str(salvAmt))
            self.costText = QLabel(str(assetCost))

            self.companyBox.setEnabled(False)
            self.descriptionText.setEnabled(False)
            self.assetTypeBox.setEnabled(False)
            self.childOfAssetBox.setEnabled(False)
            self.dateAcquiredText.setEnabled(False)
            self.dateInSvcText.setEnabled(False)
            self.usefulLifeText.setEnabled(False)
            self.depMethodBox.setEnabled(False)
            self.salvageValueText.setEnabled(False)
        else:
            self.descriptionText = QLineEdit()
            self.dateAcquiredText = gui_elements.DateLineEdit()
            self.dateInSvcText = gui_elements.DateLineEdit()
            self.usefulLifeText = QLineEdit()
            self.salvageValueText = QLineEdit()
            self.costText = QLabel()

            costLbl.hide()
            self.costText.hide()
        
        self.assetTypeBox.currentIndexChanged.connect(self.showHideDisposalInfo)
        
        self.layout.addWidget(companyLbl, 0, 0)
        self.layout.addWidget(self.companyBox, 0, 1)
        self.layout.addWidget(descriptionLbl, 1, 0)
        self.layout.addWidget(self.descriptionText, 1, 1)
        self.layout.addWidget(assetTypeLbl, 2, 0)
        self.layout.addWidget(self.assetTypeBox, 2, 1)
        self.layout.addWidget(childOfLbl, 3, 0)
        self.layout.addWidget(self.childOfAssetBox, 3, 1)
        self.layout.addWidget(dateAcquiredLbl, 4, 0)
        self.layout.addWidget(self.dateAcquiredText, 4, 1)
        self.layout.addWidget(dateInSvcLbl, 5, 0)
        self.layout.addWidget(self.dateInSvcText, 5, 1)
        self.layout.addWidget(self.usefulLifeLbl, 6, 0)
        self.layout.addWidget(self.usefulLifeText, 6, 1)
        self.layout.addWidget(self.depMethodLbl, 7, 0)
        self.layout.addWidget(self.depMethodBox, 7, 1)
        self.layout.addWidget(self.salvageValueLbl, 8, 0)
        self.layout.addWidget(self.salvageValueText, 8, 1)
        self.layout.addWidget(costLbl, 9, 0)
        self.layout.addWidget(self.costText, 9, 1)
        nextRow = 10
        
        if mode == "View":
            self.historyTreeWidget = gui_elements.AssetHistoryTreeWidget(self.dbCur, constants.ASSET_HIST_HDR_LIST, constants.ASSET_HIST_HDR_WDTH, asset)
            self.layout.addWidget(self.historyTreeWidget, nextRow, 0, 1, 2)
            nextRow += 1

        #########
        ## Add a list of proposal (tree widget)
        #########

        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.layout.addWidget(buttonWidget, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Asset")
        else:
            self.setWindowTitle("New Asset")
        
        self.showHideDisposalInfo()
        
    def showHideDisposalInfo(self):
        assetTypeId = self.parent.stripAllButNumbers(self.assetTypeBox.currentText())
        if assetTypeId:
            self.dbCur.execute("SELECT Depreciable FROM AssetTypes WHERE idNum=?",
                               (assetTypeId,))
            depreciable = bool(self.dbCur.fetchone()[0])
            if depreciable == False:
                self.usefulLifeLbl.hide()
                self.usefulLifeText.hide()
                self.depMethodLbl.hide()
                self.depMethodBox.hide()
                self.salvageValueLbl.hide()
                self.salvageValueText.hide()
            else:
                self.usefulLifeLbl.show()
                self.usefulLifeText.show()
                self.depMethodLbl.show()
                self.depMethodBox.show()
                self.salvageValueLbl.show()
                self.salvageValueText.show()

            self.resize()

    def changed(self):
        self.hasChanges = True
    
    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.descriptionText.setEnabled(True)
        self.assetTypeBox.setEnabled(True)
        self.childOfAssetBox.setEnabled(True)
        self.dateAcquiredText.setEnabled(True)
        self.dateInSvcText.setEnabled(True)
        self.usefulLifeText.setEnabled(True)
        self.depMethodBox.setEnabled(True)
        self.salvageValueText.setEnabled(True)
        
        self.companyBox.currentIndexChanged.connect(self.changed)
        self.descriptionText.textEdited.connect(self.changed)
        self.assetTypeBox.currentIndexChanged.connect(self.changed)
        self.childOfAssetBox.currentIndexChanged.connect(self.changed)
        self.dateAcquiredText.textEdited.connect(self.changed)
        self.dateInSvcText.textEdited.connect(self.changed)
        self.usefulLifeText.textEdited.connect(self.changed)
        self.depMethodBox.currentIndexChanged.connect(self.changed)
        self.salvageValueText.textEdited.connect(self.changed)

    def resize(self):
        self.setFixedSize(self.sizeHint())

class InvoicePaymentDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, invoice=None, invoicePayment=None):
        super().__init__(parent)
        self.hasChanges = False
        
        vendorLbl = QLabel("Vendor:")
        invoiceLbl = QLabel("Invoice:")
        paymentTypeLbl = QLabel("Payment Type:")
        datePaidLbl = QLabel("Date Paid:")
        amountLbl = QLabel("Amount:")
        
        self.paymentTypeBox = QComboBox()
        dbCur.execute("SELECT idNum, Description FROM PaymentTypes")
        for idNum, desc in dbCur:
            self.paymentTypeBox.addItem(constants.ID_DESC % (idNum, desc))

        dbCur.execute("""SELECT Name FROM Vendors
                         JOIN Invoices ON Vendors.idNum = Invoices.VendorId
                         WHERE Invoices.idNum=?""", (invoice,))
        name = dbCur.fetchone()[0]
        self.vendorText = QLabel(name)
        self.invoiceText = QLabel(str(invoice))
        
        if mode == "View":
            dbCur.execute("""SELECT DatePaid, AmountPaid, PaymentTypeId,
                                    Description
                             FROM InvoicesPayments JOIN PaymentTypes
                             ON InvoicesPayments.PaymentTypeId = PaymentTypes.idNum
                             WHERE InvoicesPayments.idNum=?""",
                          (invoicePayment,))
            datePd, amtPd, pymtTypeId, pymtTypeDesc = dbCur.fetchone()
            
            self.datePaidText = gui_elements.DateLineEdit(datePd)
            self.datePaidText.setEnabled(False)
            self.amountText = QLineEdit(str(amtPd))
            self.amountText.setEnabled(False)
            self.paymentTypeBox.setCurrentIndex(self.paymentTypeBox.findText(constants.ID_DESC % (pymtTypeId, pymtTypeDesc)))
            self.paymentTypeBox.setEnabled(False)
        else:
            balance = functions.CalculateInvoiceBalance(dbCur, invoice)
            
            self.datePaidText = gui_elements.DateLineEdit()
            self.amountText = QLineEdit(str(balance))
        
        self.layout = QGridLayout()
        self.layout.addWidget(vendorLbl, 0, 0)
        self.layout.addWidget(self.vendorText, 0, 1)
        self.layout.addWidget(invoiceLbl, 1, 0)
        self.layout.addWidget(self.invoiceText, 1, 1)
        self.layout.addWidget(paymentTypeLbl, 2, 0)
        self.layout.addWidget(self.paymentTypeBox, 2, 1)
        self.layout.addWidget(datePaidLbl, 3, 0)
        self.layout.addWidget(self.datePaidText, 3, 1)
        self.layout.addWidget(amountLbl, 4, 0)
        self.layout.addWidget(self.amountText, 4, 1)
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        self.layout.addWidget(buttonWidget, 5, 0, 1, 2)
        self.setLayout(self.layout)
        
        if mode == "View":
            self.setWindowTitle("View/Edit Invoice Payment")
        else:
            self.setWindowTitle("New Invoice Payment")
        
    def changed(self):
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.datePaidText.setEnabled(True)
        self.datePaidText.textEdited.connect(self.changed)
        self.amountText.setEnabled(True)
        self.amountText.textEdited.connect(self.changed)
        
class ChangeProposalStatusDialog(QDialog):
    def __init__(self, proposalStatus, parent=None):
        super().__init__(parent)

        statusLbl = QLabel("Reason:")
        self.statusTxt = QLineEdit()

        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        layout = QGridLayout()
        layout.addWidget(statusLbl, 0, 0)
        layout.addWidget(self.statusTxt, 0, 1)
        layout.addWidget(buttonWidget, 1, 0, 1, 2)
        
        self.setLayout(layout)

        self.setWindowTitle(proposalStatus + " Proposal")

class CIPAllocationDialog(QDialog):
    def __init__(self, project, dbCur, parent=None):
        super().__init__(parent)
        self.cip = functions.CalculateCIP(dbCur, project)
        
        self.gridLayout = QGridLayout()
        cipLbl = QLabel("CIP")
        cipAmt = QLabel(str(self.cip))
        self.details = gui_elements.CIPAllocationDetailWidget(self, self.cip)
        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")

        self.gridLayout.addWidget(cipLbl, 0, 0)
        self.gridLayout.addWidget(cipAmt, 0, 1)
        self.gridLayout.addWidget(self.details, 2, 0, 1, 2)
        self.gridLayout.addWidget(buttonWidget)
        
        # Add functionality
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.setLayout(self.gridLayout)
        self.setWindowTitle("Allocate Project Costs")
        
class CloseProjectDialog(QDialog):
    def __init__(self, status, dbCur, parent=None, assetName=""):
        super().__init__(parent)
        self.parent = parent
        self.dbCur = dbCur

        layout = QGridLayout()
        
        dateLbl = QLabel("Date:")
        self.dateTxt = gui_elements.DateLineEdit()

        layout.addWidget(dateLbl, 0, 0)
        layout.addWidget(self.dateTxt, 0, 1)
        nextRow = 1

        if status == constants.ABD_PROJECT_STATUS:
            reasonLbl = QLabel("Reason:")
            self.reasonTxt = QLineEdit()

            glLbl = QLabel("Expense Acct:")
            self.glBox = QComboBox()
            dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                             WHERE Placeholder=0""")
            for idNum, desc in dbCur:
                self.glBox.addItem(constants.ID_DESC % (idNum, desc))
                
            layout.addWidget(reasonLbl, nextRow, 0)
            layout.addWidget(self.reasonTxt, nextRow, 1)
            nextRow += 1

            layout.addWidget(glLbl, nextRow, 0)
            layout.addWidget(self.glBox, nextRow, 1)
            nextRow += 1
        elif status == constants.CMP_PROJECT_STATUS:
            assetNameLbl = QLabel("Asset Name:")
            self.assetNameTxt = QLineEdit(assetName)

            inSvcLbl = QLabel("In Use:")
            self.inSvcChk = QCheckBox()

            childOfLbl = QLabel("Child of:")
            self.childOfAssetBox = QComboBox()
            self.childOfAssetBox.addItem("")
            self.childOfAssetBox.addItems(parent.parent.dataConnection.assets.sortedListOfKeysAndNames())

            self.usefulLifeLbl = QLabel("Useful Life:")
            self.usefulLifeTxt = QLineEdit()

            assetTypeLbl = QLabel("Asset Type:")
            self.assetTypeBox = QComboBox()
            self.assetTypeBox.addItems(parent.parent.dataConnection.assetTypes.sortedListOfKeysAndNames())
            self.assetTypeBox.currentIndexChanged.connect(self.showHideDisposalInfo)

            self.depMethodLbl = QLabel("Depreciation Method:")
            self.depMethodBox = QComboBox()
            self.depMethodBox.addItems(constants.DEP_METHODS)
        
            self.salvageValueLbl = QLabel("Salvage Amount:")
            self.salvageValueText = QLineEdit()
            
            layout.addWidget(assetNameLbl, nextRow, 0)
            layout.addWidget(self.assetNameTxt, nextRow, 1)
            nextRow += 1

            layout.addWidget(assetTypeLbl, nextRow, 0)
            layout.addWidget(self.assetTypeBox, nextRow, 1)
            nextRow += 1

            layout.addWidget(childOfLbl, nextRow, 0)
            layout.addWidget(self.childOfAssetBox, nextRow, 1)
            nextRow += 1

            layout.addWidget(inSvcLbl, nextRow, 0)
            layout.addWidget(self.inSvcChk, nextRow, 1)
            nextRow += 1

            layout.addWidget(self.usefulLifeLbl, nextRow, 0)
            layout.addWidget(self.usefulLifeTxt, nextRow, 1)
            nextRow += 1

            layout.addWidget(self.depMethodLbl, nextRow, 0)
            layout.addWidget(self.depMethodBox, nextRow, 1)
            nextRow += 1

            layout.addWidget(self.salvageValueLbl, nextRow, 0)
            layout.addWidget(self.salvageValueText, nextRow, 1)
            nextRow += 1

            self.showHideDisposalInfo()

        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        layout.addWidget(buttonWidget, nextRow, 0, 1, 2)

        self.setLayout(layout)
        
        self.setWindowTitle(status + "Project")

    def showHideDisposalInfo(self):
        assetTypeId = self.parent.stripAllButNumbers(self.assetTypeBox.currentText())
        self.dbCur.execute("SELECT Depreciable FROM AssetTypes WHERE idNum=?",
                           (assetTypeId,))
        depreciable = bool(self.dbCur.fetchone()[0])
        if depreciable == False:
            self.usefulLifeLbl.hide()
            self.usefulLifeTxt.hide()
            self.depMethodLbl.hide()
            self.depMethodBox.hide()
            self.salvageValueLbl.hide()
            self.salvageValueText.hide()
        else:
            self.usefulLifeLbl.show()
            self.usefulLifeTxt.show()
            self.depMethodLbl.show()
            self.depMethodBox.show()
            self.salvageValueLbl.show()
            self.salvageValueText.show()

        self.resize()

    def resize(self):
        self.setFixedSize(self.sizeHint())
        
class NewAssetTypeDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, assetType=None):
        super().__init__(parent)
        self.hasChanges = False
        
        nameLbl = QLabel("Name:")
        depLbl = QLabel("Depreciable:")
        assetGLLbl = QLabel("Asset GL:")
        self.expenseGLLbl = QLabel("Dep. GL:")
        self.accumExpenseGLLbl = QLabel("Accum. Dep. GL:")
        self.depChk = QCheckBox()
        self.depChk.stateChanged.connect(self.showHideGLBoxes)
        
        self.glAssetAccountsBox = QComboBox()
        self.glExpenseAccountsBox = QComboBox()
        self.glExpenseAccountsBox.addItem("")
        self.glAccumExpenseAccountsBox = QComboBox()
        self.glAccumExpenseAccountsBox.addItem("")

        dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                         WHERE Placeholder=0""")
        for idNum, desc in dbCur:
            self.glAssetAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
            self.glExpenseAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
            self.glAccumExpenseAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
        
        if mode == "View":
            dbCur.execute("""SELECT AssetType, Depreciable, AssetGL,
                                    a.Description, AmortGL, b.Description,
                                    AccumAmortGL, c.Description
                             FROM AssetTypes
                             JOIN GLAccounts a ON a.idNum = AssetGL
                             LEFT JOIN GLAccounts b ON b.idNum = AmortGL
                             LEFT JOIN GLAccounts c ON c.idNum = AccumAmortGL
                             WHERE AssetTypes.idNum=?""", (assetType,))
            assetType, depreciable, assetGL, assetGLDesc, amortGL, amortGLDesc, accumGL, accumGLDesc = dbCur.fetchone()
            self.nameTxt = QLineEdit(assetType)
            self.glAssetAccountsBox.setCurrentIndex(self.glAssetAccountsBox.findText(constants.ID_DESC % (assetGL, assetGLDesc)))
            if bool(depreciable) == True:
                self.depChk.setCheckState(Qt.Checked)
                self.glExpenseAccountsBox.setCurrentIndex(self.glExpenseAccountsBox.findText(constants.ID_DESC % (amortGL, amortGLDesc)))
                self.glAccumExpenseAccountsBox.setCurrentIndex(self.glAccumExpenseAccountsBox.findText(constants.ID_DESC % (accumGL, accumGLDesc)))
            else:
                self.expenseGLLbl.hide()
                self.accumExpenseGLLbl.hide()
                self.glExpenseAccountsBox.hide()
                self.glAccumExpenseAccountsBox.hide()
            self.nameTxt.setEnabled(False)
            self.depChk.setEnabled(False)
            self.glAssetAccountsBox.setEnabled(False)
            self.glExpenseAccountsBox.setEnabled(False)
            self.glAccumExpenseAccountsBox.setEnabled(False)
        else:
            self.nameTxt = QLineEdit()
            self.depChk.setCheckState(Qt.Checked)
            
        buttonLayout = QHBoxLayout()
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        layout = QGridLayout()
        layout.addWidget(nameLbl, 0, 0)
        layout.addWidget(self.nameTxt, 0, 1)
        layout.addWidget(depLbl, 1, 0)
        layout.addWidget(self.depChk, 1, 1)
        layout.addWidget(assetGLLbl, 2, 0)
        layout.addWidget(self.glAssetAccountsBox, 2, 1)
        layout.addWidget(self.expenseGLLbl, 3, 0)
        layout.addWidget(self.glExpenseAccountsBox, 3, 1)
        layout.addWidget(self.accumExpenseGLLbl, 4, 0)
        layout.addWidget(self.glAccumExpenseAccountsBox, 4, 1)
        layout.addWidget(buttonWidget, 5, 0, 1, 2)
        
        self.setLayout(layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Asset Type")
        else:
            self.setWindowTitle("New Asset Type")

    def changed(self):
        self.hasChanges = True
    
    def makeLabelsEditable(self):
        self.nameTxt.setEnabled(True)
        self.nameTxt.textEdited.connect(self.changed)
        self.glAssetAccountsBox.setEnabled(True)
        self.glAssetAccountsBox.currentIndexChanged.connect(self.changed)
        self.glExpenseAccountsBox.setEnabled(True)
        self.glExpenseAccountsBox.currentIndexChanged.connect(self.changed)
        self.glAccumExpenseAccountsBox.setEnabled(True)
        self.glAccumExpenseAccountsBox.currentIndexChanged.connect(self.changed)

    def showHideGLBoxes(self, state):
        if state == Qt.Checked:
            self.expenseGLLbl.show()
            self.accumExpenseGLLbl.show()
            self.glExpenseAccountsBox.show()
            self.glAccumExpenseAccountsBox.show()
        else:
            self.glExpenseAccountsBox.setCurrentIndex(0)
            self.glAccumExpenseAccountsBox.setCurrentIndex(0)

            self.expenseGLLbl.hide()
            self.accumExpenseGLLbl.hide()
            self.glExpenseAccountsBox.hide()
            self.glAccumExpenseAccountsBox.hide()

        self.resize()
        
    def resize(self):
        self.setFixedSize(self.sizeHint())
        
class AssetTypeDialog(QDialog):
    def __init__(self, dbCur, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dbCur = dbCur
        
        layout = QHBoxLayout()

        self.listWidget = QListWidget()
        dbCur.execute("SELECT idNum, AssetType FROM AssetTypes")
        for idNum, desc in dbCur:
            self.listWidget.addItem(constants.ID_DESC % (idNum, desc))
        self.listWidget.setCurrentRow(0)

        buttonLayout = gui_elements.StandardButtonWidget()
        buttonLayout.newButton.clicked.connect(self.newAssetType)
        buttonLayout.viewButton.clicked.connect(self.showAssetType)
        buttonLayout.deleteButton.clicked.connect(self.deleteAssetType)
        buttonLayout.addSpacer()
        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.reject)
        buttonLayout.addButton(closeBtn)
        
        layout.addWidget(self.listWidget)
        layout.addWidget(buttonLayout)

        self.setLayout(layout)

        self.setWindowTitle("Asset Types")

    def newAssetType(self):
        dialog = NewAssetTypeDialog("New", self.dbCur, self)
        if dialog.exec_():
            nextAssetTypeId = self.parent.nextIdNum("AssetTypes")
            name = dialog.nameTxt.text()
            assetGLAccountNum = self.parent.stripAllButNumbers(dialog.glAssetAccountsBox.currentText())
            
            if dialog.depChk.checkState() == Qt.Checked:
                depreciable = 1
                expenseGLAccountNum = self.parent.stripAllButNumbers(dialog.glExpenseAccountsBox.currentText())
                accumExpenseGLAccountNum = self.parent.stripAllButNumbers(dialog.glAccumExpenseAccountsBox.currentText())
            else:
                depreciable = 0
                expenseGLAccountNum = None
                accumExpenseGLAccountNum = None
            
            self.listWidget.addItem(constants.ID_DESC % (nextAssetTypeId, name))

            columns = ("AssetType", "Depreciable", "AssetGL", "AmortGL",
                       "AccumAmortGL")
            values = (name, depreciable, assetGLAccountNum, expenseGLAccountNum,
                      accumExpenseGLAccountNum)
            self.parent.insertIntoDatabase("AssetTypes", columns, values)            
            self.parent.dbConn.commit()

    def showAssetType(self):
        item = self.listWidget.currentItem()
        assetTypeId = self.parent.stripAllButNumbers(item.text())
        
        dialog = NewAssetTypeDialog("View", self.dbCur, self, assetTypeId)
        if dialog.exec_():
            if dialog.hasChanges == True:
                description = dialog.nameTxt.text()
                assetGLNum = self.parent.stripAllButNumbers(dialog.glAssetAccountsBox.currentText())
                if dialog.depChk.checkState() == Qt.Checked:
                    expenseGLNum = self.parent.stripAllButNumbers(dialog.glExpenseAccountsBox.currentText())
                    accumExpGLNum = self.parent.stripAllButNumbers(dialog.glAccumExpenseAccountsBox.currentText())
                else:
                    expenseGLNum = None
                    accumExpGLNum = None
                
                colValDict = {"AssetType": description,
                              "AssetGL": assetGLNum,
                              "AmortGL": expenseGLNum,
                              "AccumAmortGL": accumExpGLNum}
                whereDict = {"idNum": assetTypeId}
                self.parent.updateDatabase("AssetTypes", colValDict, whereDict)
                self.parent.dbConn.commit()

                item.setText(constants.ID_DESC % (assetTypeId, description))

    def deleteAssetType(self):
        item = self.listWidget.currentItem()
        assetTypeId = self.parent.stripAllButNumbers(item.text())

        # Remove from the database
        self.dbCur.execute("SELECT idNum FROM Assets WHERE AssetTypeId=?",
                           (assetTypeId,))
        results = self.dbCur.fetchall()
        if results:
            deleteError = QMessageBox()
            deleteError.setWindowTitle("Can't delete")
            deleteError.setText("Cannot delete an asset type that is in use.")
            deleteError.exec_()
        else:
            self.listWidget.takeItem(self.listWidget.row(item))
            whereDict = {"idNum": assetTypeId}
            self.parent.deleteFromDatabase("AssetTypes", whereDict)
            self.parent.dbConn.commit()

class DisposeAssetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        dispDateLbl = QLabel("Dispose Date:")
        dispAmtLbl = QLabel("Disposal Amount:")
        self.dispDateTxt = gui_elements.DateLineEdit()
        self.dispAmtTxt = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(dispDateLbl, 0, 0)
        layout.addWidget(self.dispDateTxt, 0, 1)
        layout.addWidget(dispAmtLbl, 1, 0)
        layout.addWidget(self.dispAmtTxt, 1, 1)
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        layout.addWidget(buttonWidget, 2, 0, 1, 2)
        self.setLayout(layout)

        self.setWindowTitle("Dispose of Asset")

class GLAccountDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, glAccount=None):
        super().__init__(parent)
        self.hasChanges = False

        self.layout = QGridLayout()
        
        accountNumLbl = QLabel("Account #:")
        descriptionLbl = QLabel("Description:")
        acctGrpLbl = QLabel("Account Group:")
        self.listOfAcctGrpsLbl = QLabel("Group under...")
        
        self.acctGrpsBox = QComboBox()
        dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                         WHERE Placeholder=1""")
        for idNum, desc in dbCur:
            self.acctGrpsBox.addItem(constants.ID_DESC % (idNum, desc))
        
        if mode == "View":
            dbCur.execute("""SELECT Description, Placeholder FROM GLAccounts
                             WHERE idNum=?""", (glAccount,))
            desc, placeHolder = dbCur.fetchone()
            
            self.accountNumText = QLabel(str(glAccount))
            self.descriptionText = QLabel(desc)
            self.acctGrpChk = QCheckBox()
            if bool(placeHolder) == True:
                self.acctGrpChk.setCheckState(Qt.Checked)
                self.listOfAcctGrpsLbl.hide()
                self.acctGrpsBox.hide()
            else:
                dbCur.execute("""SELECT a.ParentGL, b.Description
                                 FROM GLAccounts a
                                 JOIN GLAccounts b
                                 ON a.ParentGL = b.idNum
                                 WHERE a.idNum=?""", (glAccount,))
                parentGL, parentDesc = dbCur.fetchone()
                self.acctGrpChk.setCheckState(Qt.Unchecked)
                self.acctGrpsBox.setCurrentIndex(self.acctGrpsBox.findText(constants.ID_DESC % (parentGL, parentDesc)))
            self.acctGrpsBox.setEnabled(False)
            self.acctGrpChk.setEnabled(False)
        else:
            self.accountNumText = QLineEdit()
            self.descriptionText = QLineEdit()
            self.acctGrpChk = QCheckBox()
            self.acctGrpChk.setCheckState(Qt.Checked)
            self.acctGrpChk.stateChanged.connect(self.showHideAcctGrpBox)
            
            self.listOfAcctGrpsLbl.hide()
            self.acctGrpsBox.hide()

        self.layout.addWidget(accountNumLbl, 0, 0)
        self.layout.addWidget(self.accountNumText, 0, 1)
        self.layout.addWidget(descriptionLbl, 1, 0)
        self.layout.addWidget(self.descriptionText, 1, 1)
        self.layout.addWidget(acctGrpLbl, 2, 0)
        self.layout.addWidget(self.acctGrpChk, 2, 1)
        self.layout.addWidget(self.listOfAcctGrpsLbl, 3, 0)
        self.layout.addWidget(self.acctGrpsBox, 3, 1)
        
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.layout.addWidget(buttonWidget, 4, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit GL Account")
        else:
            self.setWindowTitle("New GL Account")

    def changed(self):
        self.hasChanges = True

    def accountGroupChange(self):
        self.hasChanges = True
        self.accountGroupChanged = True

    def makeLabelsEditable(self):
        self.accountNumText_edit = QLineEdit(self.accountNumText.text())
        self.accountNumText_edit.textEdited.connect(self.changed)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.acctGrpsBox.setEnabled(True)
        self.acctGrpsBox.currentIndexChanged.connect(self.accountGroupChange)

        self.layout.addWidget(self.accountNumText_edit, 0, 1)
        self.layout.addWidget(self.descriptionText_edit, 1, 1)

    def showHideAcctGrpBox(self, state):
        if state == Qt.Checked:
            self.listOfAcctGrpsLbl.hide()
            self.acctGrpsBox.hide()
        else:
            self.listOfAcctGrpsLbl.show()
            self.acctGrpsBox.show()

class NewPaymentTypeDialog(QDialog):
    def __init__(self, mode, dbCur, parent=None, paymentType=None):
        super().__init__(parent)
        self.hasChanges = False
        
        nameLbl = QLabel("Name:")
        glLbl = QLabel("GL Account:")
        
        self.glAccountsBox = QComboBox()
        dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                         WHERE Placeholder=0""")
        for idNum, desc in dbCur:
            self.glAccountsBox.addItem(constants.ID_DESC % (idNum, desc))
        
        if mode == "View":
            dbCur.execute("""SELECT PaymentTypes.Description, GLAccount,
                                    GLAccounts.Description
                             FROM PaymentTypes
                             JOIN GLAccounts
                             ON PaymentTypes.GLAccount = GLAccounts.idNUM
                             WHERE PaymentTypes.idNum=?""", (paymentType,))
            desc, glAcct, glDesc = dbCur.fetchone()
            
            self.nameTxt = QLineEdit(desc)
            self.nameTxt.setEnabled(False)
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(constants.ID_DESC % (glAcct, glDesc)))
            self.glAccountsBox.setEnabled(False)
        else:
            self.nameTxt = QLineEdit()
            
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.layout = QGridLayout()
        self.layout.addWidget(nameLbl, 0, 0)
        self.layout.addWidget(self.nameTxt, 0, 1)
        self.layout.addWidget(glLbl, 2, 0)
        self.layout.addWidget(self.glAccountsBox, 2, 1)
        self.layout.addWidget(buttonWidget, 5, 0, 1, 2)
        
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Payment Type")
        else:
            self.setWindowTitle("New Payment Type")

    def changed(self):
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.nameTxt.setEnabled(True)
        self.nameTxt.textEdited.connect(self.changed)
        
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.changed)
            
class PaymentTypeDialog(QDialog):
    def __init__(self, dbCur, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.dbCur = dbCur
        
        layout = QHBoxLayout()

        self.listWidget = QListWidget()
        dbCur.execute("SELECT idNum, Description FROM PaymentTypes")
        for idNum, desc in dbCur:
            self.listWidget.addItem(constants.ID_DESC % (idNum, desc))
        self.listWidget.setCurrentRow(0)

        buttonLayout = gui_elements.StandardButtonWidget()
        buttonLayout.newButton.clicked.connect(self.newPaymentType)
        buttonLayout.viewButton.clicked.connect(self.showPaymentType)
        buttonLayout.deleteButton.clicked.connect(self.deletePaymentType)
        buttonLayout.addSpacer()
        closeBtn = QPushButton("Close")
        closeBtn.clicked.connect(self.reject)
        buttonLayout.addButton(closeBtn)
        
        layout.addWidget(self.listWidget)
        layout.addWidget(buttonLayout)

        self.setLayout(layout)

        self.setWindowTitle("Payment Types")

    def newPaymentType(self):
        dialog = NewPaymentTypeDialog("New", self.dbCur, self)
        if dialog.exec_():
            nextPaymentTypeId = self.parent.nextIdNum("PaymentTypes")
            desc = dialog.nameTxt.text()
            paymentGLAccountNum = self.parent.stripAllButNumbers(dialog.glAccountsBox.currentText())
            
            self.listWidget.addItem(constants.ID_DESC % (nextPaymentTypeId, desc))
            
            columns = ("Description", "GLAccount")
            values = (desc, paymentGLAccountNum)
            self.parent.insertIntoDatabase("PaymentTypes", columns, values)
            self.parent.dbConn.commit()
            
    def showPaymentType(self):
        item = self.listWidget.currentItem()
        paymentType = self.parent.stripAllButNumbers(item.text())
        
        dialog = NewPaymentTypeDialog("View", self.dbCur, self, paymentType)
        if dialog.exec_():
            if dialog.hasChanges == True:
                desc = dialog.nameTxt.text()
                glAcct = self.parent.stripAllButNumbers(dialog.glAccountsBox.currentText())

                colValDict = {"Description": desc,
                              "GLAccount": glAcct}
                whereDict = {"idNum": paymentType}
                self.parent.updateDatabase("PaymentTypes", colValDict, whereDict)
                self.parent.dbConn.commit()

                item.setText(constants.ID_DESC % (paymentType, desc))

    def deletePaymentType(self):
        idxToDelete = self.listWidget.currentRow()
        item = self.listWidget.takeItem(idxToDelete)
        paymentTypeId = self.parent.stripAllButNumbers(item.text())

        # Remove from the database
        self.paymentTypeDict.pop(paymentTypeId)
        self.parent.parent.parent.dbCursor.execute("DELETE FROM PaymentTypes WHERE idNum=?", (paymentTypeId,))
        self.parent.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectIdToAddLinkTo=? AND ObjectToAddLinkTo='paymentTypes'", (paymentTypeId,))
        self.parent.parent.parent.dbConnection.commit()
        
class NewGLPostingDialog(QDialog):
    def __init__(self, mode, companiesDict, glAcctsDict, parent=None, glPosting=None):
        super().__init__(parent)
        self.glValuesAsList = glAcctsDict.sortedListOfKeysAndNames()
        self.layout = QGridLayout()

        companyLbl = QLabel("Company:")
        dateLbl = QLabel("Date")
        memoLbl = QLabel("Memo:")

        self.companyBox = QComboBox()
        self.companyBox.addItems(companiesDict.sortedListOfKeysAndNames())
        self.postingsWidget = gui_elements.GLPostingsSection(self.glValuesAsList)
        
        if mode == "View":
            self.dateText = QLabel(glPosting.date)
            self.memoText = QLabel(glPosting.description)
        else:
            self.dateText = gui_elements.DateLineEdit()
            self.memoText = QLineEdit()
        
        self.layout.addWidget(companyLbl, 0, 0)
        self.layout.addWidget(self.companyBox, 0, 1)
        self.layout.addWidget(dateLbl, 1, 0)
        self.layout.addWidget(self.dateText, 1, 1)
        self.layout.addWidget(memoLbl, 2, 0)
        self.layout.addWidget(self.memoText, 2, 1)
        self.layout.addWidget(self.postingsWidget, 3, 1, 1, 2)

        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        self.layout.addWidget(buttonWidget, 4, 0, 1, 2)
        
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit GL Posting")
        else:
            self.setWindowTitle("New GL Posting")

    def makeLabelsEditable(self):
        pass

    def accept(self):
        if self.postingsWidget.inBalance() == True:
            super().accept()
