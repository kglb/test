"""
Database models for Laboratory Management System
"""
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and member information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Member information
    phone = db.Column(db.String(20))
    student_id = db.Column(db.String(50), unique=True)
    role = db.Column(db.String(20), default='student')  # admin, teacher, student
    grade = db.Column(db.String(20))  # undergraduate, master, phd, teacher
    major = db.Column(db.String(100))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    leave_date = db.Column(db.DateTime)
    
    # Relationships
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    created_projects = db.relationship('Project', foreign_keys='Project.creator_id', backref='creator')
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assignee_id', backref='assignee')
    announcements = db.relationship('Announcement', backref='author', lazy=True)
    equipment_usages = db.relationship('EquipmentUsage', foreign_keys='EquipmentUsage.user_id', backref='user', lazy=True)
    equipment_reservations = db.relationship('EquipmentReservation', foreign_keys='EquipmentReservation.user_id', backref='user', lazy=True)
    inventory_records = db.relationship('InventoryRecord', foreign_keys='InventoryRecord.user_id', backref='user', lazy=True)
    member_histories = db.relationship('MemberHistory', foreign_keys='MemberHistory.user_id', backref='member')
    system_logs = db.relationship('SystemLog', backref='user', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'student_id': self.student_id,
            'role': self.role,
            'grade': self.grade,
            'major': self.major,
            'is_active': self.is_active,
            'join_date': self.join_date.isoformat() if self.join_date else None,
            'leave_date': self.leave_date.isoformat() if self.leave_date else None,
            'group_id': self.group_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Group(db.Model):
    """Research group model"""
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    members = db.relationship('User', backref='group', lazy=True, foreign_keys='User.group_id')
    projects = db.relationship('Project', backref='group', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'leader_id': self.leader_id,
            'member_count': len(self.members) if self.members else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MemberHistory(db.Model):
    """Member history tracking for entry/exit and changes"""
    __tablename__ = 'member_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # join, leave, role_change, etc.
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    note = db.Column(db.Text)
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    operator = db.relationship('User', foreign_keys=[operator_id], backref='operated_histories')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'note': self.note,
            'operator_id': self.operator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Project(db.Model):
    """Project model"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, completed, archived
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'creator_id': self.creator_id,
            'group_id': self.group_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'task_count': len(self.tasks) if self.tasks else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Task model"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    priority = db.Column(db.String(20), default='medium')
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Equipment(db.Model):
    """Equipment model"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # microscope, centrifuge, pcr, etc.
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    manufacturer = db.Column(db.String(100))
    purchase_date = db.Column(db.DateTime)
    purchase_cost = db.Column(db.Float)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='available')  # available, in_use, maintenance, retired
    description = db.Column(db.Text)
    
    maintenance_interval = db.Column(db.Integer)  # days
    last_maintenance = db.Column(db.DateTime)
    
    # Relationships
    usage_records = db.relationship('EquipmentUsage', backref='equipment', lazy=True)
    reservations = db.relationship('EquipmentReservation', backref='equipment', lazy=True)
    maintenance_records = db.relationship('EquipmentMaintenance', backref='equipment', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'model': self.model,
            'serial_number': self.serial_number,
            'manufacturer': self.manufacturer,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_cost': self.purchase_cost,
            'location': self.location,
            'status': self.status,
            'description': self.description,
            'maintenance_interval': self.maintenance_interval,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EquipmentUsage(db.Model):
    """Equipment usage record"""
    __tablename__ = 'equipment_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    purpose = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    status_before = db.Column(db.String(50))
    status_after = db.Column(db.String(50))
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'project_id': self.project_id,
            'status_before': self.status_before,
            'status_after': self.status_after,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EquipmentReservation(db.Model):
    """Equipment reservation model"""
    __tablename__ = 'equipment_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    purpose = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    priority = db.Column(db.String(20), default='normal')
    
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_time = db.Column(db.DateTime)
    approval_note = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'priority': self.priority,
            'approver_id': self.approver_id,
            'approval_time': self.approval_time.isoformat() if self.approval_time else None,
            'approval_note': self.approval_note,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class EquipmentMaintenance(db.Model):
    """Equipment maintenance record"""
    __tablename__ = 'equipment_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    
    maintenance_type = db.Column(db.String(50))  # routine, repair, calibration, upgrade
    description = db.Column(db.Text)
    cost = db.Column(db.Float)
    performed_by = db.Column(db.String(100))
    maintenance_date = db.Column(db.DateTime, nullable=False)
    next_maintenance = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'cost': self.cost,
            'performed_by': self.performed_by,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Inventory(db.Model):
    """Inventory item model for reagents and consumables"""
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # reagent, consumable, chemical, etc.
    specification = db.Column(db.String(100))
    unit = db.Column(db.String(20))  # ml, g, pcs, etc.
    
    quantity = db.Column(db.Float, default=0)
    min_quantity = db.Column(db.Float, default=0)  # Alert threshold
    
    supplier = db.Column(db.String(100))
    catalog_number = db.Column(db.String(100))
    storage_location = db.Column(db.String(200))
    expiry_date = db.Column(db.DateTime)
    
    unit_price = db.Column(db.Float)
    description = db.Column(db.Text)
    
    # Relationships
    records = db.relationship('InventoryRecord', backref='item', lazy=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'specification': self.specification,
            'unit': self.unit,
            'quantity': self.quantity,
            'min_quantity': self.min_quantity,
            'supplier': self.supplier,
            'catalog_number': self.catalog_number,
            'storage_location': self.storage_location,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'unit_price': self.unit_price,
            'description': self.description,
            'is_low_stock': self.quantity <= self.min_quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class InventoryRecord(db.Model):
    """Inventory in/out record"""
    __tablename__ = 'inventory_records'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    record_type = db.Column(db.String(20), nullable=False)  # in, out
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float)
    
    purpose = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'user_id': self.user_id,
            'record_type': self.record_type,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'purpose': self.purpose,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Announcement(db.Model):
    """Announcement model"""
    __tablename__ = 'announcements'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    
    is_pinned = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'priority': self.priority,
            'is_pinned': self.is_pinned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Permission(db.Model):
    """Permission model"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    module = db.Column(db.String(50))  # user, equipment, inventory, project, etc.
    description = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'module': self.module,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RolePermission(db.Model):
    """Role-Permission mapping"""
    __tablename__ = 'role_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)
    
    permission = db.relationship('Permission', backref='role_mappings')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'permission_id': self.permission_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemLog(db.Model):
    """System audit log"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50))
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'module': self.module,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
