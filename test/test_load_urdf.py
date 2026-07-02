import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext, QOpenGLVersionProfile
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import yourdfpy
import numpy as np

class URDFViewer(QOpenGLWidget): # Ensure this is QOpenGLWidget
    def __init__(self, parent=None, urdf_path=None):
        super().__init__(parent)
        self.urdf_path = urdf_path
        self.robot_model = None
        self.rotation_x = -90 # Initial rotation for better viewing
        self.rotation_y = 0
        self.zoom = 1.0

        if self.urdf_path:
            try:
                self.robot_model = yourdfpy.URDF.load(self.urdf_path)
                print(f"URDF model loaded successfully: {self.urdf_path}")
            except Exception as e:
                print(f"Error loading URDF: {e}")
                self.robot_model = None

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

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, self.width() / self.height(), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(0, 0, 5 * self.zoom,
                  0, 0, 0,
                  0, 1, 0)

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)

        if self.robot_model:
            self._draw_robot(self.robot_model)
        else:
            glPushAttrib(GL_CURRENT_BIT)
            glColor3f(1.0, 0.0, 0.0)
            glLineWidth(2.0)
            glBegin(GL_LINES)
            glVertex3f(-1.0, 0.0, 0.0)
            glVertex3f(1.0, 0.0, 0.0)
            glVertex3f(0.0, -1.0, 0.0)
            glVertex3f(0.0, 1.0, 0.0)
            glVertex3f(0.0, 0.0, -1.0)
            glVertex3f(0.0, 0.0, 1.0)
            glEnd()
            glPopAttrib()


    def _draw_robot(self, robot):
        """
        Draws the robot model by iterating through its visual components.
        This function handles box, cylinder, and sphere geometries.
        Mesh geometries are currently placeholders.
        """
        # In yourdfpy 0.0.57, 'robot.visuals' is the correct way to access
        # all visual geometry objects.
        if not hasattr(robot, 'visuals'):
            print("Error: 'robot' object has no 'visuals' attribute. Check yourdfpy version or model loading.")
            return

        for visual in robot.visuals:
            glPushMatrix() # Save the current modelview matrix

            # Get the global transform for the link this visual belongs to
            # 'visual.link' holds the name of the link
            transform = robot.get_transform(visual.link, 'base_link')
            glMultMatrixf(transform.T.flatten()) # Apply the link's global transformation

            # Apply the visual's own local origin transformation
            # This accounts for the visual's position/orientation within its link
            if visual.origin is not None:
                # visual.origin is a 4x4 numpy array representing the transform
                glMultMatrixf(visual.origin.T.flatten())

            # Draw the geometry based on its type
            if visual.geometry is not None:
                # Set color if material exists
                if visual.material and visual.material.color:
                    color = visual.material.color.rgba
                    glColor4f(*color)
                else:
                    glColor3f(0.5, 0.5, 0.5, 1.0) # Default grey with full alpha

                if visual.geometry.box is not None:
                    size = visual.geometry.box.size
                    half_size = size / 2.0
                    glBegin(GL_QUADS)
                    # Define vertices and normals for a cube
                    # Front face
                    glNormal3f(0.0, 0.0, 1.0)
                    glVertex3f(-half_size[0], -half_size[1], half_size[2])
                    glVertex3f(half_size[0], -half_size[1], half_size[2])
                    glVertex3f(half_size[0], half_size[1], half_size[2])
                    glVertex3f(-half_size[0], half_size[1], half_size[2])
                    # Back face
                    glNormal3f(0.0, 0.0, -1.0)
                    glVertex3f(-half_size[0], -half_size[1], -half_size[2])
                    glVertex3f(-half_size[0], half_size[1], -half_size[2])
                    glVertex3f(half_size[0], half_size[1], -half_size[2])
                    glVertex3f(half_size[0], -half_size[1], -half_size[2])
                    # Top face
                    glNormal3f(0.0, 1.0, 0.0)
                    glVertex3f(-half_size[0], half_size[1], -half_size[2])
                    glVertex3f(-half_size[0], half_size[1], half_size[2])
                    glVertex3f(half_size[0], half_size[1], half_size[2])
                    glVertex3f(half_size[0], half_size[1], -half_size[2])
                    # Bottom face
                    glNormal3f(0.0, -1.0, 0.0)
                    glVertex3f(-half_size[0], -half_size[1], -half_size[2])
                    glVertex3f(half_size[0], -half_size[1], -half_size[2])
                    glVertex3f(half_size[0], -half_size[1], half_size[2])
                    glVertex3f(-half_size[0], -half_size[1], half_size[2])
                    # Right face
                    glNormal3f(1.0, 0.0, 0.0)
                    glVertex3f(half_size[0], -half_size[1], -half_size[2])
                    glVertex3f(half_size[0], half_size[1], -half_size[2])
                    glVertex3f(half_size[0], half_size[1], half_size[2])
                    glVertex3f(half_size[0], -half_size[1], half_size[2])
                    # Left face
                    glNormal3f(-1.0, 0.0, 0.0)
                    glVertex3f(-half_size[0], -half_size[1], -half_size[2])
                    glVertex3f(-half_size[0], -half_size[1], half_size[2])
                    glVertex3f(-half_size[0], half_size[1], half_size[2])
                    glVertex3f(-half_size[0], half_size[1], -half_size[2])
                    glEnd()
                elif visual.geometry.cylinder is not None:
                    radius = visual.geometry.cylinder.radius
                    length = visual.geometry.cylinder.length
                    # Set color (already done above, but reiterate for clarity if needed)
                    quadric = gluNewQuadric()
                    gluQuadricNormals(quadric, GLU_SMOOTH)
                    glPushMatrix()
                    # Cylinders in URDF are typically centered along the Z-axis of the link.
                    # gluCylinder draws from Z=0 to Z=length. We need to translate it.
                    glTranslatef(0, 0, -length / 2.0)
                    gluCylinder(quadric, radius, radius, length, 32, 32)
                    gluDeleteQuadric(quadric)
                    glPopMatrix()
                elif visual.geometry.sphere is not None:
                    radius = visual.geometry.sphere.radius
                    # Set color (already done above)
                    glutSolidSphere(radius, 32, 32)
                elif visual.geometry.mesh is not None:
                    print(f"Warning: Mesh geometry not fully implemented: {visual.geometry.mesh.filename}. Displaying placeholder.")
                    # Placeholder for mesh: a purple wireframe cube
                    glPushAttrib(GL_CURRENT_BIT) # Save current GL attributes (like color)
                    glColor3f(1.0, 0.0, 1.0) # Purple color
                    glutWireCube(0.1) # Draw a small wireframe cube
                    glPopAttrib() # Restore saved GL attributes

            glPopMatrix() # Restore the previous modelview matrix

    def mousePressEvent(self, event):
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.LeftButton:
            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5
        self.last_mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 15

        self.zoom -= num_steps * 0.1
        if self.zoom < 0.1:
            self.zoom = 0.1
        self.update()


class MainWindow(QMainWindow):
    def __init__(self, urdf_path=None):
        super().__init__()
        self.setWindowTitle("URDF Viewer")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.urdf_viewer = URDFViewer(self, urdf_path)
        layout.addWidget(self.urdf_viewer)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 替换为你的URDF文件路径
    # 你可以下载一个简单的URDF文件进行测试，例如一个机器人的URDF
    # 例如：https://github.com/ros/urdf_tutorial/blob/ros2/urdf/r2d2.urdf.xml
    # 确保URDF文件及其引用的所有mesh文件（如果存在）都在正确的相对路径下
    # 当前路径
    current_path = os.path.dirname(os.path.abspath(__file__))
    urdf_file_path = os.path.join(current_path, "simple_box.urdf")

    # 创建一个简单的URDF文件用于测试 (例如，一个简单的box)
    # 将以下内容保存为 `simple_box.urdf`
    """
    <?xml version="1.0"?>
    <robot name="simple_box">
      <link name="base_link">
        <visual>
          <geometry>
            <box size="1.0 0.5 0.2"/>
          </geometry>
          <material name="red">
            <color rgba="1.0 0.0 0.0 1.0"/>
          </material>
        </visual>
      </link>
      <link name="link1">
        <visual>
          <origin xyz="0 0 0.2"/>
          <geometry>
            <cylinder radius="0.1" length="0.4"/>
          </geometry>
          <material name="blue">
            <color rgba="0.0 0.0 1.0 1.0"/>
          </material>
        </visual>
      </link>
      <joint name="joint1" type="fixed">
        <parent link="base_link"/>
        <child link="link1"/>
        <origin xyz="0 0 0.1"/>
      </joint>
    </robot>
    """
    # 确保 urdf_file_path 指向这个文件

    main_win = MainWindow(urdf_path=urdf_file_path)
    main_win.show()
    sys.exit(app.exec())