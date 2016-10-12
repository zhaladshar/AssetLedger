from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import constants
import gui_elements
import classes

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
            self.nameText = QLabel(name)
            self.addressText = QLabel(address)
            self.cityText = QLabel(city)
            self.stateText = QLabel(state)
            self.zipText = QLabel(zip_)
            self.phoneText = QLabel(phone)
            
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
        
##        if mode == "View":
##            invoicesWidget = gui_elements.InvoiceTreeWidget(self.vendor.invoices, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
##            self.layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
##            nextRow += 1
##            
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
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.changed)
        
        self.layout.addWidget(self.nameText_edit, 0, 1)
        self.layout.addWidget(self.addressText_edit, 1, 1)
        self.layout.addWidget(self.cityText_edit, 2, 1)
        self.layout.addWidget(self.stateText_edit, 3, 1)
        self.layout.addWidget(self.zipText_edit, 4, 1)
        self.layout.addWidget(self.phoneText_edit, 5, 1)
        
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
        self.detailsWidget.detailsHaveChanged.connect(self.invoicePropDetailsChange)
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
        dialog = InvoicePaymentDialog("New", self.paymentTypesDict, self, self.invoice)
        if dialog.exec_():
            nextId = self.parent.nextIdNum("InvoicesPayments")
            paymentTypeId = self.parent.stripAllButNumbers(dialog.paymentTypeBox.currentText())
            datePd = classes.NewDate(dialog.datePaidText.text())
            amtPd = float(dialog.amountText.text())

            # Create new payment and get necessary objects
            newPayment = classes.InvoicePayment(datePd, amtPd, nextId)
            paymentType = self.paymentTypesDict[paymentTypeId]
            
            # Add to database and to data structure
            self.parent.insertIntoDatabase("InvoicesPayments", "(DatePaid, AmountPaid)", "('" + str(newPayment.datePaid) + "', " + str(newPayment.amountPaid) + ")")
            self.parent.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoices', " + str(self.invoice.idNum) + ", 'addPayment', 'invoicesPayments', " + str(nextId) + ")")
            self.parent.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoicesPayments', " + str(newPayment.idNum) + ", 'addInvoice', 'invoices', " + str(self.invoice.idNum) + ")")
            self.parent.insertIntoDatabase("Xref", "(ObjectToAddLinkTo, ObjectIdToAddLinkTo, Method, ObjectBeingLinked, ObjectIdBeingLinked)", "('invoicesPayments', " + str(newPayment.idNum) + ", 'addPaymentType', 'paymentTypes', " + str(paymentTypeId) + ")")
            self.parent.parent.parent.dbConnection.commit()
            
            newPayment.addInvoice(self.invoice)
            self.invoice.addPayment(newPayment)
            newPayment.addPaymentType(paymentType)
            self.parent.parent.dataConnection.invoicesPayments[newPayment.idNum] = newPayment
            
            # Create GL posting
            paymentTypeId = self.parent.stripAllButNumbers(dialog.paymentTypeBox.currentText())
            description = constants.GL_POST_PYMT_DESC % (self.invoice.idNum, self.invoice.vendor.idNum, str(datePd))
            details = []
            details.append((amtPd, "CR", self.paymentTypesDict[paymentTypeId].glAccount.idNum, newPayment, "invoicesPayments"))
            details.append((amtPd, "DR", self.invoice.vendor.glAccount.idNum, None, None))
            
            self.parent.postToGL.emit(self.invoice.company.idNum, datePd, description, details)
            
            # Add entry to payment tree
            item = gui_elements.InvoicePaymentTreeWidgetItem(newPayment, self.paymentHistory)
            self.paymentHistory.addTopLevelItem(item)
            
            # Refresh AP info
            self.parent.updateVendorTree.emit()
            self.parent.refreshOpenInvoiceTree()
            
    def viewPayment(self):
        idxToShow = self.paymentHistory.indexFromItem(self.paymentHistory.currentItem())
        item = self.paymentHistory.itemFromIndex(idxToShow)

        if item:
            dialog = InvoicePaymentDialog("View", self.paymentTypesDict, self, self.invoice, item.invoicePayment)
            if dialog.exec_():
                if dialog.hasChanges == True:
                    newAmtPaid = float(dialog.amountText_edit.text())
                    newDatePaid = NewDate(dialog.datePaidText_edit.text())

                    # Change values in data structure and database
                    item.invoicePayment.datePaid = newDatePaid
                    item.invoicePayment.amountPaid = newAmtPaid
                    self.parent.parent.parent.dbCursor.execute("UPDATE InvoicesPayments SET DatePaid=?, AmountPaid=? WHERE idNum=?",
                                                               (str(newDatePaid), newAmtPaid, item.invoicePayment.idNum))
                    self.parent.parent.parent.dbConnection.commit()
                    
                    # Update GL post
                    glDet = item.invoicePayment.glPosting
                    glPost = glDet.detailOf
                    glPostDesc = constants.GL_POST_PYMT_DESC % (self.invoice.idNum, self.invoice.vendor.idNum, newDatePaid)
                    for detailKey, glDetail in glPost.details.items():
                        self.parent.updateGLDet.emit(glDetail, newAmtPaid, glDetail.debitCredit)
                    self.parent.updateGLPost.emit(glPost, glPostDesc, newDatePaid)
                    self.parent.parent.updateGLTree.emit()
                    
                    # Refresh data
                    self.paymentHistory.refreshData()
                    self.parent.refreshOpenInvoiceTree()
                    self.parent.refreshPaidInvoicesTreeWidget()
                    self.parent.updateVendorTree.emit()

    def deletePayment(self):
        idxToDelete = self.paymentHistory.indexOfTopLevelItem(self.paymentHistory.currentItem())

        if idxToDelete >= 0:
            item = self.paymentHistory.takeTopLevelItem(idxToDelete)

        if item:
            # Delete payment from database
            self.parent.parent.parent.dbCursor.execute("DELETE FROM InvoicesPayments WHERE idNum=?",
                                                       (item.invoicePayment.idNum,))
            self.parent.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectToAddLinkTo='invoicesPayments' AND ObjectIdToAddLinkTo=?",
                                                       (item.invoicePayment.idNum,))
            self.parent.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectBeingLinked='invoicesPayments' AND ObjectIdBeingLinked=?",
                                                       (item.invoicePayment.idNum,))
            self.parent.parent.parent.dbConnection.commit()
            
            # Delete payment from corporate structure
            self.invoice.removePayment(item.invoicePayment)
            self.parent.parent.dataConnection.invoicesPayments.pop(item.invoicePayment.idNum)
            
            # Delete GL posting
            glDet = item.invoicePayment.glPosting
            glPost = glDet.detailOf
            self.parent.deleteGLPost.emit(glPost)
            
            # Refresh data
            self.parent.refreshOpenInvoiceTree()
            self.parent.refreshPaidInvoicesTreeWidget()
            self.parent.updateVendorTree.emit()
    
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
        pass
##        proposals = self.getAcceptedProposalsOfAssetProject()
##        self.detailsWidget.addProposals(proposals)

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.vendorChange)
        self.assetProjSelector.setEnabled(True)
        self.assetProjSelector.rdoBtnChanged.connect(self.projectAssetChange)
        self.assetProjSelector.selectorChanged.connect(self.projectAssetChange)
        self.invoiceDateText_edit = gui_elements.DateLineEdit(self.invoiceDateText.text())
        self.invoiceDateText_edit.textEdited.connect(self.changed)
        self.dueDateText_edit = gui_elements.DateLineEdit(self.dueDateText.text())
        self.dueDateText_edit.textEdited.connect(self.changed)
        self.detailsWidget.makeEditable()
        self.detailsWidget.detailsHaveChanged.connect(self.invoicePropDetailsChange)
        
        self.layout.addWidget(self.invoiceDateText_edit, 3, 1)
        self.layout.addWidget(self.dueDateText_edit, 4, 1)

    def updateAssetProjSelector(self):
        companyId = self.parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector.updateCompany(companyId)
        self.assetProjSelector.clear()

    def changed(self):
        self.hasChanges = True

    def vendorChange(self):
        self.vendorChanged = True
        self.hasChanges = True

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

        self.updateAssetProjSelector()

    def projectAssetChange(self):
        self.projectAssetChanged = True
        self.hasChanges = True

    def invoicePropDetailsChange(self):
        self.invoicePropDetailsChanged = True
        self.hasChanges = True

    def accept(self):
        QDialog.accept(self)

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
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (proposal.company.idNum, proposal.company.shortName)))
            self.companyBox.setEnabled(False)
            
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(constants.ID_DESC % (proposal.vendor.idNum, proposal.vendor.name)))
            self.vendorBox.setEnabled(False)
            
            self.statusBox.setCurrentIndex(self.statusBox.findText(proposal.status))
            self.statusBox.setEnabled(False)

            companyId = parent.stripAllButNumbers(self.companyBox.currentText())
            self.assetProjSelector.updateCompany(parent.parent.dataConnection.companies[companyId])
            
            if proposal.proposalFor[0] == "assets":
                self.assetProjSelector.assetRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % proposal.proposalFor[1].idNum) + " - " + proposal.proposalFor[1].description))
            else:
                self.assetProjSelector.projRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % proposal.proposalFor[1].idNum) + " - " + proposal.proposalFor[1].description))
            self.assetProjSelector.setEnabled(False)
            self.assetProjSelector.show()
            
            self.dateText = QLabel(str(proposal.date))
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
            self.detailsWidget = gui_elements.ProposalDetailWidget(proposal.details)
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

    def vendorChange(self):
        self.vendorChanged = True
        self.hasChanges = True

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

    def projectAssetChange(self):
        self.projectAssetChanged = True
        self.hasChanges = True
        
    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.vendorChange)
        
        self.assetProjSelector.setEnabled(True)
        self.assetProjSelector.rdoBtnChanged.connect(self.projectAssetChange)
        self.assetProjSelector.selectorChanged.connect(self.projectAssetChange)
        
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
    def __init__(self, mode, GLDict, parent=None, project=None):
        super().__init__(parent)
        self.project = project
        self.hasChanges = False
        self.companyChanged = False
        self.glAccountChanged = False

        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        startDateLbl = QLabel("Start Date:")
        self.endDateLbl = QLabel("End Date:")
        statusLbl = QLabel("Status:")
        statusReasonLbl = QLabel("Reason:")
        glAccountLbl = QLabel("GL Account:")
        
        self.companyBox = QComboBox()
        self.companyBox.addItems(parent.parent.dataConnection.companies.sortedListOfKeysAndNames())
        
        self.glAccountsBox = QComboBox()
        self.glAccountsBox.addItems(GLDict.accounts().sortedListOfKeysAndNames())
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (project.company.idNum, project.company.shortName)))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(project.description)
            self.startDateText = QLabel(str(project.dateStart))
            self.endDateText = gui_elements.DateLineEdit()
            self.statusBox = QComboBox()
            self.statusBox.addItems(constants.PROJECT_STATUSES)
            self.statusBox.setCurrentIndex(self.statusBox.findText(self.project.status()))
            self.statusBox.setEnabled(False)
            self.statusReasonText = QLabel(self.project.notes)
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(constants.ID_DESC % (project.glAccount.idNum, project.glAccount.description)))
            self.glAccountsBox.setEnabled(False)
            self.invoicesTreeWidget = gui_elements.InvoiceTreeWidget(project.invoices, constants.INVOICE_HDR_LIST, constants.INVOICE_HDR_WDTH)
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

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

    def glAccountChange(self):
        self.glAccountChanged = True
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.startDateText_edit = gui_elements.DateLineEdit(self.startDateText.text())
        self.startDateText_edit.textEdited.connect(self.changed)
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.glAccountChange)

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
    def __init__(self, mode, parent=None, asset=None):
        super().__init__(parent)
        self.parent = parent
        self.hasChanges = False
        self.companyChanged = False
        self.assetTypeChanged = False
        self.parentAssetChanged = False

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
        self.companyBox.addItems(parent.parent.dataConnection.companies.sortedListOfKeysAndNames())

        self.assetTypeBox = QComboBox()
        self.assetTypeBox.addItems(parent.parent.dataConnection.assetTypes.sortedListOfKeysAndNames())

        self.childOfAssetBox = QComboBox()
        self.childOfAssetBox.addItem("")
        self.childOfAssetBox.addItems(parent.parent.dataConnection.assets.sortedListOfKeysAndNames())
        
        self.depMethodBox = QComboBox()
        self.depMethodBox.addItems(constants.DEP_METHODS)
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(constants.ID_DESC % (asset.company.idNum, asset.company.shortName)))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(asset.description)
            self.assetTypeBox.setCurrentIndex(self.assetTypeBox.findText(constants.ID_DESC % (asset.assetType.idNum, asset.assetType.description)))
            self.assetTypeBox.setEnabled(False)
            if asset.subAssetOf == None:
                subAssetOfText = ""
            else:
                subAssetOfText = constants.ID_DESC % (asset.subAssetOf.idNum, asset.subAssetOf.description)
            self.childOfAssetBox.setCurrentText(subAssetOfText)
            self.childOfAssetBox.setEnabled(False)
            self.dateAcquiredText = QLabel(str(asset.acquireDate))
            self.dateInSvcText = QLabel(str(asset.inSvcDate))
            self.usefulLifeText = QLabel(str(asset.usefulLife))
            self.depMethodBox.setCurrentIndex(self.depMethodBox.findText(asset.depMethod))
            self.depMethodBox.setEnabled(False)
            self.salvageValueText = QLabel(str(asset.salvageAmount))
            self.costText = QLabel(str(asset.cost()))
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
            self.historyTreeWidget = gui_elements.AssetHistoryTreeWidget(asset.history, constants.ASSET_HIST_HDR_LIST, constants.ASSET_HIST_HDR_WDTH)
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
        assetType = self.parent.parent.dataConnection.assetTypes[assetTypeId]
        if assetType.depreciable == False:
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

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

    def assetTypeChange(self):
        self.assetTypeChanged = True
        self.hasChanges = True

    def parentAssetChange(self):
        self.parentAssetChanged = True
        self.hasChanges = True
        
    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.assetTypeBox.setEnabled(True)
        self.assetTypeBox.currentIndexChanged.connect(self.assetTypeChange)
        self.childOfAssetBox.setEnabled(True)
        self.childOfAssetBox.currentIndexChanged.connect(self.parentAssetChange)
        self.dateAcquiredText_edit = gui_elements.DateLineEdit(self.dateAcquiredText.text())
        self.dateAcquiredText_edit.textEdited.connect(self.changed)
        self.dateInSvcText_edit = gui_elements.DateLineEdit(self.dateInSvcText.text())
        self.dateInSvcText_edit.textEdited.connect(self.changed)
        self.usefulLifeText_edit = QLineEdit(self.usefulLifeText.text())
        self.usefulLifeText_edit.textEdited.connect(self.changed)
        self.depMethodBox.setEnabled(True)
        self.depMethodBox.currentIndexChanged.connect(self.changed)
        self.salvageValueText_edit = QLineEdit(self.salvageValueText.text())
        self.salvageValueText_edit.textEdited.connect(self.changed)
        
        self.layout.addWidget(self.descriptionText_edit, 1, 1)
        self.layout.addWidget(self.dateAcquiredText_edit, 4, 1)
        self.layout.addWidget(self.dateInSvcText_edit, 5, 1)
        self.layout.addWidget(self.usefulLifeText_edit, 6, 1)
        self.layout.addWidget(self.salvageValueText_edit, 8, 1)

        # Get asset type to determine depreciability
        assetTypeId = self.parent.stripAllButNumbers(self.assetTypeBox.currentText())
        assetType = self.parent.parent.dataConnection.assetTypes[assetTypeId]
        if assetType.depreciable == False:
            self.usefulLifeText_edit.hide()
            self.salvageValueText_edit.hide()

    def resize(self):
        self.setFixedSize(self.sizeHint())

class InvoicePaymentDialog(QDialog):
    def __init__(self, mode, paymentTypeDict, parent=None, invoice=None, invoicePayment=None):
        super().__init__(parent)
        self.hasChanges = False

        vendorLbl = QLabel("Vendor:")
        invoiceLbl = QLabel("Invoice:")
        paymentTypeLbl = QLabel("Payment Type:")
        datePaidLbl = QLabel("Date Paid:")
        amountLbl = QLabel("Amount:")
        
        self.paymentTypeBox = QComboBox()
        self.paymentTypeBox.addItems(paymentTypeDict.sortedListOfKeysAndNames())
        self.vendorText = QLabel(invoice.vendor.name)
        self.invoiceText = QLabel(str(invoice.idNum))
        
        if mode == "View":
            self.datePaidText = QLabel(str(invoicePayment.datePaid))
            self.amountText = QLabel(str(invoicePayment.amountPaid))
            self.paymentTypeBox.setCurrentIndex(self.paymentTypeBox.findText(constants.ID_DESC % (invoicePayment.paymentType.idNum, invoicePayment.paymentType.description)))
            self.paymentTypeBox.setEnabled(False)
        else:
            self.datePaidText = gui_elements.DateLineEdit()
            self.amountText = QLineEdit(str(invoice.balance()))
        
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
        self.datePaidText_edit = gui_elements.DateLineEdit(self.datePaidText.text())
        self.datePaidText_edit.textEdited.connect(self.changed)
        self.amountText_edit = QLineEdit(self.amountText.text())
        self.amountText_edit.textEdited.connect(self.changed)

        self.layout.addWidget(self.datePaidText_edit, 3, 1)
        self.layout.addWidget(self.amountText_edit, 4, 1)
        
class ChangeProposalStatusDialog(QDialog):
    def __init__(self, proposalStatus, parent=None):
        super().__init__(parent)

        statusLbl = QLabel("Reason:")
        self.statusTxt = QLineEdit()

        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        subLayout = QHBoxLayout()
        
        subLayout.addWidget(statusLbl)
        subLayout.addWidget(self.statusTxt)

        layout.addLayout(subLayout)
        layout.addWidget(buttonWidget)
        
        self.setLayout(layout)

        self.setWindowTitle(proposalStatus + " Proposal")

class CIPAllocationDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout()
        self.gridLayout = QGridLayout()
        cipLbl = QLabel("CIP")
        cipAmt = QLabel(str(project.calculateCIP()))
        assetNameLbl = QLabel("Name")
        costLbl = QLabel("Amount of CIP")
        
        self.gridLayout.addWidget(cipLbl, 0, 0)
        self.gridLayout.addWidget(cipAmt, 0, 1)
        self.gridLayout.addWidget(assetNameLbl, 1, 0)
        self.gridLayout.addWidget(costLbl, 1, 1)
        
        # Add first blank row
        assetNameTxt = QLineEdit()
        costTxt = QLineEdit()
        deleteBtn = QPushButton("-")

        assetNameTxt.editingFinished.connect(lambda: self.validateInput(3))
        costTxt.editingFinished.connect(lambda: self.validateInput(3))
        deleteBtn.clicked.connect(lambda: self.deleteLine(3))
        deleteBtn.hide()
        
        self.gridLayout.addWidget(assetNameTxt, 2, 0)
        self.gridLayout.addWidget(costTxt, 2, 1)
        self.gridLayout.addWidget(deleteBtn, 2, 2)

        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        self.layout.addLayout(self.gridLayout)
        self.layout.addWidget(buttonWidget)
        
        self.setLayout(self.layout)
        self.setWindowTitle("Allocate Project Costs")
        
    def addLine(self):
        numRows = self.gridLayout.rowCount() + 1
        
        assetNameTxt = QLineEdit()
        costTxt = QLineEdit()
        deleteBtn = QPushButton("-")

        assetNameTxt.editingFinished.connect(lambda: self.validateInput(numRows))
        costTxt.editingFinished.connect(lambda: self.validateInput(numRows))
        deleteBtn.clicked.connect(lambda: self.deleteLine(numRows))
        deleteBtn.hide()

        self.gridLayout.addWidget(assetNameTxt, numRows - 1, 0)
        self.gridLayout.addWidget(costTxt, numRows - 1, 1)
        self.gridLayout.addWidget(deleteBtn, numRows - 1, 2)
        
    def deleteLine(self, row):
        for n in range(3):
            widget = self.gridLayout.itemAtPosition(row - 1, n).widget()
            self.gridLayout.removeWidget(widget)
            widget.deleteLater()

    def validateInput(self, row):
        if self.gridLayout.itemAtPosition(row - 1, 0).widget().text() != "" and \
           self.gridLayout.itemAtPosition(row - 1, 1).widget().text() != "":
            if row == self.gridLayout.rowCount():
                self.addLine()
                self.gridLayout.itemAtPosition(row, 0).widget().setFocus()
                self.gridLayout.itemAtPosition(row - 1, 2).widget().show()
                    
class CloseProjectDialog(QDialog):
    def __init__(self, status, parent=None, assetName=""):
        super().__init__(parent)
        self.parent = parent

        layout = QGridLayout()
        
        dateLbl = QLabel("Date:")
        self.dateTxt = gui_elements.DateLineEdit()

        layout.addWidget(dateLbl, 0, 0)
        layout.addWidget(self.dateTxt, 0, 1)
        nextRow = 1

        if status == constants.ABD_PROJECT_STATUS:
            reasonLbl = QLabel("Reason:")
            self.reasonTxt = QLineEdit()
            
            layout.addWidget(reasonLbl, nextRow, 0)
            layout.addWidget(self.reasonTxt, nextRow, 1)
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

        buttonWidget = gui_elements.SaveViewCancelButtonWidget("New")
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.cancelButton.clicked.connect(self.reject)

        layout.addWidget(buttonWidget, nextRow, 0, 1, 2)

        self.setLayout(layout)
        self.showHideDisposalInfo()
        
        self.setWindowTitle(status + "Project")

    def showHideDisposalInfo(self):
        assetTypeId = self.parent.stripAllButNumbers(self.assetTypeBox.currentText())
        assetType = self.parent.parent.dataConnection.assetTypes[assetTypeId]
        
        if assetType.depreciable == False:
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
    def __init__(self, mode, GLDict, parent=None, assetType=None):
        super().__init__(parent)
        self.hasChanges = False
        self.glAccountsChanged = False
        
        nameLbl = QLabel("Name:")
        depLbl = QLabel("Depreciable:")
        assetGLLbl = QLabel("Asset GL:")
        self.expenseGLLbl = QLabel("Dep. GL:")
        self.accumExpenseGLLbl = QLabel("Accum. Dep. GL:")
        self.depChk = QCheckBox()
        self.depChk.stateChanged.connect(self.showHideGLBoxes)
        
        self.glAssetAccountsBox = QComboBox()
        self.glAssetAccountsBox.addItems(GLDict.accounts().sortedListOfKeysAndNames())
        self.glExpenseAccountsBox = QComboBox()
        self.glExpenseAccountsBox.addItem("")
        self.glExpenseAccountsBox.addItems(GLDict.accounts().sortedListOfKeysAndNames())
        self.glAccumExpenseAccountsBox = QComboBox()
        self.glAccumExpenseAccountsBox.addItem("")
        self.glAccumExpenseAccountsBox.addItems(GLDict.accounts().sortedListOfKeysAndNames())
        
        if mode == "View":
            self.nameTxt = QLabel(assetType.description)
            self.glAssetAccountsBox.setCurrentIndex(self.glAssetAccountsBox.findText(constants.ID_DESC % (assetType.assetGLAccount.idNum, assetType.assetGLAccount.description)))
            if assetType.depreciable == True:
                self.depChk.setCheckState(Qt.Checked)
                self.glExpenseAccountsBox.setCurrentIndex(self.glExpenseAccountsBox.findText(constants.ID_DESC % (assetType.expenseGLAccount.idNum, assetType.expenseGLAccount.description)))
                self.glAccumExpenseAccountsBox.setCurrentIndex(self.glAccumExpenseAccountsBox.findText(constants.ID_DESC % (assetType.accumExpGLAccount.idNum, assetType. accumExpGLAccount.description)))
            else:
                self.expenseGLLbl.hide()
                self.accumExpenseGLLbl.hide()
                self.glExpenseAccountsBox.hide()
                self.glAccumExpenseAccountsBox.hide()
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

    def glAccountsChange(self):
        self.changed()
        self.glAccountsChanged = True

    def makeLabelsEditable(self):
        self.nameTxt_edit = QLineEdit(self.nameTxt.text())
        self.nameTxt_edit.textEdited.connect(self.changed)
        
        self.glAssetAccountsBox.setEnabled(True)
        self.glAssetAccountsBox.currentIndexChanged.connect(self.glAccountsChange)
        self.glExpenseAccountsBox.setEnabled(True)
        self.glExpenseAccountsBox.currentIndexChanged.connect(self.glAccountsChange)
        self.glAccumExpenseAccountsBox.setEnabled(True)
        self.glAccumExpenseAccountsBox.currentIndexChanged.connect(self.glAccountsChange)

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
    def __init__(self, assetTypeDict, GLDict, parent=None):
        super().__init__(parent)
        self.assetTypeDict = assetTypeDict
        self.GLDict = GLDict
        self.parent = parent
        
        layout = QHBoxLayout()

        self.listWidget = QListWidget()
        self.listWidget.addItems(self.assetTypeDict.sortedListOfKeysAndNames())
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
        dialog = NewAssetTypeDialog("New", self.GLDict, self)
        if dialog.exec_():
            nextAssetTypeId = self.parent.nextIdNum("AssetTypes")
            assetGLAccountNum = self.parent.stripAllButNumbers(dialog.glAssetAccountsBox.currentText())
            
            if dialog.depChk.checkState() == Qt.Checked:
                depreciable = 1
                expenseGLAccountNum = self.parent.stripAllButNumbers(dialog.glExpenseAccountsBox.currentText())
                accumExpenseGLAccountNum = self.parent.stripAllButNumbers(dialog.glAccumExpenseAccountsBox.currentText())
            else:
                depreciable = 0
            newAssetType = classes.AssetType(dialog.nameTxt.text(),
                                             depreciable,
                                             nextAssetTypeId)
            newAssetType.addAssetGLAccount(self.GLDict[assetGLAccountNum])
            if depreciable == 1:
                newAssetType.addExpenseGLAccount(self.GLDict[expenseGLAccountNum])
                newAssetType.addAccumExpGLAccount(self.GLDict[accumExpenseGLAccountNum])
            
            self.listWidget.addItem(constants.ID_DESC % (newAssetType.idNum, newAssetType.description))
            self.parent.parent.dataConnection.assetTypes[newAssetType.idNum] = newAssetType
            
            self.parent.insertIntoDatabase("AssetTypes", "(AssetType, Depreciable)", "('" + newAssetType.description + "', " + str(depreciable) + ")")
            self.parent.insertIntoDatabase("Xref", "", "('assetTypes', " + str(newAssetType.idNum) + ", 'addAssetGLAccount', 'glAccounts', " + str(assetGLAccountNum) + ")")
            if depreciable == 1:
                self.parent.insertIntoDatabase("Xref", "", "('assetTypes', " + str(newAssetType.idNum) + ", 'addExpenseGLAccount', 'glAccounts', " + str(expenseGLAccountNum) + ")")
                self.parent.insertIntoDatabase("Xref", "", "('assetTypes', " + str(newAssetType.idNum) + ", 'addAccumExpGLAccount', 'glAccounts', " + str(accumExpenseGLAccountNum) + ")")
            
            self.parent.parent.parent.dbConnection.commit()

    def showAssetType(self):
        idxToShow = self.listWidget.currentRow()
        item = self.listWidget.item(idxToShow)
        assetTypeId = self.parent.stripAllButNumbers(item.text())
        assetType = self.assetTypeDict[assetTypeId]
        
        dialog = NewAssetTypeDialog("View", self.GLDict, self, assetType)
        if dialog.exec_():
            if dialog.hasChanges == True:
                assetType.description = dialog.nameTxt_edit.text()

                if dialog.depChk.checkState() == Qt.Checked:
                    depreciable = 1
                    assetType.depreciable = True
                else:
                    depreciable = 0
                    assetType.depreciable = False

                self.parent.parent.parent.dbCursor.execute("UPDATE AssetTypes SET AssetType=?, Depreciable=? WHERE idNum=?", (assetType.description, depreciable, assetType.idNum))

                if dialog.glAccountsChanged == True:
                    assetGLNum = self.parent.stripAllButNumbers(dialog.glAssetAccountsBox.currentText())
                    assetType.addAssetGLAccount(self.GLDict[assetGLNum])
                    self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addAssetGLAccount'",
                                                               (assetGLNum, assetTypeId))
                    if depreciable == 1:
                        expenseGLNum = self.parent.stripAllButNumbers(dialog.glExpenseAccountsBox.currentText())
                        accumExpGLNum = self.parent.stripAllButNumbers(dialog.glAccumExpenseAccountsBox.currentText())

                        assetType.addExpenseGLAccount(self.GLDict[expenseGLNum])
                        assetType.addAccumExpGLAccount(self.GLDict[accumExpGLNum])
                    
                        self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addExpenseGLAccount'",
                                                                   (expenseGLNum, assetTypeId))
                        self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addAccumExpGLAccount'",
                                                                   (accumExpGLNum, assetTypeId))

                self.parent.parent.parent.dbConnection.commit()

                item.setText(constants.ID_DESC % (assetType.idNum, assetType.description))

    def deleteAssetType(self):
        idxToDelete = self.listWidget.currentRow()
        item = self.listWidget.takeItem(idxToDelete)
        assetTypeId = self.parent.stripAllButNumbers(item.text())

        # Remove from the database
        self.assetTypeDict.pop(assetTypeId)
        self.parent.parent.parent.dbCursor.execute("DELETE FROM AssetTypes WHERE idNum=?", (assetTypeId,))
        self.parent.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectIdToAddLinkTo=? AND ObjectToAddLinkTo='assetTypes'", (assetTypeId,))
        self.parent.parent.parent.dbConnection.commit()

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
    def __init__(self, mode, parent=None, glAccount=None):
        super().__init__(parent)
        self.hasChanges = False
        self.accountGroupChanged = False

        self.layout = QGridLayout()
        
        accountNumLbl = QLabel("Account #:")
        descriptionLbl = QLabel("Description:")
        acctGrpLbl = QLabel("Account Group:")
        self.listOfAcctGrpsLbl = QLabel("Group under...")
        
        self.acctGrpsBox = QComboBox()
        self.acctGrpsBox.addItems(parent.parent.dataConnection.glAccounts.accountGroups().sortedListOfKeysAndNames())
        
        if mode == "View":
            self.accountNumText = QLabel(str(glAccount.idNum))
            self.descriptionText = QLabel(glAccount.description)
            self.acctGrpChk = QCheckBox()
            if glAccount.placeHolder == True:
                self.acctGrpChk.setCheckState(Qt.Checked)
                self.listOfAcctGrpsLbl.hide()
                self.acctGrpsBox.hide()
            else:
                self.acctGrpChk.setCheckState(Qt.Unchecked)
                self.acctGrpsBox.setCurrentIndex(self.acctGrpsBox.findText(constants.ID_DESC % (glAccount.childOf.idNum, glAccount.childOf.description)))
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
    def __init__(self, mode, GLDict, parent=None, paymentType=None):
        super().__init__(parent)
        self.hasChanges = False
        self.glAccountChanged = False
        
        nameLbl = QLabel("Name:")
        glLbl = QLabel("GL Account:")
        
        self.glAccountsBox = QComboBox()
        self.glAccountsBox.addItems(GLDict.accounts().sortedListOfKeysAndNames())
        
        if mode == "View":
            self.nameTxt = QLabel(paymentType.description)
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(constants.ID_DESC % (paymentType.glAccount.idNum, paymentType.glAccount.description)))
            self.glAccountsBox.setEnabled(False)
        else:
            self.nameTxt = QLineEdit()
            
        buttonWidget = gui_elements.SaveViewCancelButtonWidget(mode)
        buttonWidget.saveButton.clicked.connect(self.accept)
        buttonWidget.editButton.clicked.connect(self.makeLabelsEditable)
        buttonWidget.cancelButton.clicked.connect(self.reject)
        
        layout = QGridLayout()
        layout.addWidget(nameLbl, 0, 0)
        layout.addWidget(self.nameTxt, 0, 1)
        layout.addWidget(glLbl, 2, 0)
        layout.addWidget(self.glAccountsBox, 2, 1)
        layout.addWidget(buttonWidget, 5, 0, 1, 2)
        
        self.setLayout(layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Payment Type")
        else:
            self.setWindowTitle("New Payment Type")

    def changed(self):
        self.hasChanges = True

    def glAccountChange(self):
        self.changed()
        self.glAccountChanged = True

    def makeLabelsEditable(self):
        self.nameTxt_edit = QLineEdit(self.nameTxt.text())
        self.nameTxt_edit.textEdited.connect(self.changed)
        
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.glAccountChange)
            
class PaymentTypeDialog(QDialog):
    def __init__(self, paymentTypeDict, GLDict, parent=None):
        super().__init__(parent)
        self.paymentTypeDict = paymentTypeDict
        self.GLDict = GLDict
        self.parent = parent
        
        layout = QHBoxLayout()

        self.listWidget = QListWidget()
        self.listWidget.addItems(self.paymentTypeDict.sortedListOfKeysAndNames())
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
        dialog = NewPaymentTypeDialog("New", self.GLDict, self)
        if dialog.exec_():
            nextPaymentTypeId = self.parent.nextIdNum("PaymentTypes")
            paymentGLAccountNum = self.parent.stripAllButNumbers(dialog.glAccountsBox.currentText())
            
            newPaymentType = classes.PaymentType(dialog.nameTxt.text(),
                                                 nextPaymentTypeId)
            newPaymentType.addGLAccount(self.GLDict[paymentGLAccountNum])
            
            self.listWidget.addItem(constants.ID_DESC % (newPaymentType.idNum, newPaymentType.description))
            self.paymentTypeDict[newPaymentType.idNum] = newPaymentType
            
            self.parent.insertIntoDatabase("PaymentTypes", "(Description)", "('" + newPaymentType.description + "')")
            self.parent.insertIntoDatabase("Xref", "", "('paymentTypes', " + str(newPaymentType.idNum) + ", 'addGLAccount', 'glAccounts', " + str(paymentGLAccountNum) + ")")
            
            self.parent.parent.parent.dbConnection.commit()

    def showPaymentType(self):
        idxToShow = self.listWidget.currentRow()
        item = self.listWidget.item(idxToShow)
        paymentTypeId = self.parent.stripAllButNumbers(item.text())
        paymentType = self.paymentTypeDict[paymentTypeId]
        
        dialog = NewPaymentTypeDialog("View", self.GLDict, self, paymentType)
        if dialog.exec_():
            if dialog.hasChanges == True:
                paymentType.description = dialog.nameTxt_edit.text()

                self.parent.parent.parent.dbCursor.execute("UPDATE PaymentTypes SET Description=? WHERE idNum=?", (paymentType.description, paymentType.idNum))

                if dialog.glAccountChanged == True:
                    paymentGLNum = self.parent.stripAllButNumbers(dialog.glAccountsBox.currentText())
                    paymentType.addGLAccount(self.GLDict[paymentGLNum])
                    self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='paymentTypes' AND ObjectIdToAddLinkTo=? AND Method='addGLAccount'",
                                                               (paymentGLNum, paymentTypeId))
                self.parent.parent.parent.dbConnection.commit()

                item.setText(constants.ID_DESC % (paymentType.idNum, paymentType.description))

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
            self.setWindowTitle("View Edit GL Posting")
        else:
            self.setWindowTitle("New GL Posting")

    def makeLabelsEditable(self):
        pass

    def accept(self):
        if self.postingsWidget.inBalance() == True:
            super().accept()
