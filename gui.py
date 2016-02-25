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
        self.glOverview = GLView(self.data, self)
        self.APOverview = APView(self.data, self)
        self.companyViewSelected = None
        self.detailViewSelected = None

        # Make signal-slot connections
        self.companyOverview.addNewCompany.connect(self.addNewCompanyButton)
        self.companyOverview.deleteCompany.connect(self.deleteCompanyButton)
        self.proposalOverview.updateVendorWidgetTree.connect(self.APOverview.vendorWidget.refreshVendorTree)
        self.projectOverview.addAssetToAssetView.connect(self.addAssetToAssetModule)
        self.APOverview.updateProjectTree.connect(self.projectOverview.projectWidget.refreshOpenProjectTree)
        self.APOverview.updateAssetTree.connect(self.assetOverview.assetWidget.refreshAssetTree)

        # Build menus
        self.buildMenus()

        # Build layout
        self.buildLayout()

    def importData(self, dbName):
        # Check if database exists.  If so, import; otherwise, initialize db.
        if os.path.exists(constants.DB_NAME):
            self.dbConnection = sqlite3.connect(dbName)
            self.dbCursor = self.dbConnection.cursor()
            
            self.dbCursor.execute("SELECT * FROM Companies")
            for each in self.dbCursor:
                if each[3] == "Y":
                    active = True
                else:
                    active = False
                self.data.companies[each[0]] = Company(each[1], each[2], active, each[0])

            self.dbCursor.execute("SELECT * FROM Vendors")
            for each in self.dbCursor:
                self.data.vendors[each[0]] = Vendor(each[1], each[2], each[3], each[4], each[5], each[6], each[0])

            self.dbCursor.execute("SELECT * FROM Invoices")
            for each in self.dbCursor:
                self.data.invoices[each[0]] = Invoice(each[1], each[2], each[0])

            self.dbCursor.execute("SELECT * FROM InvoicesDetails")
            for each in self.dbCursor:
                self.data.invoicesDetails[each[0]] = InvoiceDetail(each[1], each[2], each[0])

            self.dbCursor.execute("SELECT * FROM InvoicesPayments")
            for each in self.dbCursor:
                self.data.invoicesPayments[each[0]] = InvoicePayment(each[1], each[2], each[0])

            self.dbCursor.execute("SELECT * FROM Proposals")
            for each in self.dbCursor:
                self.data.proposals[each[0]] = Proposal(each[1], each[2], each[3], each[0])

            self.dbCursor.execute("SELECT * FROM ProposalsDetails")
            for each in self.dbCursor:
                self.data.proposalsDetails[each[0]] = ProposalDetail(each[1], each[2], each[0])

            self.dbCursor.execute("SELECT * FROM Projects")
            for each in self.dbCursor:
                self.data.projects[each[0]] = Project(each[1], each[2], each[3], each[0], each[3])

            self.dbCursor.execute("SELECT * FROM Assets")
            for each in self.dbCursor:
                self.data.assets[each[0]] = Asset(each[1], each[2], each[3], each[4], each[5], each[6], each[7], each[8], each[0])

            self.dbCursor.execute("SELECT * FROM AssetTypes")
            for each in self.dbCursor:
                self.data.assetTypes[each[0]] = AssetType(each[1], each[2], each[0])

            self.dbCursor.execute("SELECT * FROM Costs")
            for each in self.dbCursor:
                self.data.costs[each[0]] = Cost(each[2], each[1], each[0])

            self.dbCursor.execute("SELECT * FROM GLPostings")
            for each in self.dbCursor:
                self.data.costs[each[0]] = GLPosting(each[1], each[2], each[3], each[4], each[5], each[0])

            self.dbCursor.execute("SELECT * FROM GLAccounts")
            for each in self.dbCursor:
                if each[2] == 0:
                    placeHolder = False
                else:
                    placeHolder = True
                self.data.glAccounts[each[0]] = GLAccount(each[1], placeHolder, each[0])
                
            self.dbCursor.execute("SELECT * FROM Xref")
            for each in self.dbCursor:
                eval("self.data." + each[0] + "[" + str(each[1]) + "]." + each[2] + \
                     "(" + "self.data." + each[3] + "[" + str(each[4]) + "])")
        else:
            # Need to put in db creation routine
            pass

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

    def addAssetToAssetModule(self, assetId):
        assetItem = AssetTreeWidgetItem(self.data.assets[assetId], self.assetOverview.assetWidget.currentAssetsTreeWidget)
        self.assetOverview.assetWidget.currentAssetsTreeWidget.addItem(assetItem)
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
                print("YEY")
            else:
                self.views.setCurrentIndex(COMPANY_OVERVIEW_INDEX)
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
