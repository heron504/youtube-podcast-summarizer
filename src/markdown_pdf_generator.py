"""
Markdown-aware PDF report generator
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus import HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
import re

class MarkdownPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_chinese_font()
        self.setup_custom_styles()

    def setup_chinese_font(self):
        """Setup Chinese font support"""
        try:
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',    # Microsoft YaHei
                'C:/Windows/Fonts/simsun.ttc',  # SimSun
                '/System/Library/Fonts/PingFang.ttc',  # macOS
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    pdfmetrics.registerFont(TTFont('Chinese-Bold', font_path))
                    break

        except Exception as e:
            print(f"Warning: Font setup failed: {e}")

    def setup_custom_styles(self):
        """Setup custom styles including Markdown support"""
        has_chinese = 'Chinese' in pdfmetrics.getRegisteredFontNames()
        font_name = 'Chinese' if has_chinese else 'Helvetica'
        font_bold = 'Chinese-Bold' if has_chinese else 'Helvetica-Bold'

        # 主标题
        self.title_style = ParagraphStyle(
            'ReportTitle',
            fontName=font_name,
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=20
        )

        # 副标题
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            alignment=TA_CENTER,
            spaceAfter=20
        )

        # H1 标题 (###)
        self.h1_style = ParagraphStyle(
            'H1',
            fontName=font_bold,
            fontSize=16,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=12,
            spaceBefore=18,
            leftIndent=0
        )

        # H2 标题 (##)
        self.h2_style = ParagraphStyle(
            'H2',
            fontName=font_bold,
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10,
            spaceBefore=15,
            leftIndent=5
        )

        # H3 标题 (#)
        self.h3_style = ParagraphStyle(
            'H3',
            fontName=font_bold,
            fontSize=12,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=8,
            spaceBefore=12,
            leftIndent=10
        )

        # 视频标题
        self.video_title_style = ParagraphStyle(
            'VideoTitle',
            fontName=font_bold,
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=8,
            spaceBefore=15,
            leftIndent=10,
            backColor=colors.HexColor('#f8fafc'),
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8
        )

        # 频道和链接
        self.meta_style = ParagraphStyle(
            'Meta',
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=5,
            leftIndent=10
        )

        # 正文段落
        self.body_style = ParagraphStyle(
            'Body',
            fontName=font_name,
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            spaceBefore=4,
            leftIndent=15,
            rightIndent=15,
            leading=16
        )

        # 列表项
        self.list_style = ParagraphStyle(
            'ListItem',
            fontName=font_name,
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            spaceAfter=4,
            leftIndent=25,
            bulletIndent=15,
            leading=14
        )

        # 粗体文本
        self.bold_style = ParagraphStyle(
            'Bold',
            fontName=font_bold,
            fontSize=11,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            leftIndent=15,
            rightIndent=15,
            leading=16
        )

        # 页脚
        self.footer_style = ParagraphStyle(
            'Footer',
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceBefore=30
        )

    def parse_markdown_content(self, content):
        """Convert markdown content to ReportLab paragraphs"""
        if not content or not content.strip():
            return [Paragraph("内容纪要生成失败或无可用内容", self.body_style)]

        paragraphs = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                paragraphs.append(Spacer(1, 4))
                continue

            # H3 标题 (###)
            if line.startswith('### '):
                title_text = line[4:].strip()
                paragraphs.append(Paragraph(title_text, self.h1_style))

            # H2 标题 (##)
            elif line.startswith('## '):
                title_text = line[3:].strip()
                paragraphs.append(Paragraph(title_text, self.h2_style))

            # H1 标题 (#)
            elif line.startswith('# '):
                title_text = line[2:].strip()
                paragraphs.append(Paragraph(title_text, self.h3_style))

            # 列表项
            elif line.startswith('- ') or line.startswith('* ') or re.match(r'^\d+\. ', line):
                if line.startswith('- ') or line.startswith('* '):
                    list_text = '• ' + line[2:].strip()
                else:
                    list_text = line.strip()

                # 处理粗体
                list_text = self.process_bold_text(list_text)
                paragraphs.append(Paragraph(list_text, self.list_style))

            # 普通段落
            else:
                # 处理粗体文本
                processed_text = self.process_bold_text(line)

                # 如果整行都是粗体，使用粗体样式
                if line.startswith('**') and line.endswith('**') and line.count('**') == 2:
                    clean_text = line[2:-2].strip()
                    paragraphs.append(Paragraph(clean_text, self.bold_style))
                else:
                    paragraphs.append(Paragraph(processed_text, self.body_style))

        return paragraphs

    def process_bold_text(self, text):
        """Process **bold** text in markdown"""
        # 替换 **text** 为 <b>text</b>
        processed = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return processed

    def create_header_table(self, summaries_count):
        """Create header information table"""
        current_date = datetime.now()

        header_data = [
            ['报告日期', current_date.strftime('%Y年%m月%d日 %A')],
            ['视频数量', f'{summaries_count} 个'],
            ['生成时间', current_date.strftime('%H:%M:%S')],
            ['报告类型', 'AI科技播客详细内容纪要']
        ]

        header_table = Table(header_data, colWidths=[3*cm, 8*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        return header_table

    def create_divider(self):
        """Create divider line"""
        return HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb'))

    def generate_report(self, summaries, output_path=None):
        """Generate PDF report with Markdown support"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"ai_podcast_detailed_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm
        )

        story = []

        # 主标题
        story.append(Paragraph("AI科技播客详细内容纪要", self.title_style))
        story.append(Spacer(1, 10))

        # 头部信息表格
        header_table = self.create_header_table(len(summaries))
        story.append(header_table)
        story.append(Spacer(1, 20))

        # 统计信息
        if summaries:
            stats_text = f"本期共收录 {len(summaries)} 个科技视频的详细内容纪要"
            stats_style = ParagraphStyle(
                'Stats',
                fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
                fontSize=12,
                textColor=colors.HexColor('#059669'),
                alignment=TA_CENTER,
                spaceAfter=20,
                spaceBefore=10,
                backColor=colors.HexColor('#ecfdf5'),
                borderWidth=1,
                borderColor=colors.HexColor('#a7f3d0'),
                borderPadding=10
            )
            story.append(Paragraph(stats_text, stats_style))

        story.append(Spacer(1, 20))
        story.append(self.create_divider())
        story.append(Spacer(1, 20))

        # 处理每个视频
        for i, summary in enumerate(summaries, 1):
            # 视频标题
            video_title = f"{i:02d}. {summary['title']}"
            story.append(Paragraph(video_title, self.video_title_style))

            # 频道和链接信息
            channel_info = f"频道: {summary['channel']}"
            story.append(Paragraph(channel_info, self.meta_style))

            link_text = f"链接: {summary['url']}"
            story.append(Paragraph(link_text, self.meta_style))

            if 'content_type' in summary and summary['content_type']:
                content_type_text = f"内容来源: {summary['content_type']}"
                story.append(Paragraph(content_type_text, self.meta_style))

            story.append(Spacer(1, 10))

            # 解析Markdown内容
            if summary['summary'] and summary['summary'].strip():
                markdown_paragraphs = self.parse_markdown_content(summary['summary'])
                story.extend(markdown_paragraphs)
            else:
                story.append(Paragraph("内容纪要生成失败", self.body_style))

            # 视频间分隔
            story.append(Spacer(1, 20))
            if i < len(summaries):
                story.append(self.create_divider())
                story.append(Spacer(1, 20))

            # 每个视频后换页
            if i < len(summaries):
                story.append(PageBreak())

        # 页脚
        story.append(Spacer(1, 30))
        footer_text = f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 由AI智能分析生成"
        story.append(Paragraph(footer_text, self.footer_style))

        try:
            doc.build(story)
            print(f"Markdown PDF report generated: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error generating Markdown PDF: {e}")
            return None