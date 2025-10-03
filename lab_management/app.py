"""
Laboratory Management System - Main Application
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
from functools import wraps
import os

from models import (
    db, User, Group, MemberHistory, Project, Task, Equipment,
    EquipmentUsage, EquipmentReservation, EquipmentMaintenance,
    Inventory, InventoryRecord, Announcement, Permission,
    RolePermission, SystemLog
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lab_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        user = db.session.get(User, session['user_id'])
        if not user or user.role not in ['admin', 'teacher']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        return f(*args, **kwargs)
    return decorated_function


def log_action(action, module, target_type=None, target_id=None, details=None):
    """Log system action"""
    try:
        log = SystemLog(
            user_id=session.get('user_id'),
            action=action,
            module=module,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging action: {e}")


# ============ Authentication Routes ============

@app.route('/')
def index():
    """Main entry point"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('landing'))


@app.route('/landing')
def landing():
    """Landing page for unauthenticated users"""
    return render_template('landing.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        log_action('login_failed', 'auth', details=f'Username: {username}')
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403
    
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    
    log_action('login', 'auth', details=f'User: {username}')
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })


@app.route('/logout', methods=['POST'])
def logout():
    """Logout handler"""
    user_id = session.get('user_id')
    session.clear()
    log_action('logout', 'auth')
    return jsonify({'message': 'Logout successful'})


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


# ============ User Management Routes ============

@app.route('/users')
@login_required
def users_page():
    """User management page"""
    return render_template('users.html')


@app.route('/api/users', methods=['GET'])
@login_required
def get_users():
    """Get all users"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get specific user"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())


@app.route('/api/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    data = request.get_json()
    
    # Check for existing username or email
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data.get('username'),
        email=data.get('email'),
        name=data.get('name'),
        phone=data.get('phone'),
        student_id=data.get('student_id'),
        role=data.get('role', 'student'),
        grade=data.get('grade'),
        major=data.get('major'),
        group_id=data.get('group_id')
    )
    user.set_password(data.get('password', 'password123'))
    
    db.session.add(user)
    db.session.commit()
    
    # Log member join
    history = MemberHistory(
        user_id=user.id,
        action='join',
        new_value=f"Role: {user.role}",
        operator_id=session.get('user_id')
    )
    db.session.add(history)
    db.session.commit()
    
    log_action('create_user', 'user', 'User', user.id, f'Created user: {user.username}')
    
    return jsonify(user.to_dict()), 201


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    old_data = user.to_dict()
    
    # Update fields
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    if 'phone' in data:
        user.phone = data['phone']
    if 'role' in data and user.role != data['role']:
        history = MemberHistory(
            user_id=user.id,
            action='role_change',
            old_value=user.role,
            new_value=data['role'],
            operator_id=session.get('user_id')
        )
        db.session.add(history)
        user.role = data['role']
    if 'grade' in data:
        user.grade = data['grade']
    if 'major' in data:
        user.major = data['major']
    if 'group_id' in data:
        user.group_id = data['group_id']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'password' in data:
        user.set_password(data['password'])
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_user', 'user', 'User', user.id, f'Updated user: {user.username}')
    
    return jsonify(user.to_dict())


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Log member leave
    history = MemberHistory(
        user_id=user.id,
        action='leave',
        old_value=f"Role: {user.role}",
        operator_id=session.get('user_id')
    )
    db.session.add(history)
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    log_action('delete_user', 'user', 'User', user_id, f'Deleted user: {username}')
    
    return jsonify({'message': 'User deleted successfully'})


@app.route('/api/users/<int:user_id>/history', methods=['GET'])
@login_required
def get_user_history(user_id):
    """Get user history"""
    histories = MemberHistory.query.filter_by(user_id=user_id).order_by(MemberHistory.created_at.desc()).all()
    return jsonify([h.to_dict() for h in histories])


# ============ Group Management Routes ============

@app.route('/groups')
@login_required
def groups_page():
    """Groups page"""
    return render_template('groups.html')


@app.route('/api/groups', methods=['GET'])
@login_required
def get_groups():
    """Get all groups"""
    groups = Group.query.all()
    return jsonify([group.to_dict() for group in groups])


@app.route('/api/groups', methods=['POST'])
@admin_required
def create_group():
    """Create group"""
    data = request.get_json()
    
    group = Group(
        name=data.get('name'),
        description=data.get('description'),
        leader_id=data.get('leader_id')
    )
    
    db.session.add(group)
    db.session.commit()
    
    log_action('create_group', 'group', 'Group', group.id, f'Created group: {group.name}')
    
    return jsonify(group.to_dict()), 201


@app.route('/api/groups/<int:group_id>', methods=['PUT'])
@admin_required
def update_group(group_id):
    """Update group"""
    group = db.session.get(Group, group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        group.name = data['name']
    if 'description' in data:
        group.description = data['description']
    if 'leader_id' in data:
        group.leader_id = data['leader_id']
    
    group.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_group', 'group', 'Group', group.id, f'Updated group: {group.name}')
    
    return jsonify(group.to_dict())


@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    """Delete group"""
    group = db.session.get(Group, group_id)
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    name = group.name
    db.session.delete(group)
    db.session.commit()
    
    log_action('delete_group', 'group', 'Group', group_id, f'Deleted group: {name}')
    
    return jsonify({'message': 'Group deleted successfully'})


# ============ Project Management Routes ============

@app.route('/projects')
@login_required
def projects_page():
    """Projects page"""
    return render_template('projects.html')


@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    """Get all projects"""
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])


@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    """Create project"""
    data = request.get_json()
    
    project = Project(
        name=data.get('name'),
        description=data.get('description'),
        status=data.get('status', 'active'),
        priority=data.get('priority', 'medium'),
        creator_id=session.get('user_id'),
        group_id=data.get('group_id')
    )
    
    if data.get('start_date'):
        project.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    if data.get('end_date'):
        project.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    
    db.session.add(project)
    db.session.commit()
    
    log_action('create_project', 'project', 'Project', project.id, f'Created project: {project.name}')
    
    return jsonify(project.to_dict()), 201


@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    """Update project"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'status' in data:
        project.status = data['status']
    if 'priority' in data:
        project.priority = data['priority']
    if 'start_date' in data:
        project.start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
    if 'end_date' in data:
        project.end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_project', 'project', 'Project', project.id, f'Updated project: {project.name}')
    
    return jsonify(project.to_dict())


@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    """Delete project"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    name = project.name
    db.session.delete(project)
    db.session.commit()
    
    log_action('delete_project', 'project', 'Project', project_id, f'Deleted project: {name}')
    
    return jsonify({'message': 'Project deleted successfully'})


# ============ Task Management Routes ============

@app.route('/tasks')
@login_required
def tasks_page():
    """Tasks page"""
    return render_template('tasks.html')


@app.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks"""
    project_id = request.args.get('project_id')
    if project_id:
        tasks = Task.query.filter_by(project_id=project_id).all()
    else:
        tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@app.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Create task"""
    data = request.get_json()
    
    task = Task(
        title=data.get('title'),
        description=data.get('description'),
        status=data.get('status', 'pending'),
        priority=data.get('priority', 'medium'),
        project_id=data.get('project_id'),
        assignee_id=data.get('assignee_id')
    )
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    db.session.add(task)
    db.session.commit()
    
    log_action('create_task', 'task', 'Task', task.id, f'Created task: {task.title}')
    
    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update task"""
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = data['status']
        if data['status'] == 'completed':
            task.completed_at = datetime.utcnow()
    if 'priority' in data:
        task.priority = data['priority']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_task', 'task', 'Task', task.id, f'Updated task: {task.title}')
    
    return jsonify(task.to_dict())


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete task"""
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    title = task.title
    db.session.delete(task)
    db.session.commit()
    
    log_action('delete_task', 'task', 'Task', task_id, f'Deleted task: {title}')
    
    return jsonify({'message': 'Task deleted successfully'})


# ============ Equipment Management Routes ============

@app.route('/equipment')
@login_required
def equipment_page():
    """Equipment page"""
    return render_template('equipment.html')


@app.route('/api/equipment', methods=['GET'])
@login_required
def get_equipment():
    """Get all equipment"""
    equipment_list = Equipment.query.all()
    return jsonify([eq.to_dict() for eq in equipment_list])


@app.route('/api/equipment', methods=['POST'])
@admin_required
def create_equipment():
    """Create equipment"""
    data = request.get_json()
    
    equipment = Equipment(
        name=data.get('name'),
        category=data.get('category'),
        model=data.get('model'),
        serial_number=data.get('serial_number'),
        manufacturer=data.get('manufacturer'),
        location=data.get('location'),
        status=data.get('status', 'available'),
        description=data.get('description'),
        purchase_cost=data.get('purchase_cost'),
        maintenance_interval=data.get('maintenance_interval')
    )
    
    if data.get('purchase_date'):
        equipment.purchase_date = datetime.fromisoformat(data['purchase_date'].replace('Z', '+00:00'))
    
    db.session.add(equipment)
    db.session.commit()
    
    log_action('create_equipment', 'equipment', 'Equipment', equipment.id, f'Created equipment: {equipment.name}')
    
    return jsonify(equipment.to_dict()), 201


@app.route('/api/equipment/<int:equipment_id>', methods=['PUT'])
@admin_required
def update_equipment(equipment_id):
    """Update equipment"""
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    data = request.get_json()
    
    for field in ['name', 'category', 'model', 'serial_number', 'manufacturer', 
                  'location', 'status', 'description', 'purchase_cost', 'maintenance_interval']:
        if field in data:
            setattr(equipment, field, data[field])
    
    if 'purchase_date' in data:
        equipment.purchase_date = datetime.fromisoformat(data['purchase_date'].replace('Z', '+00:00'))
    
    equipment.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_equipment', 'equipment', 'Equipment', equipment.id, f'Updated equipment: {equipment.name}')
    
    return jsonify(equipment.to_dict())


@app.route('/api/equipment/<int:equipment_id>', methods=['DELETE'])
@admin_required
def delete_equipment(equipment_id):
    """Delete equipment"""
    equipment = db.session.get(Equipment, equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    name = equipment.name
    db.session.delete(equipment)
    db.session.commit()
    
    log_action('delete_equipment', 'equipment', 'Equipment', equipment_id, f'Deleted equipment: {name}')
    
    return jsonify({'message': 'Equipment deleted successfully'})


# ============ Equipment Usage Routes ============

@app.route('/equipment/usage')
@login_required
def equipment_usage_page():
    """Equipment usage page"""
    return render_template('equipment_usage.html')


@app.route('/api/equipment/usage', methods=['GET'])
@login_required
def get_equipment_usage():
    """Get equipment usage records"""
    equipment_id = request.args.get('equipment_id')
    if equipment_id:
        records = EquipmentUsage.query.filter_by(equipment_id=equipment_id).all()
    else:
        records = EquipmentUsage.query.all()
    return jsonify([record.to_dict() for record in records])


@app.route('/api/equipment/usage', methods=['POST'])
@login_required
def create_equipment_usage():
    """Start equipment usage"""
    data = request.get_json()
    
    equipment = db.session.get(Equipment, data.get('equipment_id'))
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    if equipment.status == 'in_use':
        return jsonify({'error': 'Equipment is already in use'}), 400
    
    usage = EquipmentUsage(
        equipment_id=data.get('equipment_id'),
        user_id=session.get('user_id'),
        purpose=data.get('purpose'),
        project_id=data.get('project_id'),
        status_before=equipment.status
    )
    
    equipment.status = 'in_use'
    
    db.session.add(usage)
    db.session.commit()
    
    log_action('start_usage', 'equipment', 'Equipment', equipment.id, f'Started using: {equipment.name}')
    
    return jsonify(usage.to_dict()), 201


@app.route('/api/equipment/usage/<int:usage_id>/end', methods=['POST'])
@login_required
def end_equipment_usage(usage_id):
    """End equipment usage"""
    usage = db.session.get(EquipmentUsage, usage_id)
    if not usage:
        return jsonify({'error': 'Usage record not found'}), 404
    
    if usage.end_time:
        return jsonify({'error': 'Usage already ended'}), 400
    
    data = request.get_json()
    
    usage.end_time = datetime.utcnow()
    usage.status_after = data.get('status_after', 'available')
    usage.notes = data.get('notes')
    
    equipment = db.session.get(Equipment, usage.equipment_id)
    equipment.status = usage.status_after
    
    db.session.commit()
    
    log_action('end_usage', 'equipment', 'Equipment', equipment.id, f'Ended using: {equipment.name}')
    
    return jsonify(usage.to_dict())


# ============ Equipment Reservation Routes ============

@app.route('/equipment/reservations')
@login_required
def equipment_reservations_page():
    """Equipment reservations page"""
    return render_template('equipment_reservations.html')


@app.route('/api/equipment/reservations', methods=['GET'])
@login_required
def get_equipment_reservations():
    """Get equipment reservations"""
    reservations = EquipmentReservation.query.all()
    return jsonify([r.to_dict() for r in reservations])


@app.route('/api/equipment/reservations', methods=['POST'])
@login_required
def create_equipment_reservation():
    """Create equipment reservation"""
    data = request.get_json()
    
    start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    
    # Check for conflicts
    conflicts = EquipmentReservation.query.filter(
        EquipmentReservation.equipment_id == data['equipment_id'],
        EquipmentReservation.status == 'approved',
        EquipmentReservation.start_time < end_time,
        EquipmentReservation.end_time > start_time
    ).first()
    
    if conflicts:
        return jsonify({'error': 'Time slot conflicts with existing reservation'}), 400
    
    reservation = EquipmentReservation(
        equipment_id=data.get('equipment_id'),
        user_id=session.get('user_id'),
        start_time=start_time,
        end_time=end_time,
        purpose=data.get('purpose'),
        priority=data.get('priority', 'normal')
    )
    
    db.session.add(reservation)
    db.session.commit()
    
    log_action('create_reservation', 'equipment', 'EquipmentReservation', reservation.id, 
              f'Created reservation for equipment {data.get("equipment_id")}')
    
    return jsonify(reservation.to_dict()), 201


@app.route('/api/equipment/reservations/<int:reservation_id>/approve', methods=['POST'])
@admin_required
def approve_reservation(reservation_id):
    """Approve reservation"""
    reservation = db.session.get(EquipmentReservation, reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    data = request.get_json()
    
    reservation.status = 'approved'
    reservation.approver_id = session.get('user_id')
    reservation.approval_time = datetime.utcnow()
    reservation.approval_note = data.get('note')
    
    db.session.commit()
    
    log_action('approve_reservation', 'equipment', 'EquipmentReservation', reservation.id, 
              'Approved reservation')
    
    return jsonify(reservation.to_dict())


@app.route('/api/equipment/reservations/<int:reservation_id>/reject', methods=['POST'])
@admin_required
def reject_reservation(reservation_id):
    """Reject reservation"""
    reservation = db.session.get(EquipmentReservation, reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    data = request.get_json()
    
    reservation.status = 'rejected'
    reservation.approver_id = session.get('user_id')
    reservation.approval_time = datetime.utcnow()
    reservation.approval_note = data.get('note')
    
    db.session.commit()
    
    log_action('reject_reservation', 'equipment', 'EquipmentReservation', reservation.id, 
              'Rejected reservation')
    
    return jsonify(reservation.to_dict())


# ============ Equipment Maintenance Routes ============

@app.route('/equipment/maintenance')
@login_required
def equipment_maintenance_page():
    """Equipment maintenance page"""
    return render_template('equipment_maintenance.html')


@app.route('/api/equipment/maintenance', methods=['GET'])
@login_required
def get_equipment_maintenance():
    """Get maintenance records"""
    records = EquipmentMaintenance.query.all()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/equipment/maintenance', methods=['POST'])
@admin_required
def create_equipment_maintenance():
    """Create maintenance record"""
    data = request.get_json()
    
    maintenance = EquipmentMaintenance(
        equipment_id=data.get('equipment_id'),
        maintenance_type=data.get('maintenance_type'),
        description=data.get('description'),
        cost=data.get('cost'),
        performed_by=data.get('performed_by'),
        maintenance_date=datetime.fromisoformat(data['maintenance_date'].replace('Z', '+00:00'))
    )
    
    if data.get('next_maintenance'):
        maintenance.next_maintenance = datetime.fromisoformat(data['next_maintenance'].replace('Z', '+00:00'))
    
    # Update equipment last maintenance
    equipment = db.session.get(Equipment, data.get('equipment_id'))
    if equipment:
        equipment.last_maintenance = maintenance.maintenance_date
    
    db.session.add(maintenance)
    db.session.commit()
    
    log_action('create_maintenance', 'equipment', 'EquipmentMaintenance', maintenance.id, 
              f'Created maintenance record for equipment {data.get("equipment_id")}')
    
    return jsonify(maintenance.to_dict()), 201


# ============ Inventory Management Routes ============

@app.route('/inventory')
@login_required
def inventory_page():
    """Inventory page"""
    return render_template('inventory.html')


@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    """Get all inventory items"""
    items = Inventory.query.all()
    return jsonify([item.to_dict() for item in items])


@app.route('/api/inventory', methods=['POST'])
@admin_required
def create_inventory():
    """Create inventory item"""
    data = request.get_json()
    
    item = Inventory(
        name=data.get('name'),
        category=data.get('category'),
        specification=data.get('specification'),
        unit=data.get('unit'),
        quantity=data.get('quantity', 0),
        min_quantity=data.get('min_quantity', 0),
        supplier=data.get('supplier'),
        catalog_number=data.get('catalog_number'),
        storage_location=data.get('storage_location'),
        unit_price=data.get('unit_price'),
        description=data.get('description')
    )
    
    if data.get('expiry_date'):
        item.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
    
    db.session.add(item)
    db.session.commit()
    
    log_action('create_inventory', 'inventory', 'Inventory', item.id, f'Created inventory item: {item.name}')
    
    return jsonify(item.to_dict()), 201


@app.route('/api/inventory/<int:item_id>', methods=['PUT'])
@admin_required
def update_inventory(item_id):
    """Update inventory item"""
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    data = request.get_json()
    
    for field in ['name', 'category', 'specification', 'unit', 'quantity', 'min_quantity',
                  'supplier', 'catalog_number', 'storage_location', 'unit_price', 'description']:
        if field in data:
            setattr(item, field, data[field])
    
    if 'expiry_date' in data:
        item.expiry_date = datetime.fromisoformat(data['expiry_date'].replace('Z', '+00:00'))
    
    item.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_inventory', 'inventory', 'Inventory', item.id, f'Updated inventory item: {item.name}')
    
    return jsonify(item.to_dict())


@app.route('/api/inventory/<int:item_id>', methods=['DELETE'])
@admin_required
def delete_inventory(item_id):
    """Delete inventory item"""
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    name = item.name
    db.session.delete(item)
    db.session.commit()
    
    log_action('delete_inventory', 'inventory', 'Inventory', item_id, f'Deleted inventory item: {name}')
    
    return jsonify({'message': 'Inventory item deleted successfully'})


@app.route('/api/inventory/records', methods=['GET'])
@login_required
def get_inventory_records():
    """Get inventory records"""
    records = InventoryRecord.query.order_by(InventoryRecord.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])


@app.route('/api/inventory/records', methods=['POST'])
@login_required
def create_inventory_record():
    """Create inventory in/out record"""
    data = request.get_json()
    
    item = db.session.get(Inventory, data.get('item_id'))
    if not item:
        return jsonify({'error': 'Inventory item not found'}), 404
    
    record_type = data.get('record_type')
    quantity = float(data.get('quantity'))
    
    if record_type == 'out' and item.quantity < quantity:
        return jsonify({'error': 'Insufficient inventory'}), 400
    
    record = InventoryRecord(
        item_id=data.get('item_id'),
        user_id=session.get('user_id'),
        record_type=record_type,
        quantity=quantity,
        unit_price=data.get('unit_price'),
        purpose=data.get('purpose'),
        project_id=data.get('project_id')
    )
    
    # Update inventory quantity
    if record_type == 'in':
        item.quantity += quantity
    elif record_type == 'out':
        item.quantity -= quantity
    
    db.session.add(record)
    db.session.commit()
    
    log_action('inventory_record', 'inventory', 'InventoryRecord', record.id, 
              f'{record_type} {quantity} {item.unit} of {item.name}')
    
    return jsonify(record.to_dict()), 201


# ============ Announcement Routes ============

@app.route('/announcements')
@login_required
def announcements_page():
    """Announcements page"""
    return render_template('announcements.html')


@app.route('/api/announcements', methods=['GET'])
@login_required
def get_announcements():
    """Get all announcements"""
    announcements = Announcement.query.order_by(
        Announcement.is_pinned.desc(),
        Announcement.created_at.desc()
    ).all()
    return jsonify([a.to_dict() for a in announcements])


@app.route('/api/announcements', methods=['POST'])
@login_required
def create_announcement():
    """Create announcement"""
    data = request.get_json()
    
    announcement = Announcement(
        title=data.get('title'),
        content=data.get('content'),
        author_id=session.get('user_id'),
        priority=data.get('priority', 'normal'),
        is_pinned=data.get('is_pinned', False)
    )
    
    db.session.add(announcement)
    db.session.commit()
    
    log_action('create_announcement', 'announcement', 'Announcement', announcement.id, 
              f'Created announcement: {announcement.title}')
    
    return jsonify(announcement.to_dict()), 201


@app.route('/api/announcements/<int:announcement_id>', methods=['PUT'])
@login_required
def update_announcement(announcement_id):
    """Update announcement"""
    announcement = db.session.get(Announcement, announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404
    
    # Check if user is author or admin
    user = db.session.get(User, session['user_id'])
    if announcement.author_id != session['user_id'] and user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        announcement.title = data['title']
    if 'content' in data:
        announcement.content = data['content']
    if 'priority' in data:
        announcement.priority = data['priority']
    if 'is_pinned' in data:
        announcement.is_pinned = data['is_pinned']
    
    announcement.updated_at = datetime.utcnow()
    db.session.commit()
    
    log_action('update_announcement', 'announcement', 'Announcement', announcement.id, 
              f'Updated announcement: {announcement.title}')
    
    return jsonify(announcement.to_dict())


@app.route('/api/announcements/<int:announcement_id>', methods=['DELETE'])
@login_required
def delete_announcement(announcement_id):
    """Delete announcement"""
    announcement = db.session.get(Announcement, announcement_id)
    if not announcement:
        return jsonify({'error': 'Announcement not found'}), 404
    
    # Check if user is author or admin
    user = db.session.get(User, session['user_id'])
    if announcement.author_id != session['user_id'] and user.role not in ['admin', 'teacher']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    title = announcement.title
    db.session.delete(announcement)
    db.session.commit()
    
    log_action('delete_announcement', 'announcement', 'Announcement', announcement_id, 
              f'Deleted announcement: {title}')
    
    return jsonify({'message': 'Announcement deleted successfully'})


# ============ System Logs Routes ============

@app.route('/system/logs')
@admin_required
def system_logs_page():
    """System logs page"""
    return render_template('system_logs.html')


@app.route('/api/system/logs', methods=['GET'])
@admin_required
def get_system_logs():
    """Get system logs"""
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(500).all()
    return jsonify([log.to_dict() for log in logs])


# ============ Statistics Routes ============

@app.route('/api/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Get dashboard statistics"""
    stats = {
        'users': {
            'total': User.query.count(),
            'active': User.query.filter_by(is_active=True).count(),
            'by_role': {
                'admin': User.query.filter_by(role='admin').count(),
                'teacher': User.query.filter_by(role='teacher').count(),
                'student': User.query.filter_by(role='student').count()
            }
        },
        'projects': {
            'total': Project.query.count(),
            'active': Project.query.filter_by(status='active').count(),
            'completed': Project.query.filter_by(status='completed').count()
        },
        'tasks': {
            'total': Task.query.count(),
            'pending': Task.query.filter_by(status='pending').count(),
            'in_progress': Task.query.filter_by(status='in_progress').count(),
            'completed': Task.query.filter_by(status='completed').count()
        },
        'equipment': {
            'total': Equipment.query.count(),
            'available': Equipment.query.filter_by(status='available').count(),
            'in_use': Equipment.query.filter_by(status='in_use').count(),
            'maintenance': Equipment.query.filter_by(status='maintenance').count()
        },
        'inventory': {
            'total': Inventory.query.count(),
            'low_stock': Inventory.query.filter(Inventory.quantity <= Inventory.min_quantity).count()
        },
        'announcements': {
            'total': Announcement.query.count(),
            'pinned': Announcement.query.filter_by(is_pinned=True).count()
        }
    }
    
    return jsonify(stats)


# ============ Initialize Database ============

def init_database():
    """Initialize database with tables and default data"""
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create default admin
            admin = User(
                username='admin',
                email='admin@lab.com',
                name='Administrator',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Default admin created: admin / admin123')


if __name__ == '__main__':
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
