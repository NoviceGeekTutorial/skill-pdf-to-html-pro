---
name: pdf-to-html-copy-pro
description: |
  PDF转HTML一键复制 - 1:1 还原 PDF 并支持一键复制链接
  
  使用场景：
  - 将 PDF 文件转换为 HTML 网页格式，保持 100% 原样
  - 完整保留 PDF 的页面布局、颜色、字体样式、图片位置
  - 生成可在浏览器中查看、且文字可选中复制的网页
  - 自动识别 PDF 中的官网链接和网盘链接，点击一键复制到剪贴板
  - 创建响应式 HTML，适配桌面电脑、平板、手机
  - 需要精确还原 PDF 原始外观且安全复制链接的场景
  
  关键词：pdf转html, pdf转换, pdf to html, 文档转换, 网页生成, 1:1还原, 一键复制, 链接复制
  
  作者：萌新极客教程网
---

# PDF转HTML一键复制

将 PDF 文档转换为 HTML，使用**页面渲染为高清图片 + 透明文字层叠加 + 智能链接识别 + 一键复制**技术，实现真正 1:1 还原，点击链接即可复制地址到剪贴板。

## 核心技术

### 三层渲染架构 + 一键复制

1. **背景层**：PDF 页面渲染为高清 PNG 图片
   - 使用 PyMuPDF 的 `get_pixmap()` 方法
   - 可配置 DPI（默认 150，越高越清晰）
   - 保持 PDF 原始外观 100% 一致

2. **文字层**：透明可选择的文字覆盖在图片上
   - 文字颜色设为 `transparent`
   - 背景设为 `transparent`
   - 保留 `user-select: text` 属性，文字可选择复制

3. **链接层**：一键复制链接覆盖在对应位置
   - 提取 PDF 原始链接
   - 智能识别官网、网盘链接
   - **点击复制**：单击即可复制链接地址到剪贴板
   - **永久有效**：复制内容永久保存，无时间限制
   - **2秒提示**：显示"链接已复制，可粘贴到浏览器打开"

## 智能链接识别

### 识别的链接类型

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

- 智能识别的链接区域显示**绿色虚线边框**
- 鼠标悬停时背景变亮
- 右上角显示 📋 图标（表示可复制）
- 点击后复制链接，显示提示 2 秒后自动消失

## 核心特性

- **真正 1:1 还原**：PDF 页面渲染为高清图片，保持原样
- **文字可选中复制**：透明文字层覆盖在图片上
- **智能链接识别**：自动识别官网、网盘链接
- **一键复制链接**：点击链接即可复制地址到剪贴板，永久有效
- **安全防挂马**：不直接跳转，用户自主选择是否访问
- **图片精确还原**：直接渲染整个页面，包含所有图片
- **颜色精确还原**：使用原始 PDF 渲染，颜色 100% 一致
- **布局精确还原**：使用原始 PDF 渲染，布局 100% 一致
- **清晰度可调**：可配置 DPI（默认 150）
- **响应式设计**：自适应桌面、平板、手机等多种设备
- **纯 HTML 实现**：点击复制功能使用内联 JavaScript，无外部依赖
- **纯 Python 实现**：使用 PyMuPDF (fitz)，无需外部依赖

## 依赖安装

```bash
pip install PyMuPDF
```

## 使用方法

### 基本转换

```bash
python scripts/pdf_to_html.py <输入文件.pdf> [输出目录]
```

### 示例

```bash
# 基本转换（默认 150 DPI，启用智能链接和一键复制）
python scripts/pdf_to_html.py "我的文档.pdf"

# 指定输出目录
python scripts/pdf_to_html.py "我的文档.pdf" -o ./输出目录

# 提高清晰度（200 DPI）
python scripts/pdf_to_html.py "我的文档.pdf" --dpi 200

# 禁用文字层（仅输出图片，文字不可选择）
python scripts/pdf_to_html.py "我的文档.pdf" --no-text-layer

# 禁用智能链接识别
python scripts/pdf_to_html.py "我的文档.pdf" --no-smart-links
```

## 输出文件结构

```
输出目录/
├── [文件名].html              # 主 HTML 文件（含一键复制功能）
└── assets/
    ├── styles.css            # 样式表（响应式 + 打印友好）
    └── images/               # 渲染的页面图片
        ├── page_1.png
        ├── page_2.png
        └── ...
```

## 一键复制功能说明

### 复制流程

1. **点击链接区域**：鼠标点击绿色虚线框区域
2. **自动复制**：链接地址自动复制到系统剪贴板
3. **显示提示**：屏幕中央显示"链接已复制，可粘贴到浏览器打开"
4. **提示消失**：2 秒后提示自动消失
5. **永久有效**：复制内容永久保存，可随时粘贴使用

### 兼容性

- **现代浏览器**：Chrome、Firefox、Edge、Safari 等
- **移动端浏览器**：iOS Safari、Android Chrome 等
- **降级方案**：不支持 Clipboard API 的浏览器使用传统复制方法

## 技术细节

### DPI 设置

- **默认 DPI**: 150
- **推荐范围**: 100-300
- **文件大小**: DPI 越高，图片越大，HTML 文件越大
- **清晰度**: DPI 越高，页面越清晰

### 文字层原理

```css
/* 文字透明但可选择 */
.text-layer div {
  color: transparent;        /* 文字透明 */
  background: transparent;   /* 背景透明 */
  user-select: text;         /* 允许选择 */
  cursor: text;              /* 文本光标 */
}
```

### 链接层原理（一键复制版）

```css
/* 链接层覆盖在图片上 */
.link-layer .copy-link {
  position: absolute;
  cursor: pointer;
  z-index: 100;
}

/* 智能链接视觉提示 */
.link-layer .copy-link {
  border: 2px dashed #4CAF50;  /* 绿色虚线边框 */
  border-radius: 4px;
  background: rgba(76, 175, 80, 0.1);
}
```

### 一键复制 JavaScript

```javascript
// 点击复制功能
function copyToClipboard(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  } else {
    // 降级方案
    var textarea = document.createElement('textarea');
    textarea.value = text;
    // ...
  }
}
```

### 响应式行为

在较小屏幕上：
- 页面按比例缩放
- 保持原始宽高比
- 自适应容器宽度

### 打印样式

- 打印时去除阴影
- 每页强制分页
- 链接层隐藏（不打印）
- 优化打印质量

## 与其他方案对比

| 特性 | 本方案 (萌新极客) | 传统方案 (HTML 重构) |
|------|------------------|---------------------|
| 布局还原 | 100%（图片渲染） | 近似（CSS 模拟） |
| 颜色还原 | 100%（原始渲染） | 近似（颜色提取） |
| 图片还原 | 100%（页面渲染） | 提取后重新定位 |
| 链接交互 | 一键复制（安全） | 直接跳转（有风险） |
| 文字选择 | 透明文字层 | 原生 HTML 文字 |
| 文件大小 | 较大（含图片） | 较小 |
| 搜索功能 | 不支持 | 支持 |

## 故障排除

### 链接未识别

- 检查链接格式是否符合识别规则
- 确保链接以 `http://` 或 `https://` 开头
- 尝试禁用智能链接再启用：`--no-smart-links`

### 复制失败

- 检查浏览器是否支持 Clipboard API
- 确保页面是通过 HTTPS 或本地文件打开
- 移动端可能需要用户手势触发

### 文件太大

- 降低 DPI：`--dpi 100`
- 禁用文字层：`--no-text-layer`
- 禁用智能链接：`--no-smart-links`

### 文字无法选择

- 检查是否使用了 `--no-text-layer`
- 某些 PDF 可能没有可提取的文本层

### 图片不清晰

- 提高 DPI：`--dpi 200` 或 `--dpi 300`

## 已知限制

1. **文件大小**：由于使用图片渲染，HTML 文件较大
2. **搜索功能**：不支持在 HTML 中搜索文字（但可以选择复制）
3. **文字编辑**：无法直接编辑 HTML 中的文字
4. **矢量图形**：矢量内容被栅格化为图片
5. **链接识别**：智能链接识别基于正则表达式，可能无法识别所有格式

## 高级用法

### Python API

```python
from scripts.pdf_to_html import PDFToHTMLConverter

# 创建转换器
converter = PDFToHTMLConverter(
    pdf_path="input.pdf",
    output_dir="./output",
    dpi=150,              # 渲染分辨率
    text_layer=True,      # 启用文字层
    smart_links=True      # 启用智能链接
)

# 执行转换
result = converter.convert()

print(f"HTML: {result['html_path']}")
print(f"DPI: {result['dpi']}")
print(f"识别链接数: {result['total_links']}")
print(f"模式: {result['mode']}")
```

### 批量转换

```bash
for pdf in *.pdf; do
    python scripts/pdf_to_html.py "$pdf" -o "./output/$(basename "$pdf" .pdf)"
done
```

## 版本历史

- **v4.2** - 当前版本（PDF转HTML一键复制）
  - 链接交互改为「一键复制」模式
  - 复制内容永久有效，无时间限制
  - 2秒提示"链接已复制，可粘贴到浏览器打开"
  - 纯 HTML/JavaScript 实现，无外部依赖

- **v4.1** - 上一版本（True 1:1 Edition with Smart Links）
  - 新增智能链接识别功能
  - 自动识别官网、网盘链接
  - 链接层可视化提示
  - 页面渲染为高清图片 + 透明文字层叠加

- **v4.0** - 早期版本（True 1:1 Edition）
  - 页面渲染为高清图片 + 透明文字层叠加
  - 真正 1:1 还原 PDF 外观
  - 可配置 DPI
  - 响应式设计
