class PDFAutomationException(Exception):
    """خطای پایه برای تمام خطاهای مربوط به اتوماسیون PDF"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class TemplateNotFoundError(PDFAutomationException):
    """زمانی رخ می‌دهد که فایل قالب PDF روی سرور پیدا نشود"""
    def __init__(self, template_name: str):
        super().__init__(f"Template '{template_name}' not found on the server.", status_code=404)

class PDFProcessingError(PDFAutomationException):
    """زمانی رخ می‌دهد که عملیات نگاشت یا Flatten کردن با خطا مواجه شود"""
    def __init__(self, details: str):
        super().__init__(f"Failed to process and flatten PDF: {details}", status_code=422)