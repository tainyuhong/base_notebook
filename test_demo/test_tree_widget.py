import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import QIcon, QBrush, QColor
from PySide6.QtCore import Qt


class TreeWidgetDemo(QMainWindow):
    def __init__(self, parent=None):
        super(TreeWidgetDemo, self).__init__(parent)
        self.setWindowTitle('TreeWidget 例子')
        self.tree = QTreeWidget()
        # 设置树形结构列数
        self.tree.setColumnCount(2)
        # 设置头的标题
        self.tree.setHeaderLabels(['Key', 'Value'])
        # 设置根节点
        root = QTreeWidgetItem(self.tree)
        root.setText(0, 'root')
        root.setIcon(0, QIcon("./images/root.png"))
        # 设置列宽
        self.tree.setColumnWidth(0, 160)
        # 设置节点的背景颜色
        brush_red = QBrush(Qt.red)
        root.setBackground(0, brush_red)
        brush_green = QBrush(Qt.green)
        root.setBackground(1, brush_green)
        dict = {"child-1": "Python", "child-2": "Java", "child-3": "C++", "child-4": "C"}

        # 设置子节点1
        for key, value in dict.items():
            child = QTreeWidgetItem(root)  # 创建子节点
            child.setText(0, key)  # 设置第一列的值
            child.setText(1, value)  # 设置第二列的值
            child.setIcon(0, QIcon("./image/two.ico"))
            child.setCheckState(0, Qt.Checked)  # 设置第一列选中状态
            self.tree.addTopLevelItem(root)  # 将创建的树节点添加到树控件中

        # 设置子节点2
        child2 = QTreeWidgetItem(root)
        child2.setText(0, 'child2')
        child2.setText(1, '')
        child2.setIcon(0, QIcon("./image/three.ico"))

        # 设置子节点2下显示数据
        for key, value in dict.items():
            child3 = QTreeWidgetItem(child2)  # 创建子节点
            child3.setText(0, key)  # 设置第一列的值
            child3.setText(1, value)  # 设置第二列的值
            child3.setIcon(0, QIcon("./image/two.ico"))
            child3.setCheckState(0, Qt.Checked)  # 设置第一列选中状态
            self.tree.addTopLevelItem(root)  # 将创建的树节点添加到树控件中
            self.tree.expandAll()  # 展开所有的树节点
        # 设置子节点3
        child3 = QTreeWidgetItem(root)
        child3.setText(0, 'child3')
        child3.setText(1, 'Python数据分析实例')
        child3.setIcon(0, QIcon("./image/three.ico"))  # 为节点添加响应事件，获取所选择节点文本
        self.tree.clicked.connect(self.onTreeClicked)
        # 结点全部展开
        self.tree.expandAll()
        self.setCentralWidget(self.tree)


    def onTreeClicked(self):
        item = self.tree.currentItem()
        print("key=%s ,value=%s" % (item.text(0), item.text(1)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tree = TreeWidgetDemo()
    tree.show()
    sys.exit(app.exec())
