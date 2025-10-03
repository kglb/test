from models import db
from datetime import datetime

# 实验设备管理模块

class Equipment(db.Model):
    """实验设备基础信息表"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_code = db.Column(db.String(50), unique=True, nullable=False)  # 设备编号
    name = db.Column(db.String(200), nullable=False)  # 设备名称
    category = db.Column(db.String(100), nullable=False)  # 设备类别
    model = db.Column(db.String(100), nullable=True)  # 型号
    manufacturer = db.Column(db.String(200), nullable=True)  # 制造商
    serial_number = db.Column(db.String(100), nullable=True)  # 序列号
    purchase_date = db.Column(db.Date, nullable=True)  # 购买日期
    purchase_price = db.Column(db.Decimal(10, 2), nullable=True)  # 购买价格
    location = db.Column(db.String(200), nullable=True)  # 存放位置
    status = db.Column(db.String(20), nullable=False, default='available')  # 设备状态：available, in_use, maintenance, damaged, retired
    condition = db.Column(db.String(20), nullable=False, default='good')  # 设备状况：excellent, good, fair, poor
    description = db.Column(db.Text, nullable=True)  # 设备描述
    specifications = db.Column(db.Text, nullable=True)  # 技术规格
    usage_instructions = db.Column(db.Text, nullable=True)  # 使用说明
    safety_notes = db.Column(db.Text, nullable=True)  # 安全注意事项
    responsible_person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 负责人
    warranty_expiry = db.Column(db.Date, nullable=True)  # 保修到期日期
    last_maintenance = db.Column(db.Date, nullable=True)  # 上次维护日期
    next_maintenance = db.Column(db.Date, nullable=True)  # 下次维护日期
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    responsible_person = db.relationship('User', backref='managed_equipment')
    usage_records = db.relationship('EquipmentUsage', backref='equipment', lazy='dynamic')
    reservations = db.relationship('EquipmentReservation', backref='equipment', lazy='dynamic')
    maintenance_records = db.relationship('EquipmentMaintenance', backref='equipment', lazy='dynamic')
    
    def to_dict(self, include_relations=False):
        result = {
            'id': self.id,
            'equipment_code': self.equipment_code,
            'name': self.name,
            'category': self.category,
            'model': self.model,
            'manufacturer': self.manufacturer,
            'serial_number': self.serial_number,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_price': float(self.purchase_price) if self.purchase_price else None,
            'location': self.location,
            'status': self.status,
            'condition': self.condition,
            'description': self.description,
            'specifications': self.specifications,
            'usage_instructions': self.usage_instructions,
            'safety_notes': self.safety_notes,
            'responsible_person_id': self.responsible_person_id,
            'responsible_person_name': self.responsible_person.real_name if self.responsible_person else None,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relations:
            current_usage = self.usage_records.filter_by(status='in_use').first()
            result['current_usage'] = current_usage.to_dict() if current_usage else None
            result['pending_reservations'] = [r.to_dict() for r in self.reservations.filter_by(status='pending').all()]
            
        return result

class EquipmentUsage(db.Model):
    """设备使用记录表"""
    __tablename__ = 'equipment_usage'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)  # 关联项目
    purpose = db.Column(db.String(500), nullable=False)  # 使用目的
    start_time = db.Column(db.DateTime, nullable=False)  # 开始使用时间
    end_time = db.Column(db.DateTime, nullable=True)  # 结束使用时间
    planned_duration = db.Column(db.Integer, nullable=True)  # 计划使用时长（小时）
    actual_duration = db.Column(db.Integer, nullable=True)  # 实际使用时长（小时）
    status = db.Column(db.String(20), nullable=False, default='in_use')  # 状态：in_use, completed, cancelled
    notes = db.Column(db.Text, nullable=True)  # 使用备注
    condition_before = db.Column(db.String(20), nullable=True)  # 使用前设备状况
    condition_after = db.Column(db.String(20), nullable=True)  # 使用后设备状况
    issues_reported = db.Column(db.Text, nullable=True)  # 使用中发现的问题
    approval_status = db.Column(db.String(20), nullable=False, default='pending')  # 审批状态：pending, approved, rejected
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 审批人
    approved_at = db.Column(db.DateTime, nullable=True)  # 审批时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='equipment_usage_records')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    project = db.relationship('Project', backref='equipment_usage_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name,
            'equipment_code': self.equipment.equipment_code,
            'user_id': self.user_id,
            'user_name': self.user.real_name,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'purpose': self.purpose,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'planned_duration': self.planned_duration,
            'actual_duration': self.actual_duration,
            'status': self.status,
            'notes': self.notes,
            'condition_before': self.condition_before,
            'condition_after': self.condition_after,
            'issues_reported': self.issues_reported,
            'approval_status': self.approval_status,
            'approved_by_id': self.approved_by_id,
            'approved_by_name': self.approved_by.real_name if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentReservation(db.Model):
    """设备预约表"""
    __tablename__ = 'equipment_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    purpose = db.Column(db.String(500), nullable=False)  # 预约目的
    reserved_start = db.Column(db.DateTime, nullable=False)  # 预约开始时间
    reserved_end = db.Column(db.DateTime, nullable=False)  # 预约结束时间
    status = db.Column(db.String(20), nullable=False, default='pending')  # 状态：pending, approved, rejected, cancelled, completed
    priority = db.Column(db.String(20), nullable=False, default='normal')  # 优先级：low, normal, high, urgent
    special_requirements = db.Column(db.Text, nullable=True)  # 特殊要求
    approval_status = db.Column(db.String(20), nullable=False, default='pending')  # 审批状态
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)  # 拒绝原因
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref='equipment_reservations')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id])
    project = db.relationship('Project', backref='equipment_reservations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name,
            'equipment_code': self.equipment.equipment_code,
            'user_id': self.user_id,
            'user_name': self.user.real_name,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'purpose': self.purpose,
            'reserved_start': self.reserved_start.isoformat() if self.reserved_start else None,
            'reserved_end': self.reserved_end.isoformat() if self.reserved_end else None,
            'status': self.status,
            'priority': self.priority,
            'special_requirements': self.special_requirements,
            'approval_status': self.approval_status,
            'approved_by_id': self.approved_by_id,
            'approved_by_name': self.approved_by.real_name if self.approved_by else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EquipmentMaintenance(db.Model):
    """设备维护记录表"""
    __tablename__ = 'equipment_maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # 维护类型：routine, repair, calibration, upgrade
    description = db.Column(db.Text, nullable=False)  # 维护描述
    performed_by = db.Column(db.String(200), nullable=False)  # 维护人员
    maintenance_date = db.Column(db.Date, nullable=False)  # 维护日期
    cost = db.Column(db.Decimal(10, 2), nullable=True)  # 维护费用
    parts_replaced = db.Column(db.Text, nullable=True)  # 更换部件
    condition_before = db.Column(db.String(20), nullable=True)  # 维护前状况
    condition_after = db.Column(db.String(20), nullable=True)  # 维护后状况
    next_maintenance_date = db.Column(db.Date, nullable=True)  # 下次维护日期
    status = db.Column(db.String(20), nullable=False, default='completed')  # 状态：scheduled, in_progress, completed
    notes = db.Column(db.Text, nullable=True)  # 备注
    attachments = db.Column(db.Text, nullable=True)  # 附件路径（JSON格式）
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    created_by = db.relationship('User', backref='maintenance_records')
    
    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'equipment_name': self.equipment.name,
            'equipment_code': self.equipment.equipment_code,
            'maintenance_type': self.maintenance_type,
            'description': self.description,
            'performed_by': self.performed_by,
            'maintenance_date': self.maintenance_date.isoformat() if self.maintenance_date else None,
            'cost': float(self.cost) if self.cost else None,
            'parts_replaced': self.parts_replaced,
            'condition_before': self.condition_before,
            'condition_after': self.condition_after,
            'next_maintenance_date': self.next_maintenance_date.isoformat() if self.next_maintenance_date else None,
            'status': self.status,
            'notes': self.notes,
            'attachments': self.attachments,
            'created_by_id': self.created_by_id,
            'created_by_name': self.created_by.real_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }