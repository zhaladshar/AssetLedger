import constants

class VendorsDict(dict):
    def __init__(self):
        super().__init__()

    def vendorsByCompany(self, companyId):
        if companyId:
            newDict = VendorsDict()
            for vendorId, vendor in self.items():
                if vendor.invoices.invoicesByCompany(companyId) or vendor.proposals.proposalsByCompany(companyId):
                    newDict[vendorId] = vendor
            return newDict
        else:
            return self

class GLPostingsDetailsDict(dict):
    def __init__(self):
        super().__init__()

    def postingsByDRCR(self, drcr):
        tempDict = GLPostingsDetailsDict()
        for key, glDet in self.items():
            if glDet.debitCredit == drcr:
                tempDict[key] = glDet
        return tempDict

    def balance(self):
        balance = 0.0
        for key, glDet in self.items():
            balance += glDet.amount
        return balance
    
class GLPostingsDict(dict):
    def __init__(self):
        super().__init__()

    def postingsByGLAcct(self, glAcctNum):
        tempDict = GLPostingsDetailsDict()
        for key in self:
            for detailKey in self[key].details:
                if self[key].details[detailKey].glAccount.idNum == glAcctNum:
                    tempDict[detailKey] = self[key].details[detailKey]
        return tempDict
    
class GLAccountsDict(dict):
    def __init__(self):
        super().__init__()

    def accountGroups(self):
        tempDict = GLAccountsDict()
        for glKey in self:
            if self[glKey].placeHolder == True:
                tempDict[glKey] = self[glKey]
        return tempDict

    def accounts(self):
        tempDict = GLAccountsDict()
        for glKey in self:
            if self[glKey].placeHolder != True:
                tempDict[glKey] = self[glKey]
        return tempDict

    def sortedListOfKeys(self):
        sortedList = sorted(list(self), key=lambda x: x)
        return sortedList

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

    def invoicesByCompany(self, companyId):
        if companyId:
            newDict = InvoicesDict()
            for invoiceId, invoice in self.items():
                if invoice.company.idNum == companyId:
                    newDict[invoiceId] = invoice
            return newDict
        else:
            return self

class ProposalsDict(dict):
    def __init__(self):
        super().__init__()

    def proposalsByStatus(self, status):
        tempDict = {}
        for proposalKey in self:
            if self[proposalKey].status == status:
                tempDict[proposalKey] = self[proposalKey]
        return tempDict

    def proposalsByCompany(self, companyId):
        if companyId:
            newDict = ProposalsDict()
            for proposalId, proposal in self.items():
                if proposal.company.idNum == companyId:
                    newDict[proposalId] = proposal
            return newDict
        else:
            return self

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
        self.glAccount = None
        self.company = None
        self.becameAsset = None
        self.glPostings = {}

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

    def addGLAccount(self, glAccount):
        self.glAccount = glAccount
        
    def addCompany(self, company):
        self.company = company

    def addGLPosting(self, glPosting):
        self.glPostings[glPosting.idNum] = glPosting

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
        self.glPosting = None

    def addInvoice(self, invoice):
        self.invoicePaid = invoice

    def addGLPosting(self, glPosting):
        self.glPosting = glPosting

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
        self.glPosting = None

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

    def addGLPosting(self, glPosting):
        self.glPosting = glPosting

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
        self.glAccount = None

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

    def addGLAccount(self, glAccount):
        self.glAccount = glAccount

class Company:
    def __init__(self, name, shortName, active, idNum):
        self.idNum = idNum
        self.name = name
        self.shortName = shortName
        self.active = active
        self.proposals = {}
        self.projects = {}
        self.assets = AssetsDict()
        self.invoices = {}

    def assetsAmount(self):
        return self.assets.currentCost()

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
        self.assetGLAccount = None
        self.expenseGLAccount = None
        self.accumExpGLAccount = None

    def addAssetGLAccount(self, glAccount):
        self.assetGLAccount = glAccount

    def addExpenseGLAccount(self, glAccount):
        self.expenseGLAccount = glAccount

    def addAccumExpGLAccount(self, glAccount):
        self.accumExpGLAccount = glAccount

class GLAccount:
    def __init__(self, description, placeHolder, idNum):
        self.idNum = idNum
        self.description = description
        if placeHolder == 0:
            self.placeHolder = False
        else:
            self.placeHolder = True
        self.childOf = None
        self.parentOf = GLAccountsDict()
        self.postings = GLPostingsDetailsDict()

    def addChild(self, child):
        self.parentOf[child.idNum] = child

    def removeChild(self, child):
        self.parentOf.pop(child.idNum)

    def addParent(self, parent):
        self.childOf = parent

    def addPosting(self, posting):
        self.postings[posting.idNum] = posting

    def removePosting(self, posting):
        self.postings.pop(posting.idNum)

    def balance(self):
        balance = 0
        if self.placeHolder == True:
            for childKey in self.parentOf:
                balance += self.parentOf[childKey].balance()
        else:
            balance = self.postings.postingsByDRCR("DR").balance() - self.postings.postingsByDRCR("CR").balance()
        return balance

class GLPosting:
    def __init__(self, date, description, idNum):
        self.idNum = idNum
        self.date = date
        self.description = description
        self.details = GLPostingsDetailsDict()

    def addDetail(self, detail):
        self.details[detail.idNum] = detail

class GLPostingDetail:
    def __init__(self, amount, debitCredit, idNum):
        self.idNum = idNum
        self.amount = amount
        self.debitCredit = debitCredit
        self.glAccount = None
        self.detailOf = None

    def addDetailOf(self, detailOf):
        self.detailOf = detailOf

    def addGLAccount(self, glAccount):
        self.glAccount = glAccount

class PaymentType:
    def __init__(self, description, idNum):
        self.idNum = idNum
        self.description = description
        self.glAccount = None

    def addGLAccount(self, glAccount):
        self.glAccount = glAccount
        
class CorporateStructure:
    def __init__(self):
        self.companies = CompanyDict()
        self.vendors = VendorsDict()
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
        self.glPostings = GLPostingsDict()
        self.glPostingsDetails = {}
        self.paymentTypes = {}
