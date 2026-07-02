'''
File name: 
Descripttion: 
Author: tanzhiqiang
Email: zhiqiangtan89@gmail.com
Version: 
Date: 2025-07-02 17:37:24
History: 
'''
#!/usr/bin/env python3
"""
手部控制模块安装配置

支持多种手部类型的统一控制接口，包括Gaia灵巧手和Pantheon手部系统。
"""

from setuptools import setup, find_packages
import os
from pathlib import Path


def _get_version():
    """从 hand/__init__.py 读取版本号，避免重复定义"""
    version_file = Path(__file__).parent / "hand" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("__version__"):
                return line.split("=")[1].strip().strip('"\'').strip()
    return "0.0.0"


# 读取README文件作为长描述
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "手部控制模块 - 支持多种手部类型的统一控制接口"

# 读取requirements.txt文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="handsdk",
    version=_get_version(),
    author="tanzhiqiang",
    author_email="zhiqiangtan89@gmail.com",
    description="手部控制模块 - 支持多种手部类型的统一控制接口",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://gitee.com/stellarrobot/handsdk.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Hardware :: Hardware Drivers",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hand-control=hand:main",
        ],
    },
    include_package_data=True,
    package_data={
        "hand": [
            "*.md",
            "通信协议.md",
            "gaiahand/*.md",
            "pantheonhand/*.md",
            "can_utils/slcan/*.md",
            "sensor/*.md",
        ],
        # can_utils 动态库及配置文件（zlgcan/zlgcanfd）
        "hand.can_utils": [
            "zlgcan_win/*.dll",
            "zlgcan_win/kerneldlls/*",
            "zlgcan_win/kerneldlls/devices_property/*.xml",
            "zlgcan_win/kerneldlls/devices_property/*.ini",
            "zlgcan_linux/*.so",
            "zlgcanfd_win/*.dll",
            "zlgcanfd_linux/*.so",
        ],
        # SLCAN native：ctypes 加载，需先在 slcan/cpp 构建或随仓库提交对应平台产物
        "hand.can_utils.slcan": [
            "slcan_core.dll",
            "libslcan_core.so",
            "libslcan_core.dylib",
        ],
    },
    keywords=[
        "hand control",
        "robotics",
        "motor control",
        "serial communication",
        "gaia hand",
        "pantheon hand",
        "kinematics",
        "gesture recognition",
    ],
    project_urls={
        "Bug Reports": "https://gitee.com/stellarrobot/handsdk/issues",
        "Source": "https://gitee.com/stellarrobot/handsdk.gi",
        "Documentation": "https://hand-control.readthedocs.io/",
    },
) 