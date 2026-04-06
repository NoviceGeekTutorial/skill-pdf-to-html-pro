#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF转HTML一键复制
1:1 还原 PDF 并支持一键复制链接

核心技术：页面渲染为高清图片 + 透明文字层叠加 + 智能链接识别 + 一键复制
- 背景层：PDF 页面渲染为高清 PNG 图片（保持原样）
- 文字层：透明可选择的文字覆盖在图片上
- 链接层：一键复制链接地址（永久有效，2秒提示）

核心特性：
- 真正 1:1 还原：PDF 页面渲染为高清图片，保持原样
- 文字可选中复制：透明文字层覆盖在图片上
- 智能链接识别：自动识别官网、网盘链接
- 一键复制功能：点击链接复制地址到剪贴板，永久有效
- 2秒提示：显示"链接已复制，可粘贴到浏览器打开"
- 安全防挂马：不直接跳转，用户自主选择是否访问
- 图片精确还原：直接渲染整个页面，包含所有图片
- 颜色精确还原：使用原始 PDF 渲染，颜色 100% 一致
- 布局精确还原：使用原始 PDF 渲染，布局 100% 一致
- 清晰度保持：可配置 DPI，默认 150 DPI
- 响应式设计：自适应电脑、手机、平板等多种设备
- 纯 Python 实现：使用 PyMuPDF (fitz)，无需外部依赖
- 纯 HTML 实现：点击复制功能使用内联 JavaScript，无外部依赖

智能链接识别规则：
- 官网链接：包含 "官网"、"官方网站"、"official" 等关键词的文本
- 网盘链接：百度网盘、阿里云盘、夸克网盘、迅雷网盘等链接
- 一键复制：点击后复制链接地址到剪贴板

安全特性：
- 移除 href 跳转：防止恶意网站挂马
- 一键复制：用户自主选择是否访问链接
- 纯本地处理：无外部网络请求

作者：萌新极客教程网
版本：v4.2 (PDF转HTML一键复制)
"""

import fitz  # PyMuPDF
import os
import sys
import base64
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import io


class PDFToHTMLConverter:
    """PDF 转 HTML 转换器 - 真正 1:1 还原版 + 智能链接"""
    
    def __init__(self, pdf_path: str, output_dir: Optional[str] = None, 
                 dpi: int = 150, text_layer: bool = True, smart_links: bool = True):
        """
        初始化转换器
        
        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录（默认为 PDF 所在目录）
            dpi: 渲染分辨率（默认 150，越高越清晰但文件越大）
            text_layer: 是否添加可选中文字层
            smart_links: 是否启用智能链接识别
        """
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
        
        self.output_dir = Path(output_dir) if output_dir else self.pdf_path.parent
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.dpi = dpi
        self.text_layer = text_layer
        self.smart_links = smart_links
        self.zoom = dpi / 72  # 72 是 PDF 默认 DPI
        
        # 打开 PDF
        self.doc = fitz.open(str(self.pdf_path))
        
        # 创建资源目录
        self.assets_dir = self.output_dir / "assets"
        self.images_dir = self.assets_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # 智能链接识别模式
        self.link_patterns = {
            'official_website': [
                r'官网[:：]?\s*(https?://[^\s]+)',
                r'官方网站[:：]?\s*(https?://[^\s]+)',
                r'official\s*site[:：]?\s*(https?://[^\s]+)',
                r'homepage[:：]?\s*(https?://[^\s]+)',
            ],
            'pan_links': [
                r'(https?://pan\.baidu\.com/[^\s]+)',
                r'(https?://www\.aliyundrive\.com/[^\s]+)',
                r'(https?://pan\.quark\.cn/[^\s]+)',
                r'(https?://pan\.xunlei\.com/[^\s]+)',
                r'(https?://cloud\.189\.cn/[^\s]+)',
                r'(https?://drive\.google\.com/[^\s]+)',
                r'(https?://1drv\.ms/[^\s]+)',
            ]
        }
        
    def _render_page_to_image(self, page: fitz.Page, page_num: int) -> Dict:
        """
        将页面渲染为高清图片
        
        Args:
            page: PDF 页面对象
            page_num: 页码（从1开始）
            
        Returns:
            图片信息
        """
        # 设置矩阵进行缩放
        mat = fitz.Matrix(self.zoom, self.zoom)
        
        # 渲染页面为图片
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # 生成文件名
        image_filename = f"page_{page_num}.png"
        image_path = self.images_dir / image_filename
        
        # 保存图片
        pix.save(str(image_path))
        
        # 获取页面原始尺寸
        page_rect = page.rect
        
        return {
            "filename": image_filename,
            "path": str(image_path),
            "width": pix.width,
            "height": pix.height,
            "page_width": page_rect.width,
            "page_height": page_rect.height
        }
    
    def _extract_links_from_page(self, page: fitz.Page) -> List[Dict]:
        """
        提取页面中的链接
        
        Args:
            page: PDF 页面对象
            
        Returns:
            链接列表
        """
        links = []
        
        # 获取页面中的所有链接
        link = page.first_link
        while link:
            if link.uri:  # 确保是 URI 链接
                rect = link.rect
                links.append({
                    "uri": link.uri,
                    "x": rect.x0 * self.zoom,
                    "y": rect.y0 * self.zoom,
                    "width": (rect.x1 - rect.x0) * self.zoom,
                    "height": (rect.y1 - rect.y0) * self.zoom,
                    "type": "pdf_link"
                })
            link = link.next
        
        return links
    
    def _detect_smart_links(self, text_blocks: List[Dict]) -> List[Dict]:
        """
        智能识别文本中的官网和网盘链接
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            智能链接列表
        """
        smart_links = []
        
        for block in text_blocks:
            text = block.get("text", "")
            
            # 检查官网链接模式
            for pattern in self.link_patterns['official_website']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    url = match.group(1)
                    smart_links.append({
                        "uri": url,
                        "x": block["x"],
                        "y": block["y"],
                        "width": block["width"],
                        "height": block["height"],
                        "type": "official_website",
                        "text": text,
                        "label": "官网"
                    })
            
            # 检查网盘链接模式
            for pattern in self.link_patterns['pan_links']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    url = match.group(1)
                    # 识别网盘类型
                    pan_type = "网盘"
                    if 'baidu' in url:
                        pan_type = "百度网盘"
                    elif 'aliyun' in url or 'alipan' in url:
                        pan_type = "阿里云盘"
                    elif 'quark' in url:
                        pan_type = "夸克网盘"
                    elif 'xunlei' in url:
                        pan_type = "迅雷网盘"
                    elif '189' in url:
                        pan_type = "天翼云盘"
                    elif 'google' in url:
                        pan_type = "Google Drive"
                    elif '1drv' in url or 'onedrive' in url:
                        pan_type = "OneDrive"
                    
                    smart_links.append({
                        "uri": url,
                        "x": block["x"],
                        "y": block["y"],
                        "width": block["width"],
                        "height": block["height"],
                        "type": "pan",
                        "text": text,
                        "label": pan_type
                    })
        
        return smart_links
    
    def _extract_text_with_style(self, page: fitz.Page) -> List[Dict]:
        """
        提取带样式的文本
        
        Args:
            page: PDF 页面对象
            
        Returns:
            文本块列表，包含位置和样式信息
        """
        text_blocks = []
        
        # 获取文本块
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block.get("type") == 0:  # 文本块
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        bbox = span.get("bbox", [0, 0, 0, 0])
                        
                        text = span.get("text", "").strip()
                        if not text:
                            continue
                        
                        # 提取样式信息
                        font = span.get("font", "Arial")
                        size = span.get("size", 12)
                        color = span.get("color", 0)
                        flags = span.get("flags", 0)
                        
                        # 转换颜色
                        if isinstance(color, int):
                            r = (color >> 16) & 0xFF
                            g = (color >> 8) & 0xFF
                            b = color & 0xFF
                            color_hex = f"#{r:02X}{g:02X}{b:02X}"
                        else:
                            color_hex = "#000000"
                        
                        # 判断样式
                        is_bold = bool(flags & 2 ** 4)
                        is_italic = bool(flags & 2 ** 1)
                        
                        # 计算缩放后的位置
                        text_blocks.append({
                            "text": text,
                            "x": bbox[0] * self.zoom,
                            "y": bbox[1] * self.zoom,
                            "width": (bbox[2] - bbox[0]) * self.zoom,
                            "height": (bbox[3] - bbox[1]) * self.zoom,
                            "font": font.split(",")[0].split("-")[0],
                            "size": size * self.zoom,
                            "color": color_hex,
                            "bold": is_bold,
                            "italic": is_italic
                        })
        
        return text_blocks
    
    def _generate_html_for_page(self, page_num: int, image_info: Dict, 
                                 text_blocks: List[Dict], links: List[Dict],
                                 smart_links: List[Dict]) -> str:
        """
        为单页生成 HTML - 图片背景 + 透明文字层 + 点击复制链接（安全版）
        
        Args:
            page_num: 页码
            image_info: 图片信息
            text_blocks: 文本块列表
            links: PDF 原始链接列表
            smart_links: 智能识别链接列表
            
        Returns:
            HTML 字符串
        """
        img_width = image_info["width"]
        img_height = image_info["height"]
        
        html_parts = []
        
        # 页面容器
        html_parts.append(f'  <div class="page" style="width: {img_width}px; height: {img_height}px;">')
        
        # 背景图片层
        html_parts.append(
            f'    <img class="page-background" src="assets/images/{image_info["filename"]}" '
            f'style="position: absolute; left: 0; top: 0; width: {img_width}px; height: {img_height}px;" />'
        )
        
        # 透明文字层（如果启用）
        if self.text_layer and text_blocks:
            html_parts.append('    <div class="text-layer" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;">')
            
            for block in text_blocks:
                # 构建样式 - 文字透明但可选择
                styles = [
                    f"position: absolute",
                    f"left: {block['x']:.2f}px",
                    f"top: {block['y']:.2f}px",
                    f"width: {block['width']:.2f}px",
                    f"height: {block['height']:.2f}px",
                    f"font-family: '{block['font']}', Arial, sans-serif",
                    f"font-size: {block['size']:.2f}px",
                    f"color: transparent",
                    f"background: transparent",
                    f"line-height: {block['height']:.2f}px",
                    f"cursor: text",
                    f"user-select: text",
                    f"-webkit-user-select: text",
                    f"-moz-user-select: text",
                    f"-ms-user-select: text"
                ]
                
                if block.get("bold"):
                    styles.append("font-weight: bold")
                if block.get("italic"):
                    styles.append("font-style: italic")
                
                style_str = "; ".join(styles)
                
                # 转义 HTML 特殊字符
                text = block["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                
                html_parts.append(f'      <div style="{style_str}">{text}</div>')
            
            html_parts.append('    </div>')
        
        # 链接层（PDF 原始链接 + 智能识别链接）- 点击复制模式（安全版）
        all_links = links + smart_links
        if all_links:
            html_parts.append('    <div class="link-layer" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;">')
            
            for idx, link in enumerate(all_links):
                # 链接样式 - 保持原有样式不变
                link_styles = [
                    f"position: absolute",
                    f"left: {link['x']:.2f}px",
                    f"top: {link['y']:.2f}px",
                    f"width: {link['width']:.2f}px",
                    f"height: {link['height']:.2f}px",
                    f"cursor: pointer",
                    f"z-index: 100"
                ]
                
                # 如果是智能识别的链接，添加视觉提示
                if link.get("type") in ["official_website", "pan"]:
                    link_styles.extend([
                        f"border: 2px dashed #4CAF50",
                        f"border-radius: 4px",
                        f"background: rgba(76, 175, 80, 0.1)"
                    ])
                
                style_str = "; ".join(link_styles)
                
                # 转义 URL - 用于 data 属性存储
                uri_escaped = link["uri"].replace('&', '&amp;').replace('"', '&quot;')
                
                # 生成链接标签 - 使用 span 而非 a 标签，移除 href，添加点击复制功能
                label = link.get("label", "链接")
                title_attr = f' title="点击复制{label}地址"'
                
                html_parts.append(
                    f'      <span class="copy-link" data-url="{uri_escaped}"{title_attr} style="{style_str}"></span>'
                )
            
            html_parts.append('    </div>')
        
        html_parts.append('  </div>')
        
        return "\n".join(html_parts)
    
    def _generate_css(self) -> str:
        """
        生成 CSS 样式 - 点击复制安全版
        
        Returns:
            CSS 字符串
        """
        css = """/* 萌新极客·PDF转HTML一键复制 - 样式表 */

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f5f5f5;
  padding: 20px;
}

.container {
  max-width: 100%;
  margin: 0 auto;
}

.page {
  position: relative;
  background-color: white;
  margin: 0 auto 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.page-background {
  display: block;
  pointer-events: none;
}

.text-layer {
  pointer-events: auto;
}

.text-layer div {
  white-space: pre;
  overflow: hidden;
}

.link-layer {
  pointer-events: auto;
}

/* 点击复制链接样式 - 保持原有样式不变 */
.link-layer .copy-link {
  display: block;
  text-decoration: none;
  transition: background 0.2s ease;
}

.link-layer .copy-link:hover {
  background: rgba(76, 175, 80, 0.3) !important;
  border-color: #2E7D32 !important;
}

/* 智能链接提示 */
.link-layer .copy-link[title^="点击复制官网"]::after,
.link-layer .copy-link[title^="点击复制百度网盘"]::after,
.link-layer .copy-link[title^="点击复制阿里云盘"]::after,
.link-layer .copy-link[title^="点击复制夸克网盘"]::after,
.link-layer .copy-link[title^="点击复制迅雷网盘"]::after,
.link-layer .copy-link[title^="点击复制天翼云盘"]::after,
.link-layer .copy-link[title^="点击复制链接"]::after {
  content: "📋";
  position: absolute;
  right: 2px;
  top: 2px;
  font-size: 12px;
  opacity: 0.7;
}

/* 复制提示框样式 */
.copy-toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  z-index: 9999;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  white-space: nowrap;
}

.copy-toast.show {
  opacity: 1;
}

/* 响应式设计 */
@media screen and (max-width: 1024px) {
  body {
    padding: 10px;
  }
  
  .page {
    margin-bottom: 15px;
  }
}

@media screen and (max-width: 768px) {
  body {
    padding: 5px;
  }
  
  .page {
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  }
  
  .copy-toast {
    font-size: 12px;
    padding: 10px 16px;
  }
}

/* 打印样式 */
@media print {
  body {
    background-color: white;
    padding: 0;
  }
  
  .page {
    box-shadow: none;
    margin-bottom: 0;
    page-break-after: always;
  }
  
  .page:last-child {
    page-break-after: auto;
  }
  
  .link-layer {
    display: none;
  }
  
  .copy-toast {
    display: none !important;
  }
}

/* 暗黑模式支持 */
@media (prefers-color-scheme: dark) {
  body {
    background-color: #1a1a1a;
  }
  
  .page {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }
}
"""
        return css
    
    def _generate_html(self, pages_html: List[str], total_links: int) -> str:
        """
        生成完整 HTML 文档 - 安全复制版
        
        Args:
            pages_html: 每页的 HTML 列表
            total_links: 链接总数
            
        Returns:
            完整 HTML 字符串
        """
        title = self.pdf_path.stem
        num_pages = len(pages_html)
        
        # 内联 JavaScript - 实现点击复制功能
        inline_js = """
<script>
(function() {
  // 创建提示框元素
  var toast = document.createElement('div');
  toast.className = 'copy-toast';
  toast.textContent = '链接已复制，可粘贴到浏览器打开';
  document.body.appendChild(toast);
  
  // 复制功能
  function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    } else {
      // 降级方案
      var textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.left = '-9999px';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        return Promise.resolve();
      } catch (err) {
        return Promise.reject(err);
      } finally {
        document.body.removeChild(textarea);
      }
    }
  }
  
  // 显示提示
  function showToast() {
    toast.classList.add('show');
    setTimeout(function() {
      toast.classList.remove('show');
    }, 2000);
  }
  
  // 绑定点击事件
  document.addEventListener('click', function(e) {
    var target = e.target;
    if (target.classList.contains('copy-link')) {
      e.preventDefault();
      var url = target.getAttribute('data-url');
      if (url) {
        copyToClipboard(url).then(function() {
          showToast();
        }).catch(function() {
          toast.textContent = '复制失败，请手动复制';
          showToast();
          setTimeout(function() {
            toast.textContent = '链接已复制，可粘贴到浏览器打开';
          }, 2000);
        });
      }
    }
  });
})();
</script>"""
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <div class="container">
{chr(10).join(pages_html)}
  </div>
  <!-- 
    萌新极客·PDF转HTML一键复制
    - 原始文件: {self.pdf_path.name}
    - 页数: {num_pages}
    - 渲染 DPI: {self.dpi}
    - 文字层: {'启用' if self.text_layer else '禁用'}
    - 智能链接: {'启用' if self.smart_links else '禁用'}
    - 识别链接数: {total_links}
    - 转换时间: {self._get_timestamp()}
    - 转换工具: 萌新极客·PDF转HTML一键复制 v4.2
    - 技术: 页面渲染为高清图片 + 透明文字层叠加 + 智能链接识别 + 一键复制
    - 一键复制: 点击链接复制地址到剪贴板，永久有效，2秒提示
    - 安全特性: 移除跳转功能，改为点击复制，防止网站挂马
  -->
{inline_js}
</body>
</html>"""
        return html
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def convert(self) -> Dict:
        """
        执行 PDF 到 HTML 的转换
        
        Returns:
            转换结果信息
        """
        print(f"开始转换 (萌新极客·PDF转HTML一键复制): {self.pdf_path}")
        print(f"总页数: {len(self.doc)}")
        print(f"渲染 DPI: {self.dpi}")
        print(f"缩放比例: {self.zoom:.2f}x")
        print(f"文字层: {'启用' if self.text_layer else '禁用'}")
        print(f"智能链接: {'启用' if self.smart_links else '禁用'}")
        print(f"安全特性: 点击复制链接，防止网站挂马")
        print(f"技术: 页面渲染为高清图片 + 透明文字层叠加 + 智能链接识别 + 点击复制")
        
        pages_html = []
        total_links = 0
        
        for page_num in range(len(self.doc)):
            print(f"处理第 {page_num + 1}/{len(self.doc)} 页...")
            
            page = self.doc[page_num]
            
            # 渲染页面为图片
            image_info = self._render_page_to_image(page, page_num + 1)
            
            # 提取文字层
            text_blocks = []
            if self.text_layer:
                text_blocks = self._extract_text_with_style(page)
            
            # 提取 PDF 原始链接
            links = self._extract_links_from_page(page)
            
            # 智能识别链接
            smart_links = []
            if self.smart_links and text_blocks:
                smart_links = self._detect_smart_links(text_blocks)
            
            page_links = len(links) + len(smart_links)
            total_links += page_links
            if page_links > 0:
                print(f"  发现 {page_links} 个链接 (原始: {len(links)}, 智能识别: {len(smart_links)})")
            
            # 生成页面 HTML
            page_html = self._generate_html_for_page(
                page_num + 1, image_info, text_blocks, links, smart_links
            )
            pages_html.append(page_html)
        
        # 生成 CSS
        css_content = self._generate_css()
        css_path = self.assets_dir / "styles.css"
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # 生成 HTML
        html_content = self._generate_html(pages_html, total_links)
        html_path = self.output_dir / f"{self.pdf_path.stem}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # 关闭 PDF
        self.doc.close()
        
        result = {
            "success": True,
            "html_path": str(html_path),
            "css_path": str(css_path),
            "images_dir": str(self.images_dir),
            "total_pages": len(pages_html),
            "total_links": total_links,
            "output_dir": str(self.output_dir),
            "dpi": self.dpi,
            "zoom": self.zoom,
            "mode": "萌新极客·PDF转HTML一键复制"
        }
        
        print(f"转换完成!")
        print(f"  HTML 文件: {html_path}")
        print(f"  CSS 文件: {css_path}")
        print(f"  图片目录: {self.images_dir}")
        print(f"  总页数: {len(pages_html)}")
        print(f"  识别链接数: {total_links}")
        print(f"  渲染 DPI: {self.dpi}")
        print(f"  模式: 萌新极客·PDF转HTML一键复制")
        
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="萌新极客·PDF转HTML一键复制 - 1:1 还原 PDF 并支持一键复制链接",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python pdf_to_html.py input.pdf
  python pdf_to_html.py input.pdf -o ./output
  python pdf_to_html.py input.pdf --dpi 200
  python pdf_to_html.py input.pdf --no-text-layer
  python pdf_to_html.py input.pdf --no-smart-links

一键复制特性:
  - 点击链接复制地址到剪贴板，永久有效
  - 显示"链接已复制，可粘贴到浏览器打开"（2秒自动消失）
  - 防止恶意网站挂马，用户自主选择是否访问
  - 纯本地处理，无外部网络请求
        """
    )
    
    parser.add_argument("pdf_path", help="PDF 文件路径")
    parser.add_argument("-o", "--output", help="输出目录（默认为 PDF 所在目录）")
    parser.add_argument("--dpi", type=int, default=150,
                        help="渲染分辨率（默认 150，越高越清晰但文件越大）")
    parser.add_argument("--no-text-layer", action="store_true",
                        help="禁用文字层（仅输出图片，文字不可选择）")
    parser.add_argument("--no-smart-links", action="store_true",
                        help="禁用智能链接识别")
    
    args = parser.parse_args()
    
    try:
        converter = PDFToHTMLConverter(
            pdf_path=args.pdf_path,
            output_dir=args.output,
            dpi=args.dpi,
            text_layer=not args.no_text_layer,
            smart_links=not args.no_smart_links
        )
        result = converter.convert()
        
        print("\\n转换成功!")
        print(f"输出文件: {result['html_path']}")
        
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
