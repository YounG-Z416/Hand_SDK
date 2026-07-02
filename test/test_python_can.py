#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用 python-can 发送 CAN/CANFD 报文的测试脚本

默认发送 CANFD 报文:
- CAN ID: 0x123 (标准ID)
- 数据长度: 12字节 (DLC=9)
- 数据: 11 22 33 44 55 66 77 88 99 AA BB CC
- 仲裁段波特率: 500k
- 数据段波特率: 2M
- BRS: 已启用

SLCAN格式: b1239112233445566778899AABBCC\r
其中:
  b = CANFD + BRS 前缀
  123 = CAN ID (0x123)
  9 = DLC (表示12字节)
  112233445566778899AABBCC = 12字节数据
"""

import can
import sys
import platform
import serial
import time


def send_slcan_raw(channel='COM4', tty_baudrate=115200, 
                   arbitration_bitrate=500000, data_bitrate=2000000,
                   can_id=0x123, data=None):
    """
    直接通过串口发送 SLCAN 原始命令
    
    参数:
        channel: 串口名称（如 'COM4' 或 '/dev/ttyUSB0'）
        tty_baudrate: 串口波特率（默认 115200）
        arbitration_bitrate: CAN 仲裁段波特率（默认 500000）
        data_bitrate: CANFD 数据段波特率（默认 2000000）
        can_id: CAN ID（默认 0x123）
        data: 数据字节列表（默认 12字节测试数据）
    """
    if data is None:
        data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC]
    
    # 波特率映射到SLCAN命令
    # SLCAN 仲裁段波特率命令: S0=10k, S1=20k, S2=50k, S3=100k, S4=125k, S5=250k, S6=500k, S7=800k, S8=1M
    abit_map = {
        10000: '0', 20000: '1', 50000: '2', 100000: '3',
        125000: '4', 250000: '5', 500000: '6', 800000: '7', 1000000: '8'
    }
    abit_cmd = abit_map.get(arbitration_bitrate, '6')  # 默认500k
    
    # SLCAN 数据段波特率命令: Y0=500k, Y1=1M, Y2=2M, Y3=4M, Y4=5M, Y5=8M
    dbit_map = {
        500000: '0', 1000000: '1', 2000000: '2', 4000000: '3',
        5000000: '4', 8000000: '5'
    }
    dbit_cmd = dbit_map.get(data_bitrate, '2')  # 默认2M
    
    # 计算DLC
    dlc = len(data)
    if dlc <= 8:
        dlc_code = str(dlc)
    elif dlc == 12:
        dlc_code = '9'
    elif dlc == 16:
        dlc_code = 'A'
    elif dlc == 20:
        dlc_code = 'B'
    elif dlc == 24:
        dlc_code = 'C'
    elif dlc == 32:
        dlc_code = 'D'
    elif dlc == 48:
        dlc_code = 'E'
    elif dlc == 64:
        dlc_code = 'F'
    else:
        dlc_code = str(dlc)
    
    try:
        # 打开串口
        ser = serial.Serial(
            port=channel,
            baudrate=tty_baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        
        print(f"已打开串口: {channel}, 波特率: {tty_baudrate}")
        time.sleep(0.1)  # 等待串口稳定
        
        # 1. 设置仲裁段波特率: S6\r
        cmd = f'S{abit_cmd}\r'
        cmd_bytes = cmd.encode('ascii')
        ser.write(cmd_bytes)
        hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
        print(f"发送: {hex_str} ({cmd.strip()})")
        time.sleep(0.05)
        
        # 2. 设置数据段波特率: Y2\r
        cmd = f'Y{dbit_cmd}\r'
        cmd_bytes = cmd.encode('ascii')
        ser.write(cmd_bytes)
        hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
        print(f"发送: {hex_str} ({cmd.strip()})")
        time.sleep(0.05)
        
        # 3. 打开通道: O\r
        cmd = 'O\r'
        cmd_bytes = cmd.encode('ascii')
        ser.write(cmd_bytes)
        hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
        print(f"发送: {hex_str} ({cmd.strip()})")
        time.sleep(0.05)
        
        # 4. 发送CANFD报文: b1239112233445566778899AABBCC\r
        can_id_str = f'{can_id:03X}'
        data_str = ''.join(f'{b:02X}' for b in data)
        cmd = f'b{can_id_str}{dlc_code}{data_str}\r'
        cmd_bytes = cmd.encode('ascii')
        ser.write(cmd_bytes)
        hex_str = ' '.join(f'{b:02X}' for b in cmd_bytes)
        print(f"发送: {hex_str} ({cmd.strip()})")
        print(f"\n✓ SLCAN 命令发送成功!")
        print(f"  串口: {channel}")
        print(f"  CAN ID: 0x{can_id:03X}")
        print(f"  数据: {[hex(b) for b in data]}")
        print(f"  数据长度: {len(data)} 字节 (DLC={dlc_code})")
        print(f"  仲裁段波特率: {arbitration_bitrate} bps (S{abit_cmd})")
        print(f"  数据段波特率: {data_bitrate} bps (Y{dbit_cmd})")
        
        time.sleep(0.1)
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n✗ 串口错误: {e}")
        print("\n提示: 请确保:")
        print("  1. 串口名称正确（如 COM4 或 /dev/ttyUSB0）")
        print("  2. 串口未被其他程序占用")
        print("  3. 已安装 pyserial: pip install pyserial")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def send_can_message(interface='slcan', channel=None, bitrate=1000000, data_bitrate=None, 
                    tty_baudrate=115200, use_canfd=False, use_raw_slcan=False):
    """
    发送 CAN 或 CANFD 报文
    
    参数:
        interface: CAN 接口类型
            - 'virtual': 虚拟接口（用于测试，不需要硬件）
            - 'slcan': SLCAN 接口（通过串口连接，Windows/Linux 都支持）
            - 'pcan': Peak CAN 设备
            - 'vector': Vector CAN 设备
            - 'ixxat': IXXAT 设备
            - 'kvaser': Kvaser 设备
            - 'socketcan': Linux SocketCAN（仅 Linux）
        channel: 通道名称或编号（根据接口类型而定）
            - slcan: 串口名称（如 'COM4' 或 '/dev/ttyUSB0'，可带 @波特率 后缀）
        bitrate: CAN 仲裁域波特率（默认 1Mbps）
        data_bitrate: CANFD 数据域波特率（默认 None，使用 CAN 模式；设置后启用 CANFD）
        tty_baudrate: 串口波特率（仅用于 slcan，默认 115200）
        use_canfd: 是否使用 CANFD 模式（默认 False，使用 CAN 模式）
        use_raw_slcan: 是否使用原始SLCAN命令（直接通过串口发送ASCII命令，默认 False）
    """
    
    # 如果使用原始SLCAN命令，直接发送并返回
    if use_raw_slcan and interface == 'slcan':
        if not channel:
            if platform.system() == "Windows":
                channel = 'COM4'
            else:
                channel = '/dev/ttyUSB0'
        
        # CANFD 报文配置
        can_id = 0x123
        data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC]
        
        send_slcan_raw(channel, tty_baudrate, bitrate, data_bitrate or (bitrate * 2), can_id, data)
        return
    
    # CANFD 报文配置
    # CAN ID: 0x123 (标准ID)
    can_id = 0x123
    
    # Data: 12字节数据 (DLC=9 表示12字节)
    # 数据: 11 22 33 44 55 66 77 88 99 AA BB CC
    data = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC]
    
    # 判断是否使用 CANFD 模式
    # 如果设置了 data_bitrate 或 use_canfd=True，则使用 CANFD
    # 默认使用 CANFD 模式发送12字节数据
    if data_bitrate is not None or use_canfd or len(data) > 8:
        if data_bitrate is None:
            data_bitrate = bitrate * 2  # 默认数据域波特率为仲裁域的 2 倍
        canfd_mode = True
        print(f"使用 CANFD 模式 - 仲裁域波特率: {bitrate} bps, 数据域波特率: {data_bitrate} bps")
    else:
        canfd_mode = False
        print(f"使用 CAN 模式 - 波特率: {bitrate} bps")
    
    # 根据接口类型配置总线参数
    bus_config = {}
    
    if interface == 'virtual':
        # 虚拟接口，用于测试，不需要硬件（支持 CANFD）
        bus_config = {
            'interface': 'virtual',
            'channel': channel or 'virtual_channel'
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
        print("使用虚拟接口（virtual）- 仅用于测试，不会发送到真实硬件")
    elif interface == 'slcan':
        # SLCAN 接口（通过串口连接 CAN 设备，Windows/Linux 都支持）
        # channel 可以是串口名称，如 'COM4' 或 '/dev/ttyUSB0'
        # 也可以在 channel 中指定串口波特率，如 'COM4@115200'
        if not channel:
            if platform.system() == "Windows":
                channel = 'COM4'  # Windows 默认串口
            else:
                channel = '/dev/ttyUSB0'  # Linux 默认串口
        
        bus_config = {
            'interface': 'slcan',
            'channel': channel,
            'tty_baudrate': tty_baudrate,  # 串口波特率
            'bitrate': bitrate  # CAN 仲裁域波特率
        }
        # SLCAN 支持 CANFD，但需要设备固件支持
        if canfd_mode:
            bus_config['data_bitrate'] = data_bitrate
        print(f"使用 SLCAN 接口 - 串口: {channel}, 串口波特率: {tty_baudrate}")
    elif interface == 'pcan':
        # Peak CAN 设备（支持 CANFD）
        bus_config = {
            'interface': 'pcan',
            'channel': channel or 'PCAN_USBBUS1',
            'bitrate': bitrate
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
    elif interface == 'vector':
        # Vector CAN 设备（支持 CANFD）
        bus_config = {
            'interface': 'vector',
            'app_name': 'PythonCAN',
            'channel': channel or 0,
            'bitrate': bitrate
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
    elif interface == 'ixxat':
        # IXXAT 设备（支持 CANFD）
        bus_config = {
            'interface': 'ixxat',
            'channel': channel or 0,
            'bitrate': bitrate
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
    elif interface == 'kvaser':
        # Kvaser 设备（支持 CANFD）
        bus_config = {
            'interface': 'kvaser',
            'channel': channel or 0,
            'bitrate': bitrate
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
    elif interface == 'socketcan':
        # Linux SocketCAN（仅 Linux 系统，支持 CANFD）
        if platform.system() == "Windows":
            print(f"\n✗ 错误: socketcan 接口仅在 Linux 系统上可用")
            print(f"当前系统: {platform.system()}")
            print("\nWindows 系统可用的接口:")
            print("  - virtual: 虚拟接口（测试用）")
            print("  - slcan: SLCAN 接口（通过串口）")
            print("  - pcan: Peak CAN 设备")
            print("  - vector: Vector CAN 设备")
            print("  - ixxat: IXXAT 设备")
            print("  - kvaser: Kvaser 设备")
            print("\n建议使用虚拟接口进行测试:")
            print("  python test_python_can.py virtual")
            return
        bus_config = {
            'interface': 'socketcan',
            'channel': channel or 'can0',
            'bitrate': bitrate
        }
        if canfd_mode:
            bus_config['fd'] = True
            bus_config['data_bitrate'] = data_bitrate
    else:
        print(f"不支持的接口类型: {interface}")
        if platform.system() == "Windows":
            print("Windows 支持的接口: virtual, slcan, pcan, vector, ixxat, kvaser")
        else:
            print("支持的接口: virtual, slcan, pcan, vector, ixxat, kvaser, socketcan")
        return
    
    try:
        print(f"正在创建 CAN 总线...")
        print(f"  接口类型: {interface}")
        print(f"  通道: {bus_config.get('channel', 'N/A')}")
        if canfd_mode:
            print(f"  仲裁域波特率: {bitrate} bps")
            print(f"  数据域波特率: {data_bitrate} bps")
        else:
            print(f"  波特率: {bitrate} bps")
        
        with can.Bus(**bus_config) as bus:
            # 创建 CAN 或 CANFD 消息
            # 使用标准 ID (11位)，如果需要扩展 ID (29位)，设置 is_extended_id=True
            msg = can.Message(
                arbitration_id=can_id,
                data=data,
                is_extended_id=False,  # 标准 ID，如果 ID 是 29 位则设为 True
                is_fd=canfd_mode,  # 是否使用 CANFD 格式
                bitrate_switch=canfd_mode  # CANFD 数据域是否使用更高的波特率 (BRS)
            )
            
            # 发送消息
            bus.send(msg)
            protocol_name = "CANFD" if canfd_mode else "CAN"
            print(f"\n✓ {protocol_name} 消息发送成功!")
            print(f"  总线信息: {bus.channel_info}")
            print(f"  CAN ID: 0x{can_id:03X} (标准 ID)")
            print(f"  数据: {[hex(b) for b in data]}")
            print(f"  数据长度: {len(data)} 字节")
            if canfd_mode:
                print(f"  协议: CANFD (仲裁域: {bitrate} bps, 数据域: {data_bitrate} bps)")
                print(f"  BRS: 已启用 (Bit Rate Switch)")
                # DLC 映射: 9 = 12字节, 10 = 16字节, 11 = 20字节, 12 = 24字节, 13 = 32字节, 14 = 48字节, 15 = 64字节
                dlc = len(data)
                if dlc <= 8:
                    dlc_code = dlc
                elif dlc == 12:
                    dlc_code = 9
                elif dlc == 16:
                    dlc_code = 10
                elif dlc == 20:
                    dlc_code = 11
                elif dlc == 24:
                    dlc_code = 12
                elif dlc == 32:
                    dlc_code = 13
                elif dlc == 48:
                    dlc_code = 14
                elif dlc == 64:
                    dlc_code = 15
                else:
                    dlc_code = len(data)
                print(f"  DLC: {dlc_code} (数据长度: {len(data)} 字节)")
                print(f"  SLCAN格式: b{can_id:03X}{dlc_code}{''.join(f'{b:02X}' for b in data)}\\r")
            else:
                print(f"  协议: CAN ({bitrate} bps)")
            
    except can.CanError as e:
        print(f"\n✗ CAN 消息发送失败: {e}")
        print("\n提示: 请确保:")
        print("  1. CAN 设备已正确连接")
        print("  2. 已安装相应的 python-can 接口驱动")
        print("  3. 设备驱动已正确安装")
        print("  4. 通道和波特率配置正确")
        print("\n常见接口的安装方法:")
        print("  - slcan: 需要安装 pyserial (pip install pyserial)，支持 Windows/Linux")
        print("  - pcan: 需要安装 PCAN 驱动")
        print("  - vector: 需要安装 Vector 驱动和 XL Driver Library")
        print("  - ixxat: 需要安装 IXXAT VCI SDK")
        print("  - kvaser: 需要安装 Kvaser CANLib SDK")
        print("\n如果只是想测试代码，可以使用虚拟接口:")
        print("  python test_python_can.py virtual")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 从命令行参数获取接口类型，默认为虚拟接口
    if len(sys.argv) > 1:
        interface = sys.argv[1]
        channel = sys.argv[2] if len(sys.argv) > 2 else None
        bitrate = int(sys.argv[3]) if len(sys.argv) > 3 else 1000000
        tty_baudrate = int(sys.argv[4]) if len(sys.argv) > 4 else 115200
        # 第5个参数：数据域波特率（如果设置则启用 CANFD）
        data_bitrate = int(sys.argv[5]) if len(sys.argv) > 5 else None
        # 第6个参数：是否强制使用 CANFD（--canfd 标志）
        use_canfd = '--canfd' in sys.argv or data_bitrate is not None
        # 是否使用原始SLCAN命令（--raw 标志）
        use_raw_slcan = '--raw' in sys.argv
        
        # 检查：如果通道名称看起来像串口（COM* 或 /dev/tty*），但接口不是 slcan，给出提示
        if channel:
            is_serial_port = (channel.upper().startswith('COM') or 
                            channel.startswith('/dev/tty') or 
                            channel.startswith('/dev/cu'))
            if is_serial_port and interface != 'slcan':
                print(f"\n⚠ 警告: 检测到串口名称 '{channel}'，但接口类型是 '{interface}'")
                print(f"  串口设备应使用 'slcan' 接口")
                print(f"  建议使用: python test_python_can.py slcan {channel} {bitrate} {tty_baudrate} {data_bitrate or ''}")
                print(f"  或者添加 --raw 参数使用原始SLCAN命令: python test_python_can.py slcan {channel} {bitrate} {tty_baudrate} {data_bitrate or ''} --raw")
                print()
    else:
        # 默认使用 slcan 接口，发送 CANFD 报文
        interface = 'slcan'
        channel = None
        bitrate = 500000  # 仲裁段 500k
        tty_baudrate = 115200
        data_bitrate = 2000000  # 数据段 2M
        use_canfd = True
        use_raw_slcan = False  # 默认使用python-can接口
    
    print("=" * 60)
    print("python-can CAN/CANFD 报文发送测试")
    print("=" * 60)
    print(f"当前系统: {platform.system()}")
    print(f"\n使用方法:")
    print(f"  python test_python_can.py [接口类型] [通道] [仲裁域波特率] [串口波特率] [数据域波特率] [--canfd] [--raw]")
    print(f"\nCAN 模式示例:")
    print(f"  python test_python_can.py virtual                    # 虚拟接口（测试用）")
    print(f"  python test_python_can.py slcan COM4 1000000 115200  # Windows SLCAN (串口COM4)")
    print(f"  python test_python_can.py slcan /dev/ttyUSB0 1000000 115200  # Linux SLCAN")
    print(f"  python test_python_can.py pcan PCAN_USBBUS1 1000000  # Peak CAN")
    print(f"  python test_python_can.py vector 0 1000000            # Vector CAN")
    print(f"\nCANFD 模式示例:")
    print(f"  python test_python_can.py slcan COM4 500000 115200 2000000 --raw  # 原始SLCAN命令 (直接发送ASCII)")
    print(f"  python test_python_can.py slcan COM4 500000 115200 2000000  # SLCAN CANFD (使用python-can)")
    print(f"  python test_python_can.py slcan COM4 1000000 115200 2000000  # SLCAN CANFD (默认配置)")
    print(f"  python test_python_can.py pcan PCAN_USBBUS1 1000000 0 2000000  # Peak CANFD")
    print(f"  python test_python_can.py vector 0 1000000 0 2000000  # Vector CANFD")
    if platform.system() != "Windows":
        print(f"  python test_python_can.py socketcan can0 1000000 0 2000000  # Linux SocketCAN CANFD")
    print(f"\n默认配置 (无参数运行):")
    print(f"  python test_python_can.py")
    print(f"  将发送: CANFD ID=0x123, 12字节数据, 仲裁段500k, 数据段2M, 开启BRS")
    print(f"  对应SLCAN格式: b1239112233445566778899AABBCC\\r")
    print("\n参数说明:")
    print("  - 第3个参数: CAN 仲裁域波特率（默认 1000000 bps）")
    print("  - 第4个参数: 串口波特率（仅用于 slcan，默认 115200）")
    print("  - 第5个参数: CANFD 数据域波特率（设置后启用 CANFD 模式）")
    print("  - --canfd: 强制使用 CANFD 模式（数据域波特率默认为仲裁域的 2 倍）")
    print("  - --raw: 使用原始SLCAN命令（直接通过串口发送ASCII命令，仅用于slcan接口）")
    print("\nSLCAN 说明:")
    print("  - channel 可以是串口名称，如 'COM4' 或 '/dev/ttyUSB0'")
    print("  - 也可以在 channel 中指定串口波特率，如 'COM4@115200'")
    print("=" * 60)
    print()
    
    send_can_message(interface, channel, bitrate, data_bitrate, tty_baudrate, use_canfd, use_raw_slcan)
