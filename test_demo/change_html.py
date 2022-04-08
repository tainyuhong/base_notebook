
import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class TreeWidgetDemo(QWidget):
    def __init__(self, parent=None):
        super(TreeWidgetDemo, self).__init__(parent)
        self.setWindowTitle('获取图片 例子')
        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.btn = QPushButton('获取')
        layout.addWidget(self.text)
        layout.addWidget(self.btn)
        self.lab = QLabel('图片：')
        layout.addWidget(self.lab)
        self.setLayout(layout)
        self.btn.clicked.connect(self.get_img_info)

    def get_img_info(self):
        cur = self.text.currentCharFormat()
        img = cur.toImageFormat()
        print('图片路径：',img.name(),cur.isImageFormat())
        url = QUrl(img.name())
        print(url.isLocalFile(),url.toLocalFile())
        img_read = QImageReader(url.toLocalFile())
        # h = QInputDialog.getDouble(self,'宽高','图片长')
        # w = QInputDialog.getDouble(self,'宽高','图片宽')
        # print(h)
        # img_read.setScaledSize(QSize(h[0],w[0]))
        new_img = img_read.read()
        # text_cur = self.text.textCursor()
        # text_cur.insertImage(new_img)
        # self.text.setStyleSheet('backgroud-clip:padding;')
        # self.text.setStyleSheet('background-color-select:red;')
        self.text.setStyleSheet('QTextEdit {border-width: 5px;selection-background-color:blue;subcontrol-origin: content;selection-color: red;}')
        r = self.text.cursorRect()
        c = self.text.textCursor()
        print(c.selection().toHtml())


        print(r.getRect())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = TreeWidgetDemo()
    tree.show()
    sys.exit(app.exec())
