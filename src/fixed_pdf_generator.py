"""
Fixed PDF Generator with proper formatting, bold titles, translations, and links
"""
import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

class FixedPDFGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_fonts()
        self.setup_fixed_styles()

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

    def setup_fixed_styles(self):
        """Setup properly working styles"""
        styles = getSampleStyleSheet()

        # 页眉样式（日期）
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11,
            textColor=black,
            spaceBefore=0,
            spaceAfter=20,
            alignment=TA_LEFT,
            leading=16.5  # 1.5倍行距
        )

        # 视频标题样式 - 确保加粗生效
        self.title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=12,
            textColor=black,
            spaceBefore=20,
            spaceAfter=6,
            alignment=TA_LEFT,
            leading=18  # 1.5倍行距
        )

        # 频道和链接样式
        self.meta_style = ParagraphStyle(
            'MetaStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=black,
            spaceBefore=3,
            spaceAfter=3,
            alignment=TA_LEFT,
            leading=13.5  # 1.5倍行距
        )

        # 链接样式
        self.link_style = ParagraphStyle(
            'LinkStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            textColor=blue,
            spaceBefore=3,
            spaceAfter=12,
            alignment=TA_LEFT,
            leading=13.5
        )

        # 摘要正文样式 - 1.5倍行距，两端对齐
        self.summary_style = ParagraphStyle(
            'SummaryStyle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            textColor=black,
            spaceBefore=8,
            spaceAfter=16,
            alignment=TA_JUSTIFY,
            leading=15,  # 1.5倍行距 (10 * 1.5)
            leftIndent=0,
            rightIndent=0
        )

    def translate_title(self, title: str) -> str:
        """翻译标题"""
        translations = {
            "Write Things Down": "记录想法",
            "Navigating Data Chaos A New Approach": "应对数据混乱的新方法",
            "Opendoor is a Software Business": "Opendoor是一个软件企业",
            "Modern Politics and Starting a New Country": "现代政治与创建新国家",
            "There's never been more opportunities for young people, IF you work hard!": "年轻人从未有过如此多的机会，如果你努力工作！",
            "How Britain Defeated Germany On The Atlantic": "英国如何在大西洋击败德国",
            "How to Live in Everyone Else's Future": "如何活在他人的未来中",
            "Balaji Srinivasan": "巴拉吉·斯里尼瓦桑"
        }

        # 精确匹配
        if title in translations:
            return translations[title]

        # 部分匹配
        for en, zh in translations.items():
            if en.lower() in title.lower() or any(word in title.lower() for word in en.lower().split()[:2]):
                return zh

        return title  # 如果没有翻译就返回原标题

    def generate_report(self, summaries: list, output_path: str) -> str:
        """Generate fixed PDF report"""
        try:
            if not output_path:
                output_path = f"fixed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

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

            # 页眉 - 日期和统计
            current_date = datetime.now().strftime("%Y年%m月%d日")
            header_text = f"{current_date} YouTube播客摘要 (共{len(summaries)}个视频)"
            story.append(Paragraph(header_text, self.header_style))

            # 处理每个视频
            for i, summary in enumerate(summaries, 1):
                title = summary.get('title', '未知标题')
                channel = summary.get('channel', '未知频道')
                content = summary.get('summary', '无内容')
                video_url = summary.get('url', '')

                # 翻译标题
                translated_title = self.translate_title(title)

                # 视频标题 - 加粗，包含翻译
                if translated_title != title:
                    title_text = f"<b>{title}</b><br/><i>({translated_title})</i>"
                else:
                    title_text = f"<b>{title}</b>"

                story.append(Paragraph(title_text, self.title_style))

                # 频道信息
                story.append(Paragraph(f"频道：{channel}", self.meta_style))

                # 视频链接
                if video_url:
                    link_text = f'<link href="{video_url}" color="blue">🔗 观看视频: {video_url}</link>'
                    story.append(Paragraph(link_text, self.link_style))

                # 摘要内容 - 确保完整显示
                if content and len(content.strip()) > 0:
                    # 按段落分割内容
                    paragraphs = content.split('\n\n')
                    if not paragraphs or len(paragraphs) == 1:
                        # 如果没有段落分割，尝试按句号分割
                        paragraphs = content.split('。')
                        paragraphs = [p.strip() + '。' for p in paragraphs if p.strip()]

                    for j, para in enumerate(paragraphs):
                        para = para.strip()
                        if para:
                            # 确保段落完整
                            if not para.endswith(('。', '！', '？', '.', '!', '?')):
                                para += '。'
                            story.append(Paragraph(para, self.summary_style))
                else:
                    # 如果没有摘要，添加占位内容
                    placeholder = "该视频的摘要内容暂时无法获取，请通过上方链接观看完整视频。"
                    story.append(Paragraph(placeholder, self.summary_style))

                # 视频间分隔
                if i < len(summaries):
                    story.append(Spacer(1, 20))

            # 生成PDF
            doc.build(story)

            self.logger.info(f"修复的PDF报告生成成功: {output_path}")
            print(f"Fixed PDF report generated: {output_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            print(f"PDF生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None