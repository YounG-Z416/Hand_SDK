#!/usr/bin/env python3
"""
GaiaHand左右手功能测试脚本

测试GaiaHand的单手模式和双手模式功能。
"""

import sys
import os
import time
import math

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaiyagui', 'src'))

from core.hand import create_hand, HandSide, FingerType, JointType, GestureType

def test_single_hand(hand_side: str, port: str):
    """测试单手模式"""
    print(f"\n=== 测试 {hand_side} 手模式 ===")
    print(f"使用串口: {port}")
    
    try:
        # 创建手部实例
        hand = create_hand("gaia", hand_side, port=port)
        print(f"手部类型: {hand.hand_type.value}")
        print(f"手部侧边: {hand.hand_side_name}")
        print(f"是否为右手: {hand.is_right_hand}")
        print(f"是否为左手: {hand.is_left_hand}")
        print(f"是否为双手: {hand.is_double_hand}")
        
        # 连接
        if hand.connect():
            print(f"✅ {hand_side}手连接成功")
            
            # 使能所有电机
            success = hand.enable_all_motors(True)
            print(f"使能所有电机: {'✅ 成功' if success else '❌ 失败'}")
            
            # 测试关节角度控制
            print("\n--- 测试关节角度控制 ---")
            
            # 设置食指第一个关节角度
            angle = math.pi / 4  # 45度
            success = hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, angle)
            print(f"设置食指第一个关节角度 {math.degrees(angle):.1f}°: {'✅ 成功' if success else '❌ 失败'}")
            
            time.sleep(1)
            
            # 获取当前角度
            current_angle = hand.get_joint_angle(FingerType.INDEX, JointType.JOINT_1)
            print(f"当前食指第一个关节角度: {math.degrees(current_angle):.1f}°")
            
            # 测试手势执行
            print("\n--- 测试手势执行 ---")
            success = hand.perform_gesture(GestureType.OPEN_HAND, speed=0.5, duration=1.0)
            print(f"执行张开手势: {'✅ 成功' if success else '❌ 失败'}")
            
            time.sleep(2)
            
            # 手部回零
            print("\n--- 测试手部回零 ---")
            success = hand.hand_zero()
            print(f"手部回零: {'✅ 成功' if success else '❌ 失败'}")
            
            # 获取电机状态
            print("\n--- 获取电机状态 ---")
            status = hand.get_motor_status()
            print(f"电机状态: {status}")
            
        else:
            print(f"❌ {hand_side}手连接失败")
            
    except Exception as e:
        print(f"❌ {hand_side}手测试失败: {e}")
    finally:
        if 'hand' in locals():
            hand.close()

def test_double_hand(left_port: str, right_port: str):
    """测试双手模式"""
    print(f"\n=== 测试双手模式 ===")
    print(f"左手串口: {left_port}")
    print(f"右手串口: {right_port}")
    
    try:
        # 创建双手实例
        hand = create_hand("gaia", "double", left_port=left_port, right_port=right_port)
        print(f"手部类型: {hand.hand_type.value}")
        print(f"手部侧边: {hand.hand_side_name}")
        print(f"是否为双手: {hand.is_double_hand}")
        
        # 连接
        if hand.connect():
            print("✅ 双手连接成功")
            
            # 使能所有电机
            success = hand.enable_all_motors(True)
            print(f"使能所有电机: {'✅ 成功' if success else '❌ 失败'}")
            
            # 测试分别控制左右手
            print("\n--- 测试分别控制左右手 ---")
            
            # 控制右手食指
            angle_right = math.pi / 3  # 60度
            success = hand.set_joint_angle(FingerType.INDEX, JointType.JOINT_1, angle_right, hand_side=HandSide.RIGHT)
            print(f"设置右手食指第一个关节角度 {math.degrees(angle_right):.1f}°: {'✅ 成功' if success else '❌ 失败'}")
            
            # 控制左手拇指
            angle_left = math.pi / 6  # 30度
            success = hand.set_joint_angle(FingerType.THUMB, JointType.JOINT_1, angle_left, hand_side=HandSide.LEFT)
            print(f"设置左手拇指第一个关节角度 {math.degrees(angle_left):.1f}°: {'✅ 成功' if success else '❌ 失败'}")
            
            time.sleep(2)
            
            # 获取角度
            right_angle = hand.get_joint_angle(FingerType.INDEX, JointType.JOINT_1, hand_side=HandSide.RIGHT)
            left_angle = hand.get_joint_angle(FingerType.THUMB, JointType.JOINT_1, hand_side=HandSide.LEFT)
            print(f"右手食指角度: {math.degrees(right_angle):.1f}°")
            print(f"左手拇指角度: {math.degrees(left_angle):.1f}°")
            
            # 测试同时执行手势
            print("\n--- 测试同时执行手势 ---")
            success = hand.perform_gesture(GestureType.OPEN_HAND)
            print(f"双手同时张开: {'✅ 成功' if success else '❌ 失败'}")
            
            time.sleep(2)
            
            # 同时回零
            print("\n--- 测试同时回零 ---")
            success = hand.hand_zero()
            print(f"双手同时回零: {'✅ 成功' if success else '❌ 失败'}")
            
            # 获取电机状态
            print("\n--- 获取电机状态 ---")
            status = hand.get_motor_status()
            print(f"电机状态: {status}")
            
        else:
            print("❌ 双手连接失败")
            
    except Exception as e:
        print(f"❌ 双手测试失败: {e}")
    finally:
        if 'hand' in locals():
            hand.close()

def test_advanced_features(port: str):
    """测试高级功能"""
    print(f"\n=== 测试高级功能 ===")
    print(f"使用串口: {port}")
    
    try:
        hand = create_hand("gaia", "right", port=port)
        
        if hand.connect():
            print("✅ 连接成功")
            
            # 使能电机
            hand.enable_all_motors(True)
            
            # 测试点动控制
            print("\n--- 测试点动控制 ---")
            print("食指第一个关节顺时针转动1秒...")
            hand.jog_joint(FingerType.INDEX, JointType.JOINT_1, 1)  # 顺时针
            time.sleep(1)
            hand.jog_joint(FingerType.INDEX, JointType.JOINT_1, 0)  # 停止
            print("✅ 点动控制完成")
            
            # 测试正运动学
            print("\n--- 测试正运动学 ---")
            x, y = hand.forward_kinematics(FingerType.INDEX)
            print(f"食指指尖位置: ({x:.2f}, {y:.2f})")
            
            # 测试逆运动学
            print("\n--- 测试逆运动学 ---")
            target_x, target_y = 50.0, 30.0
            angles = hand.inverse_kinematics(FingerType.INDEX, target_x, target_y)
            print(f"到达位置({target_x}, {target_y})的关节角度: {angles}")
            
            # 测试移动到指定位置
            print("\n--- 测试移动到指定位置 ---")
            success = hand.move_finger_to_position(FingerType.INDEX, target_x, target_y)
            print(f"移动到指定位置: {'✅ 成功' if success else '❌ 失败'}")
            
        else:
            print("❌ 连接失败")
            
    except Exception as e:
        print(f"❌ 高级功能测试失败: {e}")
    finally:
        if 'hand' in locals():
            hand.close()

def main():
    """主函数"""
    print("GaiaHand左右手功能测试")
    print("=" * 50)
    
    # 配置串口（根据实际情况修改）
    RIGHT_PORT = 'COM4'  # 右手串口
    LEFT_PORT = 'COM5'   # 左手串口
    
    print(f"配置信息:")
    print(f"右手串口: {RIGHT_PORT}")
    print(f"左手串口: {LEFT_PORT}")
    
    # 测试右手
    test_single_hand("right", RIGHT_PORT)
    
    # 测试左手
    test_single_hand("left", LEFT_PORT)
    
    # 测试双手模式
    test_double_hand(LEFT_PORT, RIGHT_PORT)
    
    # 测试高级功能
    test_advanced_features(RIGHT_PORT)
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    main() 