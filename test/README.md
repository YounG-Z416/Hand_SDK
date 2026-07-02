<!--
 * @File name: 
 * @Descripttion: 
 * @Author: tanzhiqiang
 * @Email: zhiqiangtan89@gmail.com
 * @Version: 
 * @Date: 2025-06-21 10:31:50
 * @History: 
-->
# 测试文件

这个文件夹包含了各种测试脚本和测试相关文档：

## 文件说明

### 测试脚本
- `test_hand_integration.py` - 手部集成功能测试
- `test_pantheonhand_connection.py` - PantheonHand连接功能测试
- `test_gaia_sdk.py` - Gaia SDK功能测试
- `test_urdf_viewer.py` - URDF查看器测试
- `test_load_urdf.py` - URDF加载测试
- `read_hand.py` - 手部数据读取测试
- `read_urdfpy.py` - URDF解析测试

### 测试文档
- `PANTHEONHAND_CONNECTION_IMPROVEMENTS.md` - PantheonHand连接改进说明

### 测试资源
- `simple_box.urdf` - 简单盒子URDF文件
- `robot.urdf` - 机器人URDF文件

## 运行测试

### 手部集成测试
```bash
cd test
python test_hand_integration.py
```

### PantheonHand连接测试
```bash
cd test
python test_pantheonhand_connection.py
```

### Gaia SDK测试
```bash
cd test
python test_gaia_sdk.py
```

## 注意事项

- 某些测试可能需要实际硬件才能正常运行
- 测试文件会自动添加项目根目录到Python路径，无需手动设置
- 建议在运行测试前确保所有依赖包已正确安装 