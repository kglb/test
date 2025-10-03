# 实验室管理系统 (Laboratory Management System)

一个功能完整的实验室管理系统，用于管理科研团队的成员、设备、库存、项目和任务。

## 功能特性

### 核心功能模块

#### 1. 成员管理
- ✅ 成员信息录入（姓名、联系方式、身份、入组时间等）
- ✅ 角色权限分配（管理员、教师、学生）
- ✅ 出入组记录和历史变更追踪
- ✅ 成员状态管理（活跃/离职）

#### 2. 课题组管理
- ✅ 多课题组支持
- ✅ 课题组信息管理
- ✅ 成员分组管理

#### 3. 设备管理
- ✅ 设备登记和基本信息管理
- ✅ 设备状态跟踪（可用、使用中、维护中、报废）
- ✅ 设备使用记录管理
- ✅ 设备预约系统（含审批流程）
- ✅ 设备维护记录和提醒

#### 4. 库存管理
- ✅ 试剂和耗材登记
- ✅ 库存数量跟踪
- ✅ 出入库记录管理
- ✅ 库存预警（低于最小库存量提醒）

#### 5. 项目与任务管理
- ✅ 项目全生命周期管理
- ✅ 任务创建和分配
- ✅ 任务状态跟踪
- ✅ 项目进度监控

#### 6. 公告系统
- ✅ 公告发布和管理
- ✅ 公告置顶功能
- ✅ 优先级设置

#### 7. 权限管理
- ✅ 基于角色的权限控制
- ✅ 细粒度的操作权限管理
- ✅ 权限配置系统

#### 8. 系统日志与审计
- ✅ 完整的操作日志记录
- ✅ 用户行为追踪
- ✅ 系统安全审计

## 技术栈

### 后端
- **Flask 2.3.3** - Python Web 框架
- **SQLAlchemy** - ORM 数据库抽象层
- **Werkzeug** - 密码加密和安全工具
- **SQLite** - 轻量级数据库（可替换为 PostgreSQL/MySQL）

### 前端
- **Bootstrap 5** - 响应式 UI 框架
- **Bootstrap Icons** - 图标库
- **JavaScript (Vanilla)** - 前端交互逻辑

## 项目结构

```
test/
├── lab_management/
│   ├── app.py                 # Flask 应用主文件
│   ├── models.py              # 数据库模型定义
│   ├── templates/             # HTML 模板
│   │   ├── base.html         # 基础模板
│   │   ├── landing.html      # 着陆页
│   │   ├── login.html        # 登录页
│   │   ├── dashboard.html    # 仪表板
│   │   ├── users.html        # 成员管理
│   │   ├── groups.html       # 课题组管理
│   │   ├── projects.html     # 项目管理
│   │   ├── tasks.html        # 任务管理
│   │   ├── equipment.html    # 设备管理
│   │   ├── equipment_usage.html           # 设备使用记录
│   │   ├── equipment_reservations.html    # 设备预约
│   │   ├── equipment_maintenance.html     # 设备维护
│   │   ├── inventory.html    # 库存管理
│   │   ├── announcements.html # 公告管理
│   │   └── system_logs.html  # 系统日志
│   └── static/               # 静态文件（CSS、JS、图片）
├── requirements.txt          # Python 依赖
└── README.md                # 项目文档
```

## 安装与运行

### 环境要求
- Python 3.8+
- pip (Python 包管理器)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/kglb/test.git
cd test
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动应用**
```bash
cd lab_management
python app.py
```

4. **访问系统**
- 打开浏览器访问：`http://localhost:5000`
- 默认管理员账号：`admin`
- 默认密码：`admin123`

## 系统截图

### 着陆页
![Landing Page](https://github.com/user-attachments/assets/cd80facb-f572-421e-8abf-fc090959fb9e)

### 登录页
![Login Page](https://github.com/user-attachments/assets/bd225340-b84e-440f-a3d3-057bd5f3db88)

### 仪表板
![Dashboard](https://github.com/user-attachments/assets/ed3a4d9d-8487-43e0-aaac-3fbb56cc52e8)

### 成员管理
![Users Management](https://github.com/user-attachments/assets/63820d5a-8f01-4b08-b1b9-21e3a7b6ff39)

## 权限说明

系统定义了三种角色：

### 管理员 (admin)
- 所有功能的完整访问权限
- 用户管理
- 系统配置
- 查看系统日志

### 教师 (teacher)
- 成员管理
- 项目和任务管理
- 设备管理和审批
- 公告发布

### 学生 (student)
- 查看项目和任务
- 申请设备预约
- 使用设备和库存
- 查看公告

## 许可证

本项目采用 MIT 许可证。