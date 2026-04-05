# PPTAgent

> 一个面向生成与模板化的 AI PPT 项目。支持大纲生成、内容生成、模板获取/标注，以及自动化评估。

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white">
  <img alt="Node.js" src="https://img.shields.io/badge/Node.js-16%2B-339933?logo=node.js&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-Frontend-646CFF?logo=vite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-blue.svg">
</p>

---

## 项目简介

`PPTAgent` 是一个围绕 AI 生成 PPT 的完整工程，覆盖了：

- **PPT 大纲生成**：根据主题生成结构化 Markdown 大纲
- **PPT 内容生成**：将 Markdown 大纲转换为页面级 JSON 数据
- **模板体系**：支持模板获取、模板标注、模板复用
- **知识库能力**：支持个人知识库与向量检索
- **训练数据构建**：为强化学习或数据生成任务提供脚本与样例
- **前后端联调**：提供前端界面、后端服务与 Docker 部署方式

适合用于：

- AI PPT 产品原型开发
- PPT 内容生成链路验证
- 模板化演示文稿生成实验

---

## 核心能力

### 1. 大纲生成

输入一个主题，例如“2025 科技前沿动态”，系统可生成分层 Markdown 大纲，包含：

- `#` 封面主题
- `##` 一级章节
- `###` 二级主题
- `-` 具体要点

相关说明见：`doc/API_OUTLINE.md`

### 2. 内容生成

系统可将 Markdown 大纲进一步转换为适配 PPT 模板的结构化 JSON 页面数据，支持页面类型：

- `cover`
- `contents`
- `transition`
- `content`
- `end`

相关说明见：`doc/API_CONTENT.md`、`doc/PPT_Structure.md`

### 3. 模板获取与标注

项目支持：

- 下载并使用模板 JSON
- 对 PPT / PPTX 转换后的 JSON 进行标注
- 为文本节点、图片节点声明页面类型和元素类型
- 复用模板完成自动化生成

相关说明见：

- `doc/API_TEMPLATE.md`
- `doc/Template.md`
- `template/README.md`


### 4. 自动化评估



---

## 项目结构

```text
TrainPPTAgent/
├── backend/                 # 后端服务
│   ├── main_api/            # 主 API
│   ├── simpleOutline/       # 大纲生成服务
│   ├── slide_agent/         # PPT 内容生成服务
│   ├── personaldb/          # 个人知识库 / 向量检索
│   ├── mock_api/            # 模拟接口
│   ├── start_backend.py     # 后端一键启动脚本
│   └── requirements.txt
├── frontend/                # 前端界面（Vite）
├── doc/                     # 接口与设计文档
├── template/                # 模板样例、标注实验与资源
├── utils/                   # 数据生成与辅助脚本
├── start.py                 # 根目录一键启动脚本
├── docker-compose.yml       # Docker 编排
├── env_template.txt         # 环境变量模板
├── README_EN.md             # 英文说明（若存在可补充）
└── README_PRODUCTION.md     # 生产环境部署说明
```

---

## 技术栈

### 后端

- Python 3.8+
- FastAPI
- Uvicorn
- LiteLLM
- Google ADK / A2A SDK
- ChromaDB
- MarkItDown / 文档处理工具

### 前端

- Vite
- TypeScript
- Web 前端交互界面

### 其他

- Docker / Docker Compose
- 多模型供应商接入（Google、OpenAI、Claude、DeepSeek、阿里、GLM、Ollama、vLLM 等）

---

## 快速开始

### 1. 准备环境变量

在项目根目录创建 `.env` 文件，可基于模板复制：

```bash
cp env_template.txt .env
```

然后按需填写模型配置，例如：

```env
MODEL_PROVIDER=ali
LLM_MODEL=qwen-turbo-latest
PPT_WRITER_PROVIDER=ali
PPT_WRITER_MODEL=qwen-turbo-latest
PPT_CHECKER_PROVIDER=ali
PPT_CHECKER_MODEL=qwen-turbo-latest

OUTLINE_API=http://127.0.0.1:10001
CONTENT_API=http://127.0.0.1:10011
PERSONAL_DB=http://127.0.0.1:9100
```

> 请根据你使用的模型服务商补充对应的 API Key。

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python start_backend.py
```

默认会涉及以下服务：

- `main_api`：`6800`
- `simpleOutline`：`10001`
- `slide_agent`：`10011`
- `personaldb`：`9100`

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

默认访问地址：`http://127.0.0.1:5173/`

### 4. 一键启动（根目录）

如果你希望直接从根目录启动整个项目：

```bash
python start.py
```

该脚本会读取根目录 `.env`，并协调前后端相关服务启动。

---

## Docker 部署

项目已提供 Docker 编排文件，可用于快速启动主要服务：

```bash
docker compose up --build
```

默认包含：

- `personaldb`
- `outline_api`
- `content_api`
- `main_api`
- `frontend`

更多说明可参考：`README_PRODUCTION.md`、`doc/DockerDeploy.md`

---

## 典型调用链路

### 1. 生成大纲

前端调用 `/api/tools/aippt_outline`，传入主题、语言、模型等参数，返回 Markdown 大纲。

参考：`doc/API_OUTLINE.md`

### 2. 生成 PPT 页面数据

前端调用 `/api/tools/aippt`，传入 Markdown 大纲、风格、模型等参数，返回页面级 JSON 数据。

参考：`doc/API_CONTENT.md`

### 3. 选择 / 获取模板

通过模板接口获取模板 JSON，并与生成内容进行匹配。

参考：`doc/API_TEMPLATE.md`

### 4. 渲染为最终 PPT

将页面结构数据映射到模板标注节点，生成最终演示文稿。

---

## 开发说明

### 后端独立调试

可分别启动各服务：

```bash
# 主 API
cd backend/main_api
python main.py

# 大纲生成服务
cd backend/simpleOutline
python main_api.py

# PPT 内容生成服务
cd backend/slide_agent
python main_api.py

# 知识库服务
cd backend/personaldb
python main.py
```

### 模拟接口

如果只想快速联调前端，可使用模拟接口：

```bash
cd backend/mock_api
python mock_main.py
```

### 前端配置

前端开发时请检查：

- `frontend/vite.config.ts`
- 其中配置的 API 地址是否与你本地后端一致

---

## 文档索引

### 接口文档

- `doc/API_OUTLINE.md`：大纲生成接口
- `doc/API_CONTENT.md`：PPT 内容生成接口
- `doc/API_TEMPLATE.md`：模板获取接口
- `doc/API_IMAGE.md`：图片相关接口

### 设计 / 数据结构

- `doc/PPT_Structure.md`：PPT 页面 JSON 结构
- `doc/Template.md`：模板标注说明
- `doc/Train.md`：训练数据 / 奖励设计说明
- `doc/CHANGES.md`：项目变更记录

### 其他说明

- `backend/README.md`：后端说明
- `frontend/README.md`：前端说明
- `template/README.md`：模板目录说明
- `utils/README.md`：工具脚本说明

---

## 模型与配置说明

项目支持多种模型供应商，环境变量中已经预留了配置项，包括但不限于：

- `google`
- `openai`
- `claude`
- `deepseek`
- `ali`
- `glm`
- `doubao`
- `silicon`
- `modelscope`
- `vllm`
- `ollama`
- `local`

同时也支持嵌入模型配置，用于知识库向量化与检索。

推荐优先阅读：`env_template.txt`

---

## 注意事项

- 启动前请确保根目录存在 `.env`
- 前后端端口需要保持一致
- 使用在线模型时请正确配置 API Key
- 若使用 Docker，请确认本地端口未冲突
- Windows 环境可参考：`WINDOWS_NPM_FIX.md`

---

## Roadmap

- [ ] 完善根目录统一启动与部署文档
- [ ] 补充更多模板标注示例
- [ ] 增强训练数据自动评测链路
- [ ] 优化多模型切换与本地模型接入体验

---

## License

本项目采用 `MIT License`，详见：`LICENSE`

---

## 致谢

感谢项目中使用到的开源工具、模型能力与模板体系相关生态。

如果你正在做 AI PPT、模板生成、结构化演示文稿或相关训练数据工作，这个项目可以作为一个不错的起点。
