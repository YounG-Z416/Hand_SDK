"""
手部数据类型系统性能测试

此文件用于测试优化后的手部数据类型系统的性能，
包括内存使用、序列化速度、缓存效果等。
"""

import time
import sys
import json
import struct
from typing import Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict

# 导入优化后的数据类型系统
from src.core.hand_data_type import (
    HandCommand, HandStatus, HandDataManager,
    JointCommand, JointStatus, FingerCommand, FingerStatus,
    create_default_hand_command, create_default_hand_status
)
from src.core.hand_mappings import FingerType, JointType, HandType, HandSide


# ==================== 旧版本数据结构（用于对比） ====================

@dataclass
class OldJointData:
    """旧版本关节数据结构"""
    position: float = 0.0
    velocity: float = 0.0
    torque: float = 0.0
    temperature: float = 25.0
    current: float = 0.0
    status: str = "normal"
    timestamp: float = field(default_factory=time.time)


@dataclass
class OldFingerData:
    """旧版本手指数据结构"""
    joint_1: OldJointData = field(default_factory=OldJointData)
    joint_2: OldJointData = field(default_factory=OldJointData)
    joint_3: OldJointData = field(default_factory=OldJointData)


@dataclass
class OldHandData:
    """旧版本手部数据结构"""
    hand_type: str = "GaiaHand"
    hand_side: str = "right"
    thumb: OldFingerData = field(default_factory=OldFingerData)
    index: OldFingerData = field(default_factory=OldFingerData)
    middle: OldFingerData = field(default_factory=OldFingerData)
    ring: OldFingerData = field(default_factory=OldFingerData)
    little: OldFingerData = field(default_factory=OldFingerData)
    is_connected: bool = False
    is_enabled: bool = False
    error_code: int = 0
    error_message: str = ""
    battery_level: float = 100.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'hand_type': self.hand_type,
            'hand_side': self.hand_side,
            'thumb': {
                'joint_1': {
                    'position': self.thumb.joint_1.position,
                    'velocity': self.thumb.joint_1.velocity,
                    'torque': self.thumb.joint_1.torque,
                    'temperature': self.thumb.joint_1.temperature,
                    'current': self.thumb.joint_1.current,
                    'status': self.thumb.joint_1.status,
                    'timestamp': self.thumb.joint_1.timestamp
                },
                'joint_2': {
                    'position': self.thumb.joint_2.position,
                    'velocity': self.thumb.joint_2.velocity,
                    'torque': self.thumb.joint_2.torque,
                    'temperature': self.thumb.joint_2.temperature,
                    'current': self.thumb.joint_2.current,
                    'status': self.thumb.joint_2.status,
                    'timestamp': self.thumb.joint_2.timestamp
                },
                'joint_3': {
                    'position': self.thumb.joint_3.position,
                    'velocity': self.thumb.joint_3.velocity,
                    'torque': self.thumb.joint_3.torque,
                    'temperature': self.thumb.joint_3.temperature,
                    'current': self.thumb.joint_3.current,
                    'status': self.thumb.joint_3.status,
                    'timestamp': self.thumb.joint_3.timestamp
                }
            },
            'index': {
                'joint_1': {
                    'position': self.index.joint_1.position,
                    'velocity': self.index.joint_1.velocity,
                    'torque': self.index.joint_1.torque,
                    'temperature': self.index.joint_1.temperature,
                    'current': self.index.joint_1.current,
                    'status': self.index.joint_1.status,
                    'timestamp': self.index.joint_1.timestamp
                },
                'joint_2': {
                    'position': self.index.joint_2.position,
                    'velocity': self.index.joint_2.velocity,
                    'torque': self.index.joint_2.torque,
                    'temperature': self.index.joint_2.temperature,
                    'current': self.index.joint_2.current,
                    'status': self.index.joint_2.status,
                    'timestamp': self.index.joint_2.timestamp
                },
                'joint_3': {
                    'position': self.index.joint_3.position,
                    'velocity': self.index.joint_3.velocity,
                    'torque': self.index.joint_3.torque,
                    'temperature': self.index.joint_3.temperature,
                    'current': self.index.joint_3.current,
                    'status': self.index.joint_3.status,
                    'timestamp': self.index.joint_3.timestamp
                }
            },
            'middle': {
                'joint_1': {
                    'position': self.middle.joint_1.position,
                    'velocity': self.middle.joint_1.velocity,
                    'torque': self.middle.joint_1.torque,
                    'temperature': self.middle.joint_1.temperature,
                    'current': self.middle.joint_1.current,
                    'status': self.middle.joint_1.status,
                    'timestamp': self.middle.joint_1.timestamp
                },
                'joint_2': {
                    'position': self.middle.joint_2.position,
                    'velocity': self.middle.joint_2.velocity,
                    'torque': self.middle.joint_2.torque,
                    'temperature': self.middle.joint_2.temperature,
                    'current': self.middle.joint_2.current,
                    'status': self.middle.joint_2.status,
                    'timestamp': self.middle.joint_2.timestamp
                },
                'joint_3': {
                    'position': self.middle.joint_3.position,
                    'velocity': self.middle.joint_3.velocity,
                    'torque': self.middle.joint_3.torque,
                    'temperature': self.middle.joint_3.temperature,
                    'current': self.middle.joint_3.current,
                    'status': self.middle.joint_3.status,
                    'timestamp': self.middle.joint_3.timestamp
                }
            },
            'ring': {
                'joint_1': {
                    'position': self.ring.joint_1.position,
                    'velocity': self.ring.joint_1.velocity,
                    'torque': self.ring.joint_1.torque,
                    'temperature': self.ring.joint_1.temperature,
                    'current': self.ring.joint_1.current,
                    'status': self.ring.joint_1.status,
                    'timestamp': self.ring.joint_1.timestamp
                },
                'joint_2': {
                    'position': self.ring.joint_2.position,
                    'velocity': self.ring.joint_2.velocity,
                    'torque': self.ring.joint_2.torque,
                    'temperature': self.ring.joint_2.temperature,
                    'current': self.ring.joint_2.current,
                    'status': self.ring.joint_2.status,
                    'timestamp': self.ring.joint_2.timestamp
                },
                'joint_3': {
                    'position': self.ring.joint_3.position,
                    'velocity': self.ring.joint_3.velocity,
                    'torque': self.ring.joint_3.torque,
                    'temperature': self.ring.joint_3.temperature,
                    'current': self.ring.joint_3.current,
                    'status': self.ring.joint_3.status,
                    'timestamp': self.ring.joint_3.timestamp
                }
            },
            'little': {
                'joint_1': {
                    'position': self.little.joint_1.position,
                    'velocity': self.little.joint_1.velocity,
                    'torque': self.little.joint_1.torque,
                    'temperature': self.little.joint_1.temperature,
                    'current': self.little.joint_1.current,
                    'status': self.little.joint_1.status,
                    'timestamp': self.little.joint_1.timestamp
                },
                'joint_2': {
                    'position': self.little.joint_2.position,
                    'velocity': self.little.joint_2.velocity,
                    'torque': self.little.joint_2.torque,
                    'temperature': self.little.joint_2.temperature,
                    'current': self.little.joint_2.current,
                    'status': self.little.joint_2.status,
                    'timestamp': self.little.joint_2.timestamp
                },
                'joint_3': {
                    'position': self.little.joint_3.position,
                    'velocity': self.little.joint_3.velocity,
                    'torque': self.little.joint_3.torque,
                    'temperature': self.little.joint_3.temperature,
                    'current': self.little.joint_3.current,
                    'status': self.little.joint_3.status,
                    'timestamp': self.little.joint_3.timestamp
                }
            },
            'is_connected': self.is_connected,
            'is_enabled': self.is_enabled,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'battery_level': self.battery_level,
            'timestamp': self.timestamp
        }


# ==================== 性能测试函数 ====================

def test_memory_usage():
    """测试内存使用情况"""
    print("=== 内存使用测试 ===")
    
    # 创建新版本数据
    command = create_default_hand_command()
    status = create_default_hand_status()
    
    joint_cmd = JointCommand(position=0.5, velocity=0.1, torque=0.3)
    joint_status = JointStatus(position=0.48, temperature=35.0, current=0.8)
    
    command.set_joint_command(FingerType.THUMB, JointType.JOINT_1, joint_cmd)
    status.set_joint_status(FingerType.THUMB, JointType.JOINT_1, joint_status)
    
    # 计算内存使用
    command_size = sys.getsizeof(command)
    status_size = sys.getsizeof(status)
    
    print(f"命令数据内存: {command_size} 字节")
    print(f"状态数据内存: {status_size} 字节")
    print(f"总内存: {command_size + status_size} 字节")


def test_serialization_performance():
    """测试序列化性能"""
    print("\n=== 序列化性能测试 ===")
    
    # 创建测试数据
    command = create_default_hand_command()
    status = create_default_hand_status()
    
    # 设置数据
    for finger_type in FingerType:
        for joint_type in JointType:
            joint_cmd = JointCommand(position=0.5, velocity=0.1, torque=0.3)
            joint_status = JointStatus(position=0.48, temperature=35.0, current=0.8)
            
            command.set_joint_command(finger_type, joint_type, joint_cmd)
            status.set_joint_status(finger_type, joint_type, joint_status)
    
    # 测试字节序列化
    start_time = time.time()
    for _ in range(1000):
        command_bytes = command.to_bytes()
        status_bytes = status.to_bytes()
    bytes_time = time.time() - start_time
    
    print(f"字节序列化 (1000次): {bytes_time*1000:.2f} ms")
    
    # 测试数据大小
    command_bytes = command.to_bytes()
    status_bytes = status.to_bytes()
    
    print(f"命令字节流: {len(command_bytes)} 字节")
    print(f"状态字节流: {len(status_bytes)} 字节")
    print(f"总大小: {len(command_bytes) + len(status_bytes)} 字节")


def test_cache_performance():
    """测试缓存性能"""
    print("\n=== 缓存性能测试 ===")
    
    # 创建管理器
    manager = HandDataManager()
    
    # 创建测试数据
    command = create_default_hand_command()
    status = create_default_hand_status()
    
    # 设置数据
    for finger_type in FingerType:
        for joint_type in JointType:
            joint_cmd = JointCommand(position=0.5, velocity=0.1, torque=0.3)
            joint_status = JointStatus(position=0.48, temperature=35.0, current=0.8)
            
            command.set_joint_command(finger_type, joint_type, joint_cmd)
            status.set_joint_status(finger_type, joint_type, joint_status)
    
    manager.add_command("test_hand", command)
    manager.add_status("test_hand", status)
    
    # 测试无缓存性能
    start_time = time.time()
    for _ in range(1000):
        command_bytes = command.to_bytes()
        status_bytes = status.to_bytes()
    no_cache_time = time.time() - start_time
    
    # 测试有缓存性能
    start_time = time.time()
    for _ in range(1000):
        command_bytes = manager.get_command_bytes("test_hand")
        status_bytes = manager.get_status_bytes("test_hand")
    cache_time = time.time() - start_time
    
    print(f"无缓存序列化 (1000次): {no_cache_time*1000:.2f} ms")
    print(f"有缓存序列化 (1000次): {cache_time*1000:.2f} ms")
    print(f"缓存性能提升: {no_cache_time/cache_time:.1f}x")


def test_batch_operations():
    """测试批量操作性能"""
    print("\n=== 批量操作性能测试 ===")
    
    # 创建多个手部数据
    hands_count = 10
    hands = {}
    
    for i in range(hands_count):
        hand_id = f"hand_{i}"
        command = create_default_hand_command()
        status = create_default_hand_status()
        
        # 设置不同的数据
        for finger_type in FingerType:
            for joint_type in JointType:
                joint_cmd = JointCommand(position=0.5 + i * 0.1, velocity=0.1, torque=0.3)
                joint_status = JointStatus(position=0.48 + i * 0.1, temperature=35.0 + i, current=0.8)
                
                command.set_joint_command(finger_type, joint_type, joint_cmd)
                status.set_joint_status(finger_type, joint_type, joint_status)
        
        hands[hand_id] = (command, status)
    
    # 测试批量添加
    manager = HandDataManager()
    start_time = time.time()
    for hand_id, (command, status) in hands.items():
        manager.add_command(hand_id, command)
        manager.add_status(hand_id, status)
    add_time = time.time() - start_time
    
    # 测试批量获取
    start_time = time.time()
    for hand_id in hands.keys():
        command = manager.get_command(hand_id)
        status = manager.get_status(hand_id)
    get_time = time.time() - start_time
    
    # 测试批量序列化
    start_time = time.time()
    for hand_id in hands.keys():
        command_bytes = manager.get_command_bytes(hand_id)
        status_bytes = manager.get_status_bytes(hand_id)
    serialize_time = time.time() - start_time
    
    print(f"批量添加 {hands_count} 个手部数据: {add_time*1000:.2f} ms")
    print(f"批量获取 {hands_count} 个手部数据: {get_time*1000:.2f} ms")
    print(f"批量序列化 {hands_count} 个手部数据: {serialize_time*1000:.2f} ms")
    print(f"平均每个手部数据处理时间: {(add_time + get_time + serialize_time) / hands_count * 1000:.2f} ms")


def test_network_simulation():
    """测试网络传输模拟性能"""
    print("\n=== 网络传输模拟性能测试 ===")
    
    # 模拟发送端
    command = create_default_hand_command()
    status = create_default_hand_status()
    
    # 设置复杂数据
    for finger_type in FingerType:
        for joint_type in JointType:
            joint_cmd = JointCommand(
                position=0.5 + hash(finger_type) % 10 * 0.1,
                velocity=0.1 + hash(joint_type) % 5 * 0.05,
                torque=0.3 + hash(finger_type) % 3 * 0.1,
                mode="position"
            )
            joint_status = JointStatus(
                position=0.48 + hash(finger_type) % 10 * 0.1,
                velocity=0.08 + hash(joint_type) % 5 * 0.05,
                torque=0.28 + hash(finger_type) % 3 * 0.1,
                temperature=35.0 + hash(finger_type) % 10,
                current=0.8 + hash(joint_type) % 5 * 0.1,
                status="normal",
                error_code=0
            )
            
            command.set_joint_command(finger_type, joint_type, joint_cmd)
            status.set_joint_status(finger_type, joint_type, joint_status)
    
    # 测试序列化性能
    start_time = time.time()
    for _ in range(1000):
        command_bytes = command.to_bytes()
        status_bytes = status.to_bytes()
    serialize_time = time.time() - start_time
    
    # 测试反序列化性能
    command_bytes = command.to_bytes()
    status_bytes = status.to_bytes()
    
    start_time = time.time()
    for _ in range(1000):
        reconstructed_command = HandCommand.from_bytes(command_bytes)
        reconstructed_status = HandStatus.from_bytes(status_bytes)
    deserialize_time = time.time() - start_time
    
    print(f"序列化性能 (1000次): {serialize_time*1000:.2f} ms")
    print(f"反序列化性能 (1000次): {deserialize_time*1000:.2f} ms")
    print(f"总传输时间 (1000次): {(serialize_time + deserialize_time)*1000:.2f} ms")
    print(f"平均每次传输时间: {(serialize_time + deserialize_time):.6f} ms")
    
    # 验证数据完整性
    reconstructed_command = HandCommand.from_bytes(command_bytes)
    reconstructed_status = HandStatus.from_bytes(status_bytes)
    
    original_thumb = command.get_joint_command(FingerType.THUMB, JointType.JOINT_1)
    reconstructed_thumb = reconstructed_command.get_joint_command(FingerType.THUMB, JointType.JOINT_1)
    
    print(f"数据完整性验证: {original_thumb.position == reconstructed_thumb.position}")


def test_comparison_summary():
    """性能对比总结"""
    print("\n=== 性能对比总结 ===")
    
    print("优化特性:")
    print("1. 内存优化:")
    print("   - 使用 __slots__ 减少对象内存占用")
    print("   - 避免动态属性字典的开销")
    print("   - 紧凑的数据结构设计")
    
    print("\n2. 序列化优化:")
    print("   - 使用 struct 模块进行快速二进制序列化")
    print("   - 避免JSON序列化的开销")
    print("   - 支持直接字节流传输")
    
    print("\n3. 缓存机制:")
    print("   - 字节流缓存，避免重复序列化")
    print("   - 可配置的缓存TTL（默认0.1秒）")
    print("   - 自动缓存失效管理")
    
    print("\n4. 批量操作:")
    print("   - 支持批量数据添加和获取")
    print("   - 减少函数调用开销")
    print("   - 优化循环性能")
    
    print("\n5. 数据分离:")
    print("   - 区分命令数据（发送）和状态数据（接收）")
    print("   - 针对不同用途优化数据结构")
    print("   - 提高代码可读性和维护性")


def main():
    """主函数"""
    print("手部数据类型系统性能测试")
    print("=" * 60)
    
    try:
        test_memory_usage()
        test_serialization_performance()
        test_cache_performance()
        test_batch_operations()
        test_network_simulation()
        test_comparison_summary()
        
        print("\n" + "=" * 60)
        print("性能测试完成！")
        
    except Exception as e:
        print(f"执行测试时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 