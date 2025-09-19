"""
Refined PDF Generator with optimized layout, spacing, and Chinese content summaries
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

class RefinedPDFGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_fonts()
        self.setup_refined_styles()

    def setup_fonts(self):
        """Setup Chinese fonts"""
        try:
            font_path = "C:/Windows/Fonts/msyh.ttc"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                self.chinese_font = 'Chinese'
            else:
                self.chinese_font = 'Helvetica'
        except Exception as e:
            self.chinese_font = 'Helvetica'
            self.logger.warning(f"字体设置失败: {e}")

    def setup_refined_styles(self):
        """Setup refined styles with proper spacing"""
        styles = getSampleStyleSheet()

        # 文档标题
        self.doc_title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Title'],
            fontName=self.chinese_font,
            fontSize=18,
            textColor=black,
            spaceAfter=16,
            spaceBefore=0,
            alignment=TA_CENTER
        )

        # 日期和统计
        self.meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=6
        )

        # 目录标题
        self.toc_title_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=16,
            textColor=black,
            spaceBefore=20,
            spaceAfter=16,
            alignment=TA_LEFT
        )

        # 目录项
        self.toc_item_style = ParagraphStyle(
            'TOCItem',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=4,
            spaceAfter=4,
            leftIndent=0,
            alignment=TA_LEFT
        )

        # 视频标题 - 使用加粗而不是放大
        self.video_title_style = ParagraphStyle(
            'VideoTitle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=black,
            spaceBefore=20,
            spaceAfter=8,
            alignment=TA_LEFT
        )

        # H1 - 加粗不放大
        self.h1_style = ParagraphStyle(
            'H1Style',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            textColor=black,
            spaceBefore=14,
            spaceAfter=8,
            alignment=TA_LEFT
        )

        # H2 - 稍微加粗
        self.h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=12,
            spaceAfter=6,
            alignment=TA_LEFT
        )

        # 正文
        self.body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=black,
            spaceBefore=4,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        )

        # 列表项
        self.list_style = ParagraphStyle(
            'ListStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=black,
            spaceBefore=2,
            spaceAfter=2,
            leftIndent=15,
            alignment=TA_LEFT
        )

        # 频道信息
        self.channel_style = ParagraphStyle(
            'ChannelStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=black,
            spaceBefore=4,
            spaceAfter=8,
            alignment=TA_LEFT
        )

    def extract_content_summary(self, content: str) -> str:
        """提取内容的核心观点用于目录"""
        # 查找核心观点部分
        lines = content.split('\n')
        summary_lines = []
        in_core_section = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 寻找核心观点或总结部分
            if any(keyword in line for keyword in ['核心观点', '主要观点', '核心内容', '关键观点']):
                in_core_section = True
                continue
            elif line.startswith('##') and in_core_section:
                break
            elif in_core_section and (line.startswith('- ') or line.startswith('* ') or line.startswith('1.')):
                # 提取要点
                clean_line = re.sub(r'^[-*\d\.]\s*', '', line)
                clean_line = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_line)
                if len(clean_line) > 10:  # 过滤太短的内容
                    summary_lines.append(clean_line)
                    if len(summary_lines) >= 2:  # 只要前2个要点
                        break

        if summary_lines:
            return '；'.join(summary_lines[:2])

        # 如果找不到核心观点，尝试从总结中提取
        for line in lines:
            line = line.strip()
            if '总结' in line or '结论' in line:
                # 找到总结后的第一个有意义的段落
                idx = lines.index(line.strip())
                for i in range(idx + 1, min(idx + 5, len(lines))):
                    next_line = lines[i].strip()
                    if len(next_line) > 20 and not next_line.startswith('#'):
                        return next_line[:60] + '...' if len(next_line) > 60 else next_line

        # 如果都找不到，返回内容开头
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not line.startswith('#'):
                return line[:60] + '...' if len(line) > 60 else line

        return "无法提取概要"

    def translate_title_simple(self, title: str) -> str:
        """简单的标题翻译/处理"""
        # 简单处理一些常见英文词汇
        translations = {
            "AI": "人工智能",
            "How to": "如何",
            "The Future of": "未来的",
            "Behind the": "背后的",
            "Inside": "内部",
            "Why": "为什么"
        }

        translated = title
        for en, zh in translations.items():
            translated = translated.replace(en, zh)

        return translated

    def create_table_of_contents(self, summaries: list) -> list:
        """创建中文概括目录"""
        toc_elements = []

        toc_elements.append(Paragraph("目录", self.toc_title_style))
        toc_elements.append(Spacer(1, 8))

        for i, summary in enumerate(summaries, 1):
            title = summary.get('title', '未知标题')
            channel = summary.get('channel', '未知频道')
            content = summary.get('summary', '')

            # 生成中文概括
            content_summary = self.extract_content_summary(content)

            # 创建目录项
            toc_line = f"{i}. <b>{channel}</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;{content_summary}"
            toc_elements.append(Paragraph(toc_line, self.toc_item_style))
            toc_elements.append(Spacer(1, 2))

        toc_elements.append(PageBreak())
        return toc_elements

    def clean_and_parse_content(self, content: str) -> str:
        """清理并解析内容"""
        lines = content.split('\n')
        cleaned_lines = []
        skip_preamble = True

        for line in lines:
            line = line.strip()

            # 跳过模型开场白
            if skip_preamble and any(phrase in line for phrase in [
                "好的，我已经", "根据视频内容", "以下是", "我将为您", "视频内容总结", "内容纪要如下"
            ]):
                continue

            if line.startswith('#') or len(line) > 15:
                skip_preamble = False

            if not skip_preamble:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def enhanced_markdown_parser(self, content: str) -> list:
        """增强的Markdown解析器"""
        content = self.clean_and_parse_content(content)
        lines = content.split('\n')
        paragraphs = []

        for line in lines:
            line = line.strip()
            if not line:
                paragraphs.append(Spacer(1, 4))
                continue

            # H1标题 (# )
            if line.startswith('# '):
                title_text = line[2:].strip()
                title_text = f"<b>{title_text}</b>"
                paragraphs.append(Paragraph(title_text, self.h1_style))

            # H2标题 (## )
            elif line.startswith('## '):
                title_text = line[3:].strip()
                title_text = f"<b>{title_text}</b>"
                paragraphs.append(Paragraph(title_text, self.h2_style))

            # H3标题 (### )
            elif line.startswith('### '):
                title_text = line[4:].strip()
                title_text = f"<b>{title_text}</b>"
                paragraphs.append(Paragraph(title_text, self.h2_style))

            # 无序列表
            elif line.startswith('- ') or line.startswith('* '):
                list_text = line[2:].strip()
                # 处理内联格式
                list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                list_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', list_text)
                paragraphs.append(Paragraph(f"• {list_text}", self.list_style))

            # 有序列表
            elif re.match(r'^\d+\.\s+', line):
                list_text = re.sub(r'^\d+\.\s+', '', line)
                list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                list_text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', list_text)
                paragraphs.append(Paragraph(list_text, self.list_style))

            # 普通段落
            else:
                # 处理所有内联markdown格式
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)  # 粗体
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # 斜体
                text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)  # 代码
                paragraphs.append(Paragraph(text, self.body_style))

        return paragraphs

    def generate_report(self, summaries: list, output_path: str) -> str:
        """生成优化的PDF报告"""
        try:
            if not output_path:
                output_path = f"refined_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 创建文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=60,
                bottomMargin=60
            )

            story = []

            # 标题页
            story.append(Paragraph("YouTube播客内容总结报告", self.doc_title_style))
            story.append(Spacer(1, 12))

            # 日期和统计
            current_date = datetime.now().strftime("%Y年%m月%d日")
            story.append(Paragraph(f"生成日期：{current_date}", self.meta_style))
            story.append(Paragraph(f"共收录 {len(summaries)} 个播客内容", self.meta_style))
            story.append(PageBreak())

            # 目录
            story.extend(self.create_table_of_contents(summaries))

            # 内容
            for i, summary in enumerate(summaries, 1):
                title = summary.get('title', '未知标题')
                channel = summary.get('channel', '未知频道')
                content = summary.get('summary', '无内容')

                # 视频标题 - 使用加粗
                video_title = f"<b>{i}. {title}</b>"
                story.append(Paragraph(video_title, self.video_title_style))

                # 频道信息
                story.append(Paragraph(f"频道：{channel}", self.channel_style))
                story.append(Spacer(1, 4))

                # 解析内容
                content_paragraphs = self.enhanced_markdown_parser(content)
                story.extend(content_paragraphs)

                # 视频间分隔
                if i < len(summaries):
                    story.append(Spacer(1, 16))
                    story.append(PageBreak())

            # 生成PDF
            doc.build(story)

            self.logger.info(f"优化PDF报告生成成功: {output_path}")
            print(f"Refined PDF report generated: {output_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            print(f"PDF生成失败: {e}")
            return None