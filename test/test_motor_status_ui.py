'''
File name: 
Descripttion: 
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 
Date: 2025-06-24 20:17:01
History: 
'''
#!/usr/bin/env python3
"""
测试MotorStatusPanel的UI修改
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

from src.gui.motor_status import MotorStatusPanel
from src.core.hand_mappings import HandSide

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电机状态面板测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建电机状态面板
        self.motor_panel = MotorStatusPanel(self)
        layout.addWidget(self.motor_panel)
        
        # 模拟手部连接
        self.simulate_hand_connection()
    
    def simulate_hand_connection(self):
        """模拟手部连接"""
        # 这里可以模拟不同的手部侧边
        print("测试单手模式（右手）")
        # self.motor_panel.set_hand_side(HandSide.RIGHT)
        
        # 测试双手模式
        print("测试双手模式")
        self.motor_panel.set_hand_side(HandSide.DOUBLE)

def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 