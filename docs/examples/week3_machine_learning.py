#!/usr/bin/env python3
"""
智能思维项目 - 第三周机器学习基础示例
这个文件包含了Scikit-learn机器学习的实践示例
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# ==================== 监督学习：分类任务 ====================

def thinking_style_classification():
    """思维风格分类任务 - 根据认知特征预测学习风格"""
    print("🎯 思维风格分类任务")
    print("-" * 40)
    
    # 加载数据
    df = pd.read_csv('data/thinking_dataset.csv')
    
    # 特征选择：认知相关特征
    feature_cols = ['iq_score', 'creativity_score', 'logic_score', 
                   'emotional_intelligence', 'problem_solving_time', 'accuracy_rate']
    X = df[feature_cols]
    y = df['learning_style']
    
    # 数据预处理
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 编码标签
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"训练集大小: {len(X_train)}")
    print(f"测试集大小: {len(X_test)}")
    print(f"学习风格类别: {label_encoder.classes_}")
    
    # 尝试多种分类算法
    classifiers = {
        '随机森林': RandomForestClassifier(n_estimators=100, random_state=42),
        '逻辑回归': LogisticRegression(random_state=42, max_iter=1000),
        '支持向量机': SVC(random_state=42),
        'K近邻': KNeighborsClassifier(n_neighbors=5)
    }
    
    results = {}
    
    for name, clf in classifiers.items():
        # 训练模型
        clf.fit(X_train, y_train)
        
        # 预测
        y_pred = clf.predict(X_test)
        
        # 评估
        accuracy = accuracy_score(y_test, y_pred)
        
        # 交叉验证
        cv_scores = cross_val_score(clf, X_scaled, y_encoded, cv=5)
        
        results[name] = {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        
        print(f"\n{name}:")
        print(f"  测试准确率: {accuracy:.3f}")
        print(f"  交叉验证: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # 选择最佳模型
    best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
    best_model = classifiers[best_model_name]
    
    print(f"\n🏆 最佳模型: {best_model_name}")
    
    # 特征重要性分析（如果支持）
    if hasattr(best_model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n特征重要性:")
        print(feature_importance)
    
    return best_model, scaler, label_encoder

# ==================== 监督学习：回归任务 ====================

def thinking_capacity_prediction():
    """思维能力预测任务 - 预测综合思维能力指数"""
    print("\n📈 思维能力预测任务")
    print("-" * 40)
    
    # 加载数据
    df = pd.read_csv('data/thinking_dataset.csv')
    
    # 特征选择
    feature_cols = ['age', 'iq_score', 'creativity_score', 'logic_score', 
                   'emotional_intelligence', 'problem_solving_time', 'accuracy_rate']
    X = df[feature_cols]
    y = df['thinking_capacity_index']
    
    # 数据预处理
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # 尝试多种回归算法
    regressors = {
        '随机森林回归': RandomForestRegressor(n_estimators=100, random_state=42),
        '线性回归': LinearRegression()
    }
    
    results = {}
    
    for name, reg in regressors.items():
        # 训练模型
        reg.fit(X_train, y_train)
        
        # 预测
        y_pred = reg.predict(X_test)
        
        # 评估
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        results[name] = {
            'mse': mse,
            'r2': r2,
            'rmse': np.sqrt(mse)
        }
        
        print(f"\n{name}:")
        print(f"  均方误差 (MSE): {mse:.6f}")
        print(f"  R² 分数: {r2:.3f}")
        print(f"  均方根误差 (RMSE): {np.sqrt(mse):.6f}")
    
    # 选择最佳模型
    best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
    best_model = regressors[best_model_name]
    
    print(f"\n🏆 最佳回归模型: {best_model_name}")
    
    return best_model, scaler

# ==================== 无监督学习：聚类分析 ====================

def thinking_pattern_clustering():
    """思维模式聚类分析"""
    print("\n🔍 思维模式聚类分析")
    print("-" * 40)
    
    # 加载数据
    df = pd.read_csv('data/thinking_dataset.csv')
    
    # 选择认知特征
    feature_cols = ['iq_score', 'creativity_score', 'logic_score', 'emotional_intelligence']
    X = df[feature_cols]
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 确定最佳聚类数量
    inertias = []
    K_range = range(2, 9)
    
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
    
    # 使用肘部法则选择K值
    # 简单选择K=4 (对应不同的思维模式)
    optimal_k = 4
    
    print(f"选择聚类数量: {optimal_k}")
    
    # 执行K-means聚类
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)
    
    # 添加聚类标签到数据框
    df_clustered = df.copy()
    df_clustered['cluster'] = cluster_labels
    
    # 分析各聚类的特征
    print("\n聚类分析结果:")
    cluster_analysis = df_clustered.groupby('cluster')[feature_cols].mean()
    print(cluster_analysis.round(2))
    
    # 为每个聚类命名
    cluster_names = {
        0: "平衡型思维者",
        1: "逻辑主导型",
        2: "创意型思维者", 
        3: "情感智能型"
    }
    
    print(f"\n聚类解释:")
    for cluster_id, cluster_name in cluster_names.items():
        cluster_data = cluster_analysis.loc[cluster_id]
        dominant_feature = cluster_data.idxmax()
        print(f"聚类 {cluster_id} - {cluster_name}:")
        print(f"  主导特征: {dominant_feature}")
        print(f"  样本数量: {sum(cluster_labels == cluster_id)}")
    
    return kmeans, scaler, cluster_names

# ==================== 无监督学习：降维分析 ====================

def thinking_dimension_reduction():
    """思维特征降维分析"""
    print("\n📊 思维特征降维分析 (PCA)")
    print("-" * 40)
    
    # 加载数据
    df = pd.read_csv('data/thinking_dataset.csv')
    
    # 选择数值特征
    numeric_features = ['age', 'iq_score', 'creativity_score', 'logic_score', 
                       'emotional_intelligence', 'problem_solving_time', 'accuracy_rate']
    X = df[numeric_features]
    
    # 数据标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 执行PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)
    
    # 分析主成分
    print("主成分分析结果:")
    print(f"各主成分解释的方差比例:")
    for i, ratio in enumerate(pca.explained_variance_ratio_):
        print(f"  PC{i+1}: {ratio:.3f} ({ratio*100:.1f}%)")
    
    # 累积解释方差
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    print(f"\n前3个主成分累积解释方差: {cumulative_variance[2]:.3f} ({cumulative_variance[2]*100:.1f}%)")
    
    # 选择保留的主成分数量（解释95%方差）
    n_components_95 = np.argmax(cumulative_variance >= 0.95) + 1
    print(f"解释95%方差需要的主成分数量: {n_components_95}")
    
    # 重新执行PCA，保留主要成分
    pca_reduced = PCA(n_components=n_components_95)
    X_pca_reduced = pca_reduced.fit_transform(X_scaled)
    
    # 分析主成分组成
    print(f"\n主成分组成 (前{n_components_95}个):")
    components_df = pd.DataFrame(
        pca_reduced.components_[:n_components_95].T,
        columns=[f'PC{i+1}' for i in range(n_components_95)],
        index=numeric_features
    )
    print(components_df.round(3))
    
    return pca_reduced, scaler

# ==================== 模型集成与评估 ====================

def create_thinking_ai_system():
    """创建智能思维AI系统"""
    print("\n🤖 创建智能思维AI系统")
    print("-" * 40)
    
    # 训练各种模型
    print("1. 训练思维风格分类器...")
    style_classifier, style_scaler, style_encoder = thinking_style_classification()
    
    print("\n2. 训练思维能力预测器...")
    capacity_predictor, capacity_scaler = thinking_capacity_prediction()
    
    print("\n3. 训练思维模式聚类器...")
    pattern_clusterer, cluster_scaler, cluster_names = thinking_pattern_clustering()
    
    print("\n4. 训练降维分析器...")
    dimension_reducer, dim_scaler = thinking_dimension_reduction()
    
    # 创建综合AI系统类
    class ThinkingAISystem:
        def __init__(self, style_clf, capacity_pred, pattern_cluster, dim_reducer, 
                     style_scaler, capacity_scaler, cluster_scaler, dim_scaler, style_encoder, cluster_names):
            self.style_classifier = style_clf
            self.capacity_predictor = capacity_pred
            self.pattern_clusterer = pattern_cluster
            self.dimension_reducer = dim_reducer
            self.style_scaler = style_scaler
            self.capacity_scaler = capacity_scaler
            self.cluster_scaler = cluster_scaler
            self.dim_scaler = dim_scaler
            self.style_encoder = style_encoder
            self.cluster_names = cluster_names
        
        def analyze_user(self, user_data):
            """分析用户的思维特征"""
            # 提取特征
            style_features = [user_data['iq_score'], user_data['creativity_score'], user_data['logic_score'], 
                             user_data['emotional_intelligence'], user_data['problem_solving_time'], user_data['accuracy_rate']]
            capacity_features = [user_data['age'], user_data['iq_score'], user_data['creativity_score'], user_data['logic_score'], 
                                user_data['emotional_intelligence'], user_data['problem_solving_time'], user_data['accuracy_rate']]
            cluster_features = [user_data['iq_score'], user_data['creativity_score'], user_data['logic_score'], user_data['emotional_intelligence']]
            
            # 预测学习风格
            style_scaled = self.style_scaler.transform([style_features])
            style_pred = self.style_classifier.predict(style_scaled)[0]
            predicted_style = self.style_encoder.inverse_transform([style_pred])[0]
            
            # 预测思维能力 (使用正确的scaler)
            capacity_scaled = self.capacity_scaler.transform([capacity_features])
            predicted_capacity = self.capacity_predictor.predict(capacity_scaled)[0]
            
            # 聚类分析
            cluster_scaled = self.cluster_scaler.transform([cluster_features])
            cluster_pred = self.pattern_clusterer.predict(cluster_scaled)[0]
            thinking_pattern = self.cluster_names[cluster_pred]
            
            return {
                'learning_style': predicted_style,
                'thinking_capacity': predicted_capacity,
                'thinking_pattern': thinking_pattern,
                'recommendations': self._generate_recommendations(predicted_style, thinking_pattern)
            }
        
        def _generate_recommendations(self, style, pattern):
            """根据分析结果生成建议"""
            recommendations = []
            
            if style == 'visual':
                recommendations.append("使用图表、思维导图等视觉化工具")
            elif style == 'auditory':
                recommendations.append("通过讲解、讨论等听觉方式学习")
            elif style == 'kinesthetic':
                recommendations.append("通过实践操作、体验式学习")
            elif style == 'reading':
                recommendations.append("通过阅读文本、笔记等方式学习")
            
            if '创意' in pattern:
                recommendations.append("多参与头脑风暴和创新项目")
            elif '逻辑' in pattern:
                recommendations.append("加强逻辑推理和分析训练")
            elif '情感' in pattern:
                recommendations.append("注重团队协作和情感智能发展")
            
            return recommendations
    
    # 创建系统实例
    ai_system = ThinkingAISystem(
        style_classifier, capacity_predictor, pattern_clusterer, dimension_reducer,
        style_scaler, capacity_scaler, cluster_scaler, dim_scaler, style_encoder, cluster_names
    )
    
    print("\n✅ 智能思维AI系统创建完成！")
    
    return ai_system

# ==================== 主程序 ====================

def main():
    """主程序"""
    print("🧠 智能思维项目 - 第三周机器学习基础")
    print("=" * 60)
    
    # 创建智能思维AI系统
    ai_system = create_thinking_ai_system()
    
    # 测试系统
    print("\n🧪 测试智能思维AI系统")
    print("-" * 40)
    
    # 模拟用户数据
    test_user = {
        'age': 25,
        'iq_score': 120,
        'creativity_score': 8.5,
        'logic_score': 7.2,
        'emotional_intelligence': 8.0,
        'problem_solving_time': 25.0,
        'accuracy_rate': 0.85
    }
    
    # 分析用户
    analysis_result = ai_system.analyze_user(test_user)
    
    print("测试用户分析结果:")
    print(f"  学习风格: {analysis_result['learning_style']}")
    print(f"  思维能力指数: {analysis_result['thinking_capacity']:.3f}")
    print(f"  思维模式: {analysis_result['thinking_pattern']}")
    print("  个性化建议:")
    for recommendation in analysis_result['recommendations']:
        print(f"    - {recommendation}")
    
    print("\n🎉 第三周机器学习基础学习完成！")
    print("📚 下一步: 深度学习入门（第5-6周）")
    print("💡 已掌握技能: 分类、回归、聚类、降维、模型评估")

# ==================== 练习题 ====================

def practice_exercises():
    """第三周练习题"""
    print("\n🎯 第三周练习题:")
    print("-" * 30)
    
    exercises = [
        "练习1: 实现一个自定义的思维风格分类器（不使用Scikit-learn）",
        "练习2: 使用网格搜索优化模型超参数",
        "练习3: 实现模型的保存和加载功能",
        "练习4: 添加更多评估指标（精确率、召回率、F1分数）",
        "练习5: 创建一个Web界面来测试思维分析系统"
    ]
    
    for exercise in exercises:
        print(exercise)
    
    print("\n💡 提示: 这些练习将帮助你深入理解机器学习的核心概念！")

if __name__ == "__main__":
    main()
    practice_exercises() 