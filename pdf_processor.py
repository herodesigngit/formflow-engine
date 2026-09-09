import os
import logging
from typing import Dict, Any
from pypdf import PdfReader, PdfWriter

# تنظیمات لاگر برای ردیابی خطاها در سیستم‌های بزرگ
logger = logging.getLogger("pdf_processor")
logging.basicConfig(level=logging.INFO)

class PDFAutomationEngine:
    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = template_dir
        self.output_dir = output_dir

    async def fill_pdf_form(self, template_name: str, data: Dict[str, Any], output_filename: str) -> str:
        """
        دریافت دیتای JSON (دیکشنری)، نگاشت روی فیلدهای PDF و تولید فایل Flatten شده.
        """
        template_path = os.path.join(self.template_dir, template_name)
        output_path = os.path.join(self.output_dir, output_filename)

        if not os.path.exists(template_path):
            logger.error(f"Template not found: {template_path}")
            raise FileNotFoundError(f"قالب PDF مورد نظر یافت نشد: {template_name}")

        try:
            reader = PdfReader(template_path)
            writer = PdfWriter()

            # کپی کردن تمام صفحات به نویسنده PDF
            for page in reader.pages:
                writer.add_page(page)

            # بررسی وجود فرم در PDF
            if reader.get_fields() is None:
                logger.warning(f"No interactive fields found in {template_name}")
            
            # پر کردن فیلدها (AcroForm)
            # آرگومان شماره ۳ (flags=1) فیلدها را Flatten (غیرقابل ویرایش) می‌کند
            writer.update_page_form_field_values(
                writer.pages[0], 
                data,
                flags=1  # Flatten the fields
            )

            # نوشتن فایل نهایی در دایرکتوری خروجی
            with open(output_path, "wb") as output_file:
                writer.write(output_file)

            logger.info(f"Successfully generated flattened PDF: {output_filename}")
            return output_path

        except Exception as e:
            logger.critical(f"Fail to process PDF: {str(e)}")
            raise RuntimeError(f"خطا در پردازش و اتوماسیون فایل PDF: {str(e)}")