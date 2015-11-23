from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
import sys
from classes import *
from gui_elements import *
from gui_dialogs import *

VIEWS_LIST = ["Companies", "Proposals", "Projects", "Assets", "G/L", "A/P"]
SPLASH_OPTIONS = [("+New Company", "self.newCompany", "Company...", "Create new company"),
                  ("+New Project", "self.newProject", "Project...", "Create new project"),
                  ("+New Proposal", "self.newProposal", "Proposal...", "Create new proposal"),
                  ("+New Asset", "self.newAsset", "Asset...", "Create new asset"),
                  ("+New Vendor", "self.newVendor", "Vendor...", "Create new vendor"),
                  ("+New Invoice", "self.newInvoice", "Invoice...", "Create new invoice")]
MAIN_OVERVIEW_INDEX = 0
COMPANY_OVERVIEW_INDEX = 1
PROJECT_OVERVIEW_INDEX = 2
VENDOR_OVERVIEW_INDEX = 3

class Window(QMainWindow):
    def __init__(self, dbName):
        super().__init__()
        self.data = CorporateStructure()
        self.dbConnection = sqlite3.connect(dbName)
        self.dbCursor = self.dbConnection.cursor()
        self.mainMenu = self.menuBar()
        self.mainWidget = QWidget()

        # Import data
        self.importData()

        # Provide layout for views
        self.views = QStackedWidget()
        self.generalView = QWidget()
        self.companyOverview = QWidget()
        self.projectOverview = QWidget()
        self.APOverview = APView(self.data, self)
        self.companyViewSelected = None
        self.detailViewSelected = None

        # Build menus
        self.buildMenus()

        # Build layout
        self.buildLayout()

    def importData(self):
        self.dbCursor.execute("SELECT * FROM Companies")
        for each in self.dbCursor:
            self.data.companies[each[0]] = Company(each[1], each[2], each[0])

        self.dbCursor.execute("SELECT * FROM Vendors")
        for each in self.dbCursor:
            self.data.vendors[each[0]] = Vendor(each[1], each[2], each[3], each[4], each[5], each[6], each[0])

        self.dbCursor.execute("SELECT * FROM Invoices")
        for each in self.dbCursor:
            self.data.invoices[each[0]] = Invoice(each[1], each[2], each[3], each[0])

        self.dbCursor.execute("SELECT * FROM Xref")
        for each in self.dbCursor:
            eval("self.data." + each[0] + "[" + str(each[1]) + "]." + each[2] + \
                 "(" + "self.data." + each[3] + "[" + str(each[4]) + "])")

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

        companyLayout = ButtonToggleBox("Vertical")
        companyLayout.addButtons(Company.dictToList())
        companyLayout.setLayout(companyLayout.layout)
        companyLayout.selectionChanged.connect(self.changeCompanySelection)

        leftLayout.addWidget(lbl)
        leftLayout.addWidget(companyLayout)

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
        companyOverviewLayout = QVBoxLayout()
        self.companyOverviewProjects = CollapsableFrame("Projects")
        self.companyOverviewProjects.addEntry("Ongoing: # / #")
        self.companyOverviewProjects.addEntry("CIP: $#")
        self.companyOverviewProjects.addEntry("Budget vs. Actual (excl. ongoing): #â†‘")
        self.companyOverviewProjects.addEntry("Longest ongoing project: # months")
        self.companyOverviewProjects.addEntry("Unpaid invoices: # / $#")
        companyOverviewLayout.addWidget(self.companyOverviewProjects)

        self.companyOverviewAssets = CollapsableFrame("Assets")
        self.companyOverviewAssets.addEntry("Owned: # / #")
        self.companyOverviewAssets.addEntry("Cost: $#")
        self.companyOverviewAssets.addEntry("Accum. dep.: $#")
        self.companyOverviewAssets.addEntry("Avg. life: #")
        self.companyOverviewAssets.addEntry("Unpaid invoices: # / $#")
        companyOverviewLayout.addWidget(self.companyOverviewAssets)

        self.companyOverviewGL = CollapsableFrame("G/L")
        self.companyOverviewGL.addEntry("CIP: $#")
        self.companyOverviewGL.addEntry("Assets: # / $#")
        self.companyOverviewGL.addEntry("YTD deprectiation: $#")
        companyOverviewLayout.addWidget(self.companyOverviewGL)

        self.companyOverviewVendors = CollapsableFrame("Vendors")
        self.companyOverviewVendors.addEntry("Number: #")
        self.companyOverviewVendors.addEntry("Unpaid: # / $#")
        self.companyOverviewVendors.addEntry("Past due: # / $#")
        companyOverviewLayout.addWidget(self.companyOverviewVendors)
        companyOverviewLayout.addStretch(1)

        self.companyOverview.setLayout(companyOverviewLayout)
        self.views.addWidget(self.companyOverview)

        # Build the project overview widget
        projectOverviewLayout = QVBoxLayout()
        self.projectOverviewProposals = CollapsableFrame("Proposals")
        self.projectOverviewProposals.addEntry("Active bids: # / #")
        self.projectOverviewProposals.addEntry("Projects accepting bids: #")
        projectOverviewLayout.addWidget(self.projectOverviewProposals)

        self.projectOverviewBudgets = CollapsableFrame("Budgets")
        self.projectOverviewBudgets.addEntry("Active budgeted projects: # / #")
        self.projectOverviewBudgets.addEntry("Total budgeted projects: # / #")
        self.projectOverviewBudgets.addEntry("Budget vs. actual (excl. ongoing): #â†‘")
        projectOverviewLayout.addWidget(self.projectOverviewBudgets)

        self.projectOverviewProjects = CollapsableFrame("Projects")
        self.projectOverviewProjects.addEntry("Active projects: # / #")
        self.projectOverviewProjects.addEntry("CIP: $#")
        self.projectOverviewProjects.addEntry("Avg. length of active projects: # mo")
        self.projectOverviewProjects.addEntry("Avg. length of all projects: # mo")
        projectOverviewLayout.addWidget(self.projectOverviewProjects)

        self.projectOverviewAP = CollapsableFrame("A/P")
        self.projectOverviewAP.addEntry("Active vendors: # / #")
        self.projectOverviewAP.addEntry("Open invoices: # ($#)")
        self.projectOverviewAP.addEntry("Overdue invoices: # ($#)")
        projectOverviewLayout.addWidget(self.projectOverviewAP)
        projectOverviewLayout.addStretch(1)

        self.projectOverview.setLayout(projectOverviewLayout)
        self.views.addWidget(self.projectOverview)

        # Build the vendor overview widget
        self.views.addWidget(self.APOverview)

        # Build the asset overview widget
        # Build the ledger overview widget
        # Build the A/P overview widget

        rightLayout.addWidget(viewsLayout)
        rightLayout.addWidget(self.views)

        # Piece everything together
        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)

        self.mainWidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainWidget)

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
                self.views.setCurrentIndex(VENDOR_OVERVIEW_INDEX)
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
        form = Window("data.db")
        form.show()
        app.exec_()
