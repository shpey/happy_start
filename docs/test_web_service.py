#!/usr/bin/env python3
"""
测试智能思维分析Web服务
"""

import requests
import json
import time

def test_web_service():
    """测试Web服务"""
    base_url = "http://localhost:8000"
    
    print("🧪 测试智能思维分析Web服务")
    print("=" * 50)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    try:
        # 1. 测试健康检查
        print("\n1. 测试健康检查...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 服务状态: {health_data['status']}")
            print(f"✅ 模型加载: {health_data['models_loaded']}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
        
        # 2. 测试分析接口
        print("\n2. 测试思维分析接口...")
        test_data = {
            "age": 25,
            "iq_score": 120.0,
            "creativity_score": 8.5,
            "logic_score": 7.2,
            "emotional_intelligence": 8.0,
            "problem_solving_time": 25.0,
            "accuracy_rate": 0.85
        }
        
        response = requests.post(
            f"{base_url}/analyze", 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 分析成功!")
            print(f"   学习风格: {result['learning_style']}")
            print(f"   思维能力: {result['thinking_capacity']:.3f}")
            print(f"   思维模式: {result['thinking_pattern']}")
            print(f"   建议数量: {len(result['recommendations'])}")
        else:
            print(f"❌ 分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return
        
        # 3. 测试API信息
        print("\n3. 测试API信息...")
        response = requests.get(f"{base_url}/api/info", timeout=5)
        if response.status_code == 200:
            api_info = response.json()
            print(f"✅ API名称: {api_info['name']}")
            print(f"   版本: {api_info['version']}")
        
        print("\n🎉 所有测试通过！")
        print(f"\n🌐 访问地址:")
        print(f"   主页面: {base_url}/")
        print(f"   API文档: {base_url}/docs")
        print(f"   健康检查: {base_url}/health")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保服务已启动")
        print("💡 提示: 运行 'python examples/week5_web_frontend.py' 启动服务")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_web_service() 