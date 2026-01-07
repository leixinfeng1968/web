# Git仓库快速配置指南

## 🎯 目标
将您的课件直接上传到GitHub/GitLab网站，实现云端存储和在线分享。

## 📋 快速配置步骤

### 第一步：创建GitHub仓库

1. **访问GitHub**
   - 打开 https://github.com
   - 登录您的账号（没有则先注册）

2. **创建新仓库**
   - 点击右上角的 "+" 按钮
   - 选择 "New repository"
   - 填写信息：
     - 仓库名称：`初中数学课件库`
     - 描述：`初中数学动态交互课件集合`
     - 可见性：`Public`（公开）或 `Private`（私有）
   - 点击 "Create repository"

3. **复制仓库地址**
   - 创建成功后，复制仓库地址
   - 格式类似：`https://github.com/您的用户名/仓库名.git`

### 第二步：配置本地Git

1. **在当前目录下执行以下命令：**

```bash
# 1. 配置用户信息（如果还没配置）
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱"

# 2. 初始化Git仓库
git init
git branch -M main

# 3. 添加远程仓库
git remote add origin https://github.com/您的用户名/仓库名.git

# 4. 首次提交
git add .
git commit -m "初始提交：创建课件上传系统"

# 5. 推送到GitHub
git push -u origin main
```

### 第三步：启用智能上传

1. **启动智能上传服务器**
   ```bash
   python git_push_server.py
   ```

2. **访问上传页面**
   - 本机访问：http://localhost:8080
   - 网络访问：http://192.168.2.9:8080

3. **上传课件**
   - 选择HTML课件文件
   - 点击上传按钮
   - 系统自动保存到uploads目录并推送到GitHub

## 🌟 高级功能

### 自动Git推送特性
- ✅ 文件上传后自动提交到Git
- ✅ 生成唯一的Git提交记录
- ✅ 推送到远程仓库（GitHub/GitLab）
- ✅ 保留完整的版本历史

### 在线分享功能
- ✅ GitHub Pages自动发布
- ✅ 生成可直接分享的链接
- ✅ 支持在线预览HTML课件
- ✅ 移动设备友好

## 🔗 GitHub访问方式

### 查看上传的文件
```
https://github.com/您的用户名/仓库名/tree/main/uploads
```

### 在线预览课件
```
https://您的用户名.github.io/仓库名/uploads/文件名.html
```

## ⚠️ 注意事项

### 认证问题
- 如果推送失败，可能需要配置Git认证
- 建议使用GitHub Personal Access Token
- 或使用SSH密钥认证

### 文件类型
- 主要支持HTML课件文件
- 支持JavaScript和CSS文件
- 支持相关资源文件

### 网络要求
- 上传需要网络连接推送到Git仓库
- 离线时仍可本地保存文件

## 🚀 自动化脚本

如果您想自动配置Git，可以使用提供的脚本：

```bash
python setup_git.py
```

这个脚本会引导您完成整个配置过程。

## 📱 多设备使用

### 在其他设备上访问
1. 确保设备与电脑在同一WiFi网络
2. 在浏览器中访问：http://192.168.2.9:8080
3. 直接上传文件到您的Git仓库

### 校园网使用
- 支持同一校园网内跨WiFi访问
- 可能需要配置网络隔离例外

## 🎉 成功示例

配置完成后，您将拥有：

1. **本地文件**：保存在 `uploads/` 目录
2. **云端仓库**：GitHub上的完整备份
3. **在线链接**：可直接分享的课件预览地址
4. **版本控制**：每次修改都有完整记录

## 💡 使用建议

1. **定期推送**：确保文件及时备份到云端
2. **命名规范**：使用有意义的文件名
3. **测试预览**：上传前先本地测试HTML课件
4. **分享链接**：使用GitHub Pages链接分享课件

---

🎯 **现在就可以开始使用！**
1. 创建GitHub仓库
2. 运行配置命令
3. 启动智能上传服务器
4. 上传您的第一个课件