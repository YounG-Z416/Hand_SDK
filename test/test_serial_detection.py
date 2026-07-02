#!/usr/bin/env python3
"""
串口检测测试脚本

测试跨平台的串口检测功能，包括Windows和Linux系统。
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.serial_utils import (
    get_system_type, 
    get_available_ports, 
    quick_detect_ports,
    test_port_connection,
    auto_detect_gaia_ports,
    find_gaia_hand_ports,
    get_linux_permission_help,
    print_system_info,
    get_default_ports,
    check_linux_port_permissions
)

def test_system_info():
    """测试系统信息显示"""
    print("\n=== 测试系统信息 ===")
    print_system_info()

def test_basic_port_detection():
    """测试基本串口检测"""
    print("\n=== 测试基本串口检测 ===")
    
    # 获取系统类型
    system = get_system_type()
    print(f"当前系统: {system.upper()}")
    
    # 获取默认串口配置
    default_ports = get_default_ports()
    print(f"默认串口配置: {default_ports}")
    
    # 快速检测串口
    ports = quick_detect_ports()
    print(f"快速检测结果: {ports}")
    
    # 获取详细串口信息
    detailed_ports = get_available_ports()
    print(f"详细串口信息: {len(detailed_ports)} 个串口")
    for port_info in detailed_ports:
        print(f"  {port_info['port']}: {port_info['description']}")
        if port_info['manufacturer']:
            print(f"    制造商: {port_info['manufacturer']}")
        if port_info['product']:
            print(f"    产品: {port_info['product']}")

def test_port_connection():
    """测试串口连接"""
    print("\n=== 测试串口连接 ===")
    
    # 获取可用串口
    ports = quick_detect_ports()
    
    if not ports:
        print("没有可用的串口进行测试")
        return
    
    # 测试前几个串口的连接
    test_count = min(3, len(ports))
    for i in range(test_count):
        port = ports[i]
        print(f"测试串口 {port}...")
        
        # Linux系统下检查权限
        system = get_system_type()
        if system == 'linux':
            has_permission = check_linux_port_permissions(port)
            print(f"  权限检查: {'通过' if has_permission else '失败'}")
            
            if not has_permission:
                print("  权限不足，跳过连接测试")
                continue
        
        # 测试连接
        success = test_port_connection(port, baudrate=256000, timeout=2)
        print(f"  连接测试: {'成功' if success else '失败'}")

def test_gaia_port_detection():
    """测试Gaia手部控制器串口检测"""
    print("\n=== 测试Gaia手部控制器串口检测 ===")
    
    # 自动检测
    config = auto_detect_gaia_ports()
    if config:
        print(f"自动检测结果:")
        print(f"  左手串口: {config['left']}")
        print(f"  右手串口: {config['right']}")
        print(f"  可用串口: {config['available']}")
    else:
        print("自动检测失败")
    
    # 查找可能的串口
    gaia_ports = find_gaia_hand_ports()
    print(f"查找结果:")
    print(f"  左手串口: {gaia_ports['left']}")
    print(f"  右手串口: {gaia_ports['right']}")
    print(f"  可用串口: {gaia_ports['available']}")

def test_linux_permissions():
    """测试Linux权限相关功能"""
    system = get_system_type()
    if system != 'linux':
        print(f"\n=== Linux权限测试跳过 (当前系统: {system.upper()}) ===")
        return
    
    print("\n=== 测试Linux权限相关功能 ===")
    
    # 获取可用串口
    ports = quick_detect_ports()
    
    if not ports:
        print("没有可用的串口进行权限测试")
        return
    
    print("串口权限检查:")
    for port in ports[:3]:  # 只检查前3个
        has_permission = check_linux_port_permissions(port)
        print(f"  {port}: {'有权限' if has_permission else '无权限'}")
    
    # 显示权限设置帮助
    print("\nLinux权限设置帮助:")
    help_text = get_linux_permission_help()
    print(help_text)

def test_cross_platform_compatibility():
    """测试跨平台兼容性"""
    print("\n=== 测试跨平台兼容性 ===")
    
    system = get_system_type()
    print(f"当前系统: {system.upper()}")
    
    # 测试不同系统的串口命名
    from src.core.serial_utils import get_common_ports
    common_ports = get_common_ports()
    
    print("各系统常见串口:")
    for sys_name, ports in common_ports.items():
        print(f"  {sys_name.upper()}: {ports[:4]}...")  # 只显示前4个
    
    # 测试默认配置
    default_ports = get_default_ports()
    print(f"当前系统默认配置: {default_ports}")

def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    # 测试无效串口
    invalid_ports = ['INVALID_PORT', '/dev/nonexistent', 'COM999']
    
    for port in invalid_ports:
        print(f"测试无效串口 {port}...")
        try:
            success = test_port_connection(port, timeout=1)
            print(f"  结果: {'成功' if success else '失败'}")
        except Exception as e:
            print(f"  异常: {e}")

def main():
    """主测试函数"""
    print("=== 跨平台串口检测测试 ===")
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    try:
        # 运行所有测试
        test_system_info()
        test_basic_port_detection()
        test_port_connection()
        test_gaia_port_detection()
        test_linux_permissions()
        test_cross_platform_compatibility()
        test_error_handling()
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 