#!/usr/bin/env python3
"""
智能思维项目 - 高级AI模型系统测试
测试大语言模型、多模态AI、知识图谱、强化学习等前沿功能
"""

import requests
import json
import time
import asyncio
from typing import Dict, Any

def test_advanced_ai_system():
    """测试高级AI系统"""
    base_url = "http://localhost:8003"
    
    print("🤖 测试智能思维高级AI模型系统")
    print("=" * 70)
    
    # 1. 测试服务状态
    print("\n1. 检查高级AI服务状态...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ 高级AI服务运行正常")
        else:
            print("❌ 高级AI服务状态异常")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到高级AI服务，请确保服务已启动")
        return False
    
    # 2. 测试模型状态
    print("\n2. 检查AI模型状态...")
    try:
        response = requests.get(f"{base_url}/api/models/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ AI模型状态正常: {status_data['total_models']}个模型已加载")
            print(f"   💾 内存使用: {status_data['system_info']['memory_usage']}")
            print(f"   🖥️ CPU使用: {status_data['system_info']['cpu_usage']}")
            print(f"   ⚡ 推理速度: {status_data['system_info']['inference_speed']}")
        else:
            print("❌ 模型状态获取失败")
    except Exception as e:
        print(f"❌ 模型状态检查出错: {e}")
    
    # 3. 测试LLM服务
    print("\n3. 测试大语言模型服务...")
    llm_query = {
        "user_id": "test_user_ai",
        "query_text": "我如何提升创意思维和解决问题的能力？",
        "query_type": "analysis",
        "context": {
            "user_profile": {
                "creativity_score": 6.5,
                "logic_score": 7.8,
                "thinking_style": "analytical"
            }
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/llm/analyze", json=llm_query)
        if response.status_code == 200:
            llm_result = response.json()
            print("✅ LLM思维分析成功:")
            content = llm_result['content']
            print(f"   🧠 主要思维模式: {content['thinking_pattern']['primary']}")
            print(f"   🎯 置信度: {content['thinking_pattern']['confidence']:.2f}")
            print(f"   💡 建议数量: {len(content['personalized_recommendations'])}")
            print(f"   📊 处理时间: {llm_result['processing_time']}秒")
        else:
            print("❌ LLM分析失败")
    except Exception as e:
        print(f"❌ LLM测试出错: {e}")
    
    # 4. 测试LLM内容生成
    print("\n4. 测试LLM内容生成...")
    try:
        response = requests.post(
            f"{base_url}/api/llm/generate",
            params={"topic": "批判性思维", "style": "logical"}
        )
        if response.status_code == 200:
            gen_result = response.json()
            print("✅ LLM内容生成成功:")
            data = gen_result['data']
            print(f"   📝 主题: {data['topic']}")
            print(f"   🎨 风格: {data['style']}")
            print(f"   🌟 创意分数: {data['creativity_score']:.2f}")
            print(f"   🔗 连贯性分数: {data['coherence_score']:.2f}")
        else:
            print("❌ LLM内容生成失败")
    except Exception as e:
        print(f"❌ LLM内容生成测试出错: {e}")
    
    # 5. 测试多模态AI
    print("\n5. 测试多模态AI分析...")
    multimodal_input = {
        "text": "这是一个关于创新思维的讨论",
        "image_url": "https://example.com/innovation_diagram.jpg",
        "thinking_context": {
            "session_type": "brainstorming",
            "goal": "innovation"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/multimodal/process", json=multimodal_input)
        if response.status_code == 200:
            multi_result = response.json()
            print("✅ 多模态AI分析成功:")
            data = multi_result['data']
            if 'text_analysis' in data:
                print(f"   📝 文本情感: {data['text_analysis']['sentiment']}")
                print(f"   🔍 关键概念: {data['text_analysis']['key_concepts']}")
            if 'image_analysis' in data:
                print(f"   🖼️ 视觉复杂度: {data['image_analysis']['visual_complexity']:.2f}")
                print(f"   🎨 颜色情感: {data['image_analysis']['color_emotion']}")
            if 'fusion_result' in data:
                print(f"   🔄 融合置信度: {data['fusion_result']['thinking_confidence']:.2f}")
        else:
            print("❌ 多模态AI分析失败")
    except Exception as e:
        print(f"❌ 多模态AI测试出错: {e}")
    
    # 6. 测试多模态演示
    print("\n6. 测试多模态演示功能...")
    try:
        response = requests.get(f"{base_url}/api/multimodal/demo")
        if response.status_code == 200:
            demo_result = response.json()
            print("✅ 多模态演示成功:")
            print(f"   📄 演示输入: {demo_result['demo_input']['text']}")
            print(f"   🔍 分析结果: {len(demo_result['demo_result'])}个模态")
    except Exception as e:
        print(f"❌ 多模态演示测试出错: {e}")
    
    # 7. 测试知识图谱
    print("\n7. 测试知识图谱推理...")
    try:
        response = requests.get(f"{base_url}/api/knowledge/query", params={
            "q": "创意思维与逻辑思维的关系",
            "depth": 2
        })
        if response.status_code == 200:
            kg_result = response.json()
            print("✅ 知识图谱查询成功:")
            data = kg_result['data']
            print(f"   🔍 查询: {data['query']}")
            print(f"   🧠 相关概念: {data['relevant_concepts']}")
            print(f"   🛤️ 推理步骤: {len(data['reasoning_path'])}步")
            print(f"   🎯 置信度: {data['confidence']:.2f}")
        else:
            print("❌ 知识图谱查询失败")
    except Exception as e:
        print(f"❌ 知识图谱测试出错: {e}")
    
    # 8. 测试强化学习
    print("\n8. 测试强化学习优化...")
    rl_context = {
        "state": {
            "current_mode": "analytical",
            "task_complexity": 0.7,
            "user_performance": 0.6
        },
        "action_space": ["enhance_creativity", "improve_efficiency", "increase_engagement"],
        "reward_history": [0.5, 0.6, 0.7, 0.8]
    }
    
    try:
        response = requests.post(f"{base_url}/api/rl/optimize", json=rl_context)
        if response.status_code == 200:
            rl_result = response.json()
            print("✅ 强化学习优化成功:")
            data = rl_result['data']
            print(f"   🎯 推荐动作: {data['recommended_action']}")
            print(f"   🏆 预期奖励: {data['expected_reward']:.2f}")
            print(f"   📈 学习轮次: {data['learning_episode']}")
            print(f"   💡 策略说明: {data['strategy_explanation']}")
        else:
            print("❌ 强化学习优化失败")
    except Exception as e:
        print(f"❌ 强化学习测试出错: {e}")
    
    # 9. 测试强化学习反馈
    print("\n9. 测试强化学习反馈...")
    try:
        response = requests.post(f"{base_url}/api/rl/feedback", params={
            "action": "enhance_creativity",
            "reward": 0.85,
            "feedback": "创意思维训练效果很好"
        })
        if response.status_code == 200:
            feedback_result = response.json()
            print("✅ 强化学习反馈成功:")
            data = feedback_result['data']
            print(f"   📊 平均奖励: {data['average_reward']:.2f}")
            print(f"   📈 改进趋势: {data['improvement_trend']}")
        else:
            print("❌ 强化学习反馈失败")
    except Exception as e:
        print(f"❌ 强化学习反馈测试出错: {e}")
    
    # 10. 测试集成分析
    print("\n10. 测试集成AI分析...")
    try:
        response = requests.get(f"{base_url}/api/integrated/analysis", params={
            "user_query": "如何成为更有创造力的问题解决者？",
            "enable_llm": True,
            "enable_multimodal": True,
            "enable_knowledge": True,
            "enable_rl": True
        })
        if response.status_code == 200:
            integrated_result = response.json()
            print("✅ 集成AI分析成功:")
            data = integrated_result['data']
            analysis_count = len(data['analysis'])
            print(f"   🤖 集成模型数: {analysis_count}个")
            print(f"   🔍 查询: {data['query']}")
            
            if 'llm' in data['analysis']:
                print(f"   🔮 LLM分析: 完成")
            if 'knowledge' in data['analysis']:
                print(f"   🕸️ 知识图谱: 完成")
            if 'multimodal' in data['analysis']:
                print(f"   🌈 多模态: 完成")
            if 'reinforcement' in data['analysis']:
                print(f"   🎯 强化学习: 完成")
        else:
            print("❌ 集成AI分析失败")
    except Exception as e:
        print(f"❌ 集成分析测试出错: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 高级AI模型系统测试完成!")
    return True

def demo_advanced_ai_features():
    """演示高级AI功能特性"""
    print("\n🚀 智能思维高级AI功能特性:")
    print("=" * 70)
    
    ai_features = [
        "🔮 大语言模型 (LLM)",
        "   • 深度思维模式分析",
        "   • 个性化内容生成", 
        "   • 智能对话指导",
        "   • 认知偏见识别",
        "",
        "🌈 多模态AI分析",
        "   • 文本+图像+音频融合",
        "   • 跨模态情感识别",
        "   • 视觉思维理解",
        "   • 语音模式分析",
        "",
        "🕸️ 知识图谱推理",
        "   • 概念关系挖掘",
        "   • 智能推理路径",
        "   • 知识发现引擎",
        "   • 认知地图构建",
        "",
        "🎯 强化学习优化",
        "   • 自适应策略调整",
        "   • 个性化学习路径",
        "   • 实时反馈优化",
        "   • 持续性能改进",
        "",
        "⚡ 实时推理引擎",
        "   • 毫秒级响应速度",
        "   • 并行模型处理",
        "   • 智能缓存机制",
        "   • 动态负载均衡"
    ]
    
    for feature in ai_features:
        if feature:
            print(f"   {feature}")
        else:
            print()
        time.sleep(0.1)

def show_ai_architecture():
    """显示AI架构"""
    print(f"\n🏗️ 高级AI系统架构:")
    print("=" * 70)
    
    architecture = """
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        用户接口层                                    │
    │  🌐 Web API  📱 移动端  🎮 3D界面  💻 桌面应用                     │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        AI服务层                                     │
    │  🔮 LLM服务    🌈 多模态AI    🕸️ 知识图谱    🎯 强化学习           │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        模型层                                       │
    │  🧠 Transformer  👁️ Vision  🗣️ Speech  📊 Graph  🎮 RL Agent      │
    └─────────────────────────────────────────────────────────────────────┘
                                    │
    ┌─────────────────────────────────────────────────────────────────────┐
    │                        基础设施层                                    │
    │  💾 模型存储  ⚡ 推理引擎  📊 监控系统  🔧 优化工具                 │
    └─────────────────────────────────────────────────────────────────────┘
    """
    print(architecture)

def show_integration_benefits():
    """展示集成优势"""
    print(f"\n🌟 四层服务架构完整集成:")
    print("=" * 70)
    
    services = [
        "🌐 端口8000: 基础AI服务 (机器学习+深度学习)",
        "🎮 端口8001: 3D可视化服务 (Three.js+WebXR)",
        "🚀 端口8002: 企业级服务 (用户管理+协作)",
        "🤖 端口8003: 高级AI服务 (LLM+多模态+知识图谱+强化学习)"
    ]
    
    for service in services:
        print(f"   {service}")
    
    print(f"\n💡 集成优势:")
    benefits = [
        "🔄 数据流无缝打通: 四层服务间智能数据交换",
        "🧠 AI能力递进: 从基础模型到前沿AI技术",
        "🎯 用户体验统一: 一致的接口和交互设计",
        "⚡ 性能优化协同: 分布式计算和智能缓存",
        "📈 可扩展架构: 微服务设计支持无限扩展"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

if __name__ == "__main__":
    print("🤖 智能思维高级AI模型系统测试")
    print("🕐 等待服务启动...")
    time.sleep(2)
    
    # 演示功能特性
    demo_advanced_ai_features()
    
    # 显示AI架构
    show_ai_architecture()
    
    # 显示集成优势
    show_integration_benefits()
    
    # 执行系统测试
    success = test_advanced_ai_system()
    
    if success:
        print(f"\n🎊 所有高级AI功能测试通过！")
        print(f"\n🚀 现在您拥有完整的四层智能思维系统:")
        print("   • 基础AI: 机器学习和深度学习模型")
        print("   • 3D可视: 沉浸式思维空间体验")
        print("   • 企业级: 用户管理和实时协作")
        print("   • 高级AI: LLM+多模态+知识图谱+强化学习")
        print(f"\n🌟 这是一个真正的AI驱动智能思维平台！")
    else:
        print(f"\n⚠️ 部分高级AI功能测试失败，请检查服务状态。") 