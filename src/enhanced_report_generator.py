"""
Enhanced PDF report generator with beautiful formatting
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus import HRFlowable  # 分隔线
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

class EnhancedReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_chinese_font()
        self.setup_custom_styles()

    def setup_chinese_font(self):
        """Setup Chinese font support"""
        try:
            font_paths = [
                'C:/Windows/Fonts/msyh.ttc',    # Microsoft YaHei (better for display)
                'C:/Windows/Fonts/simsun.ttc',  # SimSun (fallback)
                'C:/Windows/Fonts/simhei.ttf',  # SimHei (bold)
                '/System/Library/Fonts/PingFang.ttc',  # macOS
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    break
            else:
                print("Warning: No Chinese font found")

        except Exception as e:
            print(f"Warning: Font setup failed: {e}")

    def setup_custom_styles(self):
        """Setup beautiful custom styles"""
        has_chinese = 'Chinese' in pdfmetrics.getRegisteredFontNames()
        font_name = 'Chinese' if has_chinese else 'Helvetica'

        # 主标题样式 - 大而醒目
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Title'],
            fontName=font_name,
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),  # 深蓝色
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=20
        )

        # 副标题样式
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            textColor=colors.HexColor('#374151'),  # 深灰色
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10
        )

        # 章节标题样式
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontName=font_name,
            fontSize=18,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_LEFT,
            spaceAfter=15,
            spaceBefore=20,
            leftIndent=0,
            borderWidth=0,
            borderColor=colors.HexColor('#e5e7eb'),
            borderPadding=8
        )

        # 视频标题样式 - 突出显示
        self.video_title_style = ParagraphStyle(
            'VideoTitle',
            parent=self.styles['Heading3'],
            fontName=font_name,
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            alignment=TA_LEFT,
            spaceAfter=8,
            spaceBefore=15,
            leftIndent=10,
            bulletIndent=0,
            backColor=colors.HexColor('#f8fafc'),  # 浅灰背景
            borderWidth=1,
            borderColor=colors.HexColor('#e2e8f0'),
            borderPadding=8,
            borderRadius=4
        )

        # 频道样式
        self.channel_style = ParagraphStyle(
            'Channel',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_LEFT,
            spaceAfter=5,
            leftIndent=10,
            italics=1
        )

        # 链接样式
        self.link_style = ParagraphStyle(
            'Link',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_LEFT,
            spaceAfter=10,
            leftIndent=10
        )

        # 内容正文样式
        self.content_style = ParagraphStyle(
            'Content',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            spaceBefore=8,
            leftIndent=15,
            rightIndent=15,
            leading=16,  # 行间距
            borderWidth=1,
            borderColor=colors.HexColor('#f3f4f6'),
            borderPadding=12,
            backColor=colors.HexColor('#fefefe')
        )

        # 页脚样式
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor('#9ca3af'),
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=30
        )

        # 统计信息样式
        self.stats_style = ParagraphStyle(
            'Stats',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=12,
            textColor=colors.HexColor('#059669'),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=10,
            backColor=colors.HexColor('#ecfdf5'),
            borderWidth=1,
            borderColor=colors.HexColor('#a7f3d0'),
            borderPadding=10,
            borderRadius=6
        )

    def create_header_table(self, summaries_count):
        """创建美观的头部信息表格"""
        current_date = datetime.now()

        header_data = [
            ['报告日期', current_date.strftime('%Y年%m月%d日 %A')],
            ['视频数量', f'{summaries_count} 个'],
            ['生成时间', current_date.strftime('%H:%M:%S')],
            ['报告类型', 'AI科技播客内容纪要']
        ]

        header_table = Table(header_data, colWidths=[3*cm, 8*cm])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1f2937')),
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

    def create_divider(self, color=None):
        """创建分隔线"""
        if color is None:
            color = colors.HexColor('#e5e7eb')
        return HRFlowable(width="100%", thickness=1, lineCap='round', color=color)

    def generate_report(self, summaries, output_path=None):
        """Generate beautifully formatted PDF report"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"ai_podcast_report_{timestamp}.pdf"

        # 使用更好的页面设置
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
        title = "AI科技播客每日内容纪要"
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 10))

        # 头部信息表格
        header_table = self.create_header_table(len(summaries))
        story.append(header_table)
        story.append(Spacer(1, 20))

        # 统计信息
        if summaries:
            stats_text = f"📊 本期共收录 {len(summaries)} 个优质科技视频内容"
            story.append(Paragraph(stats_text, self.stats_style))

        story.append(Spacer(1, 20))
        story.append(self.create_divider(colors.HexColor('#3b82f6')))
        story.append(Spacer(1, 20))

        # 处理每个视频摘要
        for i, summary in enumerate(summaries, 1):
            # 视频序号和标题
            video_title = f"{i:02d}. {summary['title']}"
            story.append(Paragraph(video_title, self.video_title_style))

            # 频道信息
            channel_info = f"📺 {summary['channel']}"
            story.append(Paragraph(channel_info, self.channel_style))

            # 视频链接
            link_text = f"🔗 <a href='{summary['url']}'>{summary['url']}</a>"
            story.append(Paragraph(link_text, self.link_style))

            # 内容类型标识（如果有）
            if 'content_type' in summary and summary['content_type']:
                content_type_text = f"📋 内容来源: {summary['content_type']}"
                story.append(Paragraph(content_type_text, self.channel_style))

            story.append(Spacer(1, 8))

            # 摘要内容
            if summary['summary'] and summary['summary'].strip():
                # 清理和格式化摘要内容
                clean_summary = summary['summary'].replace('\n\n', '<br/><br/>').replace('\n', '<br/>')
                story.append(Paragraph(clean_summary, self.content_style))
            else:
                error_text = "❌ 内容纪要生成失败或无可用内容"
                story.append(Paragraph(error_text, self.content_style))

            # 视频间分隔
            story.append(Spacer(1, 15))
            if i < len(summaries):  # 不是最后一个视频
                story.append(self.create_divider())
                story.append(Spacer(1, 15))

            # 每页最多2个视频
            if i % 2 == 0 and i < len(summaries):
                story.append(PageBreak())

        # 报告结尾
        story.append(Spacer(1, 30))
        story.append(self.create_divider(colors.HexColor('#6366f1')))
        story.append(Spacer(1, 15))

        # 页脚信息
        footer_text = f"📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 🤖 由AI智能生成"
        story.append(Paragraph(footer_text, self.footer_style))

        try:
            doc.build(story)
            print(f"Enhanced PDF report generated: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error generating enhanced PDF: {e}")
            return None