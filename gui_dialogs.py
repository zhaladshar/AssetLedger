from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from constants import PROPOSAL_STATUSES
import gui_elements

class VendorDialog(QDialog):
    def __init__(self, mode, parent=None, vendor=None):
        super().__init__(parent)
        self.vendor = vendor
        self.hasChanges = False

        self.layout = QGridLayout()

        nameLbl = QLabel("Name:")
        nameLbl.setStyleSheet("QLabel { background-color: red }")
        addressLbl = QLabel("Address:")
        addressLbl.setStyleSheet("QLabel { background-color: red }")
        cityLbl = QLabel("City:")
        cityLbl.setStyleSheet("QLabel { background-color: red }")
        stateLbl = QLabel("State:")
        stateLbl.setStyleSheet("QLabel { background-color: red }")
        zipLbl = QLabel("ZIP:")
        zipLbl.setStyleSheet("QLabel { background-color: red }")
        phoneLbl = QLabel("Phone:")
        phoneLbl.setStyleSheet("QLabel { background-color: red }")

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
                self.assetProjSelector.assetRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % invoice.assetProj[1].idNum) + " - " + invoice.assetProj[1].description))
            else:
                self.assetProjSelector.projRdoBtn.setChecked(True)
                self.assetProjSelector.selector.setCurrentIndex(self.assetProjSelector.selector.findText(str("%4s" % invoice.assetProj[1].idNum) + " - " + invoice.assetProj[1].description))
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
            self.detailsWidget = gui_elements.InvoiceDetailWidget(proposal.details)
        else:
            self.detailsWidget = gui_elements.InvoiceDetailWidget()
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

        ########################
        #### Add payment history for View mode
        ########################

        self.layout.addLayout(buttonLayout, 6, 0, 1, 2)
        self.setLayout(self.layout)

    def updateDetailInvoiceWidget(self):
        selection = self.assetProjSelector.selector.currentText()
        selectionId = self.parent.stripAllButNumbers(selection)
        
        if self.assetProjSelector.assetSelected() == True:
            pass
        else:
            acceptedProposal = self.parent.parent.dataConnection.projects[selectionId].proposals.proposalsByStatus("Open")

            if acceptedProposal:
                proposal = list(acceptedProposal.values())[0]
            else:
                proposal = None
            
        print("here")
        self.detailsWidget.addProposal(proposal)
        print("and here")

    def makeLabelsEditable(self):
        self.companyBox.setEnabled(True)
        self.companyBox.currentIndexChanged.connect(self.companyChange)
        self.vendorBox.setEnabled(True)
        self.vendorBox.currentIndexChanged.connect(self.vendorChange)
        self.assetProjSelector.setEnabled(True)
        self.assetProjSelector.changed.connect(self.projectAssetChange)
        self.invoiceDateText_edit = QLineEdit(self.invoiceDateText.text())
        self.invoiceDateText_edit.textEdited.connect(self.changed)
        self.dueDateText_edit = QLineEdit(self.dueDateText.text())
        self.dueDateText_edit.textEdited.connect(self.changed)

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
        self.hasChanged = True

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
        self.statusBox.addItems(PROPOSAL_STATUSES)
        
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
