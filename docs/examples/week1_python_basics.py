#!/usr/bin/env python3
"""
智能思维项目 - 第一周Python基础示例
这个文件包含了Python基础概念的实践示例
"""

import math
import random
from typing import List, Dict, Any

# ==================== 基础语法示例 ====================

def greeting(name: str) -> str:
    """简单的问候函数"""
    return f"你好，{name}！欢迎来到智能思维项目！"

def calculate_thinking_capacity(iq: int, experience: int, creativity: int) -> float:
    """
    计算思维能力指数的简单模型
    这个函数模拟了我们项目中的思维量化概念
    """
    # 简单的加权计算
    capacity = (iq * 0.4 + experience * 0.3 + creativity * 0.3) / 100
    return round(capacity, 2)

# ==================== 数据结构示例 ====================

class ThinkingNode:
    """思维节点类 - 代表知识图谱中的一个概念"""
    
    def __init__(self, concept: str, node_type: str = "general"):
        self.concept = concept
        self.node_type = node_type  # "imagery", "logic", "creative"
        self.connections = []
        self.strength = random.randint(1, 10)
    
    def connect_to(self, other_node: 'ThinkingNode', relation: str = "related"):
        """连接到另一个思维节点"""
        connection = {
            "target": other_node.concept,
            "relation": relation,
            "strength": random.randint(1, 5)
        }
        self.connections.append(connection)
    
    def __str__(self):
        return f"思维节点: {self.concept} (类型: {self.node_type}, 强度: {self.strength})"

def create_knowledge_network(concepts: List[str]) -> Dict[str, ThinkingNode]:
    """创建一个简单的知识网络"""
    network = {}
    
    # 创建节点
    for concept in concepts:
        # 根据概念类型分配节点类型
        if any(word in concept for word in ["图像", "颜色", "形状"]):
            node_type = "imagery"
        elif any(word in concept for word in ["逻辑", "推理", "证明"]):
            node_type = "logic"
        elif any(word in concept for word in ["创意", "想象", "艺术"]):
            node_type = "creative"
        else:
            node_type = "general"
        
        network[concept] = ThinkingNode(concept, node_type)
    
    # 创建随机连接
    concept_list = list(concepts)
    for concept in concepts:
        current_node = network[concept]
        # 每个节点连接到1-3个其他节点
        num_connections = random.randint(1, min(3, len(concept_list) - 1))
        other_concepts = [c for c in concept_list if c != concept]
        
        for _ in range(num_connections):
            target_concept = random.choice(other_concepts)
            current_node.connect_to(network[target_concept])
    
    return network

# ==================== 数据处理示例 ====================

def analyze_thinking_data(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析思维数据的简单统计"""
    if not data:
        return {"error": "没有数据可分析"}
    
    # 计算各种统计指标
    total_entries = len(data)
    
    # 统计思维类型分布
    type_distribution = {}
    creativity_scores = []
    logic_scores = []
    
    for entry in data:
        thinking_type = entry.get("type", "unknown")
        type_distribution[thinking_type] = type_distribution.get(thinking_type, 0) + 1
        
        if "creativity_score" in entry:
            creativity_scores.append(entry["creativity_score"])
        if "logic_score" in entry:
            logic_scores.append(entry["logic_score"])
    
    # 计算平均值
    avg_creativity = sum(creativity_scores) / len(creativity_scores) if creativity_scores else 0
    avg_logic = sum(logic_scores) / len(logic_scores) if logic_scores else 0
    
    return {
        "总数据量": total_entries,
        "思维类型分布": type_distribution,
        "平均创造力得分": round(avg_creativity, 2),
        "平均逻辑得分": round(avg_logic, 2),
        "创造力范围": f"{min(creativity_scores) if creativity_scores else 0} - {max(creativity_scores) if creativity_scores else 0}",
        "逻辑力范围": f"{min(logic_scores) if logic_scores else 0} - {max(logic_scores) if logic_scores else 0}"
    }

# ==================== 文件操作示例 ====================

def save_thinking_session(session_data: Dict[str, Any], filename: str = "thinking_session.txt"):
    """保存思维会话数据到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("智能思维系统 - 会话记录\n")
            file.write("=" * 40 + "\n\n")
            
            for key, value in session_data.items():
                file.write(f"{key}: {value}\n")
            
            file.write(f"\n记录时间: {__import__('datetime').datetime.now()}")
        
        print(f"会话数据已保存到 {filename}")
        return True
    
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def load_thinking_session(filename: str = "thinking_session.txt") -> str:
    """从文件读取思维会话数据"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "找不到会话文件，请先创建一个会话。"
    except Exception as e:
        return f"读取失败: {e}"

# ==================== 主程序示例 ====================

def main():
    """主程序 - 演示各种功能"""
    print("🧠 智能思维项目 - Python基础练习")
    print("=" * 50)
    
    # 1. 基础函数演示
    print("\n1. 基础功能演示:")
    print(greeting("学习者"))
    
    capacity = calculate_thinking_capacity(120, 75, 90)
    print(f"思维能力指数: {capacity}")
    
    # 2. 数据结构演示
    print("\n2. 知识网络演示:")
    concepts = ["逻辑推理", "图像识别", "创意写作", "数学计算", "艺术欣赏"]
    network = create_knowledge_network(concepts)
    
    for concept, node in network.items():
        print(node)
        if node.connections:
            print(f"  连接: {[conn['target'] for conn in node.connections[:2]]}")
    
    # 3. 数据分析演示
    print("\n3. 数据分析演示:")
    sample_data = [
        {"type": "imagery", "creativity_score": 8.5, "logic_score": 6.2},
        {"type": "logic", "creativity_score": 6.0, "logic_score": 9.1},
        {"type": "creative", "creativity_score": 9.2, "logic_score": 5.8},
        {"type": "imagery", "creativity_score": 7.8, "logic_score": 7.0},
        {"type": "logic", "creativity_score": 5.5, "logic_score": 8.9}
    ]
    
    analysis = analyze_thinking_data(sample_data)
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    # 4. 文件操作演示
    print("\n4. 文件操作演示:")
    session_data = {
        "用户名": "学习者",
        "会话类型": "基础练习",
        "思维能力指数": capacity,
        "处理的概念数量": len(concepts)
    }
    
    if save_thinking_session(session_data):
        content = load_thinking_session()
        print("读取的文件内容:")
        print(content[:200] + "..." if len(content) > 200 else content)

# ==================== 练习题 ====================

def practice_exercises():
    """第一周的练习题"""
    print("\n🎯 第一周练习题:")
    print("-" * 30)
    
    print("\n练习1: 修改calculate_thinking_capacity函数，添加新的参数'focus'（专注力）")
    print("练习2: 为ThinkingNode类添加一个方法calculate_influence()，计算节点的影响力")
    print("练习3: 创建一个函数filter_nodes_by_type()，筛选特定类型的节点")
    print("练习4: 实现一个简单的思维路径查找算法")
    print("练习5: 添加错误处理，让程序更加健壮")
    
    print("\n💡 提示: 这些练习将帮助你理解面向对象编程和数据处理的核心概念！")

if __name__ == "__main__":
    main()
    practice_exercises()
    
    print("\n🎉 恭喜完成第一周的Python基础学习！")
    print("下一步: 开始学习NumPy和Pandas进行数据处理") 