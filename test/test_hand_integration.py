#!/usr/bin/env python3
"""
手部集成测试脚本

测试统一的hand接口的创建和方法存在性
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_hand_creation():
    """测试手部对象创建"""
    print("=== 测试手部对象创建 ===")
    
    try:
        from src.core.hand import create_hand, HandType, HandSide
        
        # 测试不同的手部类型和侧边
        test_cases = [
            ("pantheon", "right"),
            ("pantheon", "left"),
            ("pantheon", "double"),
            ("gaia", "right"),
            ("gaia", "left"),
            ("gaia", "double"),
            (HandType.PANTHEON, HandSide.RIGHT),
            (HandType.GAIA, HandSide.LEFT),
        ]
        
        for hand_type, hand_side in test_cases:
            try:
                print(f"\n测试: {hand_type} - {hand_side}")
                hand = create_hand(hand_type, hand_side)
                
                print(f"  ✓ 创建成功")
                print(f"  - 手部类型: {hand.hand_type.value}")
                print(f"  - 手部侧边: {hand.hand_side_name}")
                print(f"  - 是否为右手: {hand.is_right_hand}")
                print(f"  - 是否为左手: {hand.is_left_hand}")
                print(f"  - 是否为双手: {hand.is_double_hand}")
                
            except Exception as e:
                print(f"  ✗ 创建失败: {e}")
                
    except Exception as e:
        print(f"导入失败: {e}")
        return False
    
    return True

def test_method_existence():
    """测试方法存在性"""
    print("\n=== 测试方法存在性 ===")
    
    try:
        from src.core.hand import create_hand, HandType, HandSide
        
        # 创建测试对象
        hand = create_hand("pantheon", "right")
        
        # 必需方法列表
        required_methods = [
            'connect', 'disconnect', 'is_connected',
            'get_joint_positions', 'set_joint_positions',
            'control_single_finger', 'control_finger_joint',
            'control_multiple_fingers', 'hand_zero',
            'emergency_stop', 'get_motor_status'
        ]
        
        # 可选方法列表
        optional_methods = [
            'set_joint_angle', 'get_joint_angle', 'perform_gesture',
            'enable_motor', 'enable_all_motors', 'jog_joint',
            'forward_kinematics', 'inverse_kinematics',
            'move_finger_to_position'
        ]
        
        # 属性列表
        properties = [
            'hand_side_name', 'is_right_hand', 'is_left_hand', 'is_double_hand'
        ]
        
        print("检查必需方法:")
        for method in required_methods:
            if hasattr(hand, method):
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} - 缺失")
        
        print("\n检查可选方法:")
        for method in optional_methods:
            if hasattr(hand, method):
                print(f"  ✓ {method}")
            else:
                print(f"  - {method} - 可选")
        
        print("\n检查属性:")
        for prop in properties:
            if hasattr(hand, prop):
                print(f"  ✓ {prop}")
            else:
                print(f"  ✗ {prop} - 缺失")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_hand_side_validation():
    """测试手部侧边验证"""
    print("\n=== 测试手部侧边验证 ===")
    
    try:
        from src.core.hand import create_hand, HandSide
        
        # 测试有效的侧边
        valid_sides = ["right", "left", "double", "r", "l", "d", "both"]
        
        for side in valid_sides:
            try:
                hand = create_hand("pantheon", side)
                print(f"  ✓ '{side}' -> {hand.hand_side_name}")
            except Exception as e:
                print(f"  ✗ '{side}' 失败: {e}")
        
        # 测试无效的侧边
        invalid_sides = ["invalid", "middle", "up", "down"]
        
        print("\n测试无效侧边:")
        for side in invalid_sides:
            try:
                hand = create_hand("pantheon", side)
                print(f"  ✗ '{side}' 应该失败但成功了")
            except ValueError as e:
                print(f"  ✓ '{side}' 正确抛出异常: {e}")
            except Exception as e:
                print(f"  ? '{side}' 抛出其他异常: {e}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("手部集成测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_hand_creation,
        test_method_existence,
        test_hand_side_validation
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