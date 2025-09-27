from werkzeug.utils import secure_filename
from flask import current_app
import os
import time
import shutil
from utils.logger import ppt_logger
from utils.file_cleanup import file_cleanup_manager


class PPTUploadService:
    """
    PPT模板文件上传服务
    负责处理PPT模板文件的上传、保存等功能
    """
    
    def __init__(self):
        """初始化上传服务"""
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.pptx'}
        self.allowed_mimes = {
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/octet-stream'  # 有些浏览器可能发送这个
        }
        self.max_filename_length = 255
    
    def _save_template(self, file):
        """
        保存上传的模板文件
        
        Args:
            file: Flask上传文件对象
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            OSError: 文件保存失败
        """
        if not file or not file.filename:
            raise ValueError("未选择文件或文件名为空")
        
        ppt_logger.info(f"收到模板文件上传 - 文件名: {file.filename}")
        
        # 保存文件
        try:
            file_path = self._save_file(file)
            ppt_logger.log_upload(
                file.filename,
                os.path.getsize(file_path) if file_path else 0,
                'success'
            )
            return file_path
        except Exception as e:
            ppt_logger.log_upload(file.filename, 0, 'failed', str(e))
            raise OSError(f'保存模板文件失败: {str(e)}')
    
    def _save_file(self, file):
        """
        保存上传的文件到临时目录
        
        Args:
            file: Flask上传文件对象
            
        Returns:
            str: 保存的文件路径
            
        Raises:
            OSError: 保存失败
            ValueError: 文件验证失败
        """
        # 生成安全的文件名
        timestamp = str(int(time.time()))
        secure_name = secure_filename(file.filename)
        
        # 确保文件名不为空
        if not secure_name:
            secure_name = "uploaded_template.pptx"
        
        filename = f"template_{timestamp}_{secure_name}"
        
        # 创建上传目录
        upload_dir = os.path.join(current_app.root_path, 'temp', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        try:
            file.save(file_path)
            ppt_logger.log_file_operation('保存上传文件', file_path, 'success')
        except Exception as e:
            ppt_logger.log_file_operation('保存上传文件', file_path, 'failed', str(e))
            raise
        
        return file_path
    
    def cleanup_file(self, file_path):
        """
        清理指定的临时文件
        
        Args:
            file_path: 要清理的文件路径
        """
        if file_path:
            file_cleanup_manager.cleanup_file(file_path)


# 创建全局实例
ppt_upload_service = PPTUploadService()