import constants

class GLAccountsDict(dict):
    def __init__(self):
        super().__init__()

    def accountGroups(self):
        tempDict = {}
        for glKey in self:
            if self[glKey].placeHolder == True:
                tempDict[glKey] = self[glKey]
        return tempDict

class InvoicesDict(dict):
    def __init__(self):
        super().__init__()

    def openInvoices(self):
        tempDict = {}
        for invoiceKey in self:
            if self[invoiceKey].balance() != 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

    def paidInvoices(self):
        tempDict = {}
        for invoiceKey in self:
            if self[invoiceKey].balance() == 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

class ProposalsDict(dict):
    def __init__(self):
        super().__init__()

    def proposalsByStatus(self, status):
        tempDict = {}
        for proposalKey in self:
            if self[proposalKey].status == status:
                tempDict[proposalKey] = self[proposalKey]
        return tempDict

class ProjectsDict(dict):
    def __init__(self):
        super().__init__()

    def projectsByStatus(self, status):
        tempDict = {}
        for projectKey in self:
            if self[projectKey].status() == status:
                tempDict[projectKey] = self[projectKey]
        return tempDict

class AssetsDict(dict):
    def __init__(self):
        super().__init__()

    def currentCost(self):
        amount = 0
        assetsDict = self.currentAssets()
        
        for key in assetsDict:
            amount += assetsDict[key].cost()
        return amount

    def disposedCost(self):
        amount = 0
        assetsDict = self.disposedAssets()

        for key in assetsDict:
            amount += assetsDict[key].cost()
        return amount

    def topLevelAssets(self):
        assetDict = AssetsDict()
        for assetKey in self:
            if self[assetKey].subAssetOf == None:
                assetDict[assetKey] = self[assetKey]
        return assetDict

    def currentAssets(self, topLevelOnlyFg=False, companyId=None):
        assetDict = AssetsDict()
        for assetKey in self:
            if self[assetKey].disposeDate == "" or self[assetKey].disposeDate == None:
                assetDict[assetKey] = self[assetKey]

        if topLevelOnlyFg == True:
            assetDict = assetDict.topLevelAssets()

        if companyId:
            assetDict = assetDict.assetsByCompany(companyId)
            
        return assetDict

    def assetsByCompany(self, companyId):
        assetDict = AssetsDict()
        for assetKey in self:
            if self[assetKey].company.idNum == companyId:
                assetDict[assetKey] = self[assetKey]
        return assetDict

    def disposedAssets(self):
        assetDict = {}
        for assetKey in self:
            if self[assetKey].disposeDate != "" and self[assetKey].disposeDate != None:
                assetDict[assetKey] = self[assetKey]
        return assetDict
            
class CompanyDict(dict):
    def __init__(self):
        super().__init__()

    def dictToList(self):
        newList = []
        for each in self.values():
            newList.append(each.shortName)

        return newList

class ProposalDetail:
    def __init__(self, description, cost, idNum):
        self.idNum = idNum
        self.description = description
        self.cost = cost
        self.detailOf = None
        self.invoiceDetails = {}

    def addDetailOf(self, proposal):
        self.detailOf = proposal

    def addInvoiceDetail(self, invoiceDetail):
        self.invoiceDetails[invoiceDetail.idNum] = invoiceDetail

    def removeInvoiceDetail(self, invoiceDetail):
        self.invoiceDetails.pop(invoiceDetail.idNum)

class Proposal:
    def __init__(self, date, status, statusReason, idNum):
        self.idNum = idNum
        self.date = date
        self.status = status
        self.statusReason = statusReason
        self.company = None
        self.vendor = None
        self.proposalFor = None
        self.details = {}

    def addCompany(self, company):
        self.company = company
        
    def addVendor(self, vendor):
        self.vendor = vendor

    def addProject(self, project):
        self.proposalFor = ("projects", project)

    def addAsset(self, asset):
        self.proposalFor = ("assets", asset)

    def addDetail(self, detail):
        self.details[detail.idNum] = detail

    def totalCost(self):
        cost = 0
        for detailKey in self.details.keys():
            cost += self.details[detailKey].cost
        return cost

    def accept(self):
        self.status = constants.ACC_PROPOSAL_STATUS

    def reject(self):
        self.status = constants.REJ_PROPOSAL_STATUS

class Project:
    def __init__(self, desc, dateStart, notes, idNum, dateEnd=None):
        self.idNum = idNum
        self.description = desc
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.notes = notes
        self.invoices = {}
        self.proposals = ProposalsDict()
        self.company = None
        self.becameAsset = None

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def addAsset(self, asset):
        self.becameAsset = asset

    def addProposal(self, proposal):
        self.proposals[proposal.idNum] = proposal

    def removeProposal(self, proposal):
        self.proposals.pop(proposal.idNum)

    def addCompany(self, company):
        self.company = company

    def status(self):
        if self.dateEnd == None or self.dateEnd == "":
            return constants.OPN_PROJECT_STATUS
        elif (self.dateEnd != None and self.dateEnd != "") and self.becameAsset == None:
            return constants.ABD_PROJECT_STATUS
        elif (self.dateEnd != None and self.dateEnd != "") and self.becameAsset != None:
            return constants.CMP_PROJECT_STATUS
        else:
            return "ERROR CALCULATING PROJECT STATUS"

    def calculateCIP(self):
        CIP = 0
        for invoiceKey in self.invoices:
            CIP += self.invoices[invoiceKey].amount()
        return CIP

class InvoicePayment:
    def __init__(self, datePaid, amountPaid, idNum):
        self.idNum = idNum
        self.invoicePaid = None
        self.datePaid = datePaid
        self.amountPaid = amountPaid

    def addInvoice(self, invoice):
        self.invoicePaid = invoice

class InvoiceDetail:
    def __init__(self, description, amount, idNum):
        self.idNum = idNum
        self.description = description
        self.cost = amount
        self.detailOf = None
        self.proposalDetail = None

    def addDetailOf(self, invoice):
        self.detailOf = invoice

    def addProposalDetail(self, propDet):
        self.proposalDetail = propDet

class Invoice:
    def __init__(self, date, dueDate, idNum):
        self.idNum = idNum
        self.invoiceDate = date
        self.dueDate = dueDate
        self.vendor = None
        self.company = None
        self.assetProj = None
        self.payments = {}
        self.details = {}

    def amount(self):
        amount = 0.0
        for detailKey in self.details:
            amount += self.details[detailKey].cost
        return amount

    def balance(self):
        return self.amount() - self.paid()

    def paid(self):
        amtPaid = 0.0
        for paymentKey in self.payments:
            amtPaid += self.payments[paymentKey].amountPaid
        return amtPaid

    def addVendor(self, vendor):
        self.vendor = vendor

    def addCompany(self, company):
        self.company = company

    def addProject(self, project):
        self.assetProj = ("projects", project)

    def addAsset(self, asset):
        self.assetProj = ("assets", asset)

    def addDetail(self, detail):
        self.details[detail.idNum] = detail

    def removeDetail(self, detail):
        self.details.pop(detail.idNum)

    def addPayment(self, payment):
        self.payments[payment.idNum] = payment

    def removePayment(self, payment):
        self.payments.pop(payment.idNum)

class Cost:
    def __init__(self, amount, date, idNum):
        self.idNum = idNum
        self.date = date
        self.cost = amount
        self.assetProj = None

    def addProject(self, project):
        self.assetProj = ("projects", project)

    def addAsset(self, asset):
        self.assetProj = ("assets", asset)

class Vendor:
    def __init__(self, name, address, city, state, zipcode, phone, idNum):
        self.idNum = idNum
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zip = zipcode
        self.phone = phone
        self.proposals = ProposalsDict()
        self.invoices = InvoicesDict()

    def balance(self):
        amountPaid = 0.0
        amountInvoiced = 0.0
        for invoiceKey in self.invoices:
            amountPaid += self.invoices[invoiceKey].paid()
            amountInvoiced += self.invoices[invoiceKey].amount()
        return amountInvoiced - amountPaid

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def openInvoiceCount(self):
        count = 0
        for invoiceKey in self.invoices:
            if self.invoices[invoiceKey].balance() != 0.0:
                count += 1
        return count

    def addProposal(self, proposal):
        self.proposals[proposal.idNum] = proposal

    def removeProposal(self, proposal):
        self.proposals.pop(proposal.idNum)

class Company:
    def __init__(self, name, shortName, active, idNum):
        self.idNum = idNum
        self.name = name
        self.shortName = shortName
        self.active = active
        self.proposals = {}
        self.projects = {}
        self.assets = {}
        self.invoices = {}

    def assetsAmount(self):
        amount = 0
        for key in self.assets:
            pass

        return amount

    def CIPAmount(self):
        CIP = 0
        for key in self.projects:
            CIP += self.projects[key].calculateCIP()

        return CIP

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def addProposal(self, proposal):
        self.proposals[proposal.idNum] = proposal

    def removeProposal(self, proposal):
        self.proposals.pop(proposal.idNum)

    def addProject(self, project):
        self.projects[project.idNum] = project

    def removeProject(self, project):
        self.projects.pop(project.idNum)

    def addAsset(self, asset):
        self.assets[asset.idNum] = asset

    def removeAsset(self, asset):
        self.assets.pop(asset.idNum)

class Asset:
    def __init__(self, desc, acqDate, inSvcDate, disposeDate, disposeAmount, usefulLife, salvageAmt, depMethod, idNum):
        self.idNum = idNum
        self.description = desc
        self.acquireDate = acqDate
        self.inSvcDate = inSvcDate
        self.disposeDate = disposeDate
        self.disposeAmount = disposeAmount
        self.usefulLife = usefulLife
        self.salvageAmount = salvageAmt
        self.depMethod = depMethod
        self.assetType = None
        self.company = None
        self.fromProject = None
        self.subAssetOf = None
        self.invoices = {}
        self.costs = {}
        self.history = {}
        self.subAssets = {}
        self.proposals = ProposalsDict()

    def addAssetType(self, assetType):
        self.assetType = assetType
        
    def addCompany(self, company):
        self.company = company

    def addProject(self, project):
        self.fromProject = project

    def addProposal(self, proposal):
        self.proposals[proposal.idNum] = proposal

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def addCost(self, cost):
        self.costs[cost.idNum] = cost

    def addSubAsset(self, asset):
        self.subAssets[asset.idNum] = asset

    def removeSubAsset(self, asset):
        self.subAssets.pop(asset.idNum)

    def addSubAssetOf(self, asset):
        self.subAssetOf = asset

    def removeSubAssetOf(self):
        self.subAssetOf = None
        
    def cost(self):
        amount = 0.0
        for invoiceKey in self.invoices:
            amount += self.invoices[invoiceKey].amount()
        for costKey in self.costs:
            amount += self.costs[costKey].cost
        return amount

    def depreciatedAmount(self):
        return 0

    def inSvc(self):
        if self.disposeDate == "" or self.disposeDate == None:
            return True
        else:
            return False

class AssetType:
    def __init__(self, description, depreciable, idNum):
        self.idNum = idNum
        self.description = description
        if depreciable == 0:
            self.depreciable = False
        else:
            self.depreciable = True

class GLAccount:
    def __init__(self, description, placeHolder, idNum):
        self.idNum = idNum
        self.description = description
        if placeHolder == 0:
            self.placeHolder = False
        else:
            self.placeHolder = True
        self.childOf = None
        self.parentOf = {}

    def addChild(self, child):
        self.parentOf[child.idNum] = child

    def addParent(self, parent):
        self.childOf = parent
        
class CorporateStructure:
    def __init__(self):
        self.companies = CompanyDict()
        self.vendors = {}
        self.invoices = InvoicesDict()
        self.invoicesDetails = {}
        self.invoicesPayments = {}
        self.costs = {}
        self.proposals = ProposalsDict()
        self.proposalsDetails = {}
        self.assets = AssetsDict()
        self.assetTypes = {}
        self.projects = ProjectsDict()
        self.glAccounts = GLAccountsDict()
