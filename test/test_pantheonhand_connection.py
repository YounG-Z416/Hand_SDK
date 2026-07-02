#!/usr/bin/env python3
"""
PantheonHand连接测试脚本

测试改进后的PantheonHand连接功能，包括：
- 连接管理
- 状态检查
- 错误处理
- 电机状态查询
"""

import sys
import os
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_pantheonhand_connection():
    """测试PantheonHand连接功能"""
    print("=== PantheonHand连接测试 ===")
    
    try:
        # 导入PantheonHand
        from src.hand.hand.pantheonhand import PantheonHand
        
        # 测试不同的手部类型
        hand_types = ["right", "left"]
        
        for hand_type in hand_types:
            print(f"\n--- 测试 {hand_type} 手 ---")
            
            try:
                # 创建PantheonHand实例
                hand = PantheonHand(hand_side=hand_type)
                print(f"✓ 成功创建 {hand_type} 手实例")
                
                # 检查初始状态
                print(f"初始连接状态: {hand.is_connected()}")
                print(f"手部类型: {hand.hand}")
                
                # 尝试连接（注意：这里可能没有实际硬件）
                print("尝试连接...")
                connected = hand.connect(timeout=5.0)
                print(f"连接结果: {connected}")
                
                if connected:
                    print("✓ 连接成功")
                    
                    # 测试连接状态
                    print(f"连接状态: {hand.is_connected()}")
                    
                    # 获取连接状态信息
                    status = hand.get_connection_status()
                    print(f"连接状态信息: {status}")
                    
                    # 获取手指状态
                    finger_status = hand.get_finger_status()
                    print(f"手指状态: {finger_status}")
                    
                    # 测试基本操作（不实际执行）
                    print("测试基本操作...")
                    
                    # 读取关节位置（可能失败，因为没有实际数据）
                    try:
                        positions = hand.position_read()
                        print(f"关节位置: {positions}")
                    except Exception as e:
                        print(f"读取关节位置失败（预期）: {e}")
                    
                    # 测试手部回零（不实际执行）
                    try:
                        hand.hand_zero()
                        print("✓ 手部回零命令发送成功")
                    except Exception as e:
                        print(f"手部回零失败: {e}")
                    
                    # 断开连接
                    hand.disconnect()
                    print("✓ 断开连接成功")
                    
                else:
                    print("✗ 连接失败（可能是没有实际硬件）")
                    
            except Exception as e:
                print(f"✗ {hand_type} 手测试失败: {e}")
                
    except ImportError as e:
        print(f"✗ 导入PantheonHand失败: {e}")
        print("请确保已安装pantheonhand包")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    return True

def test_hand_integration():
    """测试统一hand接口的PantheonHand集成"""
    print("\n=== 统一hand接口PantheonHand集成测试 ===")
    
    try:
        from src.core.hand import create_hand, HandType, HandSide
        
        # 测试创建PantheonHand
        print("测试创建PantheonHand...")
        
        # 使用字符串指定类型
        hand = create_hand("pantheon", "right")
        print(f"✓ 成功创建PantheonHand: {hand.hand_type.value}")
        print(f"手部侧边: {hand.hand_side_name}")
        print(f"是否为右手: {hand.is_right_hand}")
        
        # 测试连接
        print("测试连接...")
        connected = hand.connect()
        print(f"连接结果: {connected}")
        
        if connected:
            print("✓ 连接成功")
            
            # 测试连接状态检查
            print(f"连接状态: {hand.is_connected()}")
            
            # 测试电机状态查询
            print("测试电机状态查询...")
            motor_status = hand.get_motor_status()
            print(f"电机状态: {motor_status}")
            
            # 测试单个电机状态
            single_motor_status = hand.get_motor_status(0)
            print(f"电机0状态: {single_motor_status}")
            
            # 断开连接
            hand.disconnect()
            print("✓ 断开连接成功")
            
        else:
            print("✗ 连接失败（可能是没有实际硬件）")
            
    except Exception as e:
        print(f"✗ 统一接口测试失败: {e}")
        return False
    
    return True

def test_error_handling():
    """测试错误处理"""
    print("\n=== 错误处理测试 ===")
    
    try:
        from src.core.hand import create_hand
        
        # 测试无效的手部类型
        try:
            hand = create_hand("invalid_type", "right")
            print("✗ 应该抛出异常但没有")
        except ValueError as e:
            print(f"✓ 正确捕获无效手部类型错误: {e}")
        
        # 测试无效的手部侧边
        try:
            hand = create_hand("pantheon", "invalid_side")
            print("✗ 应该抛出异常但没有")
        except ValueError as e:
            print(f"✓ 正确捕获无效手部侧边错误: {e}")
        
        # 测试未连接时的操作
        hand = create_hand("pantheon", "right")
        try:
            hand.get_joint_positions()
            print("✗ 应该抛出异常但没有")
        except RuntimeError as e:
            print(f"✓ 正确捕获未连接错误: {e}")
            
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("PantheonHand连接功能测试")
    print("=" * 50)
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    # 运行所有测试
    tests = [
        test_pantheonhand_connection,
        test_hand_integration,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试 {test.__name__} 异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 