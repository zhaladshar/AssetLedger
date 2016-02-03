from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import constants
import gui_elements
import classes

class VendorDialog(QDialog):
    def __init__(self, mode, parent=None, vendor=None):
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
            invoicesWidget = gui_elements.InvoiceTreeWidget(self.vendor.invoices)
            invoicesWidget.setIndentation(0)
            invoicesWidget.setHeaderHidden(True)
            self.layout.addWidget(invoicesWidget, nextRow, 0, 1, 2)
            nextRow += 1

            proposalsWidget = gui_elements.ProposalTreeWidget(self.vendor.proposals, True)
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
    def __init__(self, mode, parent=None, project=None):
        super().__init__(parent)
        self.hasChanges = False
        self.companyChanged = False

        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        startDateLbl = QLabel("Start Date:")
        self.endDateLbl = QLabel("End Date:")
        
        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % project.company.idNum) + " - " + project.company.shortName))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(project.description)
            self.startDateText = QLabel(project.dateStart)
            self.endDateText = QLineEdit()
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
        
        self.layout.addLayout(buttonLayout, 4, 0, 1, 2)
        self.setLayout(self.layout)
        
    def changed(self):
        self.hasChanges = True

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.startDateText_edit = QLineEdit(self.startDateText.text())
        self.startDateText_edit.textEdited.connect(self.changed)

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

        self.layout = QGridLayout()
        
        companyLbl = QLabel("Company:")
        descriptionLbl = QLabel("Description:")
        assetTypeLbl = QLabel("Asset Type:")
        dateAcquiredLbl = QLabel("Date Acquired:")
        dateInSvcLbl = QLabel("Date in Service:")
        usefulLifeLbl = QLabel("Useful Life:")
        costLbl = QLabel("Cost:")

        self.companyBox = QComboBox()
        companyList = []
        for company in parent.parent.dataConnection.companies.values():
            companyList.append(str("%4s" % company.idNum) + " - " + company.shortName)
        self.companyBox.addItems(companyList)

        self.assetTypeBox = QComboBox()
        assetList = []
        for assetType in parent.parent.dataConnection.assetTypes.values():
            assetList.append(str("%4s" % assetType.idNum) + " - " + assetType.description)
        self.assetTypeBox.addItems(assetList)
        
        if mode == "View":
            self.companyBox.setCurrentIndex(self.companyBox.findText(str("%4s" % asset.company.idNum) + " - " + asset.company.shortName))
            self.companyBox.setEnabled(False)
            self.descriptionText = QLabel(asset.description)
            self.assetTypeBox.setCurrentIndex(self.assetTypeBox.findText(str("%4s" % asset.assetType.idNum) + " - " + asset.assetType.description))
            self.assetTypeBox.setEnabled(False)
            self.dateAcquiredText = QLabel(asset.acquireDate)
            self.dateInSvcText = QLabel(asset.inSvcDate)
            self.usefulLifeText = QLabel(str(asset.usefulLife))
            self.costText = QLabel(str(asset.cost()))
        else:
            self.descriptionText = QLineEdit()
            self.dateAcquiredText = QLineEdit()
            self.dateInSvcText = QLineEdit()
            self.usefulLifeText = QLineEdit()
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
        self.layout.addWidget(dateAcquiredLbl, 3, 0)
        self.layout.addWidget(self.dateAcquiredText, 3, 1)
        self.layout.addWidget(dateInSvcLbl, 4, 0)
        self.layout.addWidget(self.dateInSvcText, 4, 1)
        self.layout.addWidget(usefulLifeLbl, 5, 0)
        self.layout.addWidget(self.usefulLifeText, 5, 1)
        self.layout.addWidget(costLbl, 6, 0)
        self.layout.addWidget(self.costText, 6, 1)
        
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
        
        self.layout.addLayout(buttonLayout, 7, 0, 1, 2)
        self.setLayout(self.layout)
        
    def changed(self):
        self.hasChanges = True

    def companyChange(self):
        self.companyChanged = True
        self.hasChanges = True

    def assetTypeChange(self):
        self.assetTypeChanged = True
        self.hasChanges = True
        
    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.descriptionText_edit = QLineEdit(self.descriptionText.text())
        self.descriptionText_edit.textEdited.connect(self.changed)
        self.assetTypeBox.setEnabled(True)
        self.assetTypeBox.currentIndexChanged.connect(self.assetTypeChange)
        self.dateAcquiredText_edit = QLineEdit(self.dateAcquiredText.text())
        self.dateAcquiredText_edit.textEdited.connect(self.changed)
        self.dateInSvcText_edit = QLineEdit(self.dateInSvcText.text())
        self.dateInSvcText_edit.textEdited.connect(self.changed)
        self.usefulLifeText_edit = QLineEdit(self.usefulLifeText.text())
        self.usefulLifeText_edit.textEdited.connect(self.changed)
        
        self.layout.addWidget(self.descriptionText_edit, 1, 1)
        self.layout.addWidget(self.dateAcquiredText_edit, 3, 1)
        self.layout.addWidget(self.dateInSvcText_edit, 4, 1)
        self.layout.addWidget(self.usefulLifeText_edit, 5, 1)

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
    def __init__(self, mode, parent=None, assetType=None):
        super().__init__(parent)
        nameLbl = QLabel("Name:")
        depLbl = QLabel("Depreciable:")

        if mode == "View":
            self.nameTxt = QLineEdit(assetType.description)
            self.depChk = QCheckBox()
            if assetType.depreciable == True:
                self.depChk.setCheckState(Qt.Checked)
        else:
            self.nameTxt = QLineEdit()
            self.depChk = QCheckBox()
            
        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.accept)
        cancelBtn = QPushButton("Cancel")
        cancelBtn.clicked.connect(self.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(saveBtn)
        buttonLayout.addWidget(cancelBtn)
        
        layout = QGridLayout()
        layout.addWidget(nameLbl, 0, 0)
        layout.addWidget(self.nameTxt, 0, 1)
        layout.addWidget(depLbl, 1, 0)
        layout.addWidget(self.depChk, 1, 1)
        layout.addLayout(buttonLayout, 2, 0, 1, 2)

        self.setLayout(layout)
        
class AssetTypeDialog(QDialog):
    def __init__(self, assetTypeDict, parent=None):
        super().__init__(parent)
        self.assetTypeDict = assetTypeDict
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

    def newAssetType(self):
        dialog = NewAssetTypeDialog("New", self)
        if dialog.exec_():
            nextAssetTypeId = self.parent.nextIdNum("AssetTypes")
            
            if dialog.depChk.checkState() == Qt.Checked:
                depreciable = 1
            else:
                depreciable = 0
            newAssetType = classes.AssetType(dialog.nameTxt.text(),
                                             depreciable,
                                             nextAssetTypeId)
            
            self.listWidget.addItem("%4d - %s" % (newAssetType.idNum, newAssetType.description))
            self.parent.parent.dataConnection.assetTypes[newAssetType.idNum] = newAssetType
            
            self.parent.insertIntoDatabase("AssetTypes", "(AssetType, Depreciable)", "('" + newAssetType.description + "', " + str(depreciable) + ")")
            self.parent.parent.parent.dbConnection.commit()

    def showAssetType(self):
        idxToShow = self.listWidget.currentRow()
        item = self.listWidget.item(idxToShow)
        assetTypeId = self.parent.stripAllButNumbers(item.text())
        assetType = self.assetTypeDict[assetTypeId]
        
        dialog = NewAssetTypeDialog("View", self, assetType)
        if dialog.exec_():
            assetType.description = dialog.nameTxt.text()

            if dialog.depChk.checkState() == Qt.Checked:
                depreciable = 1
                assetType.depreciable = True
            else:
                depreciable = 0
                assetType.depreciable = False

            self.parent.parent.parent.dbCursor.execute("UPDATE AssetTypes SET AssetType=?, Depreciable=? WHERE idNum=?", (assetType.description, depreciable, assetType.idNum))
            self.parent.parent.parent.dbConnection.commit()

            item.setText("%4d - %s" % (assetType.idNum, assetType.description))

    def deleteAssetType(self):
        idxToDelete = self.listWidget.currentRow()
        item = self.listWidget.takeItem(idxToDelete)
        assetTypeId = self.parent.stripAllButNumbers(item.text())

        # Remove from the database
        self.parent.parent.dataConnection.assetTypes.pop(assetTypeId)
        self.parent.parent.parent.dbCursor.execute("DELETE FROM AssetTypes WHERE idNum=?", (assetTypeId,))
        self.parent.parent.parent.dbConnection.commit()
