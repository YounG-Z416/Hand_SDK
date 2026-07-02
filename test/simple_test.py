#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HandCommand测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'gaiyagui', 'src'))

from core.hand_data_type import HandCommand, JointCommand
from core.hand_mappings import HandType, HandSide, FingerType, JointType

def main():
    print("=== HandCommand 测试 ===")
    
    # 1. 创建默认HandCommand
    print("\n1. 创建默认HandCommand...")
    hand_cmd = HandCommand()
    print(f"默认: hand_type={hand_cmd.hand_type}, hand_side={hand_cmd.hand_side}")
    
    # 2. 转换为字典
    print("\n2. 转换为字典...")
    cmd_dict = hand_cmd.to_dict()
    print("字典格式:")
    import json
    print(json.dumps(cmd_dict, indent=2, ensure_ascii=False))
    
    # 3. 设置一些关节命令
    print("\n3. 设置关节命令...")
    joint_cmd = JointCommand(position=1.57, velocity=0.5, torque=0.1)
    hand_cmd.set_joint_command(HandSide.RIGHT, FingerType.THUMB, JointType.JOINT_1, joint_cmd)
    
    joint_cmd2 = JointCommand(position=0.785, velocity=0.3, torque=0.05)
    hand_cmd.set_joint_command(HandSide.RIGHT, FingerType.INDEX, JointType.JOINT_2, joint_cmd2)
    
    # 4. 再次转换为字典
    print("\n4. 设置命令后转换为字典...")
    cmd_dict2 = hand_cmd.to_dict()
    print("设置命令后的字典:")
    print(json.dumps(cmd_dict2, indent=2, ensure_ascii=False))
    
    # 5. 从字典重建
    print("\n5. 从字典重建HandCommand...")
    hand_cmd2 = HandCommand.from_dict(cmd_dict2)
    print(f"重建: hand_type={hand_cmd2.hand_type}, hand_side={hand_cmd2.hand_side}")
    
    # 6. 验证数据
    print("\n6. 验证数据...")
    thumb_joint1 = hand_cmd2.get_joint_command(HandSide.RIGHT, FingerType.THUMB, JointType.JOINT_1)
    print(f"右手拇指关节1: position={thumb_joint1.position}, velocity={thumb_joint1.velocity}")
    
    index_joint2 = hand_cmd2.get_joint_command(HandSide.RIGHT, FingerType.INDEX, JointType.JOINT_2)
    print(f"右手食指关节2: position={index_joint2.position}, velocity={index_joint2.velocity}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 