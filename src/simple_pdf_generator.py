"""
Simple PDF Generator with clean layout, no cover page, no table of contents
"""
import os
import re
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

class SimplePDFGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_fonts()
        self.setup_simple_styles()

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

    def setup_simple_styles(self):
        """Setup simple clean styles"""
        styles = getSampleStyleSheet()

        # 视频标题样式 - 加粗，附带中文翻译
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=black,
            spaceBefore=20,
            spaceAfter=8,
            alignment=TA_LEFT,
            leading=18  # 1.5倍行距
        )

        # 频道信息样式
        self.channel_style = ParagraphStyle(
            'ChannelStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=black,
            spaceBefore=4,
            spaceAfter=12,
            alignment=TA_LEFT,
            leading=13.5  # 1.5倍行距
        )

        # 摘要正文样式 - 1.5倍行距
        self.summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=0,
            spaceAfter=16,
            alignment=TA_JUSTIFY,
            leading=15,  # 1.5倍行距 (10 * 1.5)
            leftIndent=0,
            rightIndent=0
        )

        # 页眉样式（日期）
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=0,
            spaceAfter=20,
            alignment=TA_LEFT,
            leading=15
        )

    def translate_title_basic(self, title: str) -> str:
        """基本的标题翻译"""
        # 简单处理一些常见词汇
        translations = {
            "How to": "如何",
            "The Future of": "未来",
            "Behind the": "背后",
            "Inside": "内部",
            "Why": "为什么",
            "What": "什么",
            "When": "何时",
            "AI": "AI",
            "Machine Learning": "机器学习",
            "Deep Learning": "深度学习",
            "Startup": "创业",
            "Technology": "科技",
            "Business": "商业"
        }

        translated = title
        for en, zh in translations.items():
            translated = translated.replace(en, zh)

        return translated

    def generate_report(self, summaries: list, output_path: str) -> str:
        """Generate simple PDF report without cover page or TOC"""
        try:
            if not output_path:
                output_path = f"simple_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            # 创建文档
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=50,
                bottomMargin=50
            )

            story = []

            # 页眉 - 只有日期
            current_date = datetime.now().strftime("%Y年%m月%d日 YouTube播客摘要")
            story.append(Paragraph(current_date, self.header_style))

            # 直接开始内容，无封面，无目录
            for i, summary in enumerate(summaries, 1):
                title = summary.get('title', '未知标题')
                channel = summary.get('channel', '未知频道')
                content = summary.get('summary', '无内容')

                # 生成标题和中文翻译
                translated_title = self.translate_title_basic(title)
                if translated_title != title:
                    full_title = f"<b>{title}</b> ({translated_title})"
                else:
                    full_title = f"<b>{title}</b>"

                story.append(Paragraph(full_title, self.title_style))

                # 频道信息
                story.append(Paragraph(f"频道：{channel}", self.channel_style))

                # 摘要内容 - 直接添加，不做复杂解析
                # 清理内容中的markdown标记
                clean_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                clean_content = re.sub(r'\*(.*?)\*', r'<i>\1</i>', clean_content)
                clean_content = re.sub(r'^#+ ', '', clean_content, flags=re.MULTILINE)
                clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)

                # 按段落分割
                paragraphs = clean_content.split('\n\n')
                for para in paragraphs:
                    para = para.strip()
                    if para:
                        story.append(Paragraph(para, self.summary_style))

                # 视频间分隔
                if i < len(summaries):
                    story.append(Spacer(1, 20))

            # 生成PDF
            doc.build(story)

            self.logger.info(f"简化PDF报告生成成功: {output_path}")
            print(f"Simple PDF report generated: {output_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            print(f"PDF生成失败: {e}")
            return None