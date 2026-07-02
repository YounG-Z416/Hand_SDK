#!/usr/bin/env python3
"""
Gaia SDK 测试文件
演示如何使用 Gaia 灵巧手 SDK 的各种功能
"""

import sys
import os
import time
import math

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gaia_sdk import GaiaHand, FingerType, JointType, GestureType

def test_basic_control(hand: GaiaHand):
    """测试基本控制功能"""
    print("\n测试基本控制...")
    
    # 测试单个关节控制
    print("测试单个关节控制...")
    hand.set_joint_angle(FingerType.INDEX, JointType.MCP, math.pi/4, speed=0.5)
    time.sleep(1)
    
    # 测试整个手指控制
    print("测试整个手指控制...")
    finger_angles = {
        JointType.MCP: math.pi/4,
        JointType.PIP: math.pi/3,
        JointType.DIP: math.pi/6
    }
    hand.set_finger_angles(FingerType.MIDDLE, finger_angles, speed=0.4)
    time.sleep(1)
    
    print("基本控制测试完成")

def test_gestures(hand: GaiaHand):
    """测试手势控制"""
    print("\n测试手势控制...")
    
    gestures = [
        GestureType.OPEN_HAND,
        GestureType.CLOSED_FIST,
        GestureType.POINT,
        GestureType.THUMBS_UP
    ]
    
    for gesture in gestures:
        print(f"执行手势: {gesture.value}")
        hand.perform_gesture(gesture, speed=0.5, duration=2)
        time.sleep(1)
    
    print("手势控制测试完成")

def test_kinematics(hand: GaiaHand):
    """测试运动学功能"""
    print("\n测试运动学功能...")
    
    # 测试正运动学
    print("测试正运动学...")
    x, y = hand.forward_kinematics(FingerType.INDEX)
    print(f"食指指尖位置: ({x:.3f}, {y:.3f})")
    
    # 测试逆运动学
    print("测试逆运动学...")
    target_positions = [
        (0.08, 0.06),
        (0.06, 0.08),
        (0.10, 0.04)
    ]
    
    for x, y in target_positions:
        print(f"移动到位置: ({x:.3f}, {y:.3f})")
        hand.move_finger_to_position(FingerType.INDEX, x, y, speed=0.4)
        time.sleep(2)
    
    print("运动学功能测试完成")

def test_smooth_motion(hand: GaiaHand):
    """测试平滑运动"""
    print("\n测试平滑运动...")
    
    # 平滑地从张开手过渡到握拳
    print("平滑执行手势...")
    hand.perform_gesture(GestureType.OPEN_HAND)
    time.sleep(1)
    
    target_angles = hand.gestures[GestureType.CLOSED_FIST]
    hand.interpolate_to_position(target_angles, steps=100, delay=0.01)
    
    print("平滑运动测试完成")

def test_individual_finger_control(hand: GaiaHand):
    """测试单个手指控制"""
    print("\n测试单个手指控制...")
    
    fingers = [
        FingerType.THUMB,
        FingerType.INDEX,
        FingerType.MIDDLE,
        FingerType.RING,
        FingerType.LITTLE
    ]
    
    for finger in fingers:
        print(f"测试{finger.value}...")
        
        # 设置所有关节角度
        angles = {
            JointType.MCP: math.pi/4,
            JointType.PIP: math.pi/3,
            JointType.DIP: math.pi/6
        }
        
        hand.set_finger_angles(finger, angles, speed=0.4)
        time.sleep(1)
        
        # 获取当前角度
        current_angles = hand.get_current_angles(finger)
        print(f"当前角度: {current_angles}")
        
        time.sleep(1)
    
    print("单个手指控制测试完成")

def test_motor_status(hand: GaiaHand):
    """测试电机状态查询"""
    print("\n测试电机状态查询...")
    
    for finger in FingerType:
        print(f"\n{finger.value}状态:")
        for joint in JointType:
            try:
                angle = hand.get_joint_angle(finger, joint)
                motor_id = hand.get_motor_id(finger, joint)
                print(f"  {joint.value} (电机{motor_id}): {math.degrees(angle):.1f}°")
            except Exception as e:
                print(f"  获取{finger.value}{joint.value}状态失败: {e}")
    
    print("电机状态查询测试完成")

def test_jog_control(hand: GaiaHand):
    """测试点动控制"""
    print("\n测试点动控制...")
    
    # 测试食指MCP关节
    finger = FingerType.INDEX
    joint = JointType.MCP
    
    print(f"测试{finger.value}{joint.value}点动控制...")
    
    # 顺时针点动
    print("顺时针点动...")
    hand.jog_joint(finger, joint, 1)  # 1=顺时针
    time.sleep(2)
    
    # 停止
    print("停止...")
    hand.jog_joint(finger, joint, 0)  # 0=停止
    time.sleep(1)
    
    # 逆时针点动
    print("逆时针点动...")
    hand.jog_joint(finger, joint, 2)  # 2=逆时针
    time.sleep(2)
    
    # 停止
    print("停止...")
    hand.jog_joint(finger, joint, 0)
    
    print("点动控制测试完成")

def main():
    """主函数"""
    print("Gaia 灵巧手 SDK 测试程序")
    
    try:
        # 创建灵巧手实例
        hand = GaiaHand(port='COM4', baudrate=115200)
        
        # 连接到电机控制系统
        if hand.connect():
            try:
                # 运行测试
                test_basic_control(hand)
                test_gestures(hand)
                test_kinematics(hand)
                test_smooth_motion(hand)
                test_individual_finger_control(hand)
                test_motor_status(hand)
                test_jog_control(hand)
                
            finally:
                # 断开连接
                hand.disconnect()
                
        else:
            print("连接失败")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")

if __name__ == '__main__':
    main() 