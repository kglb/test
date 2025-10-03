# 课题组管理系统

一个基于Flask的课题组管理系统，支持成员管理、项目管理、任务分配和公告发布等功能。

## 功能特性

- **用户管理**: 支持用户注册、登录、角色管理
- **项目管理**: 创建、编辑、删除项目，分配项目成员
- **任务管理**: 创建任务、分配任务、跟踪任务状态
- **公告系统**: 发布和管理课题组公告
- **设备管理**: 完整的实验设备管理系统
  - **设备入库**: 设备基本信息录入、分类管理
  - **使用登记**: 设备使用记录、状态跟踪
  - **设备预约**: 预约申请、审批流程
  - **维护管理**: 维护计划、维护记录、故障处理
- **仪表板**: 直观显示项目、任务、设备和成员统计信息
- **响应式设计**: 支持桌面和移动设备

## 技术栈

- **后端**: Flask, SQLAlchemy, Flask-Login
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **数据库**: SQLite
- **UI框架**: Bootstrap 5

## 快速开始

### 环境要求

- Python 3.7+
- pip

### 安装和运行

1. 克隆项目到本地
```bash
git clone <repository-url>
cd test
```

2. 运行启动脚本（推荐）
```bash
./start.sh
```

或者手动安装：

2a. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

2b. 安装依赖
```bash
pip install -r requirements.txt
```

2c. 初始化数据库
```bash
cd lab_management
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

2d. 启动应用
```bash
python3 app.py
```

3. 打开浏览器访问 http://localhost:5000

### 默认账号

- 用户名: `admin`
- 密码: `admin123`

## 项目结构

```
lab_management/
├── app.py              # Flask应用主文件
├── models.py           # 数据模型定义
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── app.js      # 前端JavaScript
└── templates/          # HTML模板
    ├── base.html       # 基础模板
    ├── index.html      # 首页
    ├── login.html      # 登录页
    ├── dashboard.html  # 仪表板
    ├── projects.html   # 项目管理
    ├── tasks.html      # 任务管理
    ├── users.html      # 用户管理
    ├── announcements.html # 公告管理
    ├── equipment.html  # 设备管理
    ├── equipment_usage.html # 设备使用记录
    ├── equipment_reservations.html # 设备预约
    └── equipment_maintenance.html # 设备维护
```

## API接口

### 用户相关
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `PUT /api/users/<id>` - 更新用户信息
- `DELETE /api/users/<id>` - 删除用户

### 项目相关
- `GET /api/projects` - 获取项目列表
- `POST /api/projects` - 创建项目
- `PUT /api/projects/<id>` - 更新项目
- `DELETE /api/projects/<id>` - 删除项目

### 任务相关
- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建任务
- `PUT /api/tasks/<id>` - 更新任务
- `DELETE /api/tasks/<id>` - 删除任务

### 公告相关
- `GET /api/announcements` - 获取公告列表
- `POST /api/announcements` - 创建公告
- `PUT /api/announcements/<id>` - 更新公告
- `DELETE /api/announcements/<id>` - 删除公告

### 设备管理相关
- `GET /api/equipment` - 获取设备列表
- `POST /api/equipment` - 创建设备
- `GET /api/equipment/<id>` - 获取设备详情
- `PUT /api/equipment/<id>` - 更新设备信息
- `DELETE /api/equipment/<id>` - 删除设备

### 设备使用相关
- `GET /api/equipment/usage` - 获取设备使用记录
- `POST /api/equipment/usage` - 开始使用设备
- `PUT /api/equipment/usage/<id>/end` - 结束设备使用

### 设备预约相关
- `GET /api/equipment/reservations` - 获取设备预约记录
- `POST /api/equipment/reservations` - 创建设备预约
- `PUT /api/equipment/reservations/<id>/approve` - 审批设备预约

### 设备维护相关
- `GET /api/equipment/maintenance` - 获取设备维护记录
- `POST /api/equipment/maintenance` - 创建设备维护记录
- `GET /api/equipment/statistics` - 获取设备统计信息

## 功能说明

### 用户角色
- **admin**: 管理员，拥有所有权限
- **supervisor**: 导师，可以管理项目和任务
- **student**: 学生，可以查看分配给自己的任务

### 项目管理
- 创建项目并设置项目详情
- 分配项目负责人和成员
- 跟踪项目进度和状态
- 项目可以有多个关联任务

### 任务管理
- 创建任务并分配给特定用户
- 设置任务优先级和截止日期
- 跟踪任务完成状态
- 任务状态：待办、进行中、已完成

### 公告系统
- 发布课题组公告和通知
- 支持重要公告置顶
- 按时间顺序显示公告列表

### 设备管理系统
- **设备入库管理**：录入设备基本信息、分类管理、设备状态跟踪
- **使用登记**：实时记录设备使用情况、使用者信息、使用目的
- **设备预约**：预约申请、时间冲突检测、审批流程管理
- **维护管理**：维护计划制定、维护记录跟踪、成本统计
- **状态管理**：可用、使用中、维护中、故障、已退役等状态
- **权限控制**：不同角色的设备管理权限

## 开发说明

### 添加新功能

1. 在 `models.py` 中定义新的数据模型
2. 在 `app.py` 中添加相应的API路由
3. 创建或修改HTML模板
4. 在 `app.js` 中添加前端交互逻辑
5. 更新CSS样式（如需要）

### 数据库操作

```python
# 创建表
with app.app_context():
    db.create_all()

# 删除所有表
with app.app_context():
    db.drop_all()
```

## 注意事项

- 系统使用SQLite数据库，数据文件为 `lab_management.db`
- 首次运行会自动创建管理员账号
- 生产环境使用前请修改默认密码和密钥
- 建议在生产环境中使用PostgreSQL或MySQL数据库

## 许可证

MIT License

## 贡献

欢迎提交Pull Request或者Issue来帮助改进这个项目。