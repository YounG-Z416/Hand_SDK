#!/usr/bin/env python3
"""
测试设置对话框功能
"""

import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PySide6.QtWidgets import QApplication
from src.gui.gaia_gui import ConnectionSettingsDialog

def test_settings_dialog():
    """测试设置对话框"""
    app = QApplication(sys.argv)
    
    # 创建设置对话框
    dialog = ConnectionSettingsDialog()
    
    print("=== 设置对话框测试 ===")
    print("1. 测试手部类型选择")
    print(f"   当前手部类型: {dialog.hand_type_combo.currentText()}")
    print(f"   当前手部侧边: {dialog.hand_side_combo.currentText()}")
    
    # 测试手部类型切换
    print("\n2. 测试手部类型切换")
    dialog.hand_type_combo.setCurrentText("PantheonHand")
    print(f"   切换到PantheonHand后: {dialog.hand_type_combo.currentText()}")
    
    dialog.hand_type_combo.setCurrentText("GaiaHand")
    print(f"   切换到GaiaHand后: {dialog.hand_type_combo.currentText()}")
    
    # 测试手部侧边切换
    print("\n3. 测试手部侧边切换")
    for side in ["右手", "左手", "双手"]:
        dialog.hand_side_combo.setCurrentText(side)
        print(f"   切换到{side}后: {dialog.hand_side_combo.currentText()}")
    
    # 测试设置获取
    print("\n4. 测试设置获取")
    settings = dialog.get_hand_settings()
    print(f"   当前设置: {json.dumps(settings, indent=2, ensure_ascii=False)}")
    
    # 测试设置保存和加载
    print("\n5. 测试设置保存和加载")
    dialog.save_settings()
    print("   设置已保存到settings.json")
    
    # 重新加载设置
    dialog.load_settings()
    print("   设置已重新加载")
    
    print("\n=== 测试完成 ===")
    print("请手动检查设置对话框的界面和功能")
    
    # 显示对话框
    dialog.show()
    
    return app.exec()

if __name__ == "__main__":
    test_settings_dialog() 