import constants

def CalculateCIP(dbCur, projectId):
    dbCur.execute("""SELECT Sum(Cost) FROM InvoicesDetails
                     JOIN InvoicesObjects
                     ON InvoicesObjects.InvoiceId = InvoicesDetails.InvoiceId
                     WHERE ObjectType=? AND ObjectId=?""",
                  ("projects", projectId))
    cip = dbCur.fetchone()[0]
    if not cip:
        return 0.0
    else:
        return cip

def CalculateInvoiceBalance(dbCur, invoiceId):
    invoiceAmt = 0.0
    paymentAmt = 0.0

    dbCur.execute("""SELECT Cost FROM InvoicesDetails
                     WHERE InvoiceId=?""",
                  (invoiceId,))
    for cost in dbCur:
        invoiceAmt += cost[0]

    dbCur.execute("""SELECT AmountPaid FROM InvoicesPayments
                     WHERE InvoiceId=?""", (invoiceId,))
    for payment in dbCur:
        paymentAmt += payment[0]

    return round(invoiceAmt - paymentAmt, 2)

def CalculateAssetCost(dbCur, assetId):
    dbCur.execute("""SELECT Sum(Cost) FROM AssetCosts
                     WHERE AssetId=?""",
                  (assetId,))
    cost = dbCur.fetchone()[0]

    if not cost:
        return 0.0
    else:
        return cost

def AssetIsDisposed(dbCur, assetId):
    dbCur.execute("SELECT DisposeDate FROM Assets WHERE idNum=?", (assetId,))
    disposed = dbCur.fetchone()[0]
    if disposed:
        return True
    else:
        return False

def MarkPartialDisposals(dbCur, assetId):
    if assetId:
        dbCur.execute("UPDATE Assets SET PartiallyDisposed=1 WHERE idNum=?",
                      (assetId,))
        
        dbCur.execute("""SELECT ParentAssetId FROM Assets
                         WHERE idNum=?""", (assetId,))
        parentAssetId = dbCur.fetchone()[0]
        MarkPartialDisposals(dbCur, parentAssetId)

def CalculateProposalCost(dbCur, proposalId):
    dbCur.execute("SELECT Sum(Cost) FROM ProposalsDetails WHERE ProposalId=?",
                  (proposalId,))
    cost = dbCur.fetchone()[0]
    if cost:
        return cost
    else:
        return 0.0

def GetListOfAssets(dbCur, company=None):
    assets = []
    sql = "SELECT idNum, Description FROM Assets"
    if company:
        sql += " WHERE CompanyId = %d" % (company,)
    dbCur.execute(sql)
    for idNum, asset in dbCur:
        assets.append(constants.ID_DESC % (idNum, asset))
    return assets

def GetListOfAssetTypes(dbCur):
    assetTypes = []
    dbCur.execute("SELECT idNum, AssetType FROM AssetTypes")
    for idNum, assetType in dbCur:
        assetTypes.append(constants.ID_DESC % (idNum, assetType))
    return assetTypes

def GetListOfGLAccounts(dbCur):
    glAccounts = []
    dbCur.execute("""SELECT idNum, Description FROM GLAccounts
                     WHERE Placeholder=0""")
    for idNum, glAccount in dbCur:
        glAccounts.append(constants.ID_DESC % (idNum, glAccount))
    return glAccounts

def GetListOfCompanies(dbCur):
    companies = []
    dbCur.execute("SELECT idNum, ShortName FROM Companies")
    for idNum, company in dbCur:
        companies.append(constants.ID_DESC % (idNum, company))
    return companies

def GetListOfProjects(dbCur, company=None):
    projects = []
    sql = "SELECT idNum, Description FROM Projects"
    if company:
        sql += " WHERE CompanyId = %d" % (company,)
    dbCur.execute(sql)
    for idNum, project in dbCur:
        projects.append(constants.ID_DESC % (idNum, project))
    return projects

def NextIdNum(dbCur, name):
    dbCur.execute("""SELECT seq FROM sqlite_sequence
                          WHERE name = ?""", (name,))
    largestId = dbCur.fetchone()
    if largestId:
        return int(largestId[0]) + 1
    else:
        return 1

def InsertIntoDatabase(dbCur, tblName, columns, values):
    if columns:
        columnsStr = " " + str(columns).replace("'", "")
    else:
        columnsStr = ""
        
    valuesStr = "("
    for n in range(len(values)):
        valuesStr += "?, "
    valuesStr = valuesStr[:-2] + ")"
    
    sql = "INSERT INTO %s%s VALUES %s" % (tblName, columnsStr, valuesStr)
    dbCur.execute(sql, values)
        
def PostToGL(dbCur, companyId, date, description, reference, listOfDetails):
    glPostingIdNum = NextIdNum(dbCur, "GLPostings")
    glPostingDetailIdNum = NextIdNum(dbCur, "GLPostingsDetails")
    
    columns = constants.GL_POSTING_COLUMNS
    values = (date, description, companyId, reference)
    InsertIntoDatabase(dbCur, "GLPostings", columns, values)
    
    for amount, glAcct, type_, type_Id in listOfDetails:
        columns = ("GLPostingId", "GLAccount", "Amount")
        values = (glPostingIdNum, glAcct, amount)
        InsertIntoDatabase(dbCur, "GLPostingsDetails", columns, values)
        
        if type_ and type_Id:
            columns = ("GLPostingDetailId", "ObjectType", "ObjectId")
            values = (glPostingDetailIdNum, type_, type_Id)
            InsertIntoDatabase(dbCur,
                               "GLPostingsDetailsObjects",
                               columns,
                               values)
            
        glPostingDetailIdNum += 1
