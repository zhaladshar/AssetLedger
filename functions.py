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
