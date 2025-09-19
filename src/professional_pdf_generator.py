"""
Professional PDF Generator with proper Markdown support and clean black/white styling
"""
import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import re
import logging

class ProfessionalPDFGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_fonts()
        self.setup_styles()

    def setup_fonts(self):
        """Setup Chinese fonts"""
        try:
            # 使用Windows系统自带的中文字体
            font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Chinese', font_path))
                self.chinese_font = 'Chinese'
            else:
                # 备用方案
                self.chinese_font = 'Helvetica'
                self.logger.warning("中文字体未找到，使用默认字体")
        except Exception as e:
            self.chinese_font = 'Helvetica'
            self.logger.warning(f"字体设置失败: {e}")

    def setup_styles(self):
        """Setup professional black/white styles"""
        styles = getSampleStyleSheet()

        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontName=self.chinese_font,
            fontSize=18,
            textColor=black,
            spaceAfter=20,
            alignment=TA_CENTER
        )

        # 日期样式
        self.date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=black,
            alignment=TA_CENTER,
            spaceAfter=30
        )

        # H1标题样式
        self.h1_style = ParagraphStyle(
            'H1Style',
            parent=styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=16,
            textColor=black,
            spaceBefore=20,
            spaceAfter=12
        )

        # H2标题样式
        self.h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            textColor=black,
            spaceBefore=16,
            spaceAfter=8
        )

        # H3标题样式
        self.h3_style = ParagraphStyle(
            'H3Style',
            parent=styles['Heading3'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=black,
            spaceBefore=12,
            spaceAfter=6
        )

        # 正文样式
        self.body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=0,
            rightIndent=0
        )

        # 列表样式
        self.list_style = ParagraphStyle(
            'ListStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=3,
            spaceAfter=3,
            leftIndent=20
        )

        # 频道样式
        self.channel_style = ParagraphStyle(
            'ChannelStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            textColor=black,
            spaceBefore=8,
            spaceAfter=4
        )

    def clean_content(self, content: str) -> str:
        """Clean content to remove model preambles and format properly"""
        lines = content.split('\n')
        cleaned_lines = []
        skip_preamble = True

        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append('')
                continue

            # 跳过常见的模型开场白
            if skip_preamble and any(phrase in line for phrase in [
                "好的，我已经观看", "我来为您", "根据视频内容", "以下是", "我将为您",
                "根据您的要求", "已经观看完", "视频内容总结如下", "内容纪要如下"
            ]):
                continue

            # 如果遇到markdown标题或实质内容，停止跳过
            if line.startswith('#') or len(line) > 20:
                skip_preamble = False

            if not skip_preamble:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def translate_title(self, title: str) -> str:
        """Simple title translation helper"""
        # 这里可以添加标题翻译逻辑，现在先返回原标题
        return title

    def parse_markdown_to_paragraphs(self, content: str) -> list:
        """Parse markdown content into ReportLab paragraphs with proper formatting"""
        content = self.clean_content(content)
        lines = content.split('\n')
        paragraphs = []

        for line in lines:
            line = line.strip()
            if not line:
                paragraphs.append(Spacer(1, 6))
                continue

            # H1标题 (# )
            if line.startswith('# '):
                title_text = line[2:].strip()
                paragraphs.append(Paragraph(title_text, self.h1_style))

            # H2标题 (## )
            elif line.startswith('## '):
                title_text = line[3:].strip()
                paragraphs.append(Paragraph(title_text, self.h2_style))

            # H3标题 (### )
            elif line.startswith('### '):
                title_text = line[4:].strip()
                paragraphs.append(Paragraph(title_text, self.h3_style))

            # 列表项
            elif line.startswith('- ') or line.startswith('* '):
                list_text = line[2:].strip()
                # 处理粗体
                list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                paragraphs.append(Paragraph(f"• {list_text}", self.list_style))

            # 数字列表
            elif re.match(r'^\d+\.\s+', line):
                list_text = re.sub(r'^\d+\.\s+', '', line)
                list_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', list_text)
                paragraphs.append(Paragraph(list_text, self.list_style))

            # 普通段落
            else:
                # 处理粗体标记
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                paragraphs.append(Paragraph(text, self.body_style))

        return paragraphs

    def create_table_of_contents(self, summaries: list) -> list:
        """Create a table of contents"""
        toc_elements = []

        # 目录标题
        toc_elements.append(Paragraph("目录", self.title_style))
        toc_elements.append(Spacer(1, 20))

        # 目录项
        for i, summary in enumerate(summaries, 1):
            title = summary.get('title', '未知标题')
            channel = summary.get('channel', '未知频道')
            translated_title = self.translate_title(title)

            toc_line = f"{i}. {translated_title} ({channel})"
            toc_elements.append(Paragraph(toc_line, self.body_style))

        toc_elements.append(PageBreak())
        return toc_elements

    def generate_report(self, summaries: list, output_path: str) -> str:
        """Generate professional PDF report"""
        try:
            # 确保输出路径正确
            if not output_path:
                output_path = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # 创建输出目录
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 创建PDF文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            story = []

            # 标题页
            story.append(Paragraph("YouTube播客内容总结报告", self.title_style))
            story.append(Spacer(1, 20))

            # 日期
            current_date = datetime.now().strftime("%Y年%m月%d日")
            story.append(Paragraph(f"生成日期: {current_date}", self.date_style))

            # 统计信息
            stats_text = f"本次共处理 {len(summaries)} 个视频"
            story.append(Paragraph(stats_text, self.date_style))
            story.append(PageBreak())

            # 目录
            story.extend(self.create_table_of_contents(summaries))

            # 内容
            for i, summary in enumerate(summaries, 1):
                title = summary.get('title', '未知标题')
                channel = summary.get('channel', '未知频道')
                content = summary.get('summary', '无内容')

                # 视频标题
                translated_title = self.translate_title(title)
                story.append(Paragraph(f"{i}. {translated_title}", self.h1_style))

                # 频道信息
                story.append(Paragraph(f"频道: {channel}", self.channel_style))
                story.append(Paragraph(f"原标题: {title}", self.channel_style))
                story.append(Spacer(1, 12))

                # 解析并添加内容
                content_paragraphs = self.parse_markdown_to_paragraphs(content)
                story.extend(content_paragraphs)

                # 视频间分页
                if i < len(summaries):
                    story.append(PageBreak())

            # 生成PDF
            doc.build(story)

            self.logger.info(f"专业PDF报告生成成功: {output_path}")
            print(f"Professional PDF report generated: {output_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            print(f"PDF生成失败: {e}")
            return None