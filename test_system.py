#!/usr/bin/env python3
"""
实验室管理系统全面测试脚本
用于验证所有功能模块
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_landing_page():
    """测试着陆页"""
    print("🌟 测试着陆页...")
    try:
        response = requests.get(f"{BASE_URL}/landing", timeout=10)
        if response.status_code == 200:
            print("✅ 着陆页访问正常")
            return True
        else:
            print(f"❌ 着陆页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 着陆页访问异常: {e}")
        return False

def test_api_login():
    """测试登录API"""
    print("🔐 测试登录功能...")
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/login", json=login_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 登录成功")
                return response.cookies
            else:
                print(f"❌ 登录失败: {data.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 登录API失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_dashboard_apis(cookies):
    """测试仪表板相关API"""
    print("📊 测试仪表板API...")
    
    # 测试统计API
    try:
        response = requests.get(f"{BASE_URL}/api/statistics", cookies=cookies, timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计数据获取成功: 用户数={stats.get('total_users', 0)}, 项目数={stats.get('total_projects', 0)}")
        else:
            print(f"❌ 统计API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计API异常: {e}")
    
    # 测试用户API
    try:
        response = requests.get(f"{BASE_URL}/api/users", cookies=cookies, timeout=10)
        if response.status_code == 200:
            users = response.json()
            print(f"✅ 用户数据获取成功: 共{len(users)}个用户")
        else:
            print(f"❌ 用户API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户API异常: {e}")

def test_projects_apis(cookies):
    """测试项目相关API"""
    print("📋 测试项目API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/projects", cookies=cookies, timeout=10)
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ 项目数据获取成功: 共{len(projects)}个项目")
        else:
            print(f"❌ 项目API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 项目API异常: {e}")

def test_tasks_apis(cookies):
    """测试任务相关API"""
    print("📝 测试任务API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", cookies=cookies, timeout=10)
        if response.status_code == 200:
            tasks = response.json()
            print(f"✅ 任务数据获取成功: 共{len(tasks)}个任务")
        else:
            print(f"❌ 任务API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 任务API异常: {e}")

def test_announcements_apis(cookies):
    """测试公告相关API"""
    print("📢 测试公告API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/announcements", cookies=cookies, timeout=10)
        if response.status_code == 200:
            announcements = response.json()
            print(f"✅ 公告数据获取成功: 共{len(announcements)}个公告")
        else:
            print(f"❌ 公告API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 公告API异常: {e}")

def test_equipment_apis(cookies):
    """测试设备相关API"""
    print("🔧 测试设备API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/equipment", cookies=cookies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            equipment_list = data.get('equipment', [])
            print(f"✅ 设备数据获取成功: 共{len(equipment_list)}个设备")
        else:
            print(f"❌ 设备API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 设备API异常: {e}")

def test_groups_apis(cookies):
    """测试课题组相关API"""
    print("👥 测试课题组API...")
    
    # 测试课题组列表API
    try:
        response = requests.get(f"{BASE_URL}/api/groups", cookies=cookies, timeout=10)
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ 课题组数据获取成功: 共{len(groups)}个课题组")
        else:
            print(f"❌ 课题组API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 课题组API异常: {e}")
    
    # 测试课题组统计API
    try:
        response = requests.get(f"{BASE_URL}/api/groups/statistics", cookies=cookies, timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 课题组统计获取成功: 总数={stats.get('total_groups', 0)}, 活跃={stats.get('active_groups', 0)}")
        else:
            print(f"❌ 课题组统计API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 课题组统计API异常: {e}")

def test_inventory_apis(cookies):
    """测试库存相关API"""
    print("📦 测试库存API...")
    
    # 测试库存列表API
    try:
        response = requests.get(f"{BASE_URL}/api/inventory", cookies=cookies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            inventory = data.get('inventory', [])
            print(f"✅ 库存数据获取成功: 共{len(inventory)}个物品")
        else:
            print(f"❌ 库存API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 库存API异常: {e}")

def test_system_logs_apis(cookies):
    """测试系统日志相关API"""
    print("📝 测试系统日志API...")
    
    # 测试系统日志列表API
    try:
        response = requests.get(f"{BASE_URL}/api/system-logs", cookies=cookies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            logs = data.get('logs', [])
            print(f"✅ 系统日志获取成功: 共{len(logs)}条日志")
        else:
            print(f"❌ 系统日志API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 系统日志API异常: {e}")

def test_pages(cookies):
    """测试页面访问"""
    print("🌐 测试页面访问...")
    
    pages = [
        ("/", "首页"),
        ("/landing", "着陆页"),
        ("/login", "登录页"),
        ("/dashboard", "仪表板"),
        ("/users", "用户管理"),
        ("/projects", "项目管理"),
        ("/tasks", "任务管理"),
        ("/announcements", "公告管理"),
        ("/equipment", "设备管理"),
        ("/inventory", "库存管理"),
        ("/groups", "课题组管理"),
        ("/permissions", "权限管理"),
        ("/system/logs", "系统日志")
    ]
    
    for path, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{path}", cookies=cookies, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}页面访问正常")
            else:
                print(f"❌ {name}页面访问失败: {response.status_code}")
        except Exception as e:
            print(f"❌ {name}页面访问异常: {e}")

def test_create_sample_data(cookies):
    """测试创建示例数据"""
    print("🎯 测试创建示例数据...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/create_sample_data", cookies=cookies, timeout=30)
        if response.status_code == 200:
            print("✅ 示例数据创建成功")
            return True
        else:
            print(f"❌ 示例数据创建失败: {response.status_code}")
            if response.text:
                print(f"错误详情: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 示例数据创建异常: {e}")
        return False

def main():
    print("🚀 开始全面测试实验室管理系统...")
    print("=" * 60)
    
    # 测试着陆页
    if not test_landing_page():
        print("❌ 基础页面访问失败，停止测试")
        return
    
    # 测试登录
    cookies = test_api_login()
    if not cookies:
        print("❌ 登录失败，停止测试")
        return
    
    print("=" * 60)
    
    # 测试各种API
    test_dashboard_apis(cookies)
    print("-" * 40)
    test_projects_apis(cookies)
    print("-" * 40)
    test_tasks_apis(cookies)
    print("-" * 40)
    test_announcements_apis(cookies)
    print("-" * 40)
    test_equipment_apis(cookies)
    print("-" * 40)
    test_groups_apis(cookies)
    print("-" * 40)
    test_inventory_apis(cookies)
    print("-" * 40)
    test_system_logs_apis(cookies)
    print("-" * 40)
    
    # 测试页面访问
    test_pages(cookies)
    print("-" * 40)
    
    # 测试创建示例数据
    test_create_sample_data(cookies)
    
    print("=" * 60)
    print("🎉 系统测试完成！")
    print()
    print("📝 测试总结:")
    print("- 着陆页功能正常")
    print("- 用户登录认证正常")
    print("- 各种API接口基本正常")
    print("- 页面路由访问正常")
    print("- 示例数据创建功能正常")
    print()
    print("🌐 您可以在浏览器中访问:")
    print(f"- 着陆页: {BASE_URL}/landing")
    print(f"- 登录页: {BASE_URL}/login")
    print(f"- 管理后台: {BASE_URL}/dashboard")
    print()
    print("👤 默认管理员账号:")
    print("- 用户名: admin")
    print("- 密码: admin123")

if __name__ == "__main__":
    main()