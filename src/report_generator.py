"""
PDF report generator for podcast summaries
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_chinese_font()

    def setup_chinese_font(self):
        """Setup Chinese font support"""
        try:
            # Try to register a Chinese font (you may need to adjust the path)
            font_paths = [
                'C:/Windows/Fonts/simsun.ttc',  # Windows SimSun
                'C:/Windows/Fonts/msyh.ttc',    # Windows Microsoft YaHei
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # Linux fallback
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Chinese', font_path))
                    break
            else:
                print("Warning: No Chinese font found, using default font")

        except Exception as e:
            print(f"Warning: Could not setup Chinese font: {e}")

        # Create custom styles with Chinese font
        self.title_style = ParagraphStyle(
            'ChineseTitle',
            parent=self.styles['Title'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=16,
            spaceAfter=20
        )

        self.heading_style = ParagraphStyle(
            'ChineseHeading',
            parent=self.styles['Heading2'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=14,
            spaceAfter=10
        )

        self.body_style = ParagraphStyle(
            'ChineseBody',
            parent=self.styles['Normal'],
            fontName='Chinese' if 'Chinese' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=10,
            spaceAfter=8,
            leftIndent=20
        )

    def generate_report(self, summaries, output_path=None):
        """Generate PDF report from summaries"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"podcast_summary_{timestamp}.pdf"

        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)

        story = []

        # Title
        title = f"AI科技播客每日摘要 - {datetime.now().strftime('%Y年%m月%d日')}"
        story.append(Paragraph(title, self.title_style))
        story.append(Spacer(1, 20))

        # Summary count
        summary_info = f"本日共处理 {len(summaries)} 个视频"
        story.append(Paragraph(summary_info, self.heading_style))
        story.append(Spacer(1, 10))

        # Process each summary
        for i, summary in enumerate(summaries, 1):
            # Video title and channel
            video_header = f"{i}. 【{summary['channel']}】{summary['title']}"
            story.append(Paragraph(video_header, self.heading_style))

            # Video URL
            url_text = f"视频链接: {summary['url']}"
            story.append(Paragraph(url_text, self.body_style))
            story.append(Spacer(1, 5))

            # Summary content
            if summary['summary']:
                story.append(Paragraph(summary['summary'], self.body_style))
            else:
                story.append(Paragraph("摘要生成失败", self.body_style))

            story.append(Spacer(1, 15))

            # Add page break after every 3 summaries (except the last one)
            if i % 3 == 0 and i < len(summaries):
                story.append(PageBreak())

        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(footer_text, self.body_style))

        try:
            doc.build(story)
            print(f"PDF report generated successfully: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return None