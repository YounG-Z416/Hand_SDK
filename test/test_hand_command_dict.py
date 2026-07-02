#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试HandCommand类的to_dict和from_dict功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaiyagui', 'src'))

from core.hand_data_type import HandCommand, JointCommand, FingerCommand
from core.hand_mappings import HandType, HandSide, FingerType, JointType

def test_hand_command_dict():
    """测试HandCommand的字典转换功能"""
    
    print("=== 测试HandCommand字典转换功能 ===")
    
    # 1. 创建默认的HandCommand
    print("\n1. 创建默认的HandCommand...")
    hand_cmd = HandCommand()
    print(f"默认HandCommand: hand_type={hand_cmd.hand_type}, hand_side={hand_cmd.hand_side}")
    
    # 2. 转换为字典格式
    print("\n2. 转换为字典格式...")
    cmd_dict = hand_cmd.to_dict()
    print("转换后的字典:")
    import json
    print(json.dumps(cmd_dict, indent=2, ensure_ascii=False))
    
    # 3. 从字典创建HandCommand
    print("\n3. 从字典创建HandCommand...")
    new_hand_cmd = HandCommand.from_dict(cmd_dict)
    print(f"重建的HandCommand: hand_type={new_hand_cmd.hand_type}, hand_side={new_hand_cmd.hand_side}")
    
    # 4. 测试设置关节命令
    print("\n4. 测试设置关节命令...")
    # 设置右手拇指第一个关节的位置
    joint_cmd = JointCommand(position=1.57, velocity=0.5, torque=0.1)
    hand_cmd.set_joint_command(HandSide.RIGHT, FingerType.THUMB, JointType.JOINT_1, joint_cmd)
    
    # 设置右手食指第二个关节的位置
    joint_cmd2 = JointCommand(position=0.785, velocity=0.3, torque=0.05)
    hand_cmd.set_joint_command(HandSide.RIGHT, FingerType.INDEX, JointType.JOINT_2, joint_cmd2)
    
    # 5. 再次转换为字典
    print("\n5. 设置关节命令后转换为字典...")
    cmd_dict2 = hand_cmd.to_dict()
    print("设置关节命令后的字典:")
    print(json.dumps(cmd_dict2, indent=2, ensure_ascii=False))
    
    # 6. 测试双手模式
    print("\n6. 测试双手模式...")
    hand_cmd.hand_side = HandSide.DOUBLE
    
    # 设置左手拇指第一个关节的位置
    joint_cmd3 = JointCommand(position=-1.57, velocity=0.2, torque=0.08)
    hand_cmd.set_joint_command(HandSide.LEFT, FingerType.THUMB, JointType.JOINT_1, joint_cmd3)
    
    cmd_dict3 = hand_cmd.to_dict()
    print("双手模式的字典:")
    print(json.dumps(cmd_dict3, indent=2, ensure_ascii=False))
    
    # 7. 测试JSON序列化
    print("\n7. 测试JSON序列化...")
    json_str = hand_cmd.to_json()
    print("JSON字符串:")
    print(json_str)
    
    # 8. 从JSON反序列化
    print("\n8. 从JSON反序列化...")
    hand_cmd_from_json = HandCommand.from_json(json_str)
    print(f"从JSON重建: hand_type={hand_cmd_from_json.hand_type}, hand_side={hand_cmd_from_json.hand_side}")
    
    # 9. 验证数据一致性
    print("\n9. 验证数据一致性...")
    original_dict = hand_cmd.to_dict()
    restored_dict = hand_cmd_from_json.to_dict()
    
    if original_dict == restored_dict:
        print("✓ 数据一致性验证通过")
    else:
        print("✗ 数据一致性验证失败")
        print("原始数据:", original_dict)
        print("恢复数据:", restored_dict)
    
    print("\n=== 测试完成 ===")

def test_hand_command_dict_format():
    """测试HandCommand字典格式是否符合预期"""
    
    print("\n=== 测试HandCommand字典格式 ===")
    
    # 创建符合hand_command_dict格式的测试数据
    test_dict = {
        "hand_type": "GAIA",
        "hand_side": "RIGHT",
        "command_type": "position",
        "timestamp": 1620000000.123,
        "right_hand": {
            "finger_num": 5,
            "thumb": {
                "joint_num": 3,
                "joint_1": {
                    "position": 0.5,
                    "velocity": 0.1,
                    "torque": 0.05,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "joint_2": {
                    "position": 0.3,
                    "velocity": 0.05,
                    "torque": 0.02,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "joint_3": {
                    "position": 0.1,
                    "velocity": 0.02,
                    "torque": 0.01,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "timestamp": 1620000000.123
            },
            "index": {
                "joint_num": 3,
                "joint_1": {
                    "position": 0.4,
                    "velocity": 0.08,
                    "torque": 0.04,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "joint_2": {
                    "position": 0.2,
                    "velocity": 0.04,
                    "torque": 0.02,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "joint_3": {
                    "position": 0.1,
                    "velocity": 0.02,
                    "torque": 0.01,
                    "mode": "position",
                    "timestamp": 1620000000.123
                },
                "timestamp": 1620000000.123
            }
        }
    }
    
    print("测试字典格式:")
    import json
    print(json.dumps(test_dict, indent=2, ensure_ascii=False))
    
    # 从测试字典创建HandCommand
    print("\n从测试字典创建HandCommand...")
    hand_cmd = HandCommand.from_dict(test_dict)
    print(f"创建的HandCommand: hand_type={hand_cmd.hand_type}, hand_side={hand_cmd.hand_side}")
    
    # 验证关节数据
    print("\n验证关节数据...")
    thumb_joint1 = hand_cmd.get_joint_command(HandSide.RIGHT, FingerType.THUMB, JointType.JOINT_1)
    print(f"右手拇指关节1: position={thumb_joint1.position}, velocity={thumb_joint1.velocity}")
    
    index_joint2 = hand_cmd.get_joint_command(HandSide.RIGHT, FingerType.INDEX, JointType.JOINT_2)
    print(f"右手食指关节2: position={index_joint2.position}, velocity={index_joint2.velocity}")
    
    # 转换回字典并比较
    print("\n转换回字典并比较...")
    restored_dict = hand_cmd.to_dict()
    
    # 只比较right_hand部分
    if test_dict["right_hand"]["thumb"]["joint_1"]["position"] == restored_dict["right_hand"]["thumb"]["joint_1"]["position"]:
        print("✓ 关节数据一致性验证通过")
    else:
        print("✗ 关节数据一致性验证失败")
    
    print("=== 格式测试完成 ===")

if __name__ == "__main__":
    test_hand_command_dict()
    test_hand_command_dict_format() 