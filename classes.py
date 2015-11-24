class InvoicesDict(dict):
    def __init__(self):
        super().__init__()

    def openInvoices(self):
        tempDict = {}
        for invoiceKey in self.keys():
            if self[invoiceKey].balance() != 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

    def paidInvoices(self):
        tempDict = {}
        for invoiceKey in self.keys():
            if self[invoiceKey].balance() == 0:
                tempDict[invoiceKey] = self[invoiceKey]
        return tempDict

class Payment:
    paymentList = {}

    def __init__(self, invoice, datePaid, amountPaid, idNum=None):
        if self.idNum == None:
            self.idNum = len(paymentList) + 1
        else:
            self.idNum = idNum
        self.invoice = invoice
        self.datePaid = datePaid
        self.amountPaid = amountPaid

class Invoice:
    invoiceList = {}

    def __init__(self, date, dueDate, amount, idNum=None):
        if idNum == None:
            self.idNum = len(invoiceList) + 1
        else:
            self.idNum = idNum
        self.invoiceDate = date
        self.dueDate = dueDate
        self.amount = amount
        self.vendor = None
        self.payments = []

    def balance(self):
        return self.amount - self.paid()

    def paid(self):
        amtPaid = 0
        for payment in self.payments:
            amtPaid += payment.amountPaid
        return amtPaid

    def addVendor(self, vendor):
        self.vendor = vendor

class Vendor:
    vendorList = {}

    def __init__(self, name, address, city, state, zipcode, phone, idNum):
        self.idNum = idNum
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.zip = zipcode
        self.phone = phone
        self.proposals = {}
        self.invoices = {}

        Vendor.vendorList[idNum] = self

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

class Company:
    companyList = {}

    def __init__(self, name, shortName, idNum=None):
        if idNum == None:
            self.idNum = len(companyList) + 1
        else:
            self.idNum = idNum
        self.name = name
        self.shortName = shortName
        self.proposals = {}
        self.projects = {}
        self.assets = {}

        Company.companyList[self.idNum] = self

    @classmethod
    def dictToList(cls):
        newList = []
        for each in cls.companyList.values():
            newList.append(each.shortName)

        return newList

class CorporateStructure:
    def __init__(self):
        self.companies = {}
        self.vendors = {}
        self.invoices = InvoicesDict()
        self.proposals = {}
        self.assets = {}
        self.projects = {}
