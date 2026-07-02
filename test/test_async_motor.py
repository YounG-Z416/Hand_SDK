#!/usr/bin/env python3
"""
异步Motor类测试文件
演示基于队列的异步通信架构的使用
"""

import time
import threading
from src.hand.hand.gaiahand.motor import Motor, ResponseType, Response

def test_async_motor():
    """测试异步Motor类的基本功能"""
    
    # 创建Motor实例
    motor = Motor(port='COM4', baudrate=256000)
    
    # 定义响应回调函数
    def on_status_response(response: Response):
        """状态响应回调"""
        print(f"[{time.strftime('%H:%M:%S')}] 收到状态响应: {response.data}")
    
    def on_error_response(response: Response):
        """错误响应回调"""
        print(f"[{time.strftime('%H:%M:%S')}] 收到错误响应: {response.data}")
    
    def on_enable_response(response: Response):
        """使能响应回调"""
        print(f"[{time.strftime('%H:%M:%S')}] 收到使能响应: {response.data}")
    
    # 添加响应回调
    motor.add_response_callback(ResponseType.STATUS_RESPONSE, on_status_response)
    motor.add_response_callback(ResponseType.ERROR_RESPONSE, on_error_response)
    motor.add_response_callback(ResponseType.ENABLE_BROADCAST, on_enable_response)
    
    try:
        # 连接到设备
        print("正在连接设备...")
        if motor.connect():
            print("连接成功！")
            
            # 测试1: 使能单个电机
            print("\n=== 测试1: 使能单个电机 ===")
            command_id1 = motor.enable_motor(1, True)
            print(f"发送使能命令: {command_id1}")
            
            # 测试2: 使能所有电机
            print("\n=== 测试2: 使能所有电机 ===")
            command_id2 = motor.enable_all_motors_broadcast(True)
            print(f"发送所有电机使能命令: {command_id2}")
            
            # 测试3: 设置电机角度
            print("\n=== 测试3: 设置电机角度 ===")
            command_id3 = motor.set_motor_angle(1, 1.57, 0.5)  # 90度
            print(f"发送角度设置命令: {command_id3}")
            
            # 测试4: 获取电机状态
            print("\n=== 测试4: 获取电机状态 ===")
            command_id4 = motor.get_motor_status(1)
            print(f"发送状态查询命令: {command_id4}")
            
            # 测试5: 广播设置多个电机角度
            print("\n=== 测试5: 广播设置多个电机角度 ===")
            angles = {1: 45.0, 2: 90.0, 3: 135.0}  # 角度单位为度
            command_id5 = motor.set_motor_angles_broadcast(angles)
            print(f"发送广播角度设置命令: {command_id5}")
            
            # 测试6: 检查队列状态
            print("\n=== 测试6: 检查队列状态 ===")
            queue_status = motor.get_queue_status()
            print(f"队列状态: {queue_status}")
            
            # 等待一段时间让命令执行
            print("\n等待命令执行...")
            time.sleep(5)
            
            # 测试7: 获取响应数据
            print("\n=== 测试7: 获取响应数据 ===")
            for i in range(10):  # 尝试获取10个响应
                response = motor.get_response(timeout=0.5)
                if response:
                    print(f"响应 {i+1}: 类型={response.type.value}, 数据={response.data}")
                else:
                    print(f"响应 {i+1}: 超时")
            
            # 测试8: 使用回调函数
            print("\n=== 测试8: 使用回调函数 ===")
            def custom_callback(response: Response):
                print(f"自定义回调: 收到响应 {response.type.value}")
            
            command_id6 = motor.get_motor_status(2, callback=custom_callback)
            print(f"发送带回调的状态查询命令: {command_id6}")
            
            # 等待回调执行
            time.sleep(2)
            
            # 测试9: 紧急停止
            print("\n=== 测试9: 紧急停止 ===")
            command_id7 = motor.emergency_stop()
            print(f"发送紧急停止命令: {command_id7}")
            
            # 测试10: 失能所有电机
            print("\n=== 测试10: 失能所有电机 ===")
            command_id8 = motor.enable_all_motors_broadcast(False)
            print(f"发送失能命令: {command_id8}")
            
            # 等待命令执行
            time.sleep(3)
            
            # 最终队列状态
            final_queue_status = motor.get_queue_status()
            print(f"\n最终队列状态: {final_queue_status}")
            
        else:
            print("连接失败！")
            
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        
    finally:
        # 断开连接
        print("\n断开连接...")
        motor.disconnect()
        print("测试完成！")

def test_concurrent_commands():
    """测试并发命令发送"""
    
    motor = Motor(port='COM4', baudrate=256000)
    
    def on_response(response: Response):
        print(f"[{time.strftime('%H:%M:%S.%f')[:-3]}] 收到响应: {response.type.value}")
    
    motor.add_response_callback(ResponseType.STATUS_RESPONSE, on_response)
    motor.add_response_callback(ResponseType.ERROR_RESPONSE, on_response)
    
    try:
        if motor.connect():
            print("连接成功，开始并发测试...")
            
            # 创建多个线程同时发送命令
            def send_commands(thread_id: int):
                for i in range(5):
                    try:
                        # 发送状态查询命令
                        command_id = motor.get_motor_status(thread_id + 1)
                        print(f"线程{thread_id} 发送命令 {i+1}: {command_id}")
                        time.sleep(0.1)  # 短暂延时
                    except Exception as e:
                        print(f"线程{thread_id} 发送命令失败: {e}")
            
            # 启动多个线程
            threads = []
            for i in range(3):
                thread = threading.Thread(target=send_commands, args=(i,))
                threads.append(thread)
                thread.start()
            
            # 等待所有线程完成
            for thread in threads:
                thread.join()
            
            print("并发测试完成！")
            
        else:
            print("连接失败！")
            
    except Exception as e:
        print(f"并发测试过程中发生错误: {e}")
        
    finally:
        motor.disconnect()

def test_response_parsing():
    """测试响应数据解析（模拟）"""
    
    motor = Motor(port='COM4', baudrate=256000)
    
    # 模拟响应数据解析
    def simulate_response_parsing():
        """模拟响应数据解析"""
        # 这里应该根据实际协议实现响应数据解析
        # 目前只是示例
        print("响应数据解析功能需要根据实际协议实现")
        print("可以在这里添加帧头检测、数据提取、CRC校验等功能")
    
    try:
        if motor.connect():
            print("连接成功，开始响应解析测试...")
            
            # 发送一些命令
            motor.enable_motor(1, True)
            motor.get_motor_status(1)
            motor.set_motor_angle(1, 1.57, 0.5)
            
            # 等待响应
            time.sleep(3)
            
            # 获取所有响应
            responses = []
            while True:
                response = motor.get_response(timeout=0.1)
                if response:
                    responses.append(response)
                else:
                    break
            
            print(f"收到 {len(responses)} 个响应")
            for i, response in enumerate(responses):
                print(f"响应 {i+1}: 类型={response.type.value}, 时间戳={response.timestamp}")
            
            simulate_response_parsing()
            
        else:
            print("连接失败！")
            
    except Exception as e:
        print(f"响应解析测试过程中发生错误: {e}")
        
    finally:
        motor.disconnect()

if __name__ == "__main__":
    print("=== 异步Motor类测试 ===")
    print("请确保设备已连接并配置正确的串口")
    
    # 选择测试类型
    test_type = input("选择测试类型 (1: 基本功能, 2: 并发测试, 3: 响应解析): ")
    
    if test_type == "1":
        test_async_motor()
    elif test_type == "2":
        test_concurrent_commands()
    elif test_type == "3":
        test_response_parsing()
    else:
        print("无效选择，运行基本功能测试")
        test_async_motor() 