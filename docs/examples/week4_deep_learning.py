#!/usr/bin/env python3
"""
智能思维项目 - 第四周深度学习基础示例
这个文件包含了PyTorch深度学习的实践示例
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset, TensorDataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# 设置随机种子
torch.manual_seed(42)
np.random.seed(42)

# ==================== PyTorch基础操作 ====================

def pytorch_basics_demo():
    """PyTorch基础操作演示"""
    print("🔥 PyTorch基础操作演示")
    print("-" * 40)
    
    # 1. 张量创建和操作
    print("1. 张量基础操作:")
    
    # 创建张量
    x = torch.tensor([1, 2, 3, 4, 5], dtype=torch.float32)
    y = torch.randn(2, 3)
    z = torch.zeros(3, 3)
    
    print(f"一维张量: {x}")
    print(f"随机张量: \n{y}")
    print(f"零张量: \n{z}")
    
    # 张量运算
    print("\n2. 张量运算:")
    a = torch.tensor([[1, 2], [3, 4]], dtype=torch.float32)
    b = torch.tensor([[5, 6], [7, 8]], dtype=torch.float32)
    
    print(f"张量a: \n{a}")
    print(f"张量b: \n{b}")
    print(f"矩阵乘法: \n{torch.mm(a, b)}")
    print(f"元素相乘: \n{a * b}")
    
    # 3. 自动梯度计算
    print("\n3. 自动梯度计算:")
    x = torch.tensor([2.0], requires_grad=True)
    y = x ** 2 + 3 * x + 1
    
    print(f"x = {x.item()}")
    print(f"y = x² + 3x + 1 = {y.item()}")
    
    # 反向传播
    y.backward()
    print(f"dy/dx = 2x + 3 = {x.grad.item()}")
    
    # 检查GPU可用性
    print(f"\n4. 设备信息:")
    print(f"GPU可用: {torch.cuda.is_available()}")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    return device

# ==================== 简单神经网络 ====================

class SimpleThinkingNet(nn.Module):
    """简单的思维分析神经网络"""
    
    def __init__(self, input_size, hidden_size, num_classes):
        super(SimpleThinkingNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

def train_thinking_classifier():
    """训练思维风格分类器"""
    print("\n🧠 训练思维风格神经网络分类器")
    print("-" * 40)
    
    # 加载数据
    df = pd.read_csv('data/thinking_dataset.csv')
    
    # 特征选择
    feature_cols = ['iq_score', 'creativity_score', 'logic_score', 
                   'emotional_intelligence', 'problem_solving_time', 'accuracy_rate']
    X = df[feature_cols].values
    y = df['learning_style'].values
    
    # 数据预处理
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 编码标签
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # 转换为PyTorch张量
    X_tensor = torch.FloatTensor(X_scaled)
    y_tensor = torch.LongTensor(y_encoded)
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X_tensor, y_tensor, test_size=0.2, random_state=42
    )
    
    print(f"训练集大小: {len(X_train)}")
    print(f"测试集大小: {len(X_test)}")
    print(f"特征数量: {X_train.shape[1]}")
    print(f"类别数量: {len(label_encoder.classes_)}")
    
    # 创建数据加载器
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    
    # 创建模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = SimpleThinkingNet(
        input_size=X_train.shape[1], 
        hidden_size=64, 
        num_classes=len(label_encoder.classes_)
    ).to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练模型
    print("\n开始训练...")
    num_epochs = 100
    train_losses = []
    train_accuracies = []
    
    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            # 前向传播
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 统计
            epoch_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        # 记录训练指标
        avg_loss = epoch_loss / len(train_loader)
        accuracy = 100 * correct / total
        train_losses.append(avg_loss)
        train_accuracies.append(accuracy)
        
        if (epoch + 1) % 20 == 0:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%')
    
    # 测试模型
    print("\n测试模型...")
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        all_predicted = []
        all_labels = []
        
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            _, predicted = torch.max(outputs, 1)
            
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
            
            all_predicted.extend(predicted.cpu().numpy())
            all_labels.extend(batch_y.cpu().numpy())
        
        test_accuracy = 100 * correct / total
        print(f'测试准确率: {test_accuracy:.2f}%')
    
    # 详细分类报告
    print("\n分类报告:")
    print(classification_report(all_labels, all_predicted, 
                              target_names=label_encoder.classes_))
    
    return model, scaler, label_encoder, train_losses, train_accuracies

# ==================== 卷积神经网络 (CNN) ====================

class ThinkingImageCNN(nn.Module):
    """用于思维图像分析的CNN"""
    
    def __init__(self, num_classes=10):
        super(ThinkingImageCNN, self).__init__()
        
        # 卷积层
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
        
        # 池化层
        self.pool = nn.MaxPool2d(2, 2)
        
        # 全连接层
        self.fc1 = nn.Linear(64 * 4 * 4, 512)  # 假设输入是32x32
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, num_classes)
        
        # Dropout
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        # 卷积 + 激活 + 池化
        x = self.pool(F.relu(self.conv1(x)))  # 32x32 -> 16x16
        x = self.pool(F.relu(self.conv2(x)))  # 16x16 -> 8x8  
        x = self.pool(F.relu(self.conv3(x)))  # 8x8 -> 4x4
        
        # 展平
        x = x.view(-1, 64 * 4 * 4)
        
        # 全连接层
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x

def create_synthetic_image_data():
    """创建合成的思维图像数据"""
    print("\n🖼️ 创建思维模式图像数据集")
    print("-" * 40)
    
    # 生成合成的思维模式图像
    # 模拟不同的思维模式：线性、螺旋、网状、随机
    np.random.seed(42)
    
    def generate_pattern_image(pattern_type, size=32):
        """生成特定模式的图像"""
        img = np.zeros((size, size))
        
        if pattern_type == 0:  # 线性模式 (逻辑思维)
            for i in range(0, size, 4):
                img[i:i+2, :] = 1
                img[:, i:i+2] = 0.5
                
        elif pattern_type == 1:  # 螺旋模式 (创意思维)
            center = size // 2
            for i in range(size):
                for j in range(size):
                    r = np.sqrt((i - center)**2 + (j - center)**2)
                    theta = np.arctan2(j - center, i - center)
                    if abs(r - theta * 3) < 1.5:
                        img[i, j] = 1
                        
        elif pattern_type == 2:  # 网状模式 (系统思维)
            for i in range(0, size, 8):
                img[i:i+2, :] = 1
                img[:, i:i+2] = 1
            # 添加连接点
            for i in range(4, size, 8):
                for j in range(4, size, 8):
                    img[i-1:i+2, j-1:j+2] = 0.8
                    
        else:  # 随机模式 (直觉思维)
            img = np.random.random((size, size))
            img = (img > 0.7).astype(float)
        
        # 添加噪声
        noise = np.random.normal(0, 0.1, (size, size))
        img = np.clip(img + noise, 0, 1)
        
        return img
    
    # 生成数据集
    num_samples_per_class = 100
    images = []
    labels = []
    
    pattern_names = ['线性思维', '螺旋思维', '网状思维', '直觉思维']
    
    for pattern_type in range(4):
        print(f"生成 {pattern_names[pattern_type]} 样本...")
        for _ in range(num_samples_per_class):
            img = generate_pattern_image(pattern_type)
            images.append(img)
            labels.append(pattern_type)
    
    # 转换为numpy数组
    images = np.array(images)
    labels = np.array(labels)
    
    print(f"数据集形状: {images.shape}")
    print(f"标签形状: {labels.shape}")
    print(f"类别: {pattern_names}")
    
    return images, labels, pattern_names

def train_thinking_cnn():
    """训练思维模式CNN分类器"""
    print("\n🔍 训练思维模式CNN分类器")
    print("-" * 40)
    
    # 生成数据
    images, labels, pattern_names = create_synthetic_image_data()
    
    # 数据预处理
    X = images.reshape(-1, 1, 32, 32)  # 添加通道维度
    y = labels
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 转换为PyTorch张量
    X_train = torch.FloatTensor(X_train)
    X_test = torch.FloatTensor(X_test)
    y_train = torch.LongTensor(y_train)
    y_test = torch.LongTensor(y_test)
    
    # 创建数据加载器
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # 创建CNN模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ThinkingImageCNN(num_classes=4).to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练模型
    print("开始训练CNN...")
    num_epochs = 50
    
    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            # 前向传播
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 统计
            epoch_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        if (epoch + 1) % 10 == 0:
            accuracy = 100 * correct / total
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%')
    
    # 测试模型
    print("测试CNN模型...")
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            _, predicted = torch.max(outputs, 1)
            
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        test_accuracy = 100 * correct / total
        print(f'CNN测试准确率: {test_accuracy:.2f}%')
    
    return model, pattern_names

# ==================== 循环神经网络 (RNN) ====================

class ThinkingSequenceRNN(nn.Module):
    """用于思维序列分析的RNN"""
    
    def __init__(self, input_size, hidden_size, num_layers, num_classes):
        super(ThinkingSequenceRNN, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM层
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        
        # 全连接层
        self.fc = nn.Linear(hidden_size, num_classes)
        
    def forward(self, x):
        # 初始化隐藏状态
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # LSTM前向传播
        out, _ = self.lstm(x, (h0, c0))
        
        # 取最后一个时间步的输出
        out = self.fc(out[:, -1, :])
        
        return out

def create_thinking_sequence_data():
    """创建思维序列数据"""
    print("\n📈 创建思维序列数据集")
    print("-" * 40)
    
    # 模拟思维过程的时间序列数据
    np.random.seed(42)
    
    sequence_length = 20
    num_features = 5  # 注意力、创造力、逻辑、记忆、情感
    num_samples = 1000
    
    sequences = []
    labels = []
    
    for i in range(num_samples):
        # 生成不同类型的思维序列
        sequence_type = i % 3
        
        if sequence_type == 0:  # 发散思维模式
            # 创造力逐渐增强，注意力分散
            base_pattern = np.array([0.3, 0.8, 0.4, 0.6, 0.7])
            sequence = []
            for t in range(sequence_length):
                noise = np.random.normal(0, 0.1, 5)
                creativity_boost = 0.3 * np.sin(t * 0.3)
                attention_decay = -0.2 * t / sequence_length
                
                point = base_pattern + noise
                point[1] += creativity_boost  # 创造力
                point[0] += attention_decay   # 注意力
                point = np.clip(point, 0, 1)
                sequence.append(point)
                
        elif sequence_type == 1:  # 聚合思维模式
            # 逻辑性增强，注意力集中
            base_pattern = np.array([0.7, 0.4, 0.8, 0.6, 0.5])
            sequence = []
            for t in range(sequence_length):
                noise = np.random.normal(0, 0.1, 5)
                logic_boost = 0.2 * t / sequence_length
                attention_boost = 0.3 * np.cos(t * 0.2)
                
                point = base_pattern + noise
                point[2] += logic_boost      # 逻辑
                point[0] += attention_boost  # 注意力
                point = np.clip(point, 0, 1)
                sequence.append(point)
                
        else:  # 平衡思维模式
            # 各项能力保持平衡
            base_pattern = np.array([0.6, 0.6, 0.6, 0.6, 0.6])
            sequence = []
            for t in range(sequence_length):
                noise = np.random.normal(0, 0.05, 5)
                point = base_pattern + noise
                point = np.clip(point, 0, 1)
                sequence.append(point)
        
        sequences.append(sequence)
        labels.append(sequence_type)
    
    sequences = np.array(sequences)
    labels = np.array(labels)
    
    print(f"序列数据形状: {sequences.shape}")
    print(f"标签形状: {labels.shape}")
    
    thinking_modes = ['发散思维', '聚合思维', '平衡思维']
    print(f"思维模式: {thinking_modes}")
    
    return sequences, labels, thinking_modes

def train_thinking_rnn():
    """训练思维序列RNN分类器"""
    print("\n🔄 训练思维序列RNN分类器")
    print("-" * 40)
    
    # 生成序列数据
    sequences, labels, thinking_modes = create_thinking_sequence_data()
    
    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        sequences, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # 转换为PyTorch张量
    X_train = torch.FloatTensor(X_train)
    X_test = torch.FloatTensor(X_test)
    y_train = torch.LongTensor(y_train)
    y_test = torch.LongTensor(y_test)
    
    # 创建数据加载器
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # 创建RNN模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ThinkingSequenceRNN(
        input_size=5, hidden_size=64, num_layers=2, num_classes=3
    ).to(device)
    
    # 损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # 训练模型
    print("开始训练RNN...")
    num_epochs = 30
    
    model.train()
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            # 前向传播
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 统计
            epoch_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        if (epoch + 1) % 5 == 0:
            accuracy = 100 * correct / total
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {epoch_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%')
    
    # 测试模型
    print("测试RNN模型...")
    model.eval()
    with torch.no_grad():
        correct = 0
        total = 0
        
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            outputs = model(batch_X)
            _, predicted = torch.max(outputs, 1)
            
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        test_accuracy = 100 * correct / total
        print(f'RNN测试准确率: {test_accuracy:.2f}%')
    
    return model, thinking_modes

# ==================== 主程序 ====================

def main():
    """主程序"""
    print("🧠 智能思维项目 - 第四周深度学习基础")
    print("=" * 60)
    
    # 1. PyTorch基础演示
    device = pytorch_basics_demo()
    
    # 2. 训练简单神经网络
    print("\n" + "="*60)
    simple_model, scaler, label_encoder, losses, accuracies = train_thinking_classifier()
    
    # 3. 训练CNN模型
    print("\n" + "="*60)
    cnn_model, pattern_names = train_thinking_cnn()
    
    # 4. 训练RNN模型
    print("\n" + "="*60)
    rnn_model, thinking_modes = train_thinking_rnn()
    
    print("\n🎉 第四周深度学习基础学习完成！")
    print("✅ 已掌握技能:")
    print("  - PyTorch张量操作和自动梯度")
    print("  - 全连接神经网络")
    print("  - 卷积神经网络 (CNN)")
    print("  - 循环神经网络 (RNN/LSTM)")
    print("  - 深度学习训练流程")
    
    print("\n📚 下一步: Web前端基础学习（第7-8周）")
    print("💡 建议: 尝试优化模型结构和超参数！")

# ==================== 练习题 ====================

def practice_exercises():
    """第四周练习题"""
    print("\n🎯 第四周练习题:")
    print("-" * 30)
    
    exercises = [
        "练习1: 实现一个自定义的激活函数",
        "练习2: 添加学习率调度器来优化训练",
        "练习3: 实现模型的保存和加载功能",
        "练习4: 添加数据增强来提高模型泛化能力",
        "练习5: 实现一个注意力机制层",
        "练习6: 创建一个多任务学习网络",
        "练习7: 使用预训练模型进行迁移学习"
    ]
    
    for exercise in exercises:
        print(exercise)
    
    print("\n💡 提示: 这些练习将帮助你深入理解深度学习的核心概念！")

if __name__ == "__main__":
    main()
    practice_exercises() 