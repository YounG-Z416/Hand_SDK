#!/usr/bin/env python3
"""
URDF Viewer Test using yourdfpy
使用 yourdfpy 库测试 URDF 模型加载和显示
"""

import sys
import os
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QSlider, QScrollArea,
                            QGroupBox, QFormLayout, QFileDialog)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import yourdfpy
import trimesh
from trimesh.visual import ColorVisuals

class URDFGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.urdf = None
        self.meshes = {}  # 存储加载的网格
        self.rotation_x = -45  # 初始旋转角度
        self.rotation_y = 45
        self.rotation_z = 0    # Z轴旋转角度
        self.zoom = 2.0
        self.last_pos = None
        self.urdf_dir = None  # 存储 URDF 文件所在目录
        self.display_lists = {}  # 存储显示列表
        self.needs_update = True  # 标记是否需要更新显示列表
        self.transform_cache = {}  # 缓存变换矩阵
        self.joint_transforms = {}  # 存储关节变换
        self.link_tree = {}  # 存储连杆树结构
        self.dirty_links = set()  # 标记需要更新的连杆
        self.translation_x = 0.0  # 添加平移变量
        self.translation_y = 0.0
        
    def initializeGL(self):
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, (1.0, 1.0, 1.0, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # 启用双缓冲
        self.setAutoBufferSwap(True)
        
    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置相机位置
        gluLookAt(0, 0, 5 * self.zoom,
                  0, 0, 0,
                  0, 1, 0)
        
        # 应用平移
        glTranslatef(self.translation_x * self.zoom, self.translation_y * self.zoom, 0)
        
        # 应用旋转（先Y轴，再X轴，最后Z轴）
        glRotatef(self.rotation_y, 0, 1, 0)  # Y轴旋转
        glRotatef(self.rotation_x, 1, 0, 0)  # X轴旋转
        glRotatef(self.rotation_z, 0, 0, 1)  # Z轴旋转
        
        if self.urdf:
            if self.needs_update:
                self.update_display_lists()
                self.needs_update = False
            self.draw_urdf()
        else:
            self.draw_axes()
    
    def update_display_lists(self):
        """更新显示列表"""
        # 清除旧的显示列表
        for display_list in self.display_lists.values():
            glDeleteLists(display_list, 1)
        self.display_lists.clear()
        
        if not self.urdf:
            return
            
        # 为每个连杆创建显示列表
        for link_name, link in self.urdf.link_map.items():
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE)
            
            # 绘制连杆的视觉元素
            if hasattr(link, 'visuals'):
                for visual in link.visuals:
                    self.draw_visual(visual)
            
            glEndList()
            self.display_lists[link_name] = display_list
    
    def draw_urdf(self):
        """绘制 URDF 模型"""
        if not self.urdf:
            return
            
        # 如果有需要更新的连杆，只更新这些连杆的变换
        if self.dirty_links:
            self._update_dirty_transforms()
            
        # 遍历所有连杆
        for link_name, link in self.urdf.link_map.items():
            try:
                # 获取连杆的变换矩阵
                transform = self.transform_cache.get(link_name)
                if transform is None:
                    continue
                    
                # 保存当前矩阵
                glPushMatrix()
                
                # 应用变换
                glMultMatrixf(transform.T)
                
                # 使用显示列表绘制
                if link_name in self.display_lists:
                    glCallList(self.display_lists[link_name])
                
                # 恢复矩阵
                glPopMatrix()
            except Exception as e:
                print(f"Error drawing link {link_name}: {str(e)}")
    
    def _build_link_tree(self):
        """构建连杆树结构"""
        self.link_tree.clear()
        if not self.urdf:
            return
            
        # 初始化所有连杆
        for link_name in self.urdf.link_map:
            self.link_tree[link_name] = {'parent': None, 'children': []}
            
        # 建立父子关系
        for joint_name, joint in self.urdf.joint_map.items():
            parent = joint.parent
            child = joint.child
            if parent in self.link_tree and child in self.link_tree:
                self.link_tree[parent]['children'].append(child)
                self.link_tree[child]['parent'] = parent
    
    def _update_dirty_transforms(self):
        """更新需要更新的连杆的变换"""
        if not self.urdf or not self.dirty_links:
            return
            
        # 获取根连杆
        root_link = next(iter(self.urdf.link_map.values()))
        root_name = root_link.name
        
        # 从根连杆开始更新变换
        self._update_link_transform(root_name, np.eye(4))
        
        # 清除脏标记
        self.dirty_links.clear()
    
    def _update_link_transform(self, link_name, parent_transform):
        """更新连杆的变换矩阵"""
        # 应用当前连杆的变换
        current_transform = parent_transform
        self.transform_cache[link_name] = current_transform
        
        # 更新子连杆
        for child in self.link_tree[link_name]['children']:
            # 查找连接当前连杆和子连杆的关节
            joint = next((j for j in self.urdf.joint_map.values() 
                         if j.parent == link_name and j.child == child), None)
            if joint:
                # 获取关节变换
                joint_transform = self.joint_transforms.get(joint.name, joint.origin)
                
                # 计算子连杆的变换
                child_transform = np.dot(current_transform, joint_transform)
                
                # 递归更新子连杆
                self._update_link_transform(child, child_transform)
    
    def update_joint_transform(self, joint_name, transform):
        """更新关节变换"""
        if not self.urdf or joint_name not in self.urdf.joint_map:
            return
            
        # 更新关节变换
        self.joint_transforms[joint_name] = transform
        
        # 标记需要更新的连杆
        joint = self.urdf.joint_map[joint_name]
        self.dirty_links.add(joint.child)
        
        # 标记所有子连杆为脏
        self._mark_children_dirty(joint.child)
        
        # 请求重绘
        self.update()
    
    def _mark_children_dirty(self, link_name):
        """标记所有子连杆为脏"""
        for child in self.link_tree[link_name]['children']:
            self.dirty_links.add(child)
            self._mark_children_dirty(child)
    
    def load_urdf(self, urdf):
        """加载 URDF 模型"""
        self.urdf = urdf
        self.joint_transforms.clear()
        self.transform_cache.clear()
        self.dirty_links.clear()
        self._build_link_tree()
        
        # 初始化所有关节的变换矩阵
        for joint_name, joint in self.urdf.joint_map.items():
            if hasattr(joint, 'origin'):
                self.joint_transforms[joint_name] = joint.origin
            else:
                self.joint_transforms[joint_name] = np.eye(4)
        
        # 标记所有连杆为脏，强制更新所有变换
        self.dirty_links.update(self.urdf.link_map.keys())
        self._update_dirty_transforms()
        
        self.needs_update = True
        self.update()
    
    def draw_visual(self, visual):
        """绘制视觉元素"""
        if not hasattr(visual, 'geometry'):
            return
            
        geometry = visual.geometry
        
        # 设置材质颜色
        if (hasattr(visual, 'material') and 
            visual.material is not None and 
            hasattr(visual.material, 'color') and 
            visual.material.color is not None):
            color = visual.material.color.rgba
            glColor4f(*color)
        else:
            glColor4f(0.8, 0.8, 0.8, 1.0)
        
        # 绘制几何体
        if hasattr(geometry, 'box') and geometry.box is not None:
            self.draw_box(geometry.box.size)
        elif hasattr(geometry, 'cylinder') and geometry.cylinder is not None:
            self.draw_cylinder(geometry.cylinder.radius, geometry.cylinder.length)
        elif hasattr(geometry, 'sphere') and geometry.sphere is not None:
            self.draw_sphere(geometry.sphere.radius)
        elif hasattr(geometry, 'mesh') and geometry.mesh is not None:
            self.draw_mesh(geometry.mesh.filename)
    
    def draw_box(self, size):
        """绘制盒子"""
        x, y, z = size / 2.0
        glBegin(GL_QUADS)
        # 前面
        glNormal3f(0, 0, 1)
        glVertex3f(-x, -y, z)
        glVertex3f(x, -y, z)
        glVertex3f(x, y, z)
        glVertex3f(-x, y, z)
        # 后面
        glNormal3f(0, 0, -1)
        glVertex3f(-x, -y, -z)
        glVertex3f(-x, y, -z)
        glVertex3f(x, y, -z)
        glVertex3f(x, -y, -z)
        # 上面
        glNormal3f(0, 1, 0)
        glVertex3f(-x, y, -z)
        glVertex3f(-x, y, z)
        glVertex3f(x, y, z)
        glVertex3f(x, y, -z)
        # 下面
        glNormal3f(0, -1, 0)
        glVertex3f(-x, -y, -z)
        glVertex3f(x, -y, -z)
        glVertex3f(x, -y, z)
        glVertex3f(-x, -y, z)
        # 右面
        glNormal3f(1, 0, 0)
        glVertex3f(x, -y, -z)
        glVertex3f(x, y, -z)
        glVertex3f(x, y, z)
        glVertex3f(x, -y, z)
        # 左面
        glNormal3f(-1, 0, 0)
        glVertex3f(-x, -y, -z)
        glVertex3f(-x, -y, z)
        glVertex3f(-x, y, z)
        glVertex3f(-x, y, -z)
        glEnd()
    
    def draw_cylinder(self, radius, length):
        """绘制圆柱体"""
        slices = 32
        stacks = 1
        
        # 绘制圆柱体侧面
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, radius, radius, length, slices, stacks)
        gluDeleteQuadric(quad)
        glPopMatrix()
        
        # 绘制圆柱体端面
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        quad = gluNewQuadric()
        gluDisk(quad, 0, radius, slices, 1)
        glTranslatef(0, 0, length)
        gluDisk(quad, 0, radius, slices, 1)
        gluDeleteQuadric(quad)
        glPopMatrix()
    
    def draw_sphere(self, radius):
        """绘制球体"""
        quad = gluNewQuadric()
        gluSphere(quad, radius, 32, 32)
        gluDeleteQuadric(quad)
    
    def draw_mesh(self, filename):
        """绘制网格"""
        if not filename:
            return
            
        # 处理ROS package格式的路径
        if filename.startswith('package://'):
            # 移除 'package://' 前缀
            relative_path = filename[10:]  # 移除 'package://'
            # 将正斜杠转换为反斜杠
            relative_path = relative_path.replace('/', os.sep)
            # 构建完整的网格文件路径
            if self.urdf_dir:
                # 获取URDF文件所在目录的父目录
                parent_dir = os.path.dirname(self.urdf_dir)
                # 从relative_path中移除包名（第一个目录）
                path_parts = relative_path.split(os.sep)
                if len(path_parts) > 1:
                    relative_path = os.sep.join(path_parts[1:])
                mesh_path = os.path.join(parent_dir, relative_path)
            else:
                mesh_path = relative_path
        else:
            # 构建完整的网格文件路径
            if self.urdf_dir:
                mesh_path = os.path.join(self.urdf_dir, filename)
            else:
                mesh_path = filename
            
        # 检查文件是否存在
        if not os.path.exists(mesh_path):
            print(f"Warning: Mesh file not found: {mesh_path}")
            # 如果找不到网格文件，绘制一个简单的盒子作为替代
            self.draw_box(np.array([0.1, 0.1, 0.1]))
            return
            
        if mesh_path not in self.meshes:
            try:
                print(f"Loading mesh: {mesh_path}")
                # 加载网格
                mesh = trimesh.load(mesh_path)
                
                # 优化网格
                if hasattr(mesh, 'process'):
                    # 合并重复顶点
                    mesh.process(validate=True)
                    # 移除重复面（使用新的API）
                    mesh.update_faces(mesh.unique_faces())
                    # 移除零面积面（使用新的API）
                    mesh.update_faces(mesh.nondegenerate_faces())
                    # 移除未使用的顶点
                    mesh.remove_unreferenced_vertices()
                
                # 计算法线（如果不存在）
                if not hasattr(mesh, 'vertex_normals'):
                    mesh.fix_normals()
                
                # 存储优化后的网格
                self.meshes[mesh_path] = mesh
                print(f"Mesh loaded successfully: {mesh_path}")
            except Exception as e:
                print(f"Error loading mesh {mesh_path}: {str(e)}")
                # 如果加载失败，绘制一个简单的盒子作为替代
                self.draw_box(np.array([0.1, 0.1, 0.1]))
                return
        
        # 绘制网格
        mesh = self.meshes[mesh_path]
        vertices = mesh.vertices
        faces = mesh.faces
        normals = mesh.vertex_normals if hasattr(mesh, 'vertex_normals') else None
        
        # 使用顶点数组来优化绘制
        glBegin(GL_TRIANGLES)
        for face in faces:
            for vertex_id in face:
                if normals is not None:
                    glNormal3fv(normals[vertex_id])
                glVertex3fv(vertices[vertex_id])
        glEnd()
    
    def __del__(self):
        """清理资源"""
        self.meshes.clear()
    
    def mousePressEvent(self, event):
        self.last_pos = event.pos()
        # 打印鼠标按键信息以便调试
        if event.button() == Qt.RightButton:
            print("Right button pressed")
            self.setMouseTracking(True)
        elif event.button() == Qt.MiddleButton:
            print("Middle button pressed")
            self.setMouseTracking(True)
    
    def mouseMoveEvent(self, event):
        if not self.last_pos:
            return
            
        # 打印当前按下的鼠标按键
        buttons = []
        if event.buttons() & Qt.LeftButton:
            buttons.append("Left")
        if event.buttons() & Qt.RightButton:
            buttons.append("Right")
        if event.buttons() & Qt.MiddleButton:
            buttons.append("Middle")
        print(f"Mouse buttons pressed: {', '.join(buttons)}")
            
        if event.buttons() & Qt.LeftButton:
            # 左键旋转X和Y轴
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
            self.last_pos = event.pos()
            self.update()
        elif event.buttons() & Qt.RightButton:
            # 右键旋转Z轴
            dx = event.x() - self.last_pos.x()
            print(f"Right button drag: dx={dx}")
            self.rotation_z += dx * 0.5
            self.last_pos = event.pos()
            self.update()
        elif event.buttons() & Qt.MiddleButton:
            # 中键平移
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            # 调整平移速度
            scale = 0.02  # 增加平移速度
            self.translation_x += dx * scale
            self.translation_y -= dy * scale  # 注意y轴方向是反的
            self.last_pos = event.pos()
            self.update()
            print(f"Middle drag: dx={dx}, dy={dy}, trans_x={self.translation_x}, trans_y={self.translation_y}")
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            print("Right button released")
            self.setMouseTracking(False)
        elif event.button() == Qt.MiddleButton:
            print("Middle button released")
            self.setMouseTracking(False)
        self.last_pos = None
    
    def wheelEvent(self, event):
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15
        self.zoom -= num_steps * 0.1
        if self.zoom < 0.1:
            self.zoom = 0.1
        self.update()

    def draw_axes(self):
        """绘制坐标轴"""
        glPushAttrib(GL_CURRENT_BIT)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        # X轴 (红色)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, 0.0)
        # Y轴 (绿色)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 1.0, 0.0)
        # Z轴 (蓝色)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 1.0)
        glEnd()
        glPopAttrib()

class URDFViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.urdf = None
        self.current_joint_values = {}
        self.update_timer = None  # 用于控制更新频率
        
        # 创建主布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        
        # 创建左侧控制面板
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        control_panel.setMinimumWidth(300)  # 设置最小宽度
        control_panel.setMaximumWidth(400)  # 设置最大宽度
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        control_layout.addWidget(self.status_label)
        
        # 添加加载按钮
        self.load_button = QPushButton("加载 URDF")
        self.load_button.clicked.connect(self.load_urdf)
        control_layout.addWidget(self.load_button)
        
        # 创建关节控制区域
        self.joint_control_group = QGroupBox("关节控制")
        self.joint_control_layout = QVBoxLayout()  # 改用垂直布局
        self.joint_control_group.setLayout(self.joint_control_layout)
        control_layout.addWidget(self.joint_control_group)
        
        # 添加控制面板到主布局
        main_layout.addWidget(control_panel)
        
        # 创建 OpenGL 显示组件
        self.gl_widget = URDFGLWidget()
        main_layout.addWidget(self.gl_widget)
        
    def create_joint_controls(self):
        """创建关节控制滑块"""
        # 清除现有的控制
        while self.joint_control_layout.count():
            item = self.joint_control_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 为每个可移动关节创建控制
        for joint_name, joint in self.urdf.joint_map.items():
            if joint.type != 'fixed':  # 只处理非固定关节
                # 获取关节限制
                if hasattr(joint, 'limit'):
                    lower = np.degrees(joint.limit.lower)
                    upper = np.degrees(joint.limit.upper)
                else:
                    lower = -180
                    upper = 180
                
                # 创建关节控制组
                joint_group = QGroupBox(joint_name)
                joint_layout = QVBoxLayout()
                joint_group.setLayout(joint_layout)
                
                # 创建滑块
                slider = QSlider(Qt.Horizontal)
                slider.setRange(int(lower * 10), int(upper * 10))  # 放大10倍以提高精度
                slider.setValue(0)
                slider.setTickPosition(QSlider.TicksBelow)
                slider.setTickInterval(int((upper - lower) / 4))  # 设置刻度间隔
                slider.setMinimumHeight(30)  # 设置最小高度
                
                # 创建值标签
                value_label = QLabel("0.0°")
                value_label.setAlignment(Qt.AlignCenter)  # 居中对齐
                
                # 添加到关节布局
                joint_layout.addWidget(slider)
                joint_layout.addWidget(value_label)
                
                # 添加到主布局
                self.joint_control_layout.addWidget(joint_group)
                
                # 连接信号
                def create_slider_callback(joint_name, value_label):
                    def callback(value):
                        # 将值转换回实际角度
                        actual_value = value / 10.0
                        value_label.setText(f"{actual_value:.1f}°")
                        self.schedule_joint_update(joint_name, actual_value)
                    return callback
                
                slider.valueChanged.connect(create_slider_callback(joint_name, value_label))
                
                # 初始化关节值
                self.current_joint_values[joint_name] = 0.0
        
        # 添加弹性空间
        self.joint_control_layout.addStretch()
    
    def schedule_joint_update(self, joint_name, value):
        """调度关节更新"""
        # 更新当前值
        self.current_joint_values[joint_name] = np.radians(value)
        
        # 如果定时器不存在，创建一个新的
        if self.update_timer is None:
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self._process_joint_updates)
            self.update_timer.start(16)  # 约60fps
    
    def _process_joint_updates(self):
        """处理所有待更新的关节"""
        if not self.urdf:
            return
            
        # 更新所有已更改的关节
        for joint_name, value in self.current_joint_values.items():
            if joint_name in self.urdf.joint_map:
                joint = self.urdf.joint_map[joint_name]
                if hasattr(joint, 'axis'):
                    # 创建旋转矩阵
                    angle = value
                    axis = joint.axis
                    rotation = trimesh.transformations.rotation_matrix(angle, axis)
                    
                    # 更新关节变换
                    if hasattr(joint, 'origin'):
                        # 组合原始变换和旋转
                        transform = np.dot(joint.origin, rotation)
                    else:
                        transform = rotation
                    
                    # 更新 OpenGL 显示组件的关节变换
                    self.gl_widget.update_joint_transform(joint_name, transform)
        
        # 停止定时器
        self.update_timer.stop()
        self.update_timer = None
    
    def load_urdf(self):
        """加载 URDF 文件"""
        try:
            # 使用指定的URDF文件路径
            urdf_path = r"D:\03.project\gaiyagui\urdf\right_gaia\urdf\right_gaia.urdf"
            
            # 获取工作空间根目录
            workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            
            # 构建 KUKA iiwa 模型的完整路径
            # urdf_path = os.path.join(workspace_root, "urdf", "kuka iiwa", "model.urdf")

            if not os.path.exists(urdf_path):
                self.status_label.setText(f"错误：找不到 URDF 文件: {urdf_path}")
                return
            
            # 设置工作目录为 URDF 文件所在目录，以处理相对路径
            original_dir = os.getcwd()
            urdf_dir = os.path.dirname(urdf_path)
            os.chdir(urdf_dir)
            
            try:
                # 加载 URDF 模型
                self.urdf = yourdfpy.URDF.load(os.path.basename(urdf_path))
                self.gl_widget.urdf_dir = urdf_dir  # 设置 URDF 文件所在目录
                self.gl_widget.load_urdf(self.urdf)  # 使用新的加载方法
                self.status_label.setText(f"已加载: {os.path.basename(urdf_path)}")
                
                # 创建关节控制
                self.create_joint_controls()
                
                # 打印 URDF 信息
                print("\nURDF 模型信息:")
                print(f"连杆数量: {len(self.urdf.link_map)}")
                print(f"关节数量: {len(self.urdf.joint_map)}")
                
                # 打印连杆信息
                print("\n连杆信息:")
                for link_name, link in self.urdf.link_map.items():
                    print(f"\n连杆: {link_name}")
                    if hasattr(link, 'visuals'):
                        for visual in link.visuals:
                            print(f"  视觉元素:")
                            if hasattr(visual, 'geometry'):
                                geometry = visual.geometry
                                if geometry is not None:
                                    if hasattr(geometry, 'box') and geometry.box is not None:
                                        print(f"    类型: 盒子")
                                        print(f"    尺寸: {geometry.box.size}")
                                    elif hasattr(geometry, 'cylinder') and geometry.cylinder is not None:
                                        print(f"    类型: 圆柱体")
                                        print(f"    半径: {geometry.cylinder.radius}")
                                        print(f"    长度: {geometry.cylinder.length}")
                                    elif hasattr(geometry, 'sphere') and geometry.sphere is not None:
                                        print(f"    类型: 球体")
                                        print(f"    半径: {geometry.sphere.radius}")
                                    elif hasattr(geometry, 'mesh') and geometry.mesh is not None:
                                        print(f"    类型: 网格")
                                        print(f"    文件: {geometry.mesh.filename}")
                                        # 构建正确的网格文件路径
                                        if geometry.mesh.filename.startswith('package://'):
                                            # 移除 'package://' 前缀
                                            relative_path = geometry.mesh.filename[10:]
                                            # 将正斜杠转换为反斜杠
                                            relative_path = relative_path.replace('/', os.sep)
                                            # 从路径中移除包名（第一个目录）
                                            path_parts = relative_path.split(os.sep)
                                            if len(path_parts) > 1:
                                                relative_path = os.sep.join(path_parts[1:])
                                            # 构建完整路径
                                            mesh_path = os.path.join(os.path.dirname(urdf_dir), relative_path)
                                        else:
                                            mesh_path = os.path.join(urdf_dir, geometry.mesh.filename)
                                        print(f"    完整路径: {mesh_path}")
                                        print(f"    文件存在: {os.path.exists(mesh_path)}")
                            if (hasattr(visual, 'material') and 
                                visual.material is not None and 
                                hasattr(visual.material, 'color') and 
                                visual.material.color is not None):
                                print(f"    颜色: {visual.material.color.rgba}")
                            else:
                                print("    颜色: 未指定")
                                
                # 打印关节信息
                print("\n关节信息:")
                for joint_name, joint in self.urdf.joint_map.items():
                    print(f"\n关节: {joint_name}")
                    print(f"  类型: {joint.type}")
                    print(f"  父连杆: {joint.parent}")
                    print(f"  子连杆: {joint.child}")
                    print(f"  原点: {joint.origin}")
                    if hasattr(joint, 'axis'):
                        print(f"  轴: {joint.axis}")
                    if hasattr(joint, 'limit'):
                        print(f"  限制: {joint.limit}")
                        
                # 更新 OpenGL 显示
                self.gl_widget.update()
                
            finally:
                # 恢复原始工作目录
                os.chdir(original_dir)
                
        except Exception as e:
            self.status_label.setText(f"加载失败: {str(e)}")
            import traceback
            traceback.print_exc()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URDF Viewer Test (yourdfpy)")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # 创建 URDF 查看器
        self.viewer = URDFViewer()
        layout.addWidget(self.viewer)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
