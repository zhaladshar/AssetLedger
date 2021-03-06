import datetime
import constants

class NewDate(datetime.date):
    def __new__(cls, string):
        dt = datetime.datetime.strptime(string, constants.DATE_FORMAT)
        return super().__new__(cls, dt.year, dt.month, dt.day)
    
    def __str__(self):
        return self.strftime(constants.DATE_FORMAT)

    def isLeapYear(self):
        if self.year % 4 == 0:
            if self.year % 100 == 0:
                if self.year % 400 == 0:
                    return True
                else:
                    return False
            else:
                return True
        else:
            return False

    @staticmethod
    def dateDiff(diffType, fromDate, toDate):
        if diffType == "m":
            origYear = fromDate.year
            origMo = fromDate.month
            currYear = toDate.year
            currMo = toDate.month

            return (currYear - origYear) * 12 + (currMo - origMo)

    @staticmethod
    def getDaysInMonth(date, offset=0):
        if date.month + offset in [1, 3, 5, 7, 8, 10, 12]:
            day = 31
        elif date.month + offset in [4, 6, 9, 11]:
            day = 30
        else:
            if date.isLeapYear() == True:
                day = 29
            else:
                day = 28
        return day
        
    @classmethod
    def incrementMonth(cls, date):
        day = date.day
        month = date.month
        year = date.year

        month += 1
        if month == 13:
            month = 1
            year += 1

        day = min(day, NewDate.getDaysInMonth(date, 1))

        dateString = "%d/%d/%d" % (month, day, year)
        return NewDate(dateString)

    @classmethod
    def nextPeriodEnding(cls, date):
        newDate = cls.incrementMonth(date)
        day = NewDate.getDaysInMonth(newDate)
        return NewDate("%d/%d/%d" % (newDate.month, day, newDate.year))
    
class SortableDict(dict):
    def __init__(self):
        super().__init__()

    def sortedListOfKeys(self):
        sortedList = sorted(list(self), key=lambda x: x)
        return sortedList

    def sortedListOfKeysAndNames(self, attrName):
        sortedListOfKeys = self.sortedListOfKeys()
        sortedListOfKeysAndNames = []
        for key in sortedListOfKeys:
            sortedListOfKeysAndNames.append(constants.ID_DESC % (key, getattr(self[key], attrName)))
        return sortedListOfKeysAndNames

class AssetTypesDict(SortableDict):
    def __init__(self):
        super().__init__()

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames = super().sortedListOfKeysAndNames("description")
        return sortListOfKeysNames        

class PaymentTypesDict(SortableDict):
    def __init__(self):
        super().__init__()

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames = super().sortedListOfKeysAndNames("description")
        return sortListOfKeysNames        

class VendorsDict(SortableDict):
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

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames = super().sortedListOfKeysAndNames("name")
        return sortListOfKeysNames

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
    
class GLAccountsDict(SortableDict):
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

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames = super().sortedListOfKeysAndNames("description")
        return sortListOfKeysNames

class InvoicesDict(dict):
    def __init__(self):
        super().__init__()

    def openInvoices(self):
        tempDict = InvoicesDict()
        for invoiceKey in self:
            if self[invoiceKey].balance() != 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

    def paidInvoices(self):
        tempDict = InvoicesDict()
        for invoiceKey in self:
            if self[invoiceKey].balance() == 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

    def trueInvoices(self):
        tempDict = InvoicesDict()
        for invoiceKey in self:
            if self[invoiceKey].vendor:
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

class ProjectsDict(SortableDict):
    def __init__(self):
        super().__init__()

    def projectsByStatus(self, status):
        tempDict = ProjectsDict()
        for projectKey in self:
            if self[projectKey].status() == status:
                tempDict[projectKey] = self[projectKey]
        return tempDict

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames = super().sortedListOfKeysAndNames("description")
        return sortListOfKeysNames

class AssetsDict(SortableDict):
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
        assetDict = AssetsDict()
        for assetKey in self:
            if self[assetKey].disposeDate != "" and self[assetKey].disposeDate != None:
                assetDict[assetKey] = self[assetKey]
        return assetDict

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames= super().sortedListOfKeysAndNames("description")
        return sortListOfKeysNames
            
class CompanyDict(SortableDict):
    def __init__(self):
        super().__init__()

    def dictToList(self):
        newList = []
        for each in self.values():
            newList.append(each.shortName)

        return newList

    def sortedListOfKeysAndNames(self):
        sortListOfKeysNames= super().sortedListOfKeysAndNames("shortName")
        return sortListOfKeysNames

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
        self.invoices = InvoicesDict()
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
        self.paymentType = None

    def addInvoice(self, invoice):
        self.invoicePaid = invoice

    def addGLPosting(self, glPosting):
        self.glPosting = glPosting

    def addPaymentType(self, paymentType):
        self.paymentType = paymentType

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
    def __init__(self, date, dueDate, company, vendor, idNum):
        self.idNum = idNum
        self.date = date
        self.dueDate = dueDate
        self.vendor = vendor
        self.company = company
        self.assetProj = None
        self.payments = {}
        self.details = {}
        self.glPosting = None

    def amount(self):
        amount = 0.0
        for detailKey in self.details:
            amount += self.details[detailKey].cost
        return round(amount, 2)

    def balance(self):
        return round(self.amount() - self.paid(), 2)

    def paid(self):
        amtPaid = 0.0
        for paymentKey in self.payments:
            amtPaid += self.payments[paymentKey].amountPaid
        return round(amtPaid, 2)

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
        self.projects = ProjectsDict()
        self.assets = AssetsDict()
        self.invoices = {}
        self.glPostings = GLPostingsDict()

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

    def addPosting(self, posting):
        self.glPostings[posting.idNum] = posting

    def removePosting(self, posting):
        self.glPostings.pop(posting.idNum)

class DepreciationExpense:
    def __init__(self, date, amount, idNum):
        self.idNum = idNum
        self.date = date
        self.amount = amount
        self.assetCost = None

    def addAssetCost(self, assetCost):
        self.assetCost = assetCost

class AssetHistory:
    def __init__(self, date, text, amount, posNeg, idNum):
        self.idNum = idNum
        self.date = date
        self.text = text
        self.amount = amount
        self.posNeg = posNeg
        self.asset = None
        self.object = None

    def addAsset(self, asset):
        self.asset = asset

    # object_ should be the AssetCost associated with this history transaction
    def addObject(self, object_):
        self.object = object_
        
class AssetCost:
    def __init__(self, cost, date, assetId, reference, idNum):
        self.idNum = idNum
        self.cost = cost
        self.date = date
        self.depExpenses = {}
        self.reference = reference.split(".")
        self.asset = assetId

    def accumulatedDepreciation(self):
        accumDep = 0.0
        for depExp in self.depExpenses.values():
            accumDep += depExp.amount
        return accumDep
    
    def depreciate(self, prSalvAmt, depMeth, usefulLife, periodEndDate):
        numDepPrds = len(self.depExpenses)
        totalPrds = 12 * usefulLife
        if depMeth == constants.DEP_STRAIGHT:
            if NewDate.dateDiff("m", self.date, periodEndDate) < totalPrds - 1:
                depExp = (self.cost - prSalvAmt) / totalPrds
            else:
                depExp = self.cost - prSalvAmt - self.accumulatedDepreciation()
        return round(depExp, 2)

    def addInvoice(self, invoice):
        self.invoice = invoice

    def addAsset(self, asset):
        self.asset = asset

    def addDepExpense(self, depExpense):
        self.depExpenses[depExpense.idNum] = depExpense
        
class Asset:
    def __init__(self, desc, acqDate, inSvcDate, disposeDate, disposeAmount, usefulLife, salvageAmt, depMethod, partiallyDisposed, idNum):
        self.idNum = idNum
        self.description = desc
        self.acquireDate = acqDate
        self.inSvcDate = inSvcDate
        self.disposeDate = disposeDate
        self.disposeAmount = disposeAmount
        self.usefulLife = usefulLife
        self.salvageAmount = salvageAmt
        self.depMethod = depMethod
        self.partiallyDisposed = partiallyDisposed
        self.assetType = None
        self.company = None
        self.fromProject = None
        self.subAssetOf = None
        self.invoices = InvoicesDict()
        self.costs = {}
        self.history = {}
        self.subAssets = AssetsDict()
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

    def removeCost(self, cost):
        self.costs.pop(cost.idNum)

    def findCost(self, invoice):
        for cost in self.costs.values():
            if cost.invoice.idNum == invoice.idNum:
                return cost

    def addSubAsset(self, asset):
        self.subAssets[asset.idNum] = asset

    def removeSubAsset(self, asset):
        self.subAssets.pop(asset.idNum)

    def addSubAssetOf(self, asset):
        self.subAssetOf = asset

    def removeSubAssetOf(self):
        self.subAssetOf = None

    def addHistory(self, history):
        self.history[history.idNum] = history

    def findHistory(self, cost):
        for history in self.history.values():
            if history.object == cost:
                return history

    def removeHistory(self, history):
        self.history.pop(history.idNum)
        
    def cost(self):
        amount = 0.0
        for costKey in self.costs:
            amount += self.costs[costKey].cost
        return amount

    def depreciatedAmount(self):
        return 0

    def inSvc(self):
        if self.inSvcDate != "" and (self.disposeDate == "" or self.disposeDate == None):
            return True
        else:
            return False

    def disposed(self):
        if self.disposeDate == "" or self.disposeDate == None:
            return False
        else:
            return True

    def markDisposals(self, dbCursor, dbConnection):
        # Mark all subassets as fully disposed
        for subAsset in self.subAssets.values():
            subAsset.partiallyDisposed = False
            dbCursor.execute("UPDATE Assets SET PartiallyDisposed=? WHERE idNum=?",
                             (int(False), subAsset.idNum))

        parentAsset = self.subAssetOf
        while parentAsset != None:
            parentAsset.partiallyDisposed = True
            dbCursor.execute("UPDATE Assets SET PartiallyDisposed=? WHERE idNum=?",
                             (int(True), parentAsset.idNum))
            parentAsset = parentAsset.subAssetOf

        dbConnection.commit()

    def getHistoryByObject(self, object_):
        for history in self.history.values():
            if isinstance(history.object, type(object_)):
                if history.object.idNum == object_.idNum:
                    return history
                
    def depreciate(self, date):
        # We can only depreciate assets in service
        if self.inSvc() == True:
            # Get the total cost so that we know how to pro rate the salvage value
            # across cost records when depreciating.
            totalCost = 0.0
            for assetCost in self.costs.values():
                totalCost += assetCost.cost
            
            for assetCost in self.costs.values():
                proratedSalv = assetCost.cost / totalCost * self.salvageAmount
                assetCost.depreciate(proratedSalv, self.depMethod, self.usefulLife, date)
    
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
        self.parent = None
        self.children = []
        #self.parentOf = GLAccountsDict()
        self.postings = GLPostingsDetailsDict()

    def addChild(self, childId):
        self.children.append(childId)

    def removeChild(self, childId):
        self.children.pop(childId)

    def addParent(self, parentId):
        self.parent = parentId

    def addPosting(self, posting):
        self.postings[posting.idNum] = posting

    def removePosting(self, posting):
        self.postings.pop(posting.idNum)

    def balance(self):
        return 0
##        balance = 0
##        if self.placeHolder == True:
##            for childKey in self.parentOf:
##                balance += self.parentOf[childKey].balance()
##        else:
##            balance = self.postings.postingsByDRCR("DR").balance() - self.postings.postingsByDRCR("CR").balance()
##        return balance

class GLPosting:
    def __init__(self, date, description, company, idNum):
        self.idNum = idNum
        self.date = date
        self.description = description
        self.details = GLPostingsDetailsDict()
        self.company = company

    def addDetail(self, detail):
        self.details[detail.idNum] = detail

    def addCompany(self, company):
        self.company = company

class GLPostingDetail:
    def __init__(self, amount, debitCredit, glAccount, glPost, idNum):
        self.idNum = idNum
        self.amount = amount
        self.debitCredit = debitCredit
        self.glAccount = glAccount
        self.detailOf = glPost

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
        self.assetCosts = {}
        self.proposals = ProposalsDict()
        self.proposalsDetails = {}
        self.assets = AssetsDict()
        self.assetsHistory = {}
        self.assetTypes = AssetTypesDict()
        self.projects = ProjectsDict()
        self.glAccounts = GLAccountsDict()
        self.glPostings = GLPostingsDict()
        self.glPostingsDetails = {}
        self.paymentTypes = PaymentTypesDict()
