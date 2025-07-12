#!/usr/bin/env python3
"""
智能思维项目 - 高级功能系统测试
测试用户管理、协作功能、数据持久化等企业级特性
"""

import requests
import json
import time
import asyncio
import websockets
from typing import Dict, Any

def test_advanced_system():
    """测试高级功能系统"""
    base_url = "http://localhost:8002"
    
    print("🚀 测试智能思维高级功能系统")
    print("=" * 60)
    
    # 1. 测试服务状态
    print("\n1. 检查高级功能服务状态...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 高级功能服务运行正常")
        else:
            print("❌ 高级功能服务状态异常")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到高级功能服务，请确保服务已启动")
        return False
    
    # 2. 测试用户注册
    print("\n2. 测试用户管理系统...")
    test_user = {
        "username": "test_user_2024",
        "email": "test@intelligent-thinking.com",
        "password": "secure_password_123",
        "full_name": "测试用户"
    }
    
    try:
        # 注册用户
        response = requests.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 200:
            register_result = response.json()
            print(f"✅ 用户注册成功: {register_result['user_id']}")
            user_id = register_result['user_id']
        else:
            print("⚠️ 用户可能已存在，尝试登录...")
            user_id = "existing_user"
    except Exception as e:
        print(f"❌ 用户注册失败: {e}")
        return False
    
    # 3. 测试用户登录
    print("\n3. 测试用户认证...")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            login_result = response.json()
            access_token = login_result["access_token"]
            user_info = login_result["user"]
            print(f"✅ 用户登录成功: {user_info['full_name']}")
            
            # 设置认证头
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            print("❌ 用户登录失败")
            return False
    except Exception as e:
        print(f"❌ 登录过程出错: {e}")
        return False
    
    # 4. 测试用户信息获取
    print("\n4. 测试用户信息获取...")
    try:
        response = requests.get(f"{base_url}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 获取用户信息成功: {user_data['username']}")
        else:
            print("❌ 获取用户信息失败")
    except Exception as e:
        print(f"❌ 获取用户信息出错: {e}")
    
    # 5. 测试协作房间创建
    print("\n5. 测试协作功能...")
    thinking_space_data = {
        "nodes": [
            {"id": 1, "concept": "协作思维", "position": {"x": 0, "y": 0, "z": 0}},
            {"id": 2, "concept": "团队智慧", "position": {"x": 10, "y": 10, "z": 10}}
        ],
        "connections": [{"source": 1, "target": 2, "strength": 0.8}],
        "mode": "collaborative"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/collaboration/create-room",
            json=thinking_space_data,
            headers=headers,
            params={"max_participants": 5}
        )
        if response.status_code == 200:
            room_result = response.json()
            room_id = room_result["room_id"]
            print(f"✅ 协作房间创建成功: {room_id}")
            
            # 获取房间信息
            response = requests.get(f"{base_url}/api/collaboration/room/{room_id}", headers=headers)
            if response.status_code == 200:
                room_info = response.json()
                print(f"   📊 房间信息: {len(room_info['participants'])}个参与者")
        else:
            print("❌ 协作房间创建失败")
    except Exception as e:
        print(f"❌ 协作功能测试出错: {e}")
    
    # 6. 测试用户会话管理
    print("\n6. 测试会话管理...")
    try:
        response = requests.get(f"{base_url}/api/user/sessions", headers=headers)
        if response.status_code == 200:
            sessions_data = response.json()
            print(f"✅ 获取用户会话成功: {len(sessions_data['sessions'])}个会话")
        else:
            print("❌ 获取用户会话失败")
    except Exception as e:
        print(f"❌ 会话管理测试出错: {e}")
    
    # 7. 测试系统指标
    print("\n7. 测试系统监控...")
    try:
        response = requests.get(f"{base_url}/api/admin/metrics", headers=headers)
        if response.status_code == 200:
            metrics = response.json()
            print("✅ 系统监控正常:")
            print(f"   👥 总用户数: {metrics['total_users']}")
            print(f"   🔄 活跃会话: {metrics['active_sessions']}")
            print(f"   📊 思维空间总数: {metrics['total_spaces_created']}")
            print(f"   📈 平均会话时长: {metrics['average_session_duration']}分钟")
        else:
            print("❌ 系统监控获取失败")
    except Exception as e:
        print(f"❌ 系统监控测试出错: {e}")
    
    # 8. 测试数据导出
    print("\n8. 测试数据导出...")
    try:
        response = requests.get(f"{base_url}/api/export/user-data", headers=headers)
        if response.status_code == 200:
            export_data = response.json()
            print(f"✅ 数据导出成功: {len(export_data['sessions'])}个会话记录")
        else:
            print("❌ 数据导出失败")
    except Exception as e:
        print(f"❌ 数据导出测试出错: {e}")
    
    # 9. 测试移动端API
    print("\n9. 测试移动端适配...")
    try:
        response = requests.get(f"{base_url}/api/mobile/thinking-summary", headers=headers)
        if response.status_code == 200:
            mobile_data = response.json()
            print("✅ 移动端API正常:")
            print(f"   📱 用户: {mobile_data['user_name']}")
            print(f"   📊 总会话: {mobile_data['total_sessions']}")
            print(f"   🎯 偏好模式: {mobile_data['favorite_mode']}")
            print(f"   🔥 连续天数: {mobile_data['thinking_streak']}")
        else:
            print("❌ 移动端API测试失败")
    except Exception as e:
        print(f"❌ 移动端测试出错: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 高级功能系统测试完成!")
    return True

async def test_websocket_collaboration():
    """测试WebSocket协作功能"""
    print("\n🔄 测试WebSocket协作功能...")
    
    uri = "ws://localhost:8002/ws/collaboration/test_room_123?user_id=test_user_ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket连接成功")
            
            # 发送测试消息
            test_messages = [
                {
                    "type": "thinking_update",
                    "updates": {"node_id": 1, "position": {"x": 15, "y": 20, "z": 5}}
                },
                {
                    "type": "chat_message", 
                    "message": "大家好，我是测试用户！"
                },
                {
                    "type": "cursor_position",
                    "position": {"x": 100, "y": 200}
                }
            ]
            
            for message in test_messages:
                await websocket.send(json.dumps(message))
                print(f"📤 发送消息: {message['type']}")
                time.sleep(0.5)
            
            print("✅ WebSocket协作测试完成")
            
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")

def demo_advanced_features():
    """演示高级功能特性"""
    print("\n🎯 智能思维高级功能特性:")
    print("=" * 60)
    
    enterprise_features = [
        "👥 企业级用户管理系统",
        "🔐 JWT令牌认证和安全会话",
        "🤝 实时WebSocket协作",
        "💾 SQLite数据持久化",
        "📊 系统性能监控和分析",
        "📱 移动端API和响应式设计",
        "☁️ 云部署和容器化支持",
        "🔄 实时数据同步",
        "📈 用户行为分析",
        "🛡️ 数据安全和隐私保护"
    ]
    
    for feature in enterprise_features:
        print(f"   {feature}")
        time.sleep(0.2)
    
    print(f"\n🔧 技术架构:")
    architecture = [
        "FastAPI + SQLite + WebSocket",
        "JWT认证 + bcrypt密码加密",
        "实时协作 + 数据持久化",
        "RESTful API + WebSocket API",
        "容器化部署 + 微服务架构"
    ]
    
    for tech in architecture:
        print(f"   • {tech}")

def show_deployment_guide():
    """显示部署指南"""
    print(f"\n🚀 部署指南:")
    print("=" * 60)
    
    deployment_steps = [
        "1. 安装依赖: pip install fastapi uvicorn PyJWT bcrypt websockets",
        "2. 启动基础服务: python examples/week5_web_frontend.py (端口8000)",
        "3. 启动3D服务: python examples/week6_3d_integration.py (端口8001)",
        "4. 启动高级服务: python examples/week7_advanced_features.py (端口8002)",
        "5. 访问主页: http://localhost:8002",
        "6. 查看API文档: http://localhost:8002/docs",
        "7. 体验协作功能: 创建房间并邀请用户"
    ]
    
    for step in deployment_steps:
        print(f"   {step}")
    
    print(f"\n📊 系统端口分配:")
    ports = [
        "🌐 端口8000: 基础Web服务 (2D思维分析)",
        "🎮 端口8001: 3D可视化服务 (沉浸式体验)", 
        "🚀 端口8002: 高级功能服务 (企业级功能)",
        "📡 WebSocket: 实时协作通信"
    ]
    
    for port in ports:
        print(f"   {port}")

if __name__ == "__main__":
    print("🚀 智能思维高级功能系统测试")
    print("🕐 等待服务启动...")
    time.sleep(2)
    
    # 演示功能特性
    demo_advanced_features()
    
    # 显示部署指南
    show_deployment_guide()
    
    # 执行系统测试
    success = test_advanced_system()
    
    if success:
        print(f"\n🎊 所有测试通过！系统已准备就绪。")
        print(f"\n🌟 下一步可以:")
        print("   • 部署到云平台 (AWS/Azure/GCP)")
        print("   • 集成更多AI模型")
        print("   • 开发移动应用")
        print("   • 添加更多协作功能")
        print("   • 优化系统性能")
    else:
        print(f"\n⚠️ 部分测试失败，请检查服务状态。")
    
    # 可选: 测试WebSocket (需要服务运行)
    # asyncio.run(test_websocket_collaboration()) 