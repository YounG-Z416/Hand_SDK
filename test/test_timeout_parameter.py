#!/usr/bin/env python3
"""
测试timeout参数功能
验证_get_latest_all_motor_status和_get_latest_motor_status的timeout参数
"""

import sys
import time
import threading
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.hand.hand.gaiahand.motor import Motor, ResponseType, Response

def test_timeout_parameter():
    """测试timeout参数功能"""
    print("=== 测试timeout参数功能 ===")
    
    # 创建Motor实例（不连接串口）
    motor = Motor(port='COM4', baudrate=256000)
    
    # 模拟响应数据
    print("\n1. 准备测试数据...")
    test_responses = []
    for motor_id in range(1, 16):
        response = Response(
            type=ResponseType.STATUS_RESPONSE,
            data={
                'motor_id': motor_id,
                'online': motor_id % 2 == 0,  # 偶数电机在线
                'angle': motor_id * 10.0,
                'fsm_state': 1,
                'error_code': 0,
                'temp': 25.0 + motor_id,
                'bus_voltage': 24.0
            },
            timestamp=time.time(),
            raw_data=b''
        )
        test_responses.append(response)
    
    # 测试不同的timeout值
    timeout_values = [0.1, 0.3, 0.5, 1.0]
    
    for timeout in timeout_values:
        print(f"\n2. 测试timeout={timeout}s...")
        
        # 清空队列
        while not motor.response_queue.empty():
            try:
                motor.response_queue.get_nowait()
            except:
                break
        
        # 放入测试数据
        for response in test_responses:
            motor.response_queue.put(response)
        
        print(f"  队列大小: {motor.response_queue.qsize()}")
        
        # 测试获取所有电机状态
        start_time = time.time()
        all_status = motor._get_latest_all_motor_status(timeout)
        end_time = time.time()
        
        actual_time = end_time - start_time
        online_count = sum(1 for status in all_status.values() if status)
        
        print(f"  实际耗时: {actual_time*1000:.1f}ms")
        print(f"  获取到状态: {len(all_status)}个电机")
        print(f"  在线电机: {online_count}个")
        
        # 测试获取单个电机状态
        test_motor_id = 5
        start_time = time.time()
        single_status = motor._get_latest_motor_status(test_motor_id, timeout)
        end_time = time.time()
        
        actual_time = end_time - start_time
        print(f"  电机{test_motor_id}状态获取耗时: {actual_time*1000:.1f}ms")
        print(f"  电机{test_motor_id}状态: online={single_status.get('online', False)}")

def test_timeout_behavior():
    """测试timeout行为"""
    print("\n=== 测试timeout行为 ===")
    
    motor = Motor(port='COM4', baudrate=256000)
    
    # 测试空队列的情况
    print("\n1. 测试空队列...")
    
    # 确保队列为空
    while not motor.response_queue.empty():
        try:
            motor.response_queue.get_nowait()
        except:
            break
    
    # 测试短timeout
    start_time = time.time()
    all_status = motor._get_latest_all_motor_status(timeout=0.1)
    end_time = time.time()
    
    actual_time = end_time - start_time
    print(f"  空队列timeout=0.1s，实际耗时: {actual_time*1000:.1f}ms")
    print(f"  返回状态数量: {len(all_status)}")
    
    # 测试长timeout
    start_time = time.time()
    all_status = motor._get_latest_all_motor_status(timeout=0.5)
    end_time = time.time()
    
    actual_time = end_time - start_time
    print(f"  空队列timeout=0.5s，实际耗时: {actual_time*1000:.1f}ms")
    print(f"  返回状态数量: {len(all_status)}")

def test_public_methods_with_timeout():
    """测试公共方法中的timeout参数"""
    print("\n=== 测试公共方法中的timeout参数 ===")
    
    motor = Motor(port='COM4', baudrate=256000)
    
    # 模拟响应数据
    test_responses = []
    for motor_id in range(1, 6):  # 只测试前5个电机
        response = Response(
            type=ResponseType.STATUS_RESPONSE,
            data={
                'motor_id': motor_id,
                'online': True,
                'angle': motor_id * 10.0,
                'fsm_state': 1,
                'error_code': 0,
                'temp': 25.0,
                'bus_voltage': 24.0
            },
            timestamp=time.time(),
            raw_data=b''
        )
        test_responses.append(response)
    
    # 放入测试数据
    for response in test_responses:
        motor.response_queue.put(response)
    
    # 测试get_all_motor_status
    print("\n1. 测试get_all_motor_status...")
    start_time = time.time()
    all_status = motor.get_all_motor_status(sync=False, timeout=0.3)
    end_time = time.time()
    
    actual_time = end_time - start_time
    online_count = sum(1 for status in all_status.values() if status)
    print(f"  耗时: {actual_time*1000:.1f}ms")
    print(f"  在线电机: {online_count}个")
    
    # 测试get_motor_status
    print("\n2. 测试get_motor_status...")
    test_motor_id = 3
    start_time = time.time()
    motor_status = motor.get_motor_status(test_motor_id, sync=False, timeout=0.2)
    end_time = time.time()
    
    actual_time = end_time - start_time
    print(f"  电机{test_motor_id}状态获取耗时: {actual_time*1000:.1f}ms")
    print(f"  电机{test_motor_id}状态: {motor_status}")
    
    # 测试get_motor_angle
    print("\n3. 测试get_motor_angle...")
    start_time = time.time()
    angle = motor.get_motor_angle(test_motor_id, sync=False, timeout=0.2)
    end_time = time.time()
    
    actual_time = end_time - start_time
    print(f"  电机{test_motor_id}角度获取耗时: {actual_time*1000:.1f}ms")
    print(f"  电机{test_motor_id}角度: {angle:.2f}")

if __name__ == "__main__":
    try:
        test_timeout_parameter()
        test_timeout_behavior()
        test_public_methods_with_timeout()
        print("\n=== 所有测试完成 ===")
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc() 