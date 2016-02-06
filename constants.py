DB_NAME = "data.db"
VIEWS_LIST = ["Companies", "Proposals", "Projects", "Assets", "G/L", "A/P"]
SPLASH_OPTIONS = [("+New Company", "self.newCompany", "Company...", "Create new company"),
                  ("+New Project", "self.newProject", "Project...", "Create new project"),
                  ("+New Proposal", "self.newProposal", "Proposal...", "Create new proposal"),
                  ("+New Asset", "self.newAsset", "Asset...", "Create new asset"),
                  ("+New Vendor", "self.newVendor", "Vendor...", "Create new vendor"),
                  ("+New Invoice", "self.newInvoice", "Invoice...", "Create new invoice")]
MAIN_OVERVIEW_INDEX = 0
COMPANY_OVERVIEW_INDEX = 1
PROPOSAL_OVERVIEW_INDEX = 2
PROJECT_OVERVIEW_INDEX = 3
ASSET_OVERVIEW_INDEX = 4
GL_OVERVIEW_INDEX = 5
AP_OVERVIEW_INDEX = 6
REJ_PROPOSAL_STATUS = "Rejected"
ACC_PROPOSAL_STATUS = "Accepted"
OPN_PROPOSAL_STATUS = "Open"
PROPOSAL_STATUSES = [OPN_PROPOSAL_STATUS, REJ_PROPOSAL_STATUS, ACC_PROPOSAL_STATUS]
OPN_PROJECT_STATUS = "Ongoing"
ABD_PROJECT_STATUS = "Abandoned"
CMP_PROJECT_STATUS = "Completed"
