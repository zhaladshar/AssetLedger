from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import constants
import gui_elements
import classes

class VendorDialog(QDialog):
    def __init__(self, mode, GLDict, parent=None, vendor=None):
        super().__init__(parent)
        self.vendor = vendor
        self.hasChanges = False
        self.glAccountChanged = False

        self.layout = QGridLayout()

        nameLbl = QLabel("Name:")
        addressLbl = QLabel("Address:")
        cityLbl = QLabel("City:")
        stateLbl = QLabel("State:")
        zipLbl = QLabel("ZIP:")
        phoneLbl = QLabel("Phone:")
        glAccountLbl = QLabel("GL Account:")
        
        glAccountsList = []
        glAccountsDict = GLDict.accounts()
        for glKey in glAccountsDict:
            glAccountsList.append(str("%4d - %s" % (glAccountsDict[glKey].idNum, glAccountsDict[glKey].description)))
        self.glAccountsBox = QComboBox()
        self.glAccountsBox.addItems(glAccountsList)

        if mode == "View":
            self.nameText = QLabel(self.vendor.name)
            self.addressText = QLabel(self.vendor.address)
            self.cityText = QLabel(self.vendor.city)
            self.stateText = QLabel(self.vendor.state)
            self.zipText = QLabel(self.vendor.zip)
            self.phoneText = QLabel(self.vendor.phone)
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(str("%4d - %s" % (vendor.glAccount.idNum, vendor.glAccount.description))))
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
            invoicesWidget = gui_elements.InvoiceTreeWidget(self.vendor.invoices)
            invoicesWidget.setIndentation(0)
            invoicesWidget.setHeaderHidden(True)
            self.layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
            nextRow += 1
            
            proposalsWidget = gui_elements.ProposalTreeWidget(self.vendor.proposals)
            proposalsWidget.setIndentation(0)
            proposalsWidget.setHeaderHidden(True)
            self.layout.addWidget(proposalsWidget, nextRow, 0, 1, 2)
            nextRow += 1
        
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

        if mode == "View":
            self.setWindowTitle("View/Edit Vendor")
        else:
            self.setWindowTitle("New Vendor")

    def glAccountChange(self):
        self.glAccountChanged = True
        self.hasChanges = True

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
        self.glAccountsBox.currentIndexChanged.connect(self.glAccountChange)
        
        self.layout.addWidget(self.nameText_edit, 0, 1)
        self.layout.addWidget(self.addressText_edit, 1, 1)
        self.layout.addWidget(self.cityText_edit, 2, 1)
        self.layout.addWidget(self.stateText_edit, 3, 1)
        self.layout.addWidget(self.zipText_edit, 4, 1)
        self.layout.addWidget(self.phoneText_edit, 5, 1)
        
    def changed(self):
        self.hasChanges = True

class InvoiceDialog(QDialog):
    def __init__(self, mode, parent=None, invoice=None):
        super().__init__(parent)
        self.parent = parent
        self.hasChanges = False
        self.companyChanged = False
        self.vendorChanged = False
        self.projectAssetChanged = False
        self.invoicePropDetailsChanged = False
        self.mode = mode
        
        self.layout = QGridLayout()

        companyLbl = QLabel("Company:")
        vendorLbl = QLabel("Vendor:")
        invoiceDateLbl = QLabel("Invoice Date:")
        dueDateLabel = QLabel("Due Date:")
        
        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)
        self.companyBox.currentIndexChanged.connect(self.updateAssetProjSelector)
        
        self.vendorBox = QComboBox()
        vendorList = []
        for vendor in parent.parent.dataConnection.vendors.values():
            vendorList.append(str("%4s" % vendor.idNum) + " - " + vendor.name)
        self.vendorBox.addItems(vendorList)
        
        companyId = parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector = gui_elements.AssetProjSelector(parent.parent.dataConnection.companies[companyId])
        self.assetProjSelector.rdoBtnChanged.connect(self.updateDetailInvoiceWidget)
        self.assetProjSelector.selectorChanged.connect(self.updateDetailInvoiceWidget)
        
        if self.mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % invoice.company.idNum) + " - " + invoice.company.shortName))
            self.companyBox.setEnabled(False)
            
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(str("%4s" % invoice.vendor.idNum) + " - " + invoice.vendor.name))
            self.vendorBox.setEnabled(False)
            
            companyId = parent.stripAllButNumbers(self.companyBox.currentText())
            self.assetProjSelector.updateCompany(parent.parent.dataConnection.companies[companyId])
            
            if invoice.assetProj[0] == "assets":
                # Need to disable signals, otherwise checking the radio button
                # will cause a myriad of signals to be passed and will crash
                # the program.
                self.assetProjSelector.dontEmitSignals(True)
                self.assetProjSelector.assetRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % invoice.assetProj[1].idNum) + " - " + invoice.assetProj[1].description))
                self.assetProjSelector.dontEmitSignals(False)
            else:
                self.assetProjSelector.dontEmitSignals(True)
                self.assetProjSelector.projRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % invoice.assetProj[1].idNum) + " - " + invoice.assetProj[1].description))
                self.assetProjSelector.dontEmitSignals(False)
            self.assetProjSelector.setEnabled(False)
            self.assetProjSelector.show()
            
            self.invoiceDateText = QLabel(invoice.invoiceDate)
            self.dueDateText = QLabel(invoice.dueDate)
        else:
            self.invoiceDateText = QLineEdit()
            self.dueDateText = QLineEdit()

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
            proposal = self.getAcceptedProposalOfAssetProject()
            self.detailsWidget = gui_elements.InvoiceDetailWidget(invoice.details, proposal)
        else:
            self.detailsWidget = gui_elements.InvoiceDetailWidget()
        self.detailsWidget.detailsHaveChanged.connect(self.invoicePropDetailsChange)
        self.layout.addWidget(self.detailsWidget, 5, 0, 1, 2)
        
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

        nextRow = 6
        if self.mode == "View":
            self.paymentHistory = gui_elements.InvoicePaymentTreeWidget(invoice.payments)
            self.paymentHistory.setIndentation(0)
            self.paymentHistory.setHeaderHidden(True)
            self.paymentHistory.setMinimumWidth(500)
            self.paymentHistory.setMaximumHeight(200)
        
            self.layout.addWidget(self.paymentHistory, nextRow, 0, 1, 2)
            nextRow += 1
            
        self.layout.addLayout(buttonLayout, nextRow, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Invoice")
        else:
            self.setWindowTitle("New Invoice")

    def getAcceptedProposalOfAssetProject(self):
        selection = self.assetProjSelector.selector.currentText()
        selectionId = self.parent.stripAllButNumbers(selection)

        if selectionId:
            if self.assetProjSelector.assetSelected() == True:
                acceptedProposal = self.parent.parent.dataConnection.assets[selectionId].proposals.proposalsByStatus(constants.ACC_PROPOSAL_STATUS)
                
                if acceptedProposal:
                    return list(acceptedProposal.values())[0]
                else:
                    return None
            else:
                acceptedProposal = self.parent.parent.dataConnection.projects[selectionId].proposals.proposalsByStatus(constants.ACC_PROPOSAL_STATUS)

                if acceptedProposal:
                    return list(acceptedProposal.values())[0]
                else:
                    return None
        else:
            return None

    def updateDetailInvoiceWidget(self):
        proposal = self.getAcceptedProposalOfAssetProject()
        self.detailsWidget.addProposal(proposal)

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.vendorChange)
        self.assetProjSelector.setEnabled(True)
        self.assetProjSelector.rdoBtnChanged.connect(self.projectAssetChange)
        self.assetProjSelector.selectorChanged.connect(self.projectAssetChange)
        self.invoiceDateText_edit = QLineEdit(self.invoiceDateText.text())
        self.invoiceDateText_edit.textEdited.connect(self.changed)
        self.dueDateText_edit = QLineEdit(self.dueDateText.text())
        self.dueDateText_edit.textEdited.connect(self.changed)
        self.detailsWidget.makeEditable()
        self.detailsWidget.detailsHaveChanged.connect(self.invoicePropDetailsChange)
        
        self.layout.addWidget(self.invoiceDateText_edit, 3, 1)
        self.layout.addWidget(self.dueDateText_edit, 4, 1)

    def updateAssetProjSelector(self):
        companyId = self.parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector.updateCompany(self.parent.parent.dataConnection.companies[companyId])
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
    def __init__(self, mode, parent=None, proposal=None):
        super().__init__(parent)
        self.parent = parent
        self.hasChanges = False
        self.vendorChanged = False
        self.companyChanged = False
        self.projectAssetChanged = False
        self.mode = mode

        self.layout = QGridLayout()

        companyLbl = QLabel("Company:")
        vendorLbl = QLabel("Vendor:")
        statusLbl = QLabel("Status:")
        dateLbl = QLabel("Date:")
        
        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)
        self.companyBox.currentIndexChanged.connect(self.updateAssetProjSelector)
        
        self.vendorBox = QComboBox()
        vendorList = []
        for vendor in parent.parent.dataConnection.vendors.values():
            vendorList.append(str("%4s" % vendor.idNum) + " - " + vendor.name)
        self.vendorBox.addItems(vendorList)

        self.statusBox = QComboBox()
        self.statusBox.addItems(constants.PROPOSAL_STATUSES)
        
        companyId = parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector = gui_elements.AssetProjSelector(parent.parent.dataConnection.companies[companyId])
        
        if self.mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % proposal.company.idNum) + " - " + proposal.company.shortName))
            self.companyBox.setEnabled(False)
            
            self.vendorBox.setCurrentIndex(self.vendorBox.findText(str("%4s" % proposal.vendor.idNum) + " - " + proposal.vendor.name))
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
            
            self.dateText = QLabel(proposal.date)
        else:
            self.dateText = QLineEdit()

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
            self.detailsWidget = gui_elements.ProposalDetailWidget()
        self.layout.addWidget(self.detailsWidget, nextRow, 0, 1, 2)
        nextRow += 1
        
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

        self.layout.addLayout(buttonLayout, nextRow, 0, 1, 2)
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
        self.assetProjSelector.changed.connect(self.projectAssetChange)
        
        self.statusBox.setEnabled(True)
        self.statusBox.currentIndexChanged.connect(self.changed)
        
        self.dateText_edit = QLineEdit(self.dateText.text())
        self.dateText_edit.textEdited.connect(self.changed)
        self.layout.addWidget(self.dateText_edit, 4, 1)

        self.detailsWidget.makeEditable()
        self.detailsWidget.detailsHaveChanged.connect(self.changed)

    def updateAssetProjSelector(self):
        companyId = self.parent.stripAllButNumbers(self.companyBox.currentText())
        self.assetProjSelector.updateCompany(self.parent.parent.dataConnection.companies[companyId])
        self.assetProjSelector.clear()
        
class ProjectDialog(QDialog):
    def __init__(self, mode, GLDict, parent=None, project=None):
        super().__init__(parent)
        self.hasChanges = False
        self.companyChanged = False
        self.glAccountChanged = False

        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        startDateLbl = QLabel("Start Date:")
        self.endDateLbl = QLabel("End Date:")
        glAccountLbl = QLabel("GL Account:")
        
        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)
        
        glAccountsList = []
        glAccountsDict = GLDict.accounts()
        for glKey in glAccountsDict:
            glAccountsList.append(str("%4d - %s" % (glAccountsDict[glKey].idNum, glAccountsDict[glKey].description)))
        self.glAccountsBox = QComboBox()
        self.glAccountsBox.addItems(glAccountsList)
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % project.company.idNum) + " - " + project.company.shortName))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(project.description)
            self.startDateText = QLabel(project.dateStart)
            self.endDateText = QLineEdit()
            self.glAccountsBox.setCurrentIndex(self.glAccountsBox.findText(str("%4d - %s" % (project.glAccount.idNum, project.glAccount.description))))
            self.glAccountsBox.setEnabled(False)
        else:
            self.descriptionText = QLineEdit()
            self.startDateText = QLineEdit()
            self.endDateText = QLineEdit()
        
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
        
        self.endDateLbl.hide()
        self.endDateText.hide()

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
        
        self.layout.addLayout(buttonLayout, 5, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Project")
        else:
            self.setWindowTitle("New Project")
        
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
        self.startDateText_edit = QLineEdit(self.startDateText.text())
        self.startDateText_edit.textEdited.connect(self.changed)
        self.glAccountsBox.setEnabled(True)
        self.glAccountsBox.currentIndexChanged.connect(self.glAccountChange)

        self.endDateText.textEdited.connect(self.changed)

        self.layout.addWidget(self.descriptionText_edit, 1, 1)
        self.layout.addWidget(self.startDateText_edit, 2, 1)

class CompanyDialog(QDialog):
    def __init__(self, mode, parent=None, company=None):
        super().__init__(parent)
        self.hasChanges = False

        self.layout = QGridLayout()
        
        nameLbl = QLabel("Name:")
        shortNameLbl = QLabel("Short Name:")
        
        if mode == "View":
            self.nameText = QLabel(company.name)
            self.shortNameText = QLabel(company.shortName)
        else:
            self.nameText = QLineEdit()
            self.shortNameText = QLineEdit()
        
        self.layout.addWidget(nameLbl, 0, 0)
        self.layout.addWidget(self.nameText, 0, 1)
        self.layout.addWidget(shortNameLbl, 1, 0)
        self.layout.addWidget(self.shortNameText, 1, 1)

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
        
        self.layout.addLayout(buttonLayout, 4, 0, 1, 2)
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
        
        self.layout.addWidget(self.nameText_edit, 0, 1)
        self.layout.addWidget(self.shortNameText_edit, 1, 1)

class AssetDialog(QDialog):
    def __init__(self, mode, parent=None, asset=None):
        super().__init__(parent)
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
        usefulLifeLbl = QLabel("Useful Life:")
        depMethodLbl = QLabel("Depreciation Method:")
        salvageValueLbl = QLabel("Salvage Amount:")
        costLbl = QLabel("Cost:")

        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)

        self.assetTypeBox = QComboBox()
        assetTypeList = []
        for assetType in parent.parent.dataConnection.assetTypes.values():
            assetTypeList.append(str("%4s" % assetType.idNum) + " - " + assetType.description)
        self.assetTypeBox.addItems(assetTypeList)

        self.childOfAssetBox = QComboBox()
        assetList = [""]
        for assetKey in parent.parent.dataConnection.assets:
            assetList.append(str("%4d - %s" % (parent.parent.dataConnection.assets[assetKey].idNum, parent.parent.dataConnection.assets[assetKey].description)))
        self.childOfAssetBox.addItems(assetList)
        
        self.depMethodBox = QComboBox()
        self.depMethodBox.addItems(constants.DEP_METHODS)
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % asset.company.idNum) + " - " + asset.company.shortName))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(asset.description)
            self.assetTypeBox.setCurrentIndex(self.assetTypeBox.findText(str("%4s" % asset.assetType.idNum) + " - " + asset.assetType.description))
            self.assetTypeBox.setEnabled(False)
            if asset.subAssetOf == None:
                subAssetOfText = ""
            else:
                subAssetOfText = "%4d - %s" % (asset.subAssetOf.idNum, asset.subAssetOf.description)
            self.childOfAssetBox.setCurrentText(subAssetOfText)
            self.childOfAssetBox.setEnabled(False)
            self.dateAcquiredText = QLabel(asset.acquireDate)
            self.dateInSvcText = QLabel(asset.inSvcDate)
            self.usefulLifeText = QLabel(str(asset.usefulLife))
            self.depMethodBox.setCurrentIndex(self.depMethodBox.findText(asset.depMethod))
            self.depMethodBox.setEnabled(False)
            self.salvageValueText = QLabel(str(asset.salvageAmount))
            self.costText = QLabel(str(asset.cost()))
        else:
            self.descriptionText = QLineEdit()
            self.dateAcquiredText = QLineEdit()
            self.dateInSvcText = QLineEdit()
            self.usefulLifeText = QLineEdit()
            self.salvageValueText = QLineEdit()
            self.costText = QLabel()

        #########
        ## Add a history tree widget
        #########

        #########
        ## Add a list of proposal (tree widget)
        #########
            
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
        self.layout.addWidget(usefulLifeLbl, 6, 0)
        self.layout.addWidget(self.usefulLifeText, 6, 1)
        self.layout.addWidget(depMethodLbl, 7, 0)
        self.layout.addWidget(self.depMethodBox, 7, 1)
        self.layout.addWidget(salvageValueLbl, 8, 0)
        self.layout.addWidget(self.salvageValueText, 8, 1)
        self.layout.addWidget(costLbl, 9, 0)
        self.layout.addWidget(self.costText, 9, 1)
        
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
        
        self.layout.addLayout(buttonLayout, 10, 0, 1, 2)
        self.setLayout(self.layout)

        if mode == "View":
            self.setWindowTitle("View/Edit Asset")
        else:
            self.setWindowTitle("New Asset")
        
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
        self.dateAcquiredText_edit = QLineEdit(self.dateAcquiredText.text())
        self.dateAcquiredText_edit.textEdited.connect(self.changed)
        self.dateInSvcText_edit = QLineEdit(self.dateInSvcText.text())
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

class InvoicePaymentDialog(QDialog):
    def __init__(self, parent=None, invoice=None):
        super().__init__(parent)

        vendorLbl = QLabel("Vendor:")
        invoiceLbl = QLabel("Invoice:")
        datePaidLbl = QLabel("Date Paid:")
        amountLbl = QLabel("Amount:")

        self.vendorText = QLabel(invoice.vendor.name)
        self.invoiceText = QLabel(str(invoice.idNum))
        self.datePaidText = QLineEdit()
        self.amountText = QLineEdit()
        
        self.layout = QGridLayout()
        self.layout.addWidget(vendorLbl, 0, 0)
        self.layout.addWidget(self.vendorText, 0, 1)
        self.layout.addWidget(invoiceLbl, 1, 0)
        self.layout.addWidget(self.invoiceText, 1, 1)
        self.layout.addWidget(datePaidLbl, 2, 0)
        self.layout.addWidget(self.datePaidText, 2, 1)
        self.layout.addWidget(amountLbl, 3, 0)
        self.layout.addWidget(self.amountText, 3, 1)

        buttonLayout = QHBoxLayout()
        
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        buttonLayout.addWidget(saveButton)
        
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(cancelButton)

        self.layout.addLayout(buttonLayout, 4, 0, 1, 2)
        self.setLayout(self.layout)

        self.setWindowTitle("Pay Invoice")

class ChangeProposalStatusDialog(QDialog):
    def __init__(self, proposalStatus, parent=None):
        super().__init__(parent)

        statusLbl = QLabel("Reason:")
        self.statusTxt = QLineEdit()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        
        layout = QVBoxLayout()
        subLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        
        subLayout.addWidget(statusLbl)
        subLayout.addWidget(self.statusTxt)
        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(subLayout)
        layout.addLayout(buttonLayout)
        
        self.setLayout(layout)

        self.setWindowTitle(proposalStatus + " Proposal")

class CloseProjectDialog(QDialog):
    def __init__(self, status, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        
        dateLbl = QLabel("Date:")
        self.dateTxt = QLineEdit()

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
            self.assetNameTxt = QLineEdit()
            inSvcLbl = QLabel("In Use:")
            self.inSvcChk = QCheckBox()
            usefulLifeLbl = QLabel("Useful Life:")
            self.usefulLifeTxt = QLineEdit()
            assetTypeLbl = QLabel("Asset Type:")
            self.assetTypeBox = QComboBox()
            assetList = []
            for assetType in parent.parent.dataConnection.assetTypes.values():
                assetList.append(str("%4s" % assetType.idNum) + " - " + assetType.description)
            self.assetTypeBox.addItems(assetList)

            layout.addWidget(assetNameLbl, nextRow, 0)
            layout.addWidget(self.assetNameTxt, nextRow, 1)
            nextRow += 1

            layout.addWidget(inSvcLbl, nextRow, 0)
            layout.addWidget(self.inSvcChk, nextRow, 1)
            nextRow += 1

            layout.addWidget(usefulLifeLbl, nextRow, 0)
            layout.addWidget(self.usefulLifeTxt, nextRow, 1)
            nextRow += 1

            layout.addWidget(assetTypeLbl, nextRow, 0)
            layout.addWidget(self.assetTypeBox, nextRow, 1)
            nextRow += 1

        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.accept)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)

        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(cancelButton)

        layout.addLayout(buttonLayout, nextRow, 0, 1, 2)

        self.setLayout(layout)

        self.setWindowTitle(status + "Project")

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
        
        glAccountsList = []
        glAccountsDict = GLDict.accounts()
        for glKey in glAccountsDict:
            glAccountsList.append(str("%4d - %s" % (glAccountsDict[glKey].idNum, glAccountsDict[glKey].description)))
        self.glAssetAccountsBox = QComboBox()
        self.glAssetAccountsBox.addItems(glAccountsList)
        glAccountsList.insert(0, "")
        self.glExpenseAccountsBox = QComboBox()
        self.glExpenseAccountsBox.addItems(glAccountsList)
        self.glAccumExpenseAccountsBox = QComboBox()
        self.glAccumExpenseAccountsBox.addItems(glAccountsList)
        
        if mode == "View":
            self.nameTxt = QLabel(assetType.description)
            self.glAssetAccountsBox.setCurrentIndex(self.glAssetAccountsBox.findText(str("%4d - %s" % (assetType.assetGLAccount.idNum, assetType.assetGLAccount.description))))
            if assetType.depreciable == True:
                self.depChk.setCheckState(Qt.Checked)
                self.glExpenseAccountsBox.setCurrentIndex(self.glExpenseAccountsBox.findText(str("%4d - %s" % (assetType.expenseGLAccount.idNum, assetType.expenseGLAccount.description))))
                self.glAccumExpenseAccountsBox.setCurrentIndex(self.glAccumExpenseAccountsBox.findText(str("%4d - %s" % (assetType.accumExpGLAccount.idNum, assetType. accumExpGLAccount.description))))
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
            
        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.accept)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        if mode == "View":
            editBtn = QPushButton("Edit")
            editBtn.clicked.connect(self.makeLabelsEditable)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(saveBtn)
        buttonLayout.addWidget(editBtn)
        buttonLayout.addWidget(cancelBtn)
        
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
        layout.addLayout(buttonLayout, 5, 0, 1, 2)
        
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
        
class AssetTypeDialog(QDialog):
    def __init__(self, assetTypeDict, GLDict, parent=None):
        super().__init__(parent)
        self.assetTypeDict = assetTypeDict
        self.GLDict = GLDict
        self.parent = parent
        
        valuesAsList = []
        for assetTypeKey in self.assetTypeDict:
            valuesAsList.append("%4d - %s" % (self.assetTypeDict[assetTypeKey].idNum, self.assetTypeDict[assetTypeKey].description))

        layout = QHBoxLayout()

        self.listWidget = QListWidget()
        self.listWidget.addItems(valuesAsList)
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
            newAssetType.addAssetGLAccount(self.parent.parent.dataConnection.glAccounts[assetGLAccountNum])
            newAssetType.addExpenseGLAccount(self.parent.parent.dataConnection.glAccounts[expenseGLAccountNum])
            newAssetType.addAccumExpGLAccount(self.parent.parent.dataConnection.glAccounts[accumExpenseGLAccountNum])
            
            self.listWidget.addItem("%4d - %s" % (newAssetType.idNum, newAssetType.description))
            self.parent.parent.dataConnection.assetTypes[newAssetType.idNum] = newAssetType
            
            self.parent.insertIntoDatabase("AssetTypes", "(AssetType, Depreciable)", "('" + newAssetType.description + "', " + str(depreciable) + ")")
            self.parent.insertIntoDatabase("Xref", "", "('assetTypes', " + str(newAssetType.idNum) + ", 'addAssetGLAccount', 'glAccounts', " + str(assetGLAccountNum) + ")")
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
                    assetType.addAssetGLAccount(self.parent.parent.dataConnection.glAccounts[assetGLNum])
                    self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addAssetGLAccount'",
                                                               (assetGLNum, assetTypeId))
                    if depreciable == 1:
                        expenseGLNum = self.parent.stripAllButNumbers(dialog.glExpenseAccountsBox.currentText())
                        accumExpGLNum = self.parent.stripAllButNumbers(dialog.glAccumExpenseAccountsBox.currentText())

                        assetType.addExpenseGLAccount(self.parent.parent.dataConnection.glAccounts[expenseGLNum])
                        assetType.addAccumExpGLAccount(self.parent.parent.dataConnection.glAccounts[accumExpGLNum])
                    
                        self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addExpenseGLAccount'",
                                                                   (expenseGLNum, assetTypeId))
                        self.parent.parent.parent.dbCursor.execute("UPDATE Xref SET ObjectIdBeingLinked=? WHERE ObjectToAddLinkTo='assetTypes' AND ObjectIdToAddLinkTo=? AND Method='addAccumExpGLAccount'",
                                                                   (accumExpGLNum, assetTypeId))

                self.parent.parent.parent.dbConnection.commit()

                item.setText("%4d - %s" % (assetType.idNum, assetType.description))

    def deleteAssetType(self):
        idxToDelete = self.listWidget.currentRow()
        item = self.listWidget.takeItem(idxToDelete)
        assetTypeId = self.parent.stripAllButNumbers(item.text())

        # Remove from the database
        self.parent.parent.dataConnection.assetTypes.pop(assetTypeId)
        self.parent.parent.parent.dbCursor.execute("DELETE FROM AssetTypes WHERE idNum=?", (assetTypeId,))
        self.parent.parent.parent.dbCursor.execute("DELETE FROM Xref WHERE ObjectIdToAddLinkTo=? AND ObjectToAddLinkTo='assetTypes'", (assetTypeId))
        self.parent.parent.parent.dbConnection.commit()

class DisposeAssetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        dispDateLbl = QLabel("Dispose Date:")
        dispAmtLbl = QLabel("Disposal Amount:")
        self.dispDateTxt = QLineEdit()
        self.dispAmtTxt = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(dispDateLbl, 0, 0)
        layout.addWidget(self.dispDateTxt, 0, 1)
        layout.addWidget(dispAmtLbl, 1, 0)
        layout.addWidget(self.dispAmtTxt, 1, 1)
        
        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.accept)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)
        
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(saveBtn)
        buttonLayout.addWidget(cancelBtn)
        
        layout.addLayout(buttonLayout, 2, 0, 1, 2)
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
        valueAsList = []
        tempDict = parent.parent.dataConnection.glAccounts.accountGroups()
        for acctGroupKey in tempDict.sortedListOfKeys():
            valueAsList.append(str("%4d - %s" %  (tempDict[acctGroupKey].idNum, tempDict[acctGroupKey].description)))
        self.acctGrpsBox.addItems(valueAsList)
        
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
                self.acctGrpsBox.setCurrentIndex(self.acctGrpsBox.findText(str("%4d - %s" % (glAccount.childOf.idNum, glAccount.childOf.description))))
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
        
        self.layout.addLayout(buttonLayout, 4, 0, 1, 2)
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
