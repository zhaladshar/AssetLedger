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
