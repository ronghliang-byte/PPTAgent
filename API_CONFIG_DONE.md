# ✅ 项目配置完成 - API Key 配置清单

## 🎉 配置状态

所有必要的 API Key 已成功配置！

---

## 📋 已配置的 API Key

### 1. **DeepSeek API** (主要 LLM)
- **用途**: 大纲生成、PPT 内容撰写、PPT 内容检查
- **API Key**: `sk-c95955da274941619d2a55db0ce10e2e`
- **模型**: `deepseek-chat`
- **配置位置**:
  - ✅ 根目录 `.env`
  - ✅ `backend/slide_agent/.env`
  - ✅ `backend/simpleOutline/.env` (已配置)

### 2. **阿里云 API** (Embedding + 备用 LLM)
- **用途**: 
  - 知识库文件向量化（Embedding）
  - 备用 LLM 模型
- **API Key**: `sk-c5e83d3f5caa4d1aab4c60f61af71968`
- **模型**: 
  - Embedding: `text-embedding-v2`
  - LLM: `qwen-turbo-latest` (备用)
- **配置位置**:
  - ✅ 根目录 `.env`
  - ✅ `backend/personaldb/.env`
  - ✅ `backend/slide_agent/.env`
  - ✅ `backend/simpleOutline/.env`

### 3. **PEXELS API** (配图搜索)
- **用途**: PPT 配图搜索
- **API Key**: `6uU0DJArsVWLfGCRwXXtGH7RFfE9GlicR2xQWjNM99mXwxb796JRFZH6`
- **配置位置**:
  - ✅ 根目录 `.env`
  - ✅ `backend/slide_agent/.env`

---

## 🔧 模型配置详情

### 主模型配置（根目录 .env）
```bash
# LLM 配置
MODEL_PROVIDER=deepseek
LLM_MODEL=deepseek-chat

# PPT 撰写代理
PPT_WRITER_PROVIDER=deepseek
PPT_WRITER_MODEL=deepseek-chat

# PPT 检查代理
PPT_CHECKER_PROVIDER=deepseek
PPT_CHECKER_MODEL=deepseek-chat

# Embedding 配置
EMBEDDING_PROVIDER=aliyun
EMBEDDING_MODEL=text-embedding-v2
```

### slide_agent 配置
```bash
PPT_WRITER_PROVIDER=deepseek
PPT_WRITER_MODEL=deepseek-chat

PPT_CHECKER_PROVIDER=deepseek
PPT_CHECKER_MODEL=deepseek-chat
```

### personaldb 配置
```bash
EMBEDDING_PROVIDER=aliyun
EMBEDDING_MODEL=text-embedding-v2
ALI_API_KEY=sk-c5e83d3f5caa4d1aab4c60f61af71968
```

---

## 🚀 启动项目

### 方式一：一键启动（推荐）
```bash
# 在项目根目录执行
python start.py
```

这将自动：
- ✅ 安装所有依赖
- ✅ 启动前端服务（端口 5173）
- ✅ 启动后端所有服务（main_api、outline_agent、slide_agent、personaldb）

### 方式二：分别启动

#### 1. 启动后端服务
```bash
cd backend
python start_backend.py
```

#### 2. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 访问地址

启动成功后，访问以下地址：

- **前端界面**: http://127.0.0.1:5173
- **主 API**: http://127.0.0.1:6800
- **大纲服务**: http://127.0.0.1:10001
- **内容服务**: http://127.0.0.1:10011
- **知识库服务**: http://127.0.0.1:9100

---

## ✅ 配置验证清单

- [x] DeepSeek API Key 已配置到所有需要的服务
- [x] 阿里云 Embedding API Key 已配置到 personaldb
- [x] PEXELS API Key 已配置到 slide_agent
- [x] 模型提供商统一为 deepseek
- [x] Embedding 提供商设置为 aliyun
- [x] 所有.env 文件已更新

---

## 📝 下一步

1. **启动项目**: 执行 `python start.py`
2. **测试功能**:
   - 输入主题生成大纲
   - 选择模板
   - 生成 PPT 内容
   - （可选）上传文件到知识库

---

## ⚠️ 注意事项

1. **API Key 安全**: 
   - 不要将 `.env` 文件提交到 Git
   - 保护好你的 API Key

2. **网络要求**:
   - DeepSeek API 需要联网访问
   - 如果遇到网络问题，可能需要配置代理

3. **首次启动**:
   - 首次运行会自动安装依赖，可能需要几分钟
   - 确保 Python 版本 >= 3.9

---

## 🆘 常见问题

### Q: 如何测试 API Key 是否有效？
A: 启动项目后，尝试生成一个简单的大纲，如果成功说明 API Key 有效。

### Q: 遇到 "API Key 无效" 错误怎么办？
A: 检查 `.env` 文件中的 API Key 是否正确复制，没有多余空格。

### Q: 可以只使用部分功能吗？
A: 可以！如果不需要知识库功能，可以不配置 Embedding API。

---

**配置完成时间**: 2026-04-02  
**配置者**: LiangRonghui  
**状态**: ✅ 就绪，可以启动
