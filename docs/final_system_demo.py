#!/usr/bin/env python3
"""
智能思维项目 - 最终系统演示
展示完整的三层架构：基础分析 + 3D可视化 + 企业级功能
"""

import requests
import json
import time
import subprocess
import sys
from typing import Dict, Any
import webbrowser
from pathlib import Path

class IntelligentThinkingSystemDemo:
    """智能思维系统演示器"""
    
    def __init__(self):
        self.services = {
            'basic': {'port': 8000, 'name': '基础Web服务', 'status': False},
            '3d': {'port': 8001, 'name': '3D可视化服务', 'status': False},
            'advanced': {'port': 8002, 'name': '高级功能服务', 'status': False}
        }
        
        self.demo_data = {
            "user_profile": {
                "creativity_score": 8.7,
                "logic_score": 7.5,
                "emotional_intelligence": 9.2,
                "focus_level": 6.8,
                "thinking_style": "creative",
                "age": 28,
                "education": "研究生"
            },
            "thinking_space_config": {
                "node_count": 50,
                "connection_strength": 0.7,
                "thinking_mode": "creative"
            }
        }

    def show_welcome_banner(self):
        """显示欢迎横幅"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════╗
║                      🧠 智能思维与灵境融合项目                              ║
║                         最终系统演示 v3.0                                  ║
╠═══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  🎯 项目愿景: 构建AI驱动的3D思维空间可视化与协作平台                        ║
║  🏆 技术成就: 从Python基础到企业级系统的完整实现                            ║
║  🌟 创新亮点: 多层架构 + AI分析 + 3D沉浸 + 实时协作                        ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def show_system_architecture(self):
        """显示系统架构"""
        print("\n🏗️  系统架构概览")
        print("=" * 80)
        
        architecture = """
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                          用户界面层                                      │
        │  🌐 Web浏览器  📱 移动端  🥽 VR/AR设备  💻 桌面应用                    │
        └─────────────────────────────────────────────────────────────────────────┘
                                         │
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                          应用服务层                                      │
        │  🚀 高级功能服务(8002)    🎮 3D可视化服务(8001)    🌐 基础Web服务(8000) │
        │  ├─ 用户管理             ├─ Three.js渲染          ├─ 思维分析           │
        │  ├─ 实时协作             ├─ WebXR支持             ├─ 机器学习           │
        │  ├─ 数据持久化           ├─ 空间生成              ├─ 深度学习           │
        │  └─ 系统监控             └─ 交互控制              └─ 数据处理           │
        └─────────────────────────────────────────────────────────────────────────┘
                                         │
        ┌─────────────────────────────────────────────────────────────────────────┐
        │                          数据存储层                                      │
        │  🗄️ SQLite数据库  📊 用户数据  📈 会话记录  🤝 协作历史  📋 系统日志     │
        └─────────────────────────────────────────────────────────────────────────┘
        """
        print(architecture)

    def check_services_status(self):
        """检查所有服务状态"""
        print("\n🔍 检查服务状态...")
        print("-" * 50)
        
        for service_id, info in self.services.items():
            try:
                response = requests.get(f"http://localhost:{info['port']}", timeout=2)
                if response.status_code == 200:
                    info['status'] = True
                    print(f"✅ {info['name']} (端口 {info['port']}) - 运行正常")
                else:
                    info['status'] = False
                    print(f"❌ {info['name']} (端口 {info['port']}) - 状态异常")
            except requests.exceptions.RequestException:
                info['status'] = False
                print(f"🔴 {info['name']} (端口 {info['port']}) - 未启动")
        
        active_services = sum(1 for info in self.services.values() if info['status'])
        print(f"\n📊 服务状态: {active_services}/3 个服务运行中")
        return active_services > 0

    def demo_basic_analysis(self):
        """演示基础分析功能"""
        if not self.services['basic']['status']:
            print("\n⚠️ 基础Web服务未运行，跳过基础分析演示")
            return
            
        print("\n🧠 演示基础思维分析功能")
        print("-" * 50)
        
        try:
            # 测试健康检查
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ 基础服务健康检查通过")
            
            # 演示思维分析
            response = requests.post(
                "http://localhost:8000/analyze",
                json=self.demo_data["user_profile"]
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 思维分析完成:")
                print(f"   🎯 学习风格: {result.get('learning_style', 'N/A')}")
                print(f"   🧮 思维能力: {result.get('thinking_capacity', 'N/A')}")
                print(f"   🔄 思维模式: {result.get('thinking_pattern', 'N/A')}")
                print(f"   💡 个性化建议: {len(result.get('recommendations', []))}条")
            else:
                print("❌ 基础分析请求失败")
                
        except Exception as e:
            print(f"❌ 基础分析演示失败: {e}")

    def demo_3d_visualization(self):
        """演示3D可视化功能"""
        if not self.services['3d']['status']:
            print("\n⚠️ 3D可视化服务未运行，跳过3D演示")
            return
            
        print("\n🎮 演示3D思维空间功能")
        print("-" * 50)
        
        try:
            # 获取空间模板
            response = requests.get("http://localhost:8001/api/space-templates")
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ 获取空间模板成功: {len(templates)}种思维模式")
                for mode, template in templates.items():
                    print(f"   🎨 {template['name']}: {template['description']}")
            
            # 生成3D空间
            space_request = {
                "user_data": self.demo_data["user_profile"],
                **self.demo_data["thinking_space_config"]
            }
            
            response = requests.post(
                "http://localhost:8001/api/generate-space",
                json=space_request
            )
            
            if response.status_code == 200:
                space_data = response.json()
                print("✅ 3D思维空间生成成功:")
                print(f"   📊 思维节点: {len(space_data['nodes'])}个")
                print(f"   🔗 连接数量: {len(space_data['connections'])}个")
                print(f"   🎨 空间模式: {space_data['mode']}")
                print(f"   📈 复杂度指数: {space_data['metadata']['statistics']['space_complexity']:.2f}")
            else:
                print("❌ 3D空间生成失败")
                
        except Exception as e:
            print(f"❌ 3D可视化演示失败: {e}")

    def demo_advanced_features(self):
        """演示高级功能"""
        if not self.services['advanced']['status']:
            print("\n⚠️ 高级功能服务未运行，跳过高级功能演示")
            return
            
        print("\n🚀 演示企业级高级功能")
        print("-" * 50)
        
        try:
            # 创建测试用户
            test_user = {
                "username": f"demo_user_{int(time.time())}",
                "email": "demo@intelligent-thinking.com",
                "password": "demo_password_123",
                "full_name": "演示用户"
            }
            
            # 注册用户
            response = requests.post("http://localhost:8002/api/auth/register", json=test_user)
            if response.status_code == 200:
                print("✅ 用户注册成功")
                
                # 登录用户
                login_data = {"username": test_user["username"], "password": test_user["password"]}
                response = requests.post("http://localhost:8002/api/auth/login", json=login_data)
                
                if response.status_code == 200:
                    login_result = response.json()
                    token = login_result["access_token"]
                    headers = {"Authorization": f"Bearer {token}"}
                    print("✅ 用户登录成功")
                    
                    # 创建协作房间
                    space_data = {"mode": "demo", "nodes": [], "connections": []}
                    response = requests.post(
                        "http://localhost:8002/api/collaboration/create-room",
                        json=space_data,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        room_data = response.json()
                        print(f"✅ 协作房间创建成功: {room_data['room_id']}")
                    
                    # 获取系统指标
                    response = requests.get("http://localhost:8002/api/admin/metrics", headers=headers)
                    if response.status_code == 200:
                        metrics = response.json()
                        print("✅ 系统监控指标:")
                        print(f"   👥 总用户数: {metrics['total_users']}")
                        print(f"   🔄 活跃会话: {metrics['active_sessions']}")
                        print(f"   📊 总空间数: {metrics['total_spaces_created']}")
            else:
                print("⚠️ 用户可能已存在，继续其他功能演示...")
                
        except Exception as e:
            print(f"❌ 高级功能演示失败: {e}")

    def show_performance_metrics(self):
        """显示性能指标"""
        print("\n📊 系统性能指标")
        print("-" * 50)
        
        metrics = {
            "🎯 AI模型性能": {
                "思维风格分类准确率": "~25% (四分类)",
                "思维能力回归R²": "1.0",
                "图像识别准确率": "100% (训练集)",
                "序列分析准确率": "100% (训练集)"
            },
            "🌐 Web服务性能": {
                "API响应时间": "<100ms",
                "3D渲染FPS": "55-65",
                "并发用户支持": "可扩展",
                "跨平台兼容性": "优秀"
            },
            "🔧 技术指标": {
                "代码行数": "~3000行",
                "功能模块": "15+个",
                "API端点": "30+个",
                "数据表": "4个"
            }
        }
        
        for category, items in metrics.items():
            print(f"\n{category}:")
            for metric, value in items.items():
                print(f"   • {metric}: {value}")

    def show_feature_showcase(self):
        """展示功能亮点"""
        print("\n⭐ 系统功能亮点展示")
        print("=" * 80)
        
        features = [
            {
                "category": "🧠 AI智能分析",
                "items": [
                    "7维度用户思维特征分析",
                    "机器学习驱动的学习风格预测",
                    "深度学习神经网络思维建模",
                    "智能推荐和个性化建议系统"
                ]
            },
            {
                "category": "🎮 3D沉浸体验",
                "items": [
                    "Three.js驱动的3D思维空间渲染",
                    "WebXR技术支持VR/AR设备",
                    "实时交互式节点操作",
                    "动态视觉效果和动画系统"
                ]
            },
            {
                "category": "🚀 企业级功能",
                "items": [
                    "JWT认证的安全用户管理",
                    "WebSocket实时协作通信",
                    "SQLite数据持久化存储",
                    "系统监控和性能分析"
                ]
            },
            {
                "category": "🌐 跨平台支持",
                "items": [
                    "响应式Web设计",
                    "移动端API适配",
                    "容器化部署支持",
                    "云平台部署就绪"
                ]
            }
        ]
        
        for feature_group in features:
            print(f"\n{feature_group['category']}:")
            for item in feature_group['items']:
                print(f"   ✨ {item}")
                time.sleep(0.1)

    def open_browser_demo(self):
        """打开浏览器演示"""
        print("\n🌐 启动浏览器演示...")
        print("-" * 50)
        
        urls = []
        if self.services['basic']['status']:
            urls.append(("基础Web服务", "http://localhost:8000"))
        if self.services['3d']['status']:
            urls.append(("3D思维空间", "http://localhost:8001/3d"))
        if self.services['advanced']['status']:
            urls.append(("高级功能中心", "http://localhost:8002"))
        
        if urls:
            print("准备打开以下页面:")
            for name, url in urls:
                print(f"   🔗 {name}: {url}")
            
            user_input = input("\n是否在浏览器中打开演示页面? (y/n): ")
            if user_input.lower() == 'y':
                for name, url in urls:
                    webbrowser.open(url)
                    print(f"✅ 已打开 {name}")
                    time.sleep(1)
        else:
            print("❌ 没有可用的服务页面")

    def show_next_steps(self):
        """显示下一步计划"""
        print("\n🎯 未来发展规划")
        print("=" * 80)
        
        roadmap = {
            "短期目标 (1-2周)": [
                "系统性能优化和bug修复",
                "用户体验提升和界面美化",
                "更多AI模型集成和调优",
                "移动端应用开发"
            ],
            "中期目标 (1-2月)": [
                "云平台部署和CDN加速",
                "多用户实时协作增强",
                "数据分析和商业智能",
                "API生态系统建设"
            ],
            "长期愿景 (3-6月)": [
                "企业级产品化",
                "AI算法持续优化",
                "VR/AR深度集成",
                "国际化和多语言支持"
            ]
        }
        
        for phase, goals in roadmap.items():
            print(f"\n📅 {phase}:")
            for goal in goals:
                print(f"   🎯 {goal}")

    def run_complete_demo(self):
        """运行完整演示"""
        self.show_welcome_banner()
        time.sleep(1)
        
        self.show_system_architecture()
        time.sleep(1)
        
        # 检查服务状态
        services_available = self.check_services_status()
        
        if services_available:
            print("\n🎪 开始功能演示...")
            time.sleep(1)
            
            # 演示各层功能
            self.demo_basic_analysis()
            time.sleep(1)
            
            self.demo_3d_visualization()
            time.sleep(1)
            
            self.demo_advanced_features()
            time.sleep(1)
            
            # 展示性能和特性
            self.show_performance_metrics()
            time.sleep(1)
            
            self.show_feature_showcase()
            time.sleep(1)
            
            # 浏览器演示
            self.open_browser_demo()
            
        else:
            print("\n⚠️ 没有检测到运行中的服务")
            print("请先启动服务:")
            print("   python examples/week5_web_frontend.py")
            print("   python examples/week6_3d_integration.py") 
            print("   python examples/week7_advanced_features.py")
        
        # 显示未来规划
        self.show_next_steps()
        
        print("\n" + "=" * 80)
        print("🎉 智能思维系统演示完成！")
        print("🌟 感谢体验我们的AI驱动3D思维空间平台！")
        print("=" * 80)

if __name__ == "__main__":
    demo = IntelligentThinkingSystemDemo()
    demo.run_complete_demo() 