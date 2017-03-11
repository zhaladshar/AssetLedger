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
PROJECT_STATUSES = [OPN_PROJECT_STATUS, ABD_PROJECT_STATUS, CMP_PROJECT_STATUS]
DEP_STRAIGHT = "Straight-line"
DEP_PRODUCTION = "Units of production"
DEP_DEPLETION = "Depletion"
DEP_DIGITS = "Years' digits"
DEP_METHODS = [DEP_STRAIGHT, DEP_PRODUCTION, DEP_DEPLETION, DEP_DIGITS]
DEBIT = "DR"
CREDIT = "CR"
POSITIVE = "Positive"
NEGATIVE = "Negative"
DATE_FORMAT = "%m/%d/%Y"
ID_DESC = "%4d - %s"
INV_OPEN_STATUS = "Open"
INV_PAID_STATUS = "Paid"

# Strings
GL_POST_PYMT_DESC = "Post payment for invoice %d from vendor %d on %s"
GL_POST_INV_DESC = "Post invoice %d from vendor %d on %s"
GL_POST_PROJ_COMP = "Completion of project %d"
GL_POST_PROJ_ABD = "Abandoned project %d. Reason: %s"
ASSET_HIST_INV = "Invoice %d posted"
ASSET_HIST_PROJ_COMP = "Project %d completed"
ASSET_HIST_DEP = "Depreciation"
ASSET_HIST_IMP = "Impaired"
ASSET_HIST_DISP = "Disposed"

#############################
##
## Tree Widget Constants
##
#############################

# Tree Widget Constants
TREE_WIDGET_MIN_WIDTH = 500
TREE_WIDGET_MAX_HEIGHT = 200

# Tree Widget Header
VENDOR_HDR_LIST = ["ID", "Name", "Bids (O / T)", "Invoices (O / T)", "Balance"]
VENDOR_HDR_WDTH = [ .08,   .396,            .14,                .18,        .2]
INVOICE_HDR_LIST = ["ID", "Vendor", "Date", "Due", "Amount", "Paid", "Balance"]
INVOICE_HDR_WDTH = [ .08,     .396,     .1,    .1,     .108,   .108,      .108]
INVOICE_PYMT_HDR_LIST = ["ID", "Date Paid", "Amount"]
INVOICE_PYMT_HDR_WDTH = [ .08,          .5,      .42]
COMPANY_HDR_LIST = ["ID", "Name", "Short Name", "Assets", "CIP"]
COMPANY_HDR_WDTH = [ .08,     .5,           .2,      .11,   .11]
PROPOSAL_HDR_LIST = ["ID", "Vendor", "Date", "Asset/Project", "Amount"]
PROPOSAL_HDR_WDTH = [ .08,      .25,     .1,             .46,      .11]
PROJECT_HDR_LIST = ["ID", "Description", "Started", "Ended", "Duration", "CIP"]
PROJECT_HDR_WDTH = [ .08,           .45,        .1,      .1,        .15,   .12]
ASSET_HDR_LIST = ["ID", "Description", "Cost", "Deprec.", "Bought", "In Use"]
ASSET_HDR_WDTH = [ .08,           .47,    .11,       .11,      .11,      .11]
GL_HDR_LIST = ["Acct #", "Description", "Balance"]
GL_HDR_WDTH = [      .2,            .6,        .2]
GL_POST_HDR_LIST = ["Date", "Description", "Balance"]
GL_POST_HDR_WDTH = [    .1,            .7,        .2]
ASSET_HIST_HDR_LIST = ["Date", "Description", "Dollars"]
ASSET_HIST_HDR_WDTH = [    .1,            .8,        .1]
DEP_ASSET_HDR_LIST = ["Id", "Description", "Current"]
DEP_ASSET_HDR_WDTH = [  .1,            .8,        .1]

#############################
##
## Database Constants
##
#############################

ASSET_HISTORY_COLUMNS = ("Date", "Description", "Dollars", "AssetId", "Reference")
ASSET_COSTS_COLUMNS = ("Cost", "Date", "AssetId", "Reference")
GL_POSTING_COLUMNS = ("Date", "Description", "CompanyId", "Reference")
GL_POSTING_DETAIL_COLUMNS = ("GLPostingId", "GLAccount", "Amount")
