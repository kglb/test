#!/bin/bash

# 课题组管理系统启动脚本

echo "正在初始化课题组管理系统..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 进入项目目录
cd lab_management

# 初始化数据库
echo "初始化数据库..."
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"

echo ""
echo "系统初始化完成！"
echo ""
echo "启动服务器..."
echo "服务器地址: http://localhost:5000"
echo "默认管理员账号: admin"
echo "默认管理员密码: admin123"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动Flask应用
python3 app.py