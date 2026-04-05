# 🔧 Windows 系统 npm 命令修复说明

## ❌ 问题描述

在 Windows 系统上运行 `python start.py` 时，出现以下错误：

```
❌ 启动失败：[WinError 2] 系统找不到指定的文件。
```

**原因分析**:
- Windows 系统中，`subprocess.run()` 无法直接找到 `npm` 命令
- 需要使用 `npm.cmd` 或者完整路径来调用 npm

---

## ✅ 解决方案

### 方案一：已自动修复（推荐）

我已经修改了 `start.py` 脚本，添加了智能的 npm 命令检测机制：

1. **优先尝试**: 直接使用 `npm` 命令
2. **备用方案 1**: 使用 `npm.cmd`
3. **备用方案 2**: 使用完整路径 `C:\Program Files\nodejs\npm.cmd`

现在可以直接运行：
```bash
python start.py
```

脚本会自动选择可用的 npm 调用方式。

---

### 方案二：手动添加 Node.js 到 PATH（如果方案一仍失败）

#### 步骤 1：找到 Node.js 安装路径

通常 Node.js 安装在：
- `C:\Program Files\nodejs\`
- `C:\Program Files (x86)\nodejs\`

#### 步骤 2：添加到系统环境变量

1. **打开系统属性**
   - 右键点击"此电脑" → "属性"
   - 或按 `Win + Pause/Break`

2. **进入高级系统设置**
   - 点击"高级系统设置"
   - 点击"环境变量"按钮

3. **编辑 Path 变量**
   - 在"系统变量"区域找到并选中 `Path`
   - 点击"编辑"
   - 点击"新建"
   - 添加：`C:\Program Files\nodejs\`
   - 点击"确定"保存

4. **重启终端**
   - 关闭所有 PowerShell/CMD 窗口
   - 重新打开终端

#### 步骤 3：验证

```bash
# 验证 npm 是否可用
npm --version

# 验证 node 是否可用
node --version
```

---

## 🚀 现在可以启动了

修复后，运行以下命令即可一键启动所有服务：

```bash
python start.py
```

这将自动完成：
- ✅ 安装 Python 后端依赖
- ✅ 安装前端依赖（使用修复后的 npm 调用）
- ✅ 构建前端项目
- ✅ 启动所有后端服务（main_api、outline_agent、slide_agent、personaldb）
- ✅ 提供前端静态文件服务

---

## 📝 访问地址

启动成功后：

- **前端界面**: http://127.0.0.1:5173
- **主 API**: http://127.0.0.1:6800
- **大纲服务**: http://127.0.0.1:10001
- **内容服务**: http://127.0.0.1:10011
- **知识库**: http://127.0.0.1:9100

---

## 🔍 如果仍然失败

### 检查 Node.js 是否正确安装

```bash
# 查看 node 版本
node --version

# 查看 npm 版本
npm --version
```

如果显示版本号，说明安装正确。

### 重新安装 Node.js

如果 Node.js 未安装或损坏：

1. 访问官网：https://nodejs.org/
2. 下载 LTS 版本（长期支持版）
3. 运行安装程序
4. 按照提示完成安装

### 检查 npm 权限

以管理员身份运行 PowerShell，然后执行：

```bash
npm install -g npm@latest
```

这会升级 npm 到最新版本。

---

## 🆘 其他常见问题

### Q: 遇到"拒绝访问"错误怎么办？

A: 可能是权限问题，尝试：
1. 以管理员身份运行 PowerShell
2. 或者给 Node.js 目录添加完全控制权限

### Q: 可以使用国内镜像加速吗？

A: 可以！设置 npm 淘宝镜像：

```bash
npm config set registry https://registry.npmmirror.com
```

### Q: 前端构建失败怎么办？

A: 尝试手动构建：

```bash
cd frontend
npm install
npm run build
```

查看具体错误信息，然后针对性解决。

---

**修复时间**: 2026-04-03  
**修复者**: LiangRonghui  
**状态**: ✅ 已修复并测试
