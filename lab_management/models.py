from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    real_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, pi, supervisor, student
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    major = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(10), nullable=True)
    research_direction = db.Column(db.String(200), nullable=True)  # 研究方向
    advisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 导师ID
    join_date = db.Column(db.Date, nullable=True)  # 入组时间
    leave_date = db.Column(db.Date, nullable=True)  # 离组时间
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, alumni
    bio = db.Column(db.Text, nullable=True)  # 个人简介
    office_location = db.Column(db.String(100), nullable=True)  # 办公地点
    emergency_contact = db.Column(db.String(100), nullable=True)  # 紧急联系人
    emergency_phone = db.Column(db.String(20), nullable=True)  # 紧急联系电话
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    advisor = db.relationship('User', remote_side=[id], backref='advisees')  # 导师-学生关系
    created_projects = db.relationship('Project', foreign_keys='Project.creator_id', backref='creator', lazy='dynamic')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee', lazy='dynamic')
    created_tasks = db.relationship('Task', foreign_keys='Task.creator_id', backref='task_creator', lazy='dynamic')
    created_announcements = db.relationship('Announcement', backref='creator', lazy='dynamic')
    # 成员历史记录关系
    member_history = db.relationship('MemberHistory', foreign_keys='MemberHistory.member_id', lazy='dynamic', cascade='all, delete-orphan')
    operated_history = db.relationship('MemberHistory', foreign_keys='MemberHistory.operator_id', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'real_name': self.real_name,
            'role': self.role,
            'student_id': self.student_id,
            'phone': self.phone,
            'major': self.major,
            'grade': self.grade,
            'research_direction': self.research_direction,
            'advisor_id': self.advisor_id,
            'advisor_name': self.advisor.real_name if self.advisor else None,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
            'status': self.status,
            'bio': self.bio,
            'office_location': self.office_location,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            result.update({
                'emergency_contact': self.emergency_contact,
                'emergency_phone': self.emergency_phone
            })
            
        return result

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, completed, on_hold
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    members = db.relationship('ProjectMember', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy='dynamic')
    
    def to_dict(self, include_members=False, include_tasks=False):
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_members:
            result['members'] = [member.to_dict() for member in self.members]
        
        if include_tasks:
            result['tasks'] = [task.to_dict() for task in self.tasks]
            
        return result

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='member')  # leader, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='project_memberships')
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'user_username': self.user.username if self.user else None,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='todo')  # todo, in_progress, completed
    priority = db.Column(db.String(20), nullable=False, default='medium')  # low, medium, high
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee.real_name if self.assignee else None,
            'creator_id': self.creator_id,
            'creator_name': self.task_creator.real_name if self.task_creator else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Announcement(db.Model):
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_important = db.Column(db.Boolean, default=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_important': self.is_important,
            'creator_id': self.creator_id,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 设备管理模块相关模型

class Equipment(db.Model):
    """实验设备模型"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 设备名称
    model = db.Column(db.String(100), nullable=True)  # 设备型号
    serial_number = db.Column(db.String(100), unique=True, nullable=False)  # 设备序列号
    category = db.Column(db.String(50), nullable=False)  # 设备类别
    manufacturer = db.Column(db.String(200), nullable=True)  # 生产厂商
    purchase_date = db.Column(db.Date, nullable=True)  # 购买日期
    purchase_price = db.Column(db.Numeric(10, 2), nullable=True)  # 购买价格
    location = db.Column(db.String(200), nullable=True)  # 存放位置
    status = db.Column(db.String(20), nullable=False, default='available')  # 设备状态: available, in_use, maintenance, broken, retired
    description = db.Column(db.Text, nullable=True)  # 设备描述
    specifications = db.Column(db.Text, nullable=True)  # 设备规格
    maintenance_cycle = db.Column(db.Integer, nullable=True)  # 维护周期（天）
    last_maintenance = db.Column(db.Date, nullable=True)  # 上次维护日期
    next_maintenance = db.Column(db.Date, nullable=True)  # 下次维护日期
    responsible_person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 负责人
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 创建人
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    responsible_person = db.relationship('User', foreign_keys=[responsible_person_id], backref='managed_equipment')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_equipment')
    usage_records = db.relationship('EquipmentUsage', backref='equipment', lazy='dynamic', cascade='all, delete-orphan')
    reservations = db.relationship('EquipmentReservation', backref='equipment', lazy='dynamic', cascade='all, delete-orphan')
    maintenance_records = db.relationship('EquipmentMaintenance', backref='equipment', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_usage=False, include_reservations=False):
        result = {
            'id': self.id,
            'name': self.name,
            'model': self.model,
            'serial_number': self.serial_number,
            'category': self.category,
            'manufacturer': self.manufacturer,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'location': self.location,
            'status': self.status,
            'description': self.description,
            'specifications': self.specifications,
            'maintenance_cycle': self.maintenance_cycle,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'responsible_person_id': self.responsible_person_id,
            'responsible_person_name': self.responsible_person.real_name if self.responsible_person else None,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.real_name if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_usage:
            result['usage_records'] = [usage.to_dict() for usage in self.usage_records.order_by(EquipmentUsage.start_time.desc()).limit(10)]
        
        if include_reservations:
            result['active_reservations'] = [res.to_dict() for res in self.reservations.filter_by(status='approved').filter(EquipmentReservation.end_time >= datetime.utcnow())]
            
        return result

class EquipmentUsage(db.Model):
    """设备使用记录模型"""
    __tablename__ = 'equipment_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 关联项目
    purpose = db.Column(db.String(500), nullable=False)  # 使用目的
    start_time = db.Column(db.DateTime, nullable=False)  # 开始使用时间
    end_time = db.Column(db.DateTime, nullable=True)  # 结束使用时间
    status = db.Column(db.String(20), nullable=False, default='in_use')  # 状态: in_use, completed, interrupted
    notes = db.Column(db.Text, nullable=True)  # 使用备注
    condition_before = db.Column(db.String(20), nullable=False, default='good')  # 使用前状态: excellent, good, fair, poor
    condition_after = db.Column(db.String(20), nullable=True)  # 使用后状态
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='equipment_usage_records')
    project = db.relationship('Project', backref='equipment_usage_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'purpose': self.purpose,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'notes': self.notes,
            'condition_before': self.condition_before,
            'condition_after': self.condition_after,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentReservation(db.Model):
    """设备预约模型"""
    __tablename__ = 'equipment_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    purpose = db.Column(db.String(500), nullable=False)  # 预约目的
    start_time = db.Column(db.DateTime, nullable=False)  # 预约开始时间
    end_time = db.Column(db.DateTime, nullable=False)  # 预约结束时间
    status = db.Column(db.String(20), nullable=False, default='pending')  # 状态: pending, approved, rejected, cancelled, completed
    priority = db.Column(db.String(20), nullable=False, default='normal')  # 优先级: low, normal, high, urgent
    notes = db.Column(db.Text, nullable=True)  # 预约备注
    approval_notes = db.Column(db.Text, nullable=True)  # 审批备注
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 审批人
    approved_at = db.Column(db.DateTime, nullable=True)  # 审批时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='equipment_reservations')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_reservations')
    project = db.relationship('Project', backref='equipment_reservations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'purpose': self.purpose,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'priority': self.priority,
            'notes': self.notes,
            'approval_notes': self.approval_notes,
            'approved_by_id': self.approved_by_id,
            'approved_by_name': self.approved_by.real_name if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentMaintenance(db.Model):
    """设备维护记录模型"""
    __tablename__ = 'equipment_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # 维护类型: routine, repair, calibration, upgrade
    description = db.Column(db.Text, nullable=False)  # 维护描述
    performed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 执行人
    start_date = db.Column(db.Date, nullable=False)  # 维护开始日期
    end_date = db.Column(db.Date, nullable=True)  # 维护结束日期
    cost = db.Column(db.Numeric(10, 2), nullable=True)  # 维护成本
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # 状态: scheduled, in_progress, completed, cancelled
    notes = db.Column(db.Text, nullable=True)  # 维护备注
    next_maintenance_date = db.Column(db.Date, nullable=True)  # 下次维护日期
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    performed_by = db.relationship('User', backref='performed_maintenance')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name if self.equipment else None,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'performed_by_id': self.performed_by_id,
            'performed_by_name': self.performed_by.real_name if self.performed_by else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'cost': float(self.cost) if self.cost else None,
            'status': self.status,
            'notes': self.notes,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MemberHistory(db.Model):
    """成员历史记录模型"""
    __tablename__ = 'member_history'
    
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # join, leave, role_change, status_change, profile_update
    description = db.Column(db.Text, nullable=False)  # 变更描述
    old_value = db.Column(db.Text, nullable=True)  # 变更前的值
    new_value = db.Column(db.Text, nullable=True)  # 变更后的值
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 操作人
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    member = db.relationship('User', foreign_keys=[member_id], overlaps="member_history")
    operator = db.relationship('User', foreign_keys=[operator_id], overlaps="operated_history")
    
    def to_dict(self):
        return {
            'id': self.id,
            'member_id': self.member_id,
            'member_name': self.member.real_name if self.member else None,
            'action_type': self.action_type,
            'description': self.description,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Inventory(db.Model):
    """库存管理模型"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 物品名称
    category = db.Column(db.String(50), nullable=False)  # 类别：reagent, consumable, equipment_part
    type = db.Column(db.String(50), nullable=True)  # 具体类型
    brand = db.Column(db.String(100), nullable=True)  # 品牌
    model = db.Column(db.String(100), nullable=True)  # 型号
    specification = db.Column(db.String(200), nullable=True)  # 规格
    unit = db.Column(db.String(20), nullable=False)  # 单位
    current_stock = db.Column(db.Float, default=0.0)  # 当前库存
    min_stock = db.Column(db.Float, default=0.0)  # 最小库存阈值
    max_stock = db.Column(db.Float, default=0.0)  # 最大库存阈值
    unit_price = db.Column(db.Float, nullable=True)  # 单价
    supplier = db.Column(db.String(200), nullable=True)  # 供应商
    storage_location = db.Column(db.String(100), nullable=True)  # 存储位置
    expiry_date = db.Column(db.Date, nullable=True)  # 过期日期
    cas_number = db.Column(db.String(50), nullable=True)  # CAS号（试剂用）
    danger_level = db.Column(db.String(20), nullable=True)  # 危险等级
    status = db.Column(db.String(20), default='active')  # active, inactive, expired
    notes = db.Column(db.Text, nullable=True)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关系
    creator = db.relationship('User', backref='created_inventory')
    inventory_records = db.relationship('InventoryRecord', backref='inventory_item', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'type': self.type,
            'brand': self.brand,
            'model': self.model,
            'specification': self.specification,
            'unit': self.unit,
            'current_stock': self.current_stock,
            'min_stock': self.min_stock,
            'max_stock': self.max_stock,
            'unit_price': self.unit_price,
            'supplier': self.supplier,
            'storage_location': self.storage_location,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'cas_number': self.cas_number,
            'danger_level': self.danger_level,
            'status': self.status,
            'notes': self.notes,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InventoryRecord(db.Model):
    """库存记录模型"""
    __tablename__ = 'inventory_records'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    record_type = db.Column(db.String(20), nullable=False)  # in, out, adjust, expired
    quantity = db.Column(db.Float, nullable=False)  # 数量（正数为入库，负数为出库）
    unit_price = db.Column(db.Float, nullable=True)  # 单价
    total_price = db.Column(db.Float, nullable=True)  # 总价
    batch_number = db.Column(db.String(100), nullable=True)  # 批号
    supplier = db.Column(db.String(200), nullable=True)  # 供应商
    expiry_date = db.Column(db.Date, nullable=True)  # 过期日期
    purpose = db.Column(db.String(200), nullable=True)  # 用途/目的
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 关联项目
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 操作人
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 审批人
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    notes = db.Column(db.Text, nullable=True)  # 备注
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    project = db.relationship('Project', backref='inventory_records')
    operator = db.relationship('User', foreign_keys=[operator_id], backref='operated_inventory_records')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_inventory_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'inventory_id': self.inventory_id,
            'inventory_name': self.inventory_item.name if self.inventory_item else None,
            'record_type': self.record_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'batch_number': self.batch_number,
            'supplier': self.supplier,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'purpose': self.purpose,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'operator_id': self.operator_id,
            'operator_name': self.operator.real_name if self.operator else None,
            'approver_id': self.approver_id,
            'approver_name': self.approver.real_name if self.approver else None,
            'approval_status': self.approval_status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemLog(db.Model):
    """系统日志模型"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # 操作类型
    resource = db.Column(db.String(100), nullable=False)  # 资源类型
    resource_id = db.Column(db.Integer, nullable=True)  # 资源ID
    description = db.Column(db.Text, nullable=False)  # 详细描述
    ip_address = db.Column(db.String(45), nullable=True)  # IP地址
    user_agent = db.Column(db.String(500), nullable=True)  # 用户代理
    result = db.Column(db.String(20), default='success')  # success, failed, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='system_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else 'System',
            'action': self.action,
            'resource': self.resource,
            'resource_id': self.resource_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'result': self.result,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Group(db.Model):
    """课题组模型"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # 课题组名称
    code = db.Column(db.String(50), unique=True, nullable=False)  # 课题组代码
    description = db.Column(db.Text, nullable=True)  # 描述
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # 组长/PI
    department = db.Column(db.String(200), nullable=True)  # 所属院系
    institution = db.Column(db.String(200), nullable=True)  # 所属机构
    research_area = db.Column(db.Text, nullable=True)  # 研究领域
    budget = db.Column(db.Float, nullable=True)  # 预算
    status = db.Column(db.String(20), default='active')  # active, inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    leader = db.relationship('User', backref='managed_groups')
    members = db.relationship('GroupMember', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'leader_id': self.leader_id,
            'leader_name': self.leader.real_name if self.leader else None,
            'department': self.department,
            'institution': self.institution,
            'research_area': self.research_area,
            'budget': self.budget,
            'status': self.status,
            'member_count': self.members.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class GroupMember(db.Model):
    """课题组成员关系模型"""
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # pi, admin, member, visitor
    join_date = db.Column(db.Date, nullable=False)
    leave_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, inactive
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='group_memberships')
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('group_id', 'user_id', name='unique_group_user'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'group_name': self.group.name if self.group else None,
            'user_id': self.user_id,
            'user_name': self.user.real_name if self.user else None,
            'role': self.role,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Permission(db.Model):
    """权限模型"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # 权限名称
    code = db.Column(db.String(100), unique=True, nullable=False)  # 权限代码
    resource = db.Column(db.String(100), nullable=False)  # 资源类型
    action = db.Column(db.String(50), nullable=False)  # 操作类型
    description = db.Column(db.Text, nullable=True)  # 描述
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'resource': self.resource,
            'action': self.action,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RolePermission(db.Model):
    """角色权限关系模型"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=False)  # admin, pi, supervisor, student
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    permission = db.relationship('Permission', backref='role_assignments')
    granter = db.relationship('User', backref='granted_permissions')
    
    # 唯一约束
    __table_args__ = (db.UniqueConstraint('role', 'permission_id', name='unique_role_permission'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'permission_id': self.permission_id,
            'permission_name': self.permission.name if self.permission else None,
            'permission_code': self.permission.code if self.permission else None,
            'granted_by': self.granted_by,
            'granter_name': self.granter.real_name if self.granter else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
