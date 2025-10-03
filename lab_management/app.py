from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from models import (
    db, User, Project, ProjectMember, Task, Announcement, Equipment, EquipmentUsage, 
    EquipmentReservation, EquipmentMaintenance, MemberHistory, Inventory,
    InventoryRecord, SystemLog, Group, GroupMember, Permission, RolePermission
)
from datetime import datetime, timedelta
import random
from faker import Faker
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db.init_app(app)

def init_database():
    """初始化数据库和默认用户"""
    with app.app_context():
        db.create_all()
        
        # 创建默认管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@lab.com',
                real_name='系统管理员',
                role='admin',
                student_id='ADMIN001'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("默认管理员用户已创建")
        else:
            print("默认管理员用户已存在")

# 登录检查装饰器
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限检查装饰器
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': '权限不足'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 路由定义
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/landing')
def landing_page():
    return render_template('landing.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/members')
@login_required
def members_page():
    return render_template('members.html')

@app.route('/users')
@login_required
def users_page():
    return render_template('users.html')

@app.route('/inventory')
@login_required
def inventory_page():
    return render_template('inventory.html')

@app.route('/inventory/records')
@login_required
def inventory_records_page():
    return render_template('inventory_records.html')

@app.route('/system/logs')
@admin_required
def system_logs_page():
    return render_template('system_logs.html')

@app.route('/groups')
@admin_required
def groups_page():
    return render_template('groups.html')

@app.route('/permissions')
@admin_required
def permissions_page():
    return render_template('permissions.html')

@app.route('/projects')
def projects_page():
    return render_template('projects.html')

@app.route('/tasks')
def tasks_page():
    return render_template('tasks.html')

@app.route('/announcements')
def announcements_page():
    return render_template('announcements.html')

# API路由

# 用户认证API
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password) and user.is_active:
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'message': '登录成功'
        })
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True, 'message': '退出成功'})

@app.route('/api/current_user')
@login_required
def api_current_user():
    user = db.session.get(User, session['user_id'])
    return jsonify(user.to_dict())

# 用户管理API
@app.route('/api/users', methods=['GET'])
@login_required
def api_get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@app.route('/api/users', methods=['POST'])
@admin_required
def api_create_user():
    data = request.get_json()
    
    # 检查用户名和邮箱是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': '用户名已存在'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': '邮箱已存在'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        real_name=data['real_name'],
        role=data.get('role', 'student'),
        student_id=data.get('student_id'),
        major=data.get('major'),
        grade=data.get('grade'),
        phone=data.get('phone'),
        research_direction=data.get('research_direction'),
        advisor_id=data.get('advisor_id'),
        join_date=datetime.strptime(data.get('join_date'), '%Y-%m-%d').date() if data.get('join_date') else None,
        bio=data.get('bio'),
        office_location=data.get('office_location'),
        emergency_contact=data.get('emergency_contact'),
        emergency_phone=data.get('emergency_phone'),
        status=data.get('status', 'active')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # 记录成员历史
    history = MemberHistory(
        member_id=user.id,
        action_type='join',
        description=f'新成员加入课题组，角色：{user.role}',
        new_value=user.role,
        operator_id=session['user_id']
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # 记录变更前的值
    old_values = {
        'role': user.role,
        'real_name': user.real_name,
        'email': user.email,
        'status': user.status,
        'research_direction': user.research_direction,
        'advisor_id': user.advisor_id
    }
    
    # 更新用户信息
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': '邮箱已存在'}), 400
        user.email = data['email']
    
    if 'real_name' in data:
        user.real_name = data['real_name']
    if 'role' in data:
        user.role = data['role']
    if 'student_id' in data:
        user.student_id = data['student_id']
    if 'major' in data:
        user.major = data['major']
    if 'grade' in data:
        user.grade = data['grade']
    if 'phone' in data:
        user.phone = data['phone']
    if 'research_direction' in data:
        user.research_direction = data['research_direction']
    if 'advisor_id' in data:
        user.advisor_id = data['advisor_id']
    if 'leave_date' in data:
        user.leave_date = datetime.strptime(data['leave_date'], '%Y-%m-%d').date() if data['leave_date'] else None
    if 'bio' in data:
        user.bio = data['bio']
    if 'office_location' in data:
        user.office_location = data['office_location']
    if 'emergency_contact' in data:
        user.emergency_contact = data['emergency_contact']
    if 'emergency_phone' in data:
        user.emergency_phone = data['emergency_phone']
    if 'status' in data:
        user.status = data['status']
    
    # 如果密码字段存在，更新密码
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    # 记录重要字段的变更历史
    for field, old_value in old_values.items():
        new_value = getattr(user, field)
        if old_value != new_value:
            action_type = 'role_change' if field == 'role' else 'update'
            description = f'{field}从"{old_value}"更改为"{new_value}"'
            
            history = MemberHistory(
                member_id=user.id,
                action_type=action_type,
                description=description,
                old_value=str(old_value) if old_value else None,
                new_value=str(new_value) if new_value else None,
                operator_id=session['user_id']
            )
            db.session.add(history)
    
    if user.status == 'inactive' and old_values['status'] == 'active':
        # 记录成员离组
        history = MemberHistory(
            member_id=user.id,
            action_type='leave',
            description='成员离开课题组',
            old_value='active',
            new_value='inactive',
            operator_id=session['user_id']
        )
        db.session.add(history)
    
    db.session.commit()
    
    return jsonify(user.to_dict())

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': '用户删除成功'})

# 项目管理API
@app.route('/api/projects', methods=['GET'])
@login_required
def api_get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])

@app.route('/api/projects', methods=['POST'])
@login_required
def api_create_project():
    data = request.get_json()
    
    project = Project(
        name=data['name'],
        description=data.get('description'),
        creator_id=data.get('creator_id', session['user_id']),
        priority=data.get('priority', 'medium'),
        end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None
    )
    
    db.session.add(project)
    db.session.commit()
    
    # 添加项目负责人为项目成员
    member = ProjectMember(
        project_id=project.id,
        user_id=project.creator_id,
        role='leader'
    )
    db.session.add(member)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def api_update_project(project_id):
    project = Project.query.get_or_404(project_id)
    data = request.get_json()
    
    project.name = data.get('name', project.name)
    project.description = data.get('description', project.description)
    project.status = data.get('status', project.status)
    project.priority = data.get('priority', project.priority)
    project.progress = data.get('progress', project.progress)
    
    if data.get('end_date'):
        project.end_date = datetime.fromisoformat(data['end_date'])
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(project.to_dict())

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def api_delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True, 'message': '项目删除成功'})

@app.route('/api/projects/<int:project_id>/members', methods=['GET'])
@login_required
def api_get_project_members(project_id):
    members = ProjectMember.query.filter_by(project_id=project_id).all()
    return jsonify([member.to_dict() for member in members])

@app.route('/api/projects/<int:project_id>/members', methods=['POST'])
@login_required
def api_add_project_member(project_id):
    data = request.get_json()
    
    # 检查是否已是成员
    existing = ProjectMember.query.filter_by(
        project_id=project_id,
        user_id=data['user_id']
    ).first()
    
    if existing:
        return jsonify({'error': '用户已是项目成员'}), 400
    
    member = ProjectMember(
        project_id=project_id,
        user_id=data['user_id'],
        role=data.get('role', 'member')
    )
    
    db.session.add(member)
    db.session.commit()
    
    return jsonify(member.to_dict()), 201

# 任务管理API
@app.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    project_id = request.args.get('project_id')
    assignee_id = request.args.get('assignee_id')
    
    query = Task.query
    
    if project_id:
        query = query.filter_by(project_id=project_id)
    if assignee_id:
        query = query.filter_by(assignee_id=assignee_id)
    
    tasks = query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
@login_required
def api_create_task():
    data = request.get_json()
    
    task = Task(
        title=data['title'],
        description=data.get('description'),
        project_id=data['project_id'],
        assignee_id=data.get('assignee_id'),
        priority=data.get('priority', 'medium'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def api_update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.assignee_id = data.get('assignee_id', task.assignee_id)
    task.status = data.get('status', task.status)
    task.priority = data.get('priority', task.priority)
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data['due_date'])
    
    if data.get('status') == 'completed' and task.status != 'completed':
        task.completed_at = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True, 'message': '任务删除成功'})

# 公告管理API
@app.route('/api/announcements', methods=['GET'])
@login_required
def api_get_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([announcement.to_dict() for announcement in announcements])

@app.route('/api/announcements', methods=['POST'])
@login_required
def api_create_announcement():
    data = request.get_json()
    
    announcement = Announcement(
        title=data['title'],
        content=data['content'],
        creator_id=session['user_id'],
        is_important=data.get('is_important', False)
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    return jsonify(announcement.to_dict()), 201

@app.route('/api/announcements/<int:announcement_id>', methods=['PUT'])
@login_required
def api_update_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    data = request.get_json()
    
    announcement.title = data.get('title', announcement.title)
    announcement.content = data.get('content', announcement.content)
    announcement.is_important = data.get('is_important', announcement.is_important)
    announcement.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(announcement.to_dict())

@app.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
@login_required
def api_delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    return jsonify({'success': True, 'message': '公告删除成功'})

# 统计API
@app.route('/api/statistics')
@login_required
def api_statistics():
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'total_projects': Project.query.count(),
        'active_projects': Project.query.filter_by(status='active').count(),
        'total_tasks': Task.query.count(),
        'completed_tasks': Task.query.filter_by(status='completed').count(),
        'pending_tasks': Task.query.filter(Task.status.in_(['todo', 'in_progress'])).count(),
        'recent_announcements': Announcement.query.order_by(Announcement.created_at.desc()).limit(5).count(),
        # 设备管理统计
        'total_equipment': Equipment.query.count(),
        'available_equipment': Equipment.query.filter_by(status='available').count(),
        'in_use_equipment': Equipment.query.filter_by(status='in_use').count(),
        'maintenance_equipment': Equipment.query.filter_by(status='maintenance').count(),
        'pending_reservations': EquipmentReservation.query.filter_by(status='pending').count(),
        # 库存管理统计
        'total_inventory': Inventory.query.count(),
        'low_stock_items': Inventory.query.filter(Inventory.current_stock <= Inventory.min_stock).count(),
        'inventory_categories': db.session.query(Inventory.category, db.func.count(Inventory.id)).group_by(Inventory.category).all(),
        # 今日统计
        'today_equipment_usage': EquipmentUsage.query.filter(
            db.func.date(EquipmentUsage.start_time) == datetime.now().date()
        ).count() if hasattr(EquipmentUsage, 'start_time') else 0,
        'today_inventory_records': InventoryRecord.query.filter(
            db.func.date(InventoryRecord.created_at) == datetime.now().date()
        ).count(),
        # 课题组统计
        'total_groups': Group.query.count(),
        'active_groups': Group.query.filter_by(status='active').count()
    }
    return jsonify(stats)

# ======================
# 设备管理 API
# ======================

# 设备管理页面路由
@app.route('/equipment')
@login_required
def equipment_page():
    return render_template('equipment.html')

@app.route('/equipment/usage')
@login_required
def equipment_usage_page():
    return render_template('equipment_usage.html')

@app.route('/equipment/reservations')
@login_required
def equipment_reservations_page():
    return render_template('equipment_reservations.html')

@app.route('/equipment/maintenance')
@login_required
def equipment_maintenance_page():
    return render_template('equipment_maintenance.html')

# 设备 CRUD API
@app.route('/api/equipment', methods=['GET'])
@login_required
def api_get_equipment():
    """获取设备列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Equipment.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Equipment.name.contains(search) | 
                           Equipment.model.contains(search) |
                           Equipment.serial_number.contains(search))
    
    equipment_list = query.order_by(Equipment.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'equipment': [eq.to_dict() for eq in equipment_list.items],
        'total': equipment_list.total,
        'pages': equipment_list.pages,
        'current_page': page
    })

@app.route('/api/equipment/<int:equipment_id>', methods=['GET'])
@login_required
def api_get_equipment_detail(equipment_id):
    """获取设备详情"""
    equipment = Equipment.query.get_or_404(equipment_id)
    return jsonify(equipment.to_dict(include_usage=True, include_reservations=True))

@app.route('/api/equipment', methods=['POST'])
@login_required
def api_create_equipment():
    """创建设备"""
    user = User.query.get(session['user_id'])
    if user.role not in ['admin', 'supervisor']:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    # 检查序列号是否已存在
    if Equipment.query.filter_by(serial_number=data.get('serial_number')).first():
        return jsonify({'error': '设备序列号已存在'}), 400
    
    equipment = Equipment(
        name=data.get('name'),
        model=data.get('model'),
        serial_number=data.get('serial_number'),
        category=data.get('category'),
        manufacturer=data.get('manufacturer'),
        purchase_date=datetime.strptime(data.get('purchase_date'), '%Y-%m-%d').date() if data.get('purchase_date') else None,
        purchase_price=data.get('purchase_price'),
        location=data.get('location'),
        status=data.get('status', 'available'),
        description=data.get('description'),
        specifications=data.get('specifications'),
        maintenance_cycle=data.get('maintenance_cycle'),
        responsible_person_id=data.get('responsible_person_id'),
        created_by_id=session['user_id']
    )
    
    db.session.add(equipment)
    db.session.commit()
    
    return jsonify({'success': True, 'equipment': equipment.to_dict()}), 201

@app.route('/api/equipment/<int:equipment_id>', methods=['PUT'])
@login_required
def api_update_equipment(equipment_id):
    """更新设备信息"""
    user = User.query.get(session['user_id'])
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # 检查权限：管理员、导师或设备负责人可以更新
    if user.role not in ['admin', 'supervisor'] and equipment.responsible_person_id != user.id:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    # 检查序列号唯一性（如果有更改）
    if data.get('serial_number') and data.get('serial_number') != equipment.serial_number:
        if Equipment.query.filter_by(serial_number=data.get('serial_number')).first():
            return jsonify({'error': '设备序列号已存在'}), 400
    
    # 更新字段
    for field in ['name', 'model', 'serial_number', 'category', 'manufacturer', 
                  'location', 'status', 'description', 'specifications', 
                  'maintenance_cycle', 'responsible_person_id']:
        if field in data:
            setattr(equipment, field, data[field])
    
    # 处理日期字段
    if data.get('purchase_date'):
        equipment.purchase_date = datetime.strptime(data.get('purchase_date'), '%Y-%m-%d').date()
    if data.get('purchase_price'):
        equipment.purchase_price = data.get('purchase_price')
    
    db.session.commit()
    
    return jsonify({'success': True, 'equipment': equipment.to_dict()})

@app.route('/api/equipment/<int:equipment_id>', methods=['DELETE'])
@admin_required
def api_delete_equipment(equipment_id):
    """删除设备"""
    equipment = Equipment.query.get_or_404(equipment_id)
    
    # 检查是否有正在进行的使用记录或预约
    active_usage = EquipmentUsage.query.filter_by(equipment_id=equipment_id, status='in_use').first()
    active_reservations = EquipmentReservation.query.filter_by(equipment_id=equipment_id, status='approved').filter(
        EquipmentReservation.end_time >= datetime.utcnow()
    ).first()
    
    if active_usage or active_reservations:
        return jsonify({'error': '设备有正在进行的使用记录或预约，无法删除'}), 400
    
    db.session.delete(equipment)
    db.session.commit()
    
    return jsonify({'success': True})

# 设备使用记录 API
@app.route('/api/equipment/usage', methods=['GET'])
@login_required
def api_get_equipment_usage():
    """获取设备使用记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    equipment_id = request.args.get('equipment_id')
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    query = EquipmentUsage.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    usage_list = query.order_by(EquipmentUsage.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'usage_records': [usage.to_dict() for usage in usage_list.items],
        'total': usage_list.total,
        'pages': usage_list.pages,
        'current_page': page
    })

@app.route('/api/equipment/usage', methods=['POST'])
@login_required
def api_create_equipment_usage():
    """开始使用设备"""
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    
    # 检查设备是否可用
    equipment = Equipment.query.get_or_404(equipment_id)
    if equipment.status != 'available':
        return jsonify({'error': '设备当前不可用'}), 400
    
    # 检查是否有正在进行的使用记录
    active_usage = EquipmentUsage.query.filter_by(equipment_id=equipment_id, status='in_use').first()
    if active_usage:
        return jsonify({'error': '设备正在被使用'}), 400
    
    usage = EquipmentUsage(
        equipment_id=equipment_id,
        user_id=session['user_id'],
        project_id=data.get('project_id'),
        purpose=data.get('purpose'),
        start_time=datetime.utcnow(),
        condition_before=data.get('condition_before', 'good'),
        notes=data.get('notes')
    )
    
    # 更新设备状态
    equipment.status = 'in_use'
    
    db.session.add(usage)
    db.session.commit()
    
    return jsonify({'success': True, 'usage': usage.to_dict()}), 201

@app.route('/api/equipment/usage/<int:usage_id>/end', methods=['PUT'])
@login_required
def api_end_equipment_usage(usage_id):
    """结束设备使用"""
    usage = EquipmentUsage.query.get_or_404(usage_id)
    
    # 检查权限：只有使用者本人或管理员可以结束使用
    user = User.query.get(session['user_id'])
    if usage.user_id != user.id and user.role not in ['admin', 'supervisor']:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    usage.end_time = datetime.utcnow()
    usage.status = 'completed'
    usage.condition_after = data.get('condition_after', 'good')
    usage.notes = data.get('notes', usage.notes)
    
    # 更新设备状态
    equipment = usage.equipment
    equipment.status = 'available'
    
    # 如果设备状态变差，可能需要维护
    if data.get('condition_after') in ['poor', 'broken']:
        equipment.status = 'maintenance'
    
    db.session.commit()
    
    return jsonify({'success': True, 'usage': usage.to_dict()})

# 设备预约 API
@app.route('/api/equipment/reservations', methods=['GET'])
@login_required
def api_get_equipment_reservations():
    """获取设备预约记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    equipment_id = request.args.get('equipment_id')
    user_id = request.args.get('user_id')
    status = request.args.get('status')
    
    query = EquipmentReservation.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    reservations = query.order_by(EquipmentReservation.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'reservations': [res.to_dict() for res in reservations.items],
        'total': reservations.total,
        'pages': reservations.pages,
        'current_page': page
    })

@app.route('/api/equipment/reservations', methods=['POST'])
@login_required
def api_create_equipment_reservation():
    """创建设备预约"""
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    
    # 检查时间冲突
    start_time = datetime.fromisoformat(data.get('start_time'))
    end_time = datetime.fromisoformat(data.get('end_time'))
    
    conflict = EquipmentReservation.query.filter_by(
        equipment_id=equipment_id, 
        status='approved'
    ).filter(
        EquipmentReservation.start_time < end_time,
        EquipmentReservation.end_time > start_time
    ).first()
    
    if conflict:
        return jsonify({'error': '预约时间与现有预约冲突'}), 400
    
    reservation = EquipmentReservation(
        equipment_id=equipment_id,
        user_id=session['user_id'],
        project_id=data.get('project_id'),
        purpose=data.get('purpose'),
        start_time=start_time,
        end_time=end_time,
        priority=data.get('priority', 'normal'),
        notes=data.get('notes')
    )
    
    db.session.add(reservation)
    db.session.commit()
    
    return jsonify({'success': True, 'reservation': reservation.to_dict()}), 201

@app.route('/api/equipment/reservations/<int:reservation_id>/approve', methods=['PUT'])
@login_required
def api_approve_equipment_reservation(reservation_id):
    """审批设备预约"""
    user = User.query.get(session['user_id'])
    if user.role not in ['admin', 'supervisor']:
        return jsonify({'error': '权限不足'}), 403
    
    reservation = EquipmentReservation.query.get_or_404(reservation_id)
    data = request.get_json()
    
    action = data.get('action')  # 'approve' or 'reject'
    
    if action == 'approve':
        reservation.status = 'approved'
    elif action == 'reject':
        reservation.status = 'rejected'
    else:
        return jsonify({'error': '无效的操作'}), 400
    
    reservation.approval_notes = data.get('approval_notes')
    reservation.approved_by_id = session['user_id']
    reservation.approved_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'reservation': reservation.to_dict()})

# 设备维护 API
@app.route('/api/equipment/maintenance', methods=['GET'])
@login_required
def api_get_equipment_maintenance():
    """获取设备维护记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    equipment_id = request.args.get('equipment_id')
    maintenance_type = request.args.get('maintenance_type')
    status = request.args.get('status')
    
    query = EquipmentMaintenance.query
    
    if equipment_id:
        query = query.filter_by(equipment_id=equipment_id)
    if maintenance_type:
        query = query.filter_by(maintenance_type=maintenance_type)
    if status:
        query = query.filter_by(status=status)
    
    maintenance_list = query.order_by(EquipmentMaintenance.start_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'maintenance_records': [maint.to_dict() for maint in maintenance_list.items],
        'total': maintenance_list.total,
        'pages': maintenance_list.pages,
        'current_page': page
    })

@app.route('/api/equipment/maintenance', methods=['POST'])
@login_required
def api_create_equipment_maintenance():
    """创建设备维护记录"""
    user = User.query.get(session['user_id'])
    if user.role not in ['admin', 'supervisor']:
        return jsonify({'error': '权限不足'}), 403
    
    data = request.get_json()
    
    maintenance = EquipmentMaintenance(
        equipment_id=data.get('equipment_id'),
        maintenance_type=data.get('maintenance_type'),
        description=data.get('description'),
        performed_by_id=session['user_id'],
        start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
        end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None,
        cost=data.get('cost'),
        status=data.get('status', 'scheduled'),
        notes=data.get('notes')
    )
    
    # 如果是例行维护，更新设备的维护日期
    if data.get('maintenance_type') == 'routine':
        equipment = Equipment.query.get(data.get('equipment_id'))
        equipment.last_maintenance = maintenance.start_date
        if equipment.maintenance_cycle:
            from datetime import timedelta
            equipment.next_maintenance = maintenance.start_date + timedelta(days=equipment.maintenance_cycle)
    
    db.session.add(maintenance)
    db.session.commit()
    
    return jsonify({'success': True, 'maintenance': maintenance.to_dict()}), 201

# 成员历史记录API
@app.route('/api/users/<int:user_id>/history')
@login_required
def api_get_user_history(user_id):
    user = User.query.get_or_404(user_id)
    history = MemberHistory.query.filter_by(member_id=user_id).order_by(MemberHistory.created_at.desc()).all()
    return jsonify([h.to_dict() for h in history])

@app.route('/api/member_history')
@admin_required
def api_get_all_member_history():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    history_query = MemberHistory.query.order_by(MemberHistory.created_at.desc())
    
    # 按操作类型筛选
    action_type = request.args.get('action_type')
    if action_type:
        history_query = history_query.filter_by(action_type=action_type)
    
    # 按时间范围筛选
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date:
        history_query = history_query.filter(MemberHistory.created_at >= start_date)
    if end_date:
        history_query = history_query.filter(MemberHistory.created_at <= end_date)
    
    paginated_history = history_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'history': [h.to_dict() for h in paginated_history.items],
        'total': paginated_history.total,
        'pages': paginated_history.pages,
        'current_page': page
    })

# 示例数据管理API
@app.route('/api/create_sample_data', methods=['POST'])
@admin_required
def api_create_sample_data():
    """管理员创建示例数据"""
    try:
        create_sample_data()
        return jsonify({'message': '示例数据创建成功'}), 200
    except Exception as e:
        return jsonify({'error': f'创建示例数据失败: {str(e)}'}), 500

# 库存管理API
@app.route('/api/inventory', methods=['GET'])
@login_required
def api_get_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    status = request.args.get('status')
    search = request.args.get('search')
    
    query = Inventory.query
    
    if category:
        query = query.filter_by(category=category)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                Inventory.name.contains(search),
                Inventory.brand.contains(search),
                Inventory.model.contains(search)
            )
        )
    
    paginated_inventory = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'inventory': [item.to_dict() for item in paginated_inventory.items],
        'total': paginated_inventory.total,
        'pages': paginated_inventory.pages,
        'current_page': page
    })

@app.route('/api/inventory', methods=['POST'])
@admin_required
def api_create_inventory():
    data = request.get_json()
    
    inventory = Inventory(
        name=data['name'],
        category=data['category'],
        type=data.get('type'),
        brand=data.get('brand'),
        model=data.get('model'),
        specification=data.get('specification'),
        unit=data['unit'],
        current_stock=data.get('current_stock', 0.0),
        min_stock=data.get('min_stock', 0.0),
        max_stock=data.get('max_stock', 0.0),
        unit_price=data.get('unit_price'),
        supplier=data.get('supplier'),
        storage_location=data.get('storage_location'),
        expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
        cas_number=data.get('cas_number'),
        danger_level=data.get('danger_level'),
        notes=data.get('notes'),
        creator_id=session['user_id']
    )
    
    db.session.add(inventory)
    db.session.commit()
    
    # 记录日志
    log_action('CREATE', 'inventory', inventory.id, f'创建库存物品: {inventory.name}')
    
    return jsonify(inventory.to_dict()), 201

@app.route('/api/inventory/<int:inventory_id>', methods=['PUT'])
@admin_required
def api_update_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    data = request.get_json()
    
    old_name = inventory.name
    
    # 更新字段
    for field in ['name', 'category', 'type', 'brand', 'model', 'specification', 
                  'unit', 'min_stock', 'max_stock', 'unit_price', 'supplier', 
                  'storage_location', 'cas_number', 'danger_level', 'notes', 'status']:
        if field in data:
            setattr(inventory, field, data[field])
    
    if 'expiry_date' in data and data['expiry_date']:
        inventory.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
    
    inventory.updated_at = datetime.utcnow()
    db.session.commit()
    
    # 记录日志
    log_action('UPDATE', 'inventory', inventory.id, f'更新库存物品: {old_name} -> {inventory.name}')
    
    return jsonify(inventory.to_dict())

@app.route('/api/inventory/<int:inventory_id>', methods=['DELETE'])
@admin_required
def api_delete_inventory(inventory_id):
    inventory = Inventory.query.get_or_404(inventory_id)
    inventory_name = inventory.name
    
    db.session.delete(inventory)
    db.session.commit()
    
    # 记录日志
    log_action('DELETE', 'inventory', inventory_id, f'删除库存物品: {inventory_name}')
    
    return jsonify({'message': '库存物品删除成功'})

# 库存记录API
@app.route('/api/inventory/<int:inventory_id>/records', methods=['GET'])
@login_required
def api_get_inventory_records(inventory_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    records = InventoryRecord.query.filter_by(inventory_id=inventory_id)\
                                  .order_by(InventoryRecord.created_at.desc())\
                                  .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'records': [record.to_dict() for record in records.items],
        'total': records.total,
        'pages': records.pages,
        'current_page': page
    })

@app.route('/api/inventory/records', methods=['POST'])
@login_required
def api_create_inventory_record():
    data = request.get_json()
    
    inventory = Inventory.query.get_or_404(data['inventory_id'])
    
    record = InventoryRecord(
        inventory_id=data['inventory_id'],
        record_type=data['record_type'],
        quantity=data['quantity'],
        unit_price=data.get('unit_price'),
        total_price=data.get('total_price'),
        batch_number=data.get('batch_number'),
        supplier=data.get('supplier'),
        expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
        purpose=data.get('purpose'),
        project_id=data.get('project_id'),
        operator_id=session['user_id'],
        approver_id=data.get('approver_id'),
        notes=data.get('notes')
    )
    
    # 更新库存数量
    if data['record_type'] == 'in':
        inventory.current_stock += data['quantity']
    elif data['record_type'] == 'out':
        inventory.current_stock -= data['quantity']
    elif data['record_type'] == 'adjust':
        inventory.current_stock = data['quantity']
    
    db.session.add(record)
    db.session.commit()
    
    # 记录日志
    log_action('CREATE', 'inventory_record', record.id, 
              f'{data["record_type"]}库记录: {inventory.name}, 数量: {data["quantity"]}')
    
    return jsonify(record.to_dict()), 201

# 系统日志API
@app.route('/api/system-logs', methods=['GET'])
@admin_required
def api_get_system_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action = request.args.get('action')
    resource = request.args.get('resource')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = SystemLog.query.order_by(SystemLog.created_at.desc())
    
    if action:
        query = query.filter_by(action=action)
    if resource:
        query = query.filter_by(resource=resource)
    if start_date:
        query = query.filter(SystemLog.created_at >= start_date)
    if end_date:
        query = query.filter(SystemLog.created_at <= end_date)
    
    paginated_logs = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in paginated_logs.items],
        'total': paginated_logs.total,
        'pages': paginated_logs.pages,
        'current_page': page
    })

# 课题组管理API
@app.route('/api/groups', methods=['GET'])
@login_required
def api_get_groups():
    groups = Group.query.all()
    return jsonify([group.to_dict() for group in groups])

@app.route('/api/groups/statistics', methods=['GET'])
@login_required
def api_get_groups_statistics():
    total_groups = Group.query.count()
    active_groups = Group.query.filter_by(status='active').count()
    total_members = GroupMember.query.count()
    
    return jsonify({
        'total_groups': total_groups,
        'active_groups': active_groups,
        'total_members': total_members
    })

@app.route('/api/groups', methods=['POST'])
@admin_required
def api_create_group():
    data = request.get_json()
    
    group = Group(
        name=data['name'],
        code=data['code'],
        description=data.get('description'),
        leader_id=data['leader_id'],
        status=data.get('status', 'active')
    )
    
    db.session.add(group)
    db.session.commit()
    
    # 记录日志
    log_action('CREATE', 'group', group.id, f'创建课题组: {group.name}')
    
    return jsonify(group.to_dict()), 201

@app.route('/api/groups/<int:group_id>/members', methods=['GET'])
@login_required
def api_get_group_members(group_id):
    members = GroupMember.query.filter_by(group_id=group_id).all()
    return jsonify([member.to_dict() for member in members])

@app.route('/api/groups/<int:group_id>/members', methods=['POST'])
@admin_required
def api_add_group_member(group_id):
    data = request.get_json()
    
    member = GroupMember(
        group_id=group_id,
        user_id=data['user_id'],
        role=data['role'],
        join_date=datetime.strptime(data['join_date'], '%Y-%m-%d').date(),
        notes=data.get('notes')
    )
    
    db.session.add(member)
    db.session.commit()
    
    # 记录日志
    log_action('CREATE', 'group_member', member.id, f'添加课题组成员: 用户ID {data["user_id"]}')
    
    return jsonify(member.to_dict()), 201

# 权限管理API
@app.route('/api/permissions', methods=['GET'])
@admin_required
def api_get_permissions():
    permissions = Permission.query.filter_by(is_active=True).all()
    return jsonify([perm.to_dict() for perm in permissions])

@app.route('/api/role_permissions/<role>', methods=['GET'])
@admin_required
def api_get_role_permissions(role):
    role_perms = RolePermission.query.filter_by(role=role).all()
    return jsonify([rp.to_dict() for rp in role_perms])

# 辅助函数
def log_action(action, resource, resource_id, description, result='success'):
    """记录系统操作日志"""
    try:
        log = SystemLog(
            user_id=session.get('user_id'),
            action=action,
            resource=resource,
            resource_id=resource_id,
            description=description,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            result=result
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"记录日志失败: {str(e)}")

# 设备统计 API
@app.route('/api/equipment/statistics')
@login_required
def api_equipment_statistics():
    """获取设备统计信息"""
    stats = {
        'total_equipment': Equipment.query.count(),
        'available_equipment': Equipment.query.filter_by(status='available').count(),
        'in_use_equipment': Equipment.query.filter_by(status='in_use').count(),
        'maintenance_equipment': Equipment.query.filter_by(status='maintenance').count(),
        'broken_equipment': Equipment.query.filter_by(status='broken').count(),
        'total_usage_today': EquipmentUsage.query.filter(
            EquipmentUsage.start_time >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).count(),
        'pending_reservations': EquipmentReservation.query.filter_by(status='pending').count(),
        'approved_reservations': EquipmentReservation.query.filter_by(status='approved').filter(
            EquipmentReservation.end_time >= datetime.utcnow()
        ).count(),
        'overdue_maintenance': Equipment.query.filter(
            Equipment.next_maintenance < datetime.utcnow().date()
        ).count() if Equipment.query.filter(Equipment.next_maintenance.isnot(None)).count() > 0 else 0
    }
    
    # 按类别统计
    category_stats = db.session.query(
        Equipment.category, 
        db.func.count(Equipment.id).label('count')
    ).group_by(Equipment.category).all()
    
    stats['by_category'] = [{'category': cat, 'count': count} for cat, count in category_stats]
    
    return jsonify(stats)

def create_sample_data():
    """创建示例数据 - 已禁用避免约束错误"""
    print("示例数据创建已禁用，避免约束错误")
    return

if __name__ == '__main__':
    with app.app_context():
        init_database()
        # 创建示例数据
        # try:
        #     create_sample_data()
        # except Exception as e:
        #     print(f"创建示例数据失败: {e}")
    app.run(debug=True, host='0.0.0.0', port=5000)