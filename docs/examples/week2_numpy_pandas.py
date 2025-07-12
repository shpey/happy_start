#!/usr/bin/env python3
"""
智能思维项目 - 第二周NumPy和Pandas学习示例
这个文件包含了数据处理和科学计算的实践示例
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# ==================== NumPy基础示例 ====================

def numpy_basics_demo():
    """NumPy基础操作演示"""
    print("🔢 NumPy基础操作演示")
    print("-" * 30)
    
    # 1. 数组创建
    print("1. 数组创建:")
    arr1 = np.array([1, 2, 3, 4, 5])
    arr2 = np.zeros((3, 3))
    arr3 = np.random.randn(2, 4)
    
    print(f"一维数组: {arr1}")
    print(f"零矩阵: \n{arr2}")
    print(f"随机矩阵: \n{arr3}")
    
    # 2. 数组运算
    print("\n2. 数组运算:")
    x = np.array([[1, 2], [3, 4]])
    y = np.array([[5, 6], [7, 8]])
    
    print(f"矩阵x: \n{x}")
    print(f"矩阵y: \n{y}")
    print(f"矩阵乘法: \n{np.dot(x, y)}")
    print(f"元素相乘: \n{x * y}")
    
    # 3. 统计运算
    print("\n3. 统计运算:")
    data = np.random.randint(1, 100, 20)
    print(f"随机数据: {data}")
    print(f"平均值: {np.mean(data):.2f}")
    print(f"标准差: {np.std(data):.2f}")
    print(f"最大值: {np.max(data)}")
    print(f"最小值: {np.min(data)}")

def thinking_matrix_operations():
    """思维矩阵操作 - 模拟神经网络中的矩阵运算"""
    print("\n🧠 思维矩阵操作演示")
    print("-" * 30)
    
    # 模拟神经元激活值
    neurons = np.random.rand(5, 3)  # 5个神经元，3个特征
    weights = np.random.rand(3, 4)  # 权重矩阵：3个输入，4个输出
    
    print(f"神经元激活值: \n{neurons}")
    print(f"权重矩阵: \n{weights}")
    
    # 前向传播计算
    output = np.dot(neurons, weights)
    print(f"输出结果: \n{output}")
    
    # 应用激活函数（sigmoid）
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))
    
    activated_output = sigmoid(output)
    print(f"激活后输出: \n{activated_output}")
    
    return activated_output

# ==================== Pandas基础示例 ====================

def pandas_basics_demo():
    """Pandas基础操作演示"""
    print("\n📊 Pandas基础操作演示")
    print("-" * 30)
    
    # 1. DataFrame创建
    print("1. DataFrame创建:")
    thinking_data = {
        'person_id': range(1, 11),
        'iq_score': np.random.randint(90, 150, 10),
        'creativity_score': np.random.rand(10) * 10,
        'logic_score': np.random.rand(10) * 10,
        'learning_type': np.random.choice(['visual', 'auditory', 'kinesthetic'], 10),
        'age': np.random.randint(18, 65, 10)
    }
    
    df = pd.DataFrame(thinking_data)
    print(df.head())
    
    # 2. 基础统计
    print("\n2. 基础统计:")
    print(df.describe())
    
    # 3. 数据筛选和分组
    print("\n3. 数据分析:")
    print(f"高IQ群体（>120）数量: {len(df[df['iq_score'] > 120])}")
    print(f"按学习类型分组的平均创造力:")
    print(df.groupby('learning_type')['creativity_score'].mean())
    
    return df

def create_thinking_dataset():
    """创建智能思维项目的模拟数据集"""
    print("\n🎯 创建思维能力数据集")
    print("-" * 30)
    
    # 生成更复杂的思维数据
    np.random.seed(42)  # 确保可重现性
    n_samples = 100
    
    data = {
        'user_id': range(1, n_samples + 1),
        'age': np.random.randint(18, 70, n_samples),
        'education_level': np.random.choice(['high_school', 'bachelor', 'master', 'phd'], n_samples),
        'iq_score': np.random.normal(100, 15, n_samples),
        'creativity_score': np.random.beta(2, 5, n_samples) * 10,
        'logic_score': np.random.gamma(2, 2, n_samples),
        'emotional_intelligence': np.random.uniform(1, 10, n_samples),
        'learning_style': np.random.choice(['visual', 'auditory', 'kinesthetic', 'reading'], n_samples),
        'problem_solving_time': np.random.exponential(30, n_samples),  # 秒
        'accuracy_rate': np.random.beta(8, 2, n_samples),  # 0-1之间
    }
    
    df = pd.DataFrame(data)
    
    # 数据清理
    df['iq_score'] = np.clip(df['iq_score'], 70, 160)  # IQ范围限制
    df['logic_score'] = np.clip(df['logic_score'], 0, 10)  # 逻辑分数限制
    df['problem_solving_time'] = np.clip(df['problem_solving_time'], 5, 300)  # 时间限制
    
    # 计算综合思维能力指数
    df['thinking_capacity_index'] = (
        df['iq_score'] * 0.3 + 
        df['creativity_score'] * 0.25 + 
        df['logic_score'] * 0.25 + 
        df['emotional_intelligence'] * 0.2
    ) / 100
    
    print(f"数据集形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print("\n样本数据:")
    print(df.head())
    
    return df

def analyze_thinking_patterns(df):
    """分析思维模式"""
    print("\n🔍 思维模式分析")
    print("-" * 30)
    
    # 1. 相关性分析
    print("1. 各能力指标相关性:")
    correlation_cols = ['iq_score', 'creativity_score', 'logic_score', 'emotional_intelligence']
    correlation_matrix = df[correlation_cols].corr()
    print(correlation_matrix.round(3))
    
    # 2. 教育水平与能力分析
    print("\n2. 教育水平与思维能力关系:")
    education_analysis = df.groupby('education_level').agg({
        'iq_score': 'mean',
        'creativity_score': 'mean',
        'logic_score': 'mean',
        'thinking_capacity_index': 'mean'
    }).round(2)
    print(education_analysis)
    
    # 3. 学习风格分析
    print("\n3. 学习风格与表现关系:")
    learning_style_analysis = df.groupby('learning_style').agg({
        'accuracy_rate': 'mean',
        'problem_solving_time': 'mean',
        'thinking_capacity_index': 'mean'
    }).round(2)
    print(learning_style_analysis)
    
    # 4. 年龄与能力关系
    print("\n4. 年龄段分析:")
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 50, 100], labels=['18-25', '26-35', '36-50', '51+'])
    age_analysis = df.groupby('age_group')['thinking_capacity_index'].mean()
    print(age_analysis.round(3))
    
    return correlation_matrix

def save_analysis_results(df, correlation_matrix):
    """保存分析结果"""
    print("\n💾 保存分析结果")
    print("-" * 30)
    
    # 保存数据集
    df.to_csv('data/thinking_dataset.csv', index=False, encoding='utf-8')
    print("✅ 数据集已保存到: data/thinking_dataset.csv")
    
    # 保存相关性矩阵
    correlation_matrix.to_csv('data/correlation_analysis.csv', encoding='utf-8')
    print("✅ 相关性分析已保存到: data/correlation_analysis.csv")
    
    # 创建分析报告
    report = f"""
智能思维项目 - 数据分析报告
==============================

数据集概况:
- 样本数量: {len(df)}
- 特征数量: {len(df.columns)}
- 平均思维能力指数: {df['thinking_capacity_index'].mean():.3f}

关键发现:
1. IQ与逻辑思维能力相关性最高: {correlation_matrix.loc['iq_score', 'logic_score']:.3f}
2. 创造力与情商相关性: {correlation_matrix.loc['creativity_score', 'emotional_intelligence']:.3f}
3. 最佳年龄段: {df.groupby('age_group')['thinking_capacity_index'].mean().idxmax()}

建议:
- 重点培养逻辑思维和创造力的平衡发展
- 根据学习风格设计个性化训练方案
- 关注不同年龄段的认知特点
"""
    
    with open('data/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("✅ 分析报告已保存到: data/analysis_report.txt")

# ==================== 主程序 ====================

def main():
    """主程序"""
    print("🧠 智能思维项目 - 第二周NumPy & Pandas学习")
    print("=" * 60)
    
    # 创建数据目录
    import os
    os.makedirs('data', exist_ok=True)
    
    # 1. NumPy基础演示
    numpy_basics_demo()
    
    # 2. 思维矩阵操作
    thinking_matrix_operations()
    
    # 3. Pandas基础演示
    simple_df = pandas_basics_demo()
    
    # 4. 创建复杂数据集
    thinking_df = create_thinking_dataset()
    
    # 5. 数据分析
    correlation_matrix = analyze_thinking_patterns(thinking_df)
    
    # 6. 保存结果
    save_analysis_results(thinking_df, correlation_matrix)
    
    print("\n🎉 第二周学习完成！")
    print("📚 下一步: 开始机器学习基础学习（第3-4周）")
    print("💡 建议: 复习今天学到的NumPy和Pandas操作，它们是AI开发的基础！")

# ==================== 练习题 ====================

def practice_exercises():
    """第二周练习题"""
    print("\n🎯 第二周练习题:")
    print("-" * 30)
    
    exercises = [
        "练习1: 创建一个函数，计算两个向量的余弦相似度",
        "练习2: 使用Pandas分析不同学习风格的最佳学习时间",
        "练习3: 实现一个简单的数据标准化函数（z-score归一化）",
        "练习4: 创建一个函数，找出思维能力最相似的用户对",
        "练习5: 使用NumPy实现一个简单的神经元激活函数库"
    ]
    
    for exercise in exercises:
        print(exercise)
    
    print("\n💡 提示: 这些练习将帮助你掌握数据科学的核心技能！")

if __name__ == "__main__":
    main()
    practice_exercises() 