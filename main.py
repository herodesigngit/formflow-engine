import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, Any
from src.pdf_processor import PDFAutomationEngine

app = FastAPI(
    title="Enterprise PDF Automation API",
    description="High-volume JSON-to-PDF Mapping & Flattening Service",
    version="1.0.0"
)

# تعاریف مسیرها
TEMPLATE_DIR = os.path.abspath("templates")
OUTPUT_DIR = os.path.abspath("storage/output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# مقداردهی اولیه موتور پردازشگر
engine = PDFAutomationEngine(template_dir=TEMPLATE_DIR, output_dir=OUTPUT_DIR)

# ساختار اعتبارسنجی داده‌های ورودی با Pydantic
class PDFRequestModel(BaseModel):
    template_name: str = Field(..., example="W4_Form_Template.pdf", description="نام فایل تمپلیت موجود در سرور")
    payload: Dict[str, Any] = Field(..., example={"First Name": "Farbod", "Last Name": "Ahmadi"}, description="داده‌های نگاشت شده برای فرم")

def clean_up_file(file_path: str):
    """حذف فایل از روی سرور پس از ارسال به مشتری برای مدیریت فضای دیسک"""
    if os.path.exists(file_path):
        os.remove(file_path)

@app.post("/api/v1/generate-pdf", summary="پر کردن خودکار فرم PDF از روی داده‌های JSON")
async def generate_pdf(request: PDFRequestModel, background_tasks: BackgroundTasks):
    try:
        output_filename = f"completed_{request.template_name.split('.')[0]}_{os.urandom(4).hex()}.pdf"
        
        # اجرای ماژول پردازش به صورت کاملاً Async
        file_path = await engine.fill_pdf_form(
            template_name=request.template_name,
            data=request.payload,
            output_filename=output_filename
        )
        
        # اضافه کردن تسک پاک‌سازی حافظه سرور در بک‌گراند پس از اتمام دانلود
        background_tasks.add_task(clean_up_file, file_path)
        
        return FileResponse(
            path=file_path, 
            filename=output_filename, 
            media_type="application/pdf"
        )

    except FileNotFoundError as fnf:
        raise HTTPException(status_code=404, detail=str(fnf))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")