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

    def addDetailOf(self, proposal):
        self.detailOf = proposal

class Proposal:
    def __init__(self, date, status, idNum):
        self.idNum = idNum
        self.date = date
        self.status = status
        self.vendor = None
        self.proposalFor = None
        self.details = {}

    def addVendor(self, vendor):
        self.vendor = vendor

    def addProject(self, project):
        self.proposalFor = ("Project", project)

    def addAsset(self, asset):
        self.proposalFor = ("Asset", asset)

    def addDetail(self, detail):
        self.details[detail.idNum] = detail

    def totalCost(self):
        cost = 0
        for detailKey in self.details.keys():
            cost += self.details[detailKey].cost
        return cost

class Project:
    def __init__(self, desc, dateStart, idNum, dateEnd=None):
        self.idNum = idNum
        self.description = desc
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.invoices = {}
        self.company = None
        self.becameAsset = None
        self.fromProposal = None

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def addAsset(self, asset):
        self.becameAsset = asset

    def appProposal(self, proposal):
        self.fromProposal = proposal

    def addCompany(self, company):
        self.company = company

    def status(self):
        if self.dateEnd == None or self.dateEnd == "":
            return "Open"
        else:
            return "Closed"

    def calculateCIP(self):
        CIP = 0
        for invoiceKey in self.invoices:
            CIP += self.invoices[invoiceKey].amount
        return CIP

class Payment:
    def __init__(self, datePaid, amountPaid, idNum):
        self.idNum = idNum
        self.invoicePaid = None
        self.datePaid = datePaid
        self.amountPaid = amountPaid

    def addInvoice(self, invoice):
        self.invoicePaid = invoice

class Invoice:
    def __init__(self, date, dueDate, amount, idNum):
        self.idNum = idNum
        self.invoiceDate = date
        self.dueDate = dueDate
        self.amount = amount
        self.vendor = None
        self.company = None
        self.assetProj = None
        self.payments = []

    def balance(self):
        return self.amount - self.paid()

    def paid(self):
        amtPaid = 0.0
        for payment in self.payments:
            amtPaid += payment.amountPaid
        return amtPaid

    def addVendor(self, vendor):
        self.vendor = vendor

    def addCompany(self, company):
        self.company = company

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
        amountPaid = 0
        amountInvoiced = 0
        for invoiceKey in self.invoices.keys():
            amountPaid += self.invoices[invoiceKey].paid()
            amountInvoiced += self.invoices[invoiceKey].balance()
        return amountInvoiced - amountPaid

    def addInvoice(self, invoice):
        self.invoices[invoice.idNum] = invoice

    def removeInvoice(self, invoice):
        self.invoices.pop(invoice.idNum)

    def openInvoiceCount(self):
        count = 0
        for invoiceKey in self.invoices.keys():
            if self.invoices[invoiceKey].balance != 0:
                count += 1
        return count

    def addProposal(self, proposal):
        self.proposals[proposal.idNum] = proposal

    def removeProposal(self, proposal):
        self.proposals.pop(proposal.idNum)

class Company:
    def __init__(self, name, shortName, idNum):
        self.idNum = idNum
        self.name = name
        self.shortName = shortName
        self.proposals = {}
        self.projects = {}
        self.assets = {}
        self.invoices = {}

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

class CorporateStructure:
    def __init__(self):
        self.companies = CompanyDict()
        self.vendors = {}
        self.invoices = InvoicesDict()
        self.proposals = ProposalsDict()
        self.proposalsDetails = {}
        self.assets = {}
        self.projects = ProjectsDict()
