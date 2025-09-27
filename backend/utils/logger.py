import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class PPTLogger:
    """PPT系统日志管理器"""
    
    def __init__(self, name='ppt_system'):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self._setup_logger()
    
    def _setup_logger(self):
        """设置日志配置"""
        self.logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'log')
        os.makedirs(log_dir, exist_ok=True)
        
        # 文件处理器
        log_file = os.path.join(log_dir, 'ppt_system.log')
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        """记录信息日志"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message, **kwargs):
        """记录警告日志"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message, **kwargs):
        """记录错误日志"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def debug(self, message, **kwargs):
        """记录调试日志"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def log_file_operation(self, operation, file_path, status='success', error_msg=None, **kwargs):
        """记录文件操作日志"""
        message = f"文件操作: {operation} - 路径: {file_path} - 状态: {status}"
        if error_msg:
            message += f" - 错误: {error_msg}"
        
        if status == 'success':
            self.info(message, **kwargs)
        else:
            self.error(message, **kwargs)
    
    def log_ppt_generation(self, input_content_preview, page_count, model, status='start', 
                          template_path=None, result_file=None, error_msg=None, **kwargs):
        """记录PPT生成日志"""
        content_preview = input_content_preview[:100] + '...' if len(input_content_preview) > 100 else input_content_preview
        
        message = f"PPT生成 - 状态: {status} - 内容预览: {content_preview} - 页数: {page_count} - 模型: {model}"
        
        if template_path:
            message += f" - 模板: {os.path.basename(template_path)}"
        if result_file:
            message += f" - 结果文件: {os.path.basename(result_file)}"
        if error_msg:
            message += f" - 错误: {error_msg}"
        
        if status in ['start', 'success']:
            self.info(message, **kwargs)
        else:
            self.error(message, **kwargs)
    
    def log_upload(self, filename, file_size, status='success', error_msg=None, **kwargs):
        """记录文件上传日志"""
        message = f"文件上传 - 文件名: {filename} - 大小: {file_size} 字节 - 状态: {status}"
        if error_msg:
            message += f" - 错误: {error_msg}"
        
        if status == 'success':
            self.info(message, **kwargs)
        else:
            self.error(message, **kwargs)
    
    def _format_message(self, message, **kwargs):
        """格式化日志消息"""
        if kwargs:
            extra_info = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            return f"{message} | {extra_info}"
        return message

# 创建全局日志实例
ppt_logger = PPTLogger()