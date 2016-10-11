from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
import sys
import os.path
from classes import *
from constants import *
from gui_elements import *
from gui_dialogs import *

class Window(QMainWindow):
    def __init__(self, dbName):
        super().__init__()
        self.data = CorporateStructure()
        self.mainMenu = self.menuBar()
        self.mainWidget = QWidget()

        # Import data
        self.importData(dbName)

        # Provide layout for views
        self.views = QStackedWidget()
        self.generalView = QWidget()
        self.companyOverview = CompanyView(self.data, self)
        self.proposalOverview = ProposalView(self.data, self)
        self.projectOverview = ProjectView(self.data, self)
        self.assetOverview = AssetView(self.data, self)
        self.glOverview = GLView(self.data, self.dbCursor, self)
        self.APOverview = APView(self.data, self, self.dbConnection, self.dbCursor)
        self.companyViewSelected = None
        self.detailViewSelected = None

        # Make signal-slot connections
        self.companyOverview.addNewCompany.connect(self.addNewCompanyButton)
        self.companyOverview.deleteCompany.connect(self.deleteCompanyButton)
        self.proposalOverview.updateVendorWidgetTree.connect(self.APOverview.vendorWidget.refreshVendorTree)
        self.projectOverview.addAssetToAssetView.connect(self.addAssetToAssetModule)
        self.glOverview.updateGLTree.connect(self.glOverview.refreshGL)
        self.APOverview.updateProjectTree.connect(self.projectOverview.projectWidget.refreshOpenProjectTree)
        self.APOverview.updateAssetTree.connect(self.assetOverview.assetWidget.refreshAssetTree)
        self.APOverview.updateCompanyTree.connect(self.companyOverview.companyWidget.refreshCompanyTree)
        self.APOverview.updateGLTree.connect(self.glOverview.refreshGL)

        # Build menus
        self.buildMenus()

        # Build layout
        self.buildLayout()

        self.setWindowTitle("AssetLedger")

    def importData(self, dbName):
        # Check if database exists.  If so, import; otherwise, initialize db.
        databaseExists = os.path.exists(constants.DB_NAME)
        self.dbConnection = sqlite3.connect(dbName)
        self.dbCursor = self.dbConnection.cursor()
        if databaseExists:
            self.dbCursor.execute("SELECT * FROM Companies")
            for idNum, name, shortName, active in self.dbCursor:
                self.data.companies[idNum] = Company(name, shortName, bool(active), idNum)
            
##            self.dbCursor.execute("SELECT * FROM Invoices")
##            for idNum, invoiceDateTxt, dueDateTxt in self.dbCursor:
##                invoiceDate = NewDate(invoiceDateTxt)
##                dueDate = NewDate(dueDateTxt)
##                self.data.invoices[idNum] = Invoice(invoiceDate, dueDate, idNum)

##            self.dbCursor.execute("SELECT * FROM InvoicesDetails")
##            for idNum, desc, cost in self.dbCursor:
##                self.data.invoicesDetails[idNum] = InvoiceDetail(desc, cost, idNum)
##
##            self.dbCursor.execute("SELECT * FROM InvoicesPayments")
##            for idNum, dateTxt, amtPd in self.dbCursor:
##                datePd = NewDate(dateTxt)
##                self.data.invoicesPayments[idNum] = InvoicePayment(datePd, amtPd, idNum)

            self.dbCursor.execute("SELECT * FROM Proposals")
            for idNum, propDate, status, statusReason in self.dbCursor:
                date = NewDate(propDate)
                self.data.proposals[idNum] = Proposal(date, status, statusReason, idNum)

            self.dbCursor.execute("SELECT * FROM ProposalsDetails")
            for idNum, desc, cost in self.dbCursor:
                self.data.proposalsDetails[idNum] = ProposalDetail(desc, cost, idNum)

##            self.dbCursor.execute("SELECT * FROM Projects")
##            for idNum, desc, ds, de, notes in self.dbCursor:
##                dateStart = classes.NewDate(ds)
##                if de == "" or de == None:
##                    dateEnd = ""
##                else:
##                    dateEnd = classes.NewDate(de)
##                self.data.projects[idNum] = Project(desc, dateStart, notes, idNum, dateEnd)

##            self.dbCursor.execute("SELECT * FROM Assets")
##            for idNum, desc, acqD, inSvcD, dDate, dAmt, uLife, sAmt, dMeth, pDis in self.dbCursor:
##                dateAcq = classes.NewDate(acqD)
##                if inSvcD == "" or inSvcD == None:
##                    dateInSvc = ""
##                else:
##                    dateInSvc = classes.NewDate(inSvcD)
##                if dDate == "" or dDate == None:
##                    dateDis = ""
##                else:
##                    dateDis = classes.NewDate(dDate)
##                self.data.assets[idNum] = Asset(desc, dateAcq, dateInSvc, dateDis, dAmt, uLife, sAmt, dMeth, bool(pDis), idNum)

##            self.dbCursor.execute("SELECT * FROM AssetTypes")
##            for idNum, assetType, dep in self.dbCursor:
##                self.data.assetTypes[idNum] = AssetType(assetType, dep, idNum)

##            self.dbCursor.execute("SELECT * FROM AssetCosts")
##            for idNum, cost, dateTxt in self.dbCursor:
##                if dateTxt == "" or dateTxt == None:
##                    date = ""
##                else:
##                    date = classes.NewDate(dateTxt)
##                self.data.assetCosts[idNum] = AssetCost(cost, date, idNum)
##
##            self.dbCursor.execute("SELECT * FROM AssetHistory")
##            for idNum, date, desc, dollars, posNeg in self.dbCursor:
##                self.data.assetsHistory[idNum] = AssetHistory(date, desc, dollars, posNeg, idNum)

##            self.dbCursor.execute("SELECT * FROM GLPostings")
##            for idNum, dateTxt, desc in self.dbCursor:
##                date = NewDate(dateTxt)
##                self.data.glPostings[idNum] = GLPosting(date, desc, idNum)
##
##            self.dbCursor.execute("SELECT * FROM GLPostingsDetails")
##            for idNum, amt, drCr in self.dbCursor:
##                self.data.glPostingsDetails[idNum] = GLPostingDetail(amt, drCr, idNum)

##            self.dbCursor.execute("SELECT * FROM GLAccounts")
##            for idNum, desc, pHolder, parentGL in self.dbCursor:
##                self.data.glAccounts[idNum] = GLAccount(desc, bool(pHolder), idNum)
##
##            for glNum in self.data.glAccounts.accountGroups().keys():
##                self.dbCursor.execute("SELECT idNum FROM GLAccounts WHERE ParentGL=?",
##                                      (glNum,))
##                for glAccount in self.dbCursor:
##                    self.data.glAccounts[glNum].addChild(glAccount[0])
##                    self.data.glAccounts[glAccount[0]].addParent(glNum)
                    
            self.dbCursor.execute("SELECT * FROM PaymentTypes")
            for idNum, desc in self.dbCursor:
                self.data.paymentTypes[idNum] = PaymentType(desc, idNum)
                
##            self.dbCursor.execute("SELECT * FROM Xref")
##            for each in self.dbCursor:
##                print(each)
##                eval("self.data." + each[0] + "[" + str(each[1]) + "]." + each[2] + \
##                     "(" + "self.data." + each[3] + "[" + str(each[4]) + "])")
        else:
            # Need to put in db creation routine
            self.dbCursor.execute("""CREATE TABLE AssetCosts
                                    (idNum     INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Cost      REAL,
                                     Date      TEXT,
                                     AssetId   INTEGER,
                                     Reference TEXT
                                    )""")
            
            self.dbCursor.execute("""CREATE TABLE AssetHistory
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Date        TEXT,
                                     Description TEXT,
                                     Dollars     REAL,
                                     PosNeg      TEXT,
                                     AssetId     INTEGER,
                                     Reference   TEXT
                                    )""")

            self.dbCursor.execute("""CREATE TABLE AssetTypes
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     AssetType   TEXT,
                                     Depreciable INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Assets
                                    (idNum              INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Description        TEXT,
                                     AcquireDate        TEXT,
                                     InSvcDate          TEXT,
                                     DisposeDate        TEXT,
                                     DisposeAmount      REAL,
                                     UsefulLife         REAL,
                                     SalvageAmount      REAL,
                                     DepreciationMethod TEXT,
                                     PartiallyDisposed  INTEGER,
                                     CompanyId          INTEGER,
                                     AssetTypeId        INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Companies
                                    (idNum     INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Name      TEXT NOT NULL,
                                     ShortName TEXT NOT NULL,
                                     Active    INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE GLAccounts
                                    (idNum       INTEGER,
                                     Description TEXT,
                                     Placeholder INTEGER,
                                     ParentGL    INTEGER,
                                     PRIMARY KEY(idNum)
                                    )""")

            self.dbCursor.execute("""CREATE TABLE GLPostings
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Date        TEXT,
                                     Description TEXT,
                                     CompanyId   INTEGER,
                                     Reference   TEXT
                                    )""")

            self.dbCursor.execute("""CREATE TABLE GLPostingsDetails
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     GLPostingId INTEGER,
                                     Amount      REAL,
                                     DebitCredit TEXT
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Invoices
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     InvoiceDate TEXT,
                                     DueDate     TEXT,
                                     CompanyId   INTEGER,
                                     VendorId    INTEGER,
                                     GLPostingId INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE InvoicesDetails
                                    (idNum         INTEGER PRIMARY KEY AUTOINCREMENT,
                                     InvoiceId     INTEGER,
                                     Description   TEXT,
                                     Cost          REAL,
                                     ProposalDetId INTEGER
                                    )""")
            
            self.dbCursor.execute("""CREATE TABLE InvoicesObjects
                                    (InvoiceId  INTEGER,
                                     ObjectType TEXT,
                                     ObjectId   INTEGER,
                                     PRIMARY KEY(InvoiceId)
                                    )""")
            
            self.dbCursor.execute("""CREATE TABLE InvoicesPayments
                                    (idNum      INTEGER PRIMARY KEY AUTOINCREMENT,
                                     DatePaid   TEXT,
                                     AmountPaid REAL,
                                     InvoiceId  INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE PaymentTypes
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Description TEXT
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Projects
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Description TEXT,
                                     DateStart   TEXT,
                                     DateEnd     TEXT,
                                     Notes       TEXT,
                                     CompanyId   INTEGER,
                                     GLAccount   INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Proposals
                                    (idNum        INTEGER PRIMARY KEY AUTOINCREMENT,
                                     ProposalDate TEXT,
                                     Status       TEXT,
                                     StatusReason TEXT
                                    )""")

            self.dbCursor.execute("""CREATE TABLE ProposalsDetails
                                    (idNum       INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Description TEXT,
                                     Cost        REAL
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Vendors
                                    (idNum     INTEGER PRIMARY KEY AUTOINCREMENT,
                                     Name      TEXT,
                                     Address   TEXT,
                                     City      TEXT,
                                     State     TEXT,
                                     ZIP       TEXT,
                                     Phone     TEXT,
                                     GLAccount INTEGER
                                    )""")

            self.dbCursor.execute("""CREATE TABLE Xref
                                    (ObjectToAddLinkTo   TEXT,
                                     ObjectIdToAddLinkTo INTEGER,
                                     Method              TEXT,
                                     ObjectBeingLinked   TEXT,
                                     ObjectIdBeingLinked INTEGER
                                    )""")

            self.dbConnection.commit()

    def newFile(self):
        pass

    def openFile(self):
        pass

    def close(self):
        self.dbConnection = None
        self.dbCursor = None

        sys.exit()

    def buildMenus(self):
        self.statusBar()

        newAction = QAction("New...", self)
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("Create a new family of companies")
        newAction.triggered.connect(self.newFile)

        openAction = QAction("Open...", self)
        openAction.setShortcut("Ctrl+O")
        openAction.setStatusTip("Open an existing family of companies")
        openAction.triggered.connect(self.openFile)

        quitAction = QAction("Quit", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Close the application")
        quitAction.triggered.connect(self.close)

        self.fileMenu = self.mainMenu.addMenu("File")
        self.fileMenu.addAction(newAction)
        self.fileMenu.addAction(openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(quitAction)

        self.createMenu = self.mainMenu.addMenu("Create")
        for option in SPLASH_OPTIONS:
            action = QAction(option[2], self)
            action.setStatusTip(option[3])
            action.triggered.connect(eval(option[1]))
            self.createMenu.addAction(action)

    def buildLayout(self):
        # The mainLayout will be a horizontal layout that will hold a left
        # vertical layout and a right vertical layout
        mainLayout = QHBoxLayout()
        mainLayout.setSpacing(0)

        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()

        # Build the left vertical layout
        lbl = QLabel("")
        lbl.setFixedSize(100, 100)
        lbl.setStyleSheet("QLabel { background-color: black }")

        self.companyLayout = ButtonToggleBox("Vertical")
        self.companyLayout.addButtons(self.data.companies.dictToList())
        self.companyLayout.setLayout(self.companyLayout.layout)
        self.companyLayout.selectionChanged.connect(self.changeCompanySelection)

        leftLayout.addWidget(lbl)
        leftLayout.addWidget(self.companyLayout)

        # Build the right vertical layout
        viewsLayout = ButtonToggleBox("Horizontal")
        viewsLayout.addButtons(VIEWS_LIST)
        viewsLayout.setLayout(viewsLayout.layout)
        viewsLayout.selectionChanged.connect(self.changeDetailViewSelected)

        # Build the main overview widget as the first element of the stacked
        # widget
        mainOverviewLayout = QGridLayout()
        mainOverview = QVBoxLayout()

        for option in SPLASH_OPTIONS:
            lbl = ClickableLabel(option[0])
            lbl.setStyleSheet("QLabel { font-size: 20px }")
            lbl.released.connect(eval(option[1]))
            mainOverview.addWidget(lbl)

        mainOverviewLayout.addLayout(mainOverview, 1, 1)
        mainOverviewLayout.setColumnStretch(0, 1)
        mainOverviewLayout.setColumnStretch(2, 1)
        mainOverviewLayout.setRowStretch(0, 1)
        mainOverviewLayout.setRowStretch(2, 1)

        self.generalView.setLayout(mainOverviewLayout)
        self.views.addWidget(self.generalView)

        # Build the company overview widget
        self.views.addWidget(self.companyOverview)

        # Build the proposal overview widget
        self.views.addWidget(self.proposalOverview)

        # Build the project overview widget
        self.views.addWidget(self.projectOverview)

        # Build the asset overview widget
        self.views.addWidget(self.assetOverview)

        # Build the GL overview widget
        self.views.addWidget(self.glOverview)

        # Build the A/P overview widget
        self.views.addWidget(self.APOverview)

        # Build the ledger overview widget

        rightLayout.addWidget(viewsLayout)
        rightLayout.addWidget(self.views)

        # Piece everything together
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)

        self.mainWidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainWidget)

    def addNewCompanyButton(self, shortName):
        newButton = [shortName]
        self.companyLayout.addButtons(newButton)

    def deleteCompanyButton(self, shortName):
        button = [shortName]
        self.companyLayout.deleteButtons(button)

    def addAssetToAssetModule(self, asset):
        if asset.subAssetOf:
            parentItem = self.assetOverview.assetWidget.getParentItem(asset.idNum)
            assetItem = AssetTreeWidgetItem(asset, parentItem)
            parentItem.addChild(assetItem)
        else:
            assetItem = AssetTreeWidgetItem(asset, self.assetOverview.assetWidget.currentAssetsTreeWidget)
            self.assetOverview.assetWidget.currentAssetsTreeWidget.addTopLevelItem(assetItem)
        
        self.assetOverview.assetWidget.updateAssetsCount()

    def changeCompanySelection(self, companyChanged):
        if self.companyViewSelected == companyChanged:
            self.companyViewSelected = None
        else:
            self.companyViewSelected = companyChanged
        self.updateViews()

    def changeDetailViewSelected(self, viewChanged):
        if self.detailViewSelected == viewChanged:
            self.detailViewSelected = None
        else:
            self.detailViewSelected = viewChanged
        self.updateViews()

    def updateViews(self):
        if self.companyViewSelected:
            if self.detailViewSelected:
                if self.detailViewSelected == "Companies":
                    self.views.setCurrentIndex(COMPANY_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Proposals":
                    self.views.setCurrentIndex(PROPOSAL_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Projects":
                    self.views.setCurrentIndex(PROJECT_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Assets":
                    self.views.setCurrentIndex(ASSET_OVERVIEW_INDEX)
                elif self.detailViewSelected == "G/L":
                    self.views.setCurrentIndex(GL_OVERVIEW_INDEX)
                elif self.detailViewSelected == "A/P":
                    self.views.setCurrentIndex(AP_OVERVIEW_INDEX)
            else:
                self.views.setCurrentIndex(MAIN_OVERVIEW_INDEX)
        else:
            if self.detailViewSelected:
                if self.detailViewSelected == "Companies":
                    self.views.setCurrentIndex(COMPANY_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Proposals":
                    self.views.setCurrentIndex(PROPOSAL_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Projects":
                    self.views.setCurrentIndex(PROJECT_OVERVIEW_INDEX)
                elif self.detailViewSelected == "Assets":
                    self.views.setCurrentIndex(ASSET_OVERVIEW_INDEX)
                elif self.detailViewSelected == "G/L":
                    self.views.setCurrentIndex(GL_OVERVIEW_INDEX)
                elif self.detailViewSelected == "A/P":
                    self.views.setCurrentIndex(AP_OVERVIEW_INDEX)
            else:
                self.views.setCurrentIndex(MAIN_OVERVIEW_INDEX)

    def newCompany(self):
        print("New company")

    def newProject(self):
        print("New project")

    def newProposal(self):
        print("New proposal")

    def newAsset(self):
        print("New asset")

    def newVendor(self):
        print("New vendor")

    def newInvoice(self):
        print("New invoice")


if __name__ == "__main__":
        app = QApplication(sys.argv)
        form = Window(constants.DB_NAME)
        form.show()
        app.exec_()
