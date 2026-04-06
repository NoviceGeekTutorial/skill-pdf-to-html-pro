# skill-pdf-to-html-pro-openclaw - 兼容OpenClaw架构的PDF转HTML专业工具

### 📋 文档信息
- **文档版本**: v4.1
- **最后更新**: 2026-04-06
- **作者**: 萌新极客教程网，保留所有权利.
- **适用系统**: Windows / macOS / Linux
- **兼容架构**: OpenClaw

---

## 📁 文件位置

### Skill 安装位置
```
C:\Users\Administrator\.qclaw\skills\pdf-to-html-pro\
├── SKILL.md                          # Skill 定义文件
└── scripts\
    └── pdf_to_html.py                # 主程序脚本
```

### 打包文件位置
```
C:\Users\Administrator\.qclaw\workspace\pdf-to-html-pro.skill
```

---

## 🎯 功能概述

PDF to HTML Converter Pro 是一个高精度 PDF 转 HTML 转换工具，采用**页面渲染为高清图片 + 透明文字层叠加 + 智能链接识别**技术，实现真正 1:1 还原。

### 核心功能

| 功能 | 说明 |
|------|------|
| **1:1 布局还原** | PDF 页面渲染为高清 PNG 图片，保持原样 |
| **文字可选中复制** | 透明文字层覆盖在图片上，支持选择复制 |
| **智能链接识别** | 自动识别官网、网盘链接，转换为可点击跳转 |
| **图片精确还原** | 直接渲染整个页面，包含所有图片 |
| **颜色精确还原** | 使用原始 PDF 渲染，颜色 100% 一致 |
| **响应式设计** | 自适应电脑、手机、平板等多种设备 |

---

## 🔧 技术架构

### 三层渲染架构

```
┌─────────────────────────────────────┐
│  链接层 (Link Layer)                │  ← 可点击链接覆盖
│  - PDF 原始链接                      │
│  - 智能识别的官网/网盘链接            │
├─────────────────────────────────────┤
│  文字层 (Text Layer)                │  ← 透明可选择文字
│  - 字体、大小、颜色保留              │
│  - 支持选择复制                      │
├─────────────────────────────────────┤
│  背景层 (Background Layer)          │  ← 高清 PNG 渲染
│  - 页面完整渲染为图片                │
│  - 保持原始外观 100% 一致            │
└─────────────────────────────────────┘
```

### 技术栈

- **核心库**: PyMuPDF (fitz) - PDF 解析与渲染
- **语言**: Python 3.x
- **输出**: HTML5 + CSS3
- **依赖**: 仅需 `pip install PyMuPDF`

---

## 📦 安装与依赖

### 系统要求

- Python 3.8+
- pip 包管理器
- 支持 Windows / macOS / Linux

### 依赖列表

| 依赖包 | 版本要求 | 用途 |
|--------|---------|------|
| **PyMuPDF** | >= 1.23.0 | PDF 解析与渲染（核心依赖）|

### 安装命令

```bash
# 安装核心依赖
pip install PyMuPDF>=1.23.0

# 或安装最新版
pip install PyMuPDF
```

### 验证安装

```bash
python -c "import fitz; print(f'PyMuPDF 版本: {fitz.__doc__.split()[0]}')"
```

---

## 🚀 使用方法

### 基本转换

```bash
python pdf_to_html.py <输入文件.pdf>
```

### 完整参数

```bash
python pdf_to_html.py <输入文件.pdf> [选项]

选项:
  -o, --output <目录>      指定输出目录（默认为 PDF 所在目录）
  --dpi <数值>             渲染分辨率（默认 150，范围 100-300）
  --no-text-layer          禁用文字层（仅输出图片，文字不可选择）
  --no-smart-links         禁用智能链接识别
```

### 使用示例

```bash
# 基本转换
python pdf_to_html.py "document.pdf"

# 指定输出目录
python pdf_to_html.py "document.pdf" -o ./output

# 提高清晰度（200 DPI）
python pdf_to_html.py "document.pdf" --dpi 200

# 禁用智能链接
python pdf_to_html.py "document.pdf" --no-smart-links
```

---

## 🔗 智能链接识别

### 支持的链接类型

| 类型 | 识别规则 | 示例 |
|------|---------|------|
| **官网链接** | 包含"官网"、"官方网站"等关键词 + URL | `官网: https://example.com` |
| **百度网盘** | pan.baidu.com 域名 | `https://pan.baidu.com/s/xxx` |
| **阿里云盘** | aliyundrive.com / alipan.com 域名 | `https://www.aliyundrive.com/xxx` |
| **夸克网盘** | pan.quark.cn 域名 | `https://pan.quark.cn/xxx` |
| **迅雷网盘** | pan.xunlei.com 域名 | `https://pan.xunlei.com/xxx` |
| **天翼云盘** | cloud.189.cn 域名 | `https://cloud.189.cn/xxx` |
| **Google Drive** | drive.google.com 域名 | `https://drive.google.com/xxx` |
| **OneDrive** | 1drv.ms / onedrive 域名 | `https://1drv.ms/xxx` |

### 链接视觉提示

- 绿色虚线边框标识链接区域
- 鼠标悬停时背景变亮
- 右上角显示 🔗 图标
- 点击后在新标签页打开链接

---

## 📂 输出文件结构

```
输出目录/
├── [文件名].html              # 主 HTML 文件
└── assets/
    ├── styles.css            # 样式表（响应式 + 打印友好）
    └── images/               # 渲染的页面图片
        ├── page_1.png
        ├── page_2.png
        └── ...
```

---

## ⚠️ 已知限制

1. **文件大小**: 由于使用图片渲染，HTML 文件较大
2. **搜索功能**: 不支持在 HTML 中搜索文字（但可以选择复制）
3. **文字编辑**: 无法直接编辑 HTML 中的文字
4. **矢量图形**: 矢量内容被栅格化为图片
5. **链接识别**: 智能链接识别基于正则表达式，可能无法识别所有格式

---

## 🔒 安全与权限

### 文件系统权限

| 操作 | 权限要求 | 说明 |
|------|---------|------|
| 读取 PDF | 读取权限 | 需要访问输入 PDF 文件 |
| 创建目录 | 写入权限 | 在输出目录创建 `assets/images/` |
| 写入文件 | 写入权限 | 生成 HTML、CSS、PNG 文件 |

### 网络安全

- 链接使用 `target="_blank"` 在新标签页打开
- 包含 `rel="noopener noreferrer"` 防止标签页钓鱼攻击
- 不收集或上传任何用户数据

### 依赖安全

- 仅依赖 PyMuPDF (fitz) 官方库
- 无外部网络请求
- 纯本地处理，数据不离开本机

---

## 🐛 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| 文件太大 | 降低 DPI：`--dpi 100` |
| 文字无法选择 | 检查是否使用了 `--no-text-layer` |
| 链接未识别 | 确保链接格式符合识别规则 |
| 图片不清晰 | 提高 DPI：`--dpi 200` 或 `--dpi 300` |
| 转换失败 | 检查 PDF 是否损坏或加密 |

---

## 📜 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v4.1 | 2026-04-06 | 新增智能链接识别功能 |
| v4.0 | 2026-04-06 | 页面渲染 + 透明文字层架构 |
| v3.1 | 2026-04-06 | 去除水印裁剪，完整页面尺寸 |
| v3.0 | 2026-04-04 | 初始版本，基本转换功能 |

---

## 📞 技术支持

如有问题或建议，请联系开发团队。

---

**文档结束**
