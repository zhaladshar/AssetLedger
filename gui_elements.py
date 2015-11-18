from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ClickableLabel(QLabel):
    released = pyqtSignal()
    
    def __init__(self, text):
        super().__init__(text)

    def mouseReleaseEvent(self, event):
        self.released.emit()

class CollapsableFrame(QFrame):
    def __init__(self, headerText):
        super().__init__()
        self.entries = []
        self.setStyleSheet("QFrame { border: 1px solid red }")
        self.setContentsMargins(-8,-8,-8,-8)

        headerLayout = QHBoxLayout()
        headerLayout.setSpacing(0)
        self.bodyLayout = QVBoxLayout()
        self.body = QWidget()
        
        mainLayout = QVBoxLayout()

        headerWidget = QWidget()
        headerWidget.setStyleSheet("QWidget { background-color: red }")
        headerLbl = QLabel(headerText)
        headerLbl.setMaximumHeight(15)
        headerLbl.setMargin(0)
        self.caretLbl = ClickableLabel("▲")
        self.caretLbl.setMaximumWidth(15)
        self.caretLbl.setStyleSheet("QLabel:hover { color: yellow }")
        self.caretLbl.released.connect(lambda: self.showHideBody())
        headerLayout.addWidget(headerLbl)
        headerLayout.addStretch(0)
        headerLayout.addWidget(self.caretLbl)
        headerWidget.setLayout(headerLayout)

        self.body.setLayout(self.bodyLayout)
        
        mainLayout.addWidget(headerWidget)
        mainLayout.addWidget(self.body)

        self.setLayout(mainLayout)

    def addEntry(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("QLabel { border: none }")

        self.entries.append(lbl)
        self.bodyLayout.addWidget(lbl)

    def changeEntry(self, index, newText):
        self.entries[index].setText(newText)

    def showHideBody(self):
        if self.body.isHidden() == True:
            self.body.show()
            self.caretLbl.setText("▲")
        else:
            self.body.hide()
            self.caretLbl.setText("▼")
            
class ButtonToggleBoxItem(QPushButton):
        buttonPressed = pyqtSignal(str)
        
        def __init__(self, text):
                super().__init__()
                self.setCheckable(True)
                self.setChecked(False)
                self.setText(text)
                
        def mousePressEvent(self, event):
                self.buttonPressed.emit(self.text())
                event.accept()
                
class ButtonToggleBox(QWidget):
        selectionChanged = pyqtSignal(str)
    
        def __init__(self, layoutStyle):
                super().__init__()
                self.btnList = []
                if layoutStyle == "Vertical":
                    self.layout = QVBoxLayout()
                else:
                    self.layout = QHBoxLayout()
                self.layout.setSpacing(0)
                self.layout.addStretch(1)
                
        def addButton(self, button):
                button.setCheckable(True)
                button.setChecked(False)
                button.buttonPressed.connect(self.changeSelection)
                
                self.btnList.append(button)

                self.layout.takeAt(self.layout.count() - 1)
                self.layout.addWidget(button)
                self.layout.addStretch(1)

                newWidth = self.determineMinButtonWidth()
                for each in self.btnList:
                        each.setMaximumWidth(newWidth + 20)

        def addButtons(self, listToAdd):
            for item in listToAdd:
                button = ButtonToggleBoxItem(item)
                self.addButton(button)

        def determineMinButtonWidth(self):
                widths = []
                for each in self.btnList:
                        test = each.fontMetrics().boundingRect(each.text()).width()
                        widths.append(test)
                return max(widths)

        def changeSelection(self, btnText):
                for each in self.btnList:
                        if each.text() != btnText:
                                each.setChecked(False)
                        else:
                            if each.isChecked() == True:
                                each.setChecked(False)
                            else:
                                each.setChecked(True)
                self.selectionChanged.emit(btnText)

class VendorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, vendorItem):
        super().__init__()
        self.vendor = vendorItem
        self.main = QWidget()

        idLabel = QLabel(str(self.vendor.idNum))
        self.nameLabel = QLabel(self.vendor.name)
        self.bidsLabel = QLabel("Bids: %d / %d" % (len(self.vendor.proposals),
                                                   0))
        self.invoicesLabel = QLabel("Invoices: %d / %d" % (0,
                                                           len(self.vendor.invoices)))
        self.balanceLabel = QLabel(str(self.vendor.balance()))

        layout = QHBoxLayout()
        layout.addWidget(idLabel)
        layout.addWidget(self.nameLabel)
        layout.addWidget(self.bidsLabel)
        layout.addWidget(self.invoicesLabel)
        layout.addWidget(self.balanceLabel)

        self.main.setLayout(layout)

    def refreshData(self):
        self.nameLabel = QLabel(self.vendor.name)
        self.bidsLabel = QLabel("Bids: %d / %d" % (len(self.vendor.proposals),
                                                   0))
        self.invoicesLabel = QLabel("Invoices: %d / %d" % (0,
                                                           len(self.vendor.invoices)))
        self.balanceLabel = QLabel(str(self.vendor.balance()))
        
class VendorTreeWidget(QTreeWidget):
    def __init__(self, vendorDict):
        super().__init__()
        self.vendors = vendorDict
        self.buildItems()

    def buildItems(self):
        for vendorKey in self.vendors.keys():
            item = VendorTreeWidgetItem(self.vendors[vendorKey])
            self.setItemWidget(item, 0, item.main)

    def refreshData(self):
        for item in self.items():
            item.refreshData()
