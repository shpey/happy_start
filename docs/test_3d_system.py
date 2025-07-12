#!/usr/bin/env python3
"""
智能思维项目 - 3D思维空间系统测试
测试AI驱动的3D可视化功能
"""

import requests
import json
import time
from typing import Dict, Any

def test_3d_system():
    """测试3D思维空间系统"""
    base_url = "http://localhost:8001"
    
    print("🧠 测试智能思维3D空间系统")
    print("=" * 50)
    
    # 1. 测试服务状态
    print("\n1. 检查3D服务状态...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 3D服务运行正常")
        else:
            print("❌ 3D服务状态异常")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到3D服务，请确保服务已启动")
        return
    
    # 2. 测试空间模板
    print("\n2. 获取思维空间模板...")
    try:
        response = requests.get(f"{base_url}/api/space-templates")
        templates = response.json()
        print("✅ 成功获取空间模板:")
        for mode, template in templates.items():
            print(f"   🎯 {template['name']}: {template['description']}")
    except Exception as e:
        print(f"❌ 获取模板失败: {e}")
    
    # 3. 测试3D空间生成
    print("\n3. 生成个性化3D思维空间...")
    test_user_data = {
        "user_data": {
            "creativity_score": 8.5,
            "logic_score": 7.2,
            "emotional_intelligence": 9.1,
            "focus_level": 6.8,
            "thinking_style": "creative",
            "preferences": {"color_theme": "vibrant", "complexity": "high"}
        },
        "node_count": 30,
        "connection_strength": 0.7,
        "thinking_mode": "creative"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-space",
            json=test_user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            space_data = response.json()
            print("✅ 成功生成3D思维空间!")
            print(f"   📊 思维节点数: {len(space_data['nodes'])}")
            print(f"   🔗 连接数: {len(space_data['connections'])}")
            print(f"   🎨 思维模式: {space_data['mode']}")
            print(f"   📈 空间复杂度: {space_data['metadata']['statistics']['space_complexity']:.2f}")
            
            # 分析节点分布
            analyze_space_structure(space_data)
            
        else:
            print(f"❌ 生成空间失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 生成空间出错: {e}")
    
    # 4. 测试思维分析
    print("\n4. 进行思维模式分析...")
    try:
        response = requests.get(f"{base_url}/api/thinking-analysis/test_space_001")
        if response.status_code == 200:
            analysis = response.json()
            print("✅ 思维分析完成!")
            print(f"   🧩 主导集群: {analysis['patterns']['dominant_clusters']}个")
            print(f"   💪 连接强度: {analysis['patterns']['connection_strength']:.2f}")
            print(f"   🌈 思维多样性: {analysis['patterns']['thinking_diversity']:.2f}")
            print(f"   🧠 认知负荷: {analysis['patterns']['cognitive_load']:.2f}")
            
            print("\n   💡 洞察建议:")
            for insight in analysis['insights'][:2]:
                print(f"   • {insight}")
    except Exception as e:
        print(f"❌ 思维分析失败: {e}")
    
    # 5. 测试不同思维模式
    print("\n5. 测试不同思维模式...")
    modes = ['logical', 'analytical', 'intuitive']
    
    for mode in modes:
        test_mode_data = test_user_data.copy()
        test_mode_data['thinking_mode'] = mode
        test_mode_data['node_count'] = 20  # 减少节点数以加快测试
        
        try:
            response = requests.post(
                f"{base_url}/api/generate-space",
                json=test_mode_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                space_data = response.json()
                print(f"   ✅ {mode}模式空间: {len(space_data['nodes'])}节点, {len(space_data['connections'])}连接")
            else:
                print(f"   ❌ {mode}模式生成失败")
        except Exception as e:
            print(f"   ❌ {mode}模式出错: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 3D思维空间系统测试完成!")
    print("🌐 访问 http://localhost:8001/3d 体验完整的3D可视化")

def analyze_space_structure(space_data: Dict[str, Any]):
    """分析空间结构"""
    nodes = space_data['nodes']
    connections = space_data['connections']
    
    # 计算统计信息
    concepts = [node['concept'] for node in nodes]
    strengths = [node['strength'] for node in nodes]
    
    print(f"\n   📋 空间结构分析:")
    print(f"   • 平均节点强度: {sum(strengths)/len(strengths):.2f}")
    print(f"   • 最强概念: {nodes[strengths.index(max(strengths))]['concept']}")
    print(f"   • 连接密度: {len(connections)}/{len(nodes)*(len(nodes)-1)//2} = {len(connections)/(len(nodes)*(len(nodes)-1)//2)*100:.1f}%")
    
    # 分析概念分布
    concept_counts = {}
    for concept in concepts:
        concept_counts[concept] = concept_counts.get(concept, 0) + 1
    
    top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"   • 主要概念: {', '.join([f'{c}({n})' for c, n in top_concepts])}")

def demo_3d_features():
    """演示3D功能特性"""
    print("\n🎮 3D思维空间功能特性:")
    print("=" * 50)
    
    features = [
        "🌐 沉浸式3D可视化",
        "🧠 AI驱动的个性化空间生成",
        "🎨 四种思维模式（创意/逻辑/分析/直觉）",
        "🔗 智能概念连接和关系映射",
        "📊 实时思维性能监控",
        "🎮 VR/AR设备支持（WebXR）",
        "🎯 交互式节点探索",
        "💡 智能思维分析和建议",
        "🌈 动态颜色和动画效果",
        "📱 响应式设计，支持多设备"
    ]
    
    for feature in features:
        print(f"   {feature}")
        time.sleep(0.3)  # 添加动画效果
    
    print(f"\n🚀 技术栈:")
    tech_stack = [
        "Three.js - 3D图形渲染",
        "WebXR - VR/AR支持", 
        "FastAPI - 后端API服务",
        "NumPy/Pandas - 数据处理",
        "AI算法 - 智能空间生成"
    ]
    
    for tech in tech_stack:
        print(f"   • {tech}")

if __name__ == "__main__":
    print("🧠 智能思维3D空间系统测试")
    print("🕐 等待服务启动...")
    time.sleep(3)  # 等待服务完全启动
    
    # 演示功能特性
    demo_3d_features()
    
    # 执行系统测试
    test_3d_system()
    
    print(f"\n📝 使用说明:")
    print("1. 打开浏览器访问: http://localhost:8001")
    print("2. 点击 '进入3D思维空间' 按钮")
    print("3. 使用鼠标控制视角，点击节点查看详情")
    print("4. 调整控制面板参数体验不同效果")
    print("5. 如有VR设备，点击VR按钮进入沉浸模式") 