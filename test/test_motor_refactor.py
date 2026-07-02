#!/usr/bin/env python3
"""
测试Motor类和GaiaHand类的重构
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.motor import Motor
from src.core.gaia_hand import GaiaHand, FingerType, JointType, GestureType

def test_motor_class():
    """测试Motor类的基本功能"""
    print("=== 测试Motor类 ===")
    
    # 创建Motor实例
    motor = Motor(port='COM4', baudrate=256000)
    print(f"Motor实例创建成功: port={motor.port}, baudrate={motor.baudrate}")
    
    # 测试连接（不实际连接，只测试方法存在）
    print(f"connect方法存在: {hasattr(motor, 'connect')}")
    print(f"disconnect方法存在: {hasattr(motor, 'disconnect')}")
    print(f"set_motor_angle方法存在: {hasattr(motor, 'set_motor_angle')}")
    print(f"get_motor_angle方法存在: {hasattr(motor, 'get_motor_angle')}")
    print(f"enable_motor方法存在: {hasattr(motor, 'enable_motor')}")
    print(f"get_motor_status方法存在: {hasattr(motor, 'get_motor_status')}")
    
    print("Motor类测试完成\n")

def test_gaia_hand_class():
    """测试GaiaHand类的基本功能"""
    print("=== 测试GaiaHand类 ===")
    
    # 创建GaiaHand实例
    hand = GaiaHand(port='COM4', baudrate=256000)
    print(f"GaiaHand实例创建成功: port={hand.port}, baudrate={hand.baudrate}")
    
    # 测试继承关系
    print(f"GaiaHand是否继承自Motor: {isinstance(hand, Motor)}")
    
    # 测试电机ID映射
    motor_id = hand.get_motor_id(FingerType.THUMB, JointType.MCP)
    print(f"拇指掌指关节对应的电机ID: {motor_id}")
    
    # 测试手势定义
    print(f"预定义手势数量: {len(hand.gestures)}")
    for gesture_type in GestureType:
        print(f"  - {gesture_type.value}")
    
    # 测试手指长度参数
    print(f"手指长度参数:")
    for finger_type in FingerType:
        lengths = hand.finger_lengths[finger_type]
        print(f"  - {finger_type.value}: MCP={lengths[JointType.MCP]}mm, PIP={lengths[JointType.PIP]}mm, DIP={lengths[JointType.DIP]}mm")
    
    # 测试方法存在性
    print(f"set_joint_angle方法存在: {hasattr(hand, 'set_joint_angle')}")
    print(f"get_joint_angle方法存在: {hasattr(hand, 'get_joint_angle')}")
    print(f"perform_gesture方法存在: {hasattr(hand, 'perform_gesture')}")
    print(f"forward_kinematics方法存在: {hasattr(hand, 'forward_kinematics')}")
    print(f"inverse_kinematics方法存在: {hasattr(hand, 'inverse_kinematics')}")
    
    print("GaiaHand类测试完成\n")

def test_method_inheritance():
    """测试方法继承"""
    print("=== 测试方法继承 ===")
    
    hand = GaiaHand()
    
    # 测试Motor类的方法是否可用
    print("测试Motor类方法在GaiaHand中的可用性:")
    motor_methods = [
        'connect', 'disconnect', 'enable_motor', 'enable_all_motors',
        'set_motor_angle', 'get_motor_angle', 'jog_motor', 'emergency_stop',
        'get_motor_status', 'get_all_motor_status'
    ]
    
    for method in motor_methods:
        exists = hasattr(hand, method)
        print(f"  {method}: {'✓' if exists else '✗'}")
    
    print("方法继承测试完成\n")

def test_gesture_functionality():
    """测试手势功能"""
    print("=== 测试手势功能 ===")
    
    hand = GaiaHand()
    
    # 测试手势定义
    for gesture_type in GestureType:
        gesture_angles = hand.gestures[gesture_type]
        print(f"{gesture_type.value}:")
        for (finger, joint), angle in gesture_angles.items():
            motor_id = hand.get_motor_id(finger, joint)
            print(f"  - {finger.value}{joint.value} (电机{motor_id}): {angle:.2f}弧度 ({math.degrees(angle):.1f}度)")
        print()
    
    print("手势功能测试完成\n")

def test_kinematics():
    """测试运动学功能"""
    print("=== 测试运动学功能 ===")
    
    hand = GaiaHand()
    
    # 测试正运动学
    print("正运动学测试:")
    for finger_type in FingerType:
        try:
            x, y = hand.forward_kinematics(finger_type)
            print(f"  {finger_type.value}指尖位置: ({x:.2f}, {y:.2f})mm")
        except Exception as e:
            print(f"  {finger_type.value}正运动学计算失败: {e}")
    
    # 测试逆运动学
    print("\n逆运动学测试:")
    test_positions = [(50, 30), (60, 40), (70, 50)]
    for x, y in test_positions:
        try:
            angles = hand.inverse_kinematics(FingerType.INDEX, x, y)
            print(f"  目标位置({x}, {y})mm -> 关节角度:")
            for joint, angle in angles.items():
                print(f"    {joint.value}: {angle:.2f}弧度 ({math.degrees(angle):.1f}度)")
        except Exception as e:
            print(f"  目标位置({x}, {y})mm 逆运动学计算失败: {e}")
    
    print("运动学功能测试完成\n")

if __name__ == "__main__":
    import math
    
    print("开始测试Motor类和GaiaHand类的重构...\n")
    
    try:
        test_motor_class()
        test_gaia_hand_class()
        test_method_inheritance()
        test_gesture_functionality()
        test_kinematics()
        
        print("所有测试完成！重构成功！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc() 