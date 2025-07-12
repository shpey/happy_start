# GitHub Container Registry 设置指南

## 🔧 解决权限问题

您遇到的错误 `denied: installation not allowed to Create organization package` 是由于 GitHub Container Registry 权限配置问题。

## 📋 解决步骤

### 1. 启用 GitHub Packages

1. 进入您的 GitHub 仓库
2. 点击 **Settings** 标签
3. 在左侧菜单中找到 **Actions** > **General**
4. 滚动到 **Workflow permissions** 部分
5. 选择 **Read and write permissions**
6. 勾选 **Allow GitHub Actions to create and approve pull requests**
7. 点击 **Save**

### 2. 配置包权限（如果是组织仓库）

如果您的仓库属于组织：

1. 进入组织设置：https://github.com/organizations/YOUR_ORG/settings
2. 点击左侧的 **Packages**
3. 在 **Package creation** 部分：
   - 选择 **Public** 或 **Private**
   - 或者选择 **Internal** (如果适用)
4. 确保允许创建包

### 3. 个人访问令牌设置（备选方案）

如果上述方法不起作用，可以使用个人访问令牌：

1. 进入 GitHub 设置：https://github.com/settings/tokens
2. 点击 **Generate new token** > **Generate new token (classic)**
3. 设置权限：
   - `repo` (Full control of private repositories)
   - `write:packages` (Upload packages to GitHub Package Registry)
   - `delete:packages` (Delete packages from GitHub Package Registry)
4. 复制生成的令牌
5. 在仓库设置中添加 Secret：
   - 名称：`GHCR_TOKEN`
   - 值：您的个人访问令牌

### 4. 更新 Workflow（如果使用个人令牌）

如果您选择使用个人访问令牌，可以这样更新 workflow：

```yaml
- name: Log in to Container Registry
  uses: docker/login-action@v3
  with:
    registry: ${{ env.REGISTRY }}
    username: ${{ github.actor }}
    password: ${{ secrets.GHCR_TOKEN }}  # 使用自定义令牌
```

## 🚀 替代方案：使用 Docker Hub

如果 GitHub Container Registry 问题持续存在，您可以切换到 Docker Hub：

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: your-dockerhub-username/intelligent-thinking
```

然后添加 Docker Hub 的 secrets：
- `DOCKERHUB_USERNAME`: 您的 Docker Hub 用户名
- `DOCKERHUB_TOKEN`: 您的 Docker Hub 访问令牌

## 🔍 验证设置

完成设置后，您可以通过以下方式验证：

1. **检查仓库权限**：
   - 进入仓库 Settings > Actions > General
   - 确认 Workflow permissions 为 "Read and write permissions"

2. **测试构建**：
   ```bash
   git add .
   git commit -m "test: 验证 GitHub Container Registry 设置"
   git push origin main
   ```

3. **查看包**：
   - 构建成功后，在仓库页面应该能看到 "Packages" 部分
   - 或访问：https://github.com/YOUR_USERNAME/YOUR_REPO/pkgs/container/YOUR_REPO

## 📊 修复后的预期行为

修复后，您应该看到：

✅ **前端构建**：现在会正常执行（不再跳过）
✅ **微服务构建**：所有 7 个微服务都会正常构建
✅ **包推送**：镜像会成功推送到 GitHub Container Registry
✅ **权限正常**：不再出现 "denied" 错误

## 🔧 故障排除

### 如果仍然遇到权限问题：

1. **检查组织设置**（如果适用）：
   ```
   https://github.com/organizations/YOUR_ORG/settings/packages
   ```

2. **确认仓库可见性**：
   - 私有仓库需要特殊权限
   - 考虑临时设为公开仓库测试

3. **清除缓存**：
   ```bash
   git commit --allow-empty -m "fix: 清除 GitHub Actions 缓存"
   git push origin main
   ```

### 如果前端仍然跳过：

1. **强制触发所有构建**：
   ```bash
   git commit --allow-empty -m "build: 强制触发所有服务构建"
   git push origin main
   ```

2. **检查文件变化**：
   - 确保您的提交包含前端文件变化
   - 或者手动触发 workflow

## 📝 注意事项

- **首次构建**：第一次推送镜像可能需要额外时间
- **私有包**：默认情况下，包会设为私有
- **存储配额**：注意 GitHub 的包存储配额限制
- **清理旧包**：定期清理不需要的镜像版本

完成这些设置后，您的 GitHub Actions workflow 应该能够正常构建和推送所有服务的 Docker 镜像！ 