# API配置指南 - Cursor自定义模型设置

## 🎯 目标
配置Cursor IDE使用Silicon（sk）等自定义AI模型API，提升开发体验。

## 📋 准备工作

### 1. 获取Silicon API Key
- 访问 [Silicon Flow官网](https://siliconflow.cn)
- 注册账号并获取API Key
- 记录你的API Key（格式类似：`sk-xxxxxxxxxxxxxxxxx`）

### 2. 确认API端点
- Silicon API端点：`https://api.siliconflow.cn/v1`
- 支持的模型：gpt-3.5-turbo, gpt-4, claude-3-sonnet等

## 🛠️ 配置方法

### 方法一：Cursor设置界面（推荐）

1. **打开Cursor设置**
   ```
   快捷键: Ctrl + , (Windows) 或 Cmd + , (Mac)
   或: 点击左下角齿轮图标 → Settings
   ```

2. **导航到API配置**
   ```
   Settings → Extensions → Cursor
   或搜索 "API" 或 "Models"
   ```

3. **添加自定义模型**
   ```
   Provider: Custom
   Name: Silicon
   API Key: [你的sk API key]
   Base URL: https://api.siliconflow.cn/v1
   Model: gpt-3.5-turbo (或其他支持的模型)
   ```

### 方法二：环境变量配置

1. **创建环境变量文件**
   在项目根目录创建 `.env` 文件：
   ```bash
   # Silicon Flow API配置
   SILICON_API_KEY=sk-your-api-key-here
   SILICON_BASE_URL=https://api.siliconflow.cn/v1
   SILICON_MODEL=gpt-3.5-turbo
   
   # 其他API Keys（可选）
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   ```

2. **添加到.gitignore**
   确保 `.env` 文件不被提交到版本控制：
   ```gitignore
   # API Keys
   .env
   *.key
   ```

### 方法三：Cursor配置文件

1. **创建cursor配置**
   在 `.vscode/settings.json` 中添加：
   ```json
   {
     "cursor.customModels": [
       {
         "name": "Silicon GPT",
         "provider": "openai-compatible",
         "apiKey": "${SILICON_API_KEY}",
         "baseUrl": "https://api.siliconflow.cn/v1",
         "defaultModel": "gpt-3.5-turbo"
       }
     ]
   }
   ```

## 🔧 高级配置

### 模型参数调优
```json
{
  "cursor.modelSettings": {
    "silicon": {
      "temperature": 0.7,
      "maxTokens": 2048,
      "topP": 1.0,
      "frequencyPenalty": 0.0,
      "presencePenalty": 0.0
    }
  }
}
```

### 代理设置（如需要）
```json
{
  "http.proxy": "http://your-proxy:port",
  "https.proxy": "http://your-proxy:port"
}
```

## ✅ 验证配置

### 1. 测试API连接
在Cursor中尝试使用AI助手功能：
- 快捷键：`Ctrl + K`（代码生成）
- 快捷键：`Ctrl + L`（对话模式）

### 2. 检查模型响应
观察AI响应是否来自Silicon模型：
- 响应速度和质量
- 错误信息中的API端点信息

### 3. 日志检查
查看Cursor日志：
```
Help → Toggle Developer Tools → Console
```

## 🚨 故障排除

### 常见问题

1. **API Key无效**
   ```
   错误: 401 Unauthorized
   解决: 检查API Key格式和有效性
   ```

2. **网络连接问题**
   ```
   错误: Connection timeout
   解决: 检查网络连接和代理设置
   ```

3. **模型不支持**
   ```
   错误: Model not found
   解决: 确认Silicon支持的模型列表
   ```

4. **配额超限**
   ```
   错误: Rate limit exceeded
   解决: 检查API使用配额和计费状态
   ```

### 调试技巧

1. **启用详细日志**
   ```json
   {
     "cursor.debug": true,
     "cursor.logLevel": "debug"
   }
   ```

2. **使用curl测试API**
   ```bash
   curl -X POST "https://api.siliconflow.cn/v1/chat/completions" \
     -H "Authorization: Bearer sk-your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [{"role": "user", "content": "Hello"}]
     }'
   ```

## 💡 最佳实践

1. **安全性**
   - 不要在代码中硬编码API Key
   - 使用环境变量管理敏感信息
   - 定期轮换API Key

2. **性能优化**
   - 选择合适的模型（平衡成本和性能）
   - 合理设置超时时间
   - 启用缓存机制

3. **成本控制**
   - 监控API使用量
   - 设置合理的token限制
   - 选择cost-effective的模型

## 📚 相关资源

- [Silicon Flow文档](https://docs.siliconflow.cn)
- [Cursor官方文档](https://cursor.sh/docs)
- [OpenAI API兼容性文档](https://platform.openai.com/docs)

## 🔄 更新配置

当需要更新API配置时：
1. 修改 `.env` 文件中的相应值
2. 重启Cursor IDE
3. 验证新配置是否生效

---

*配置完成后，你就可以在Cursor中使用Silicon的强大AI模型来辅助编程了！* 