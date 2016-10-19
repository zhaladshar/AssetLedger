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

    return invoiceAmt - paymentAmt
