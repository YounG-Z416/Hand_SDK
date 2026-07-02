'''
File name: test_urdf_viewer.py
Description: 测试 URDF 查看器的独立启动程序
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 1.0
Date: 2025-05-29 15:59:11
History: Initial version
'''

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from src.gui.urdf_viewer import MainWindow

def main():
    """主函数：启动 URDF 查看器界面"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
