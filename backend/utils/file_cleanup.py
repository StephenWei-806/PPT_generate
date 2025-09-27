import os
import time
import threading
from datetime import datetime, timedelta
from utils.logger import ppt_logger

class FileCleanupManager:
    """文件清理管理器"""
    
    def __init__(self):
        self.cleanup_thread = None
        self.running = False
        self.cleanup_interval = 3600  # 1小时清理一次
        self.file_max_age = 24 * 3600  # 文件最大保持24小时
        self.backend_root_path = None  # 初始化时设置
    
    def start_cleanup_service(self, backend_root_path):
        """启动文件清理服务"""
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            return
        
        self.running = True
        self.backend_root_path = backend_root_path
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_worker, 
            daemon=True,
            name="FileCleanupThread"
        )
        self.cleanup_thread.start()
        ppt_logger.info("文件清理服务已启动")
    
    def stop_cleanup_service(self):
        """停止文件清理服务"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        ppt_logger.info("文件清理服务已停止")
    
    def _cleanup_worker(self):
        """清理工作线程"""
        while self.running:
            try:
                self.cleanup_temp_files()
                time.sleep(self.cleanup_interval)
            except Exception as e:
                ppt_logger.error(f"文件清理线程异常: {str(e)}")
                time.sleep(60)  # 异常时等待1分钟再重试
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        current_time = time.time()
        cleanup_paths = [
            os.path.join(self.backend_root_path, 'temp', 'uploads'),
            os.path.join(self.backend_root_path, 'temp', 'generated')
        ]
        
        total_cleaned = 0
        total_size_cleaned = 0
        
        for cleanup_path in cleanup_paths:
            if not os.path.exists(cleanup_path):
                continue
            
            try:
                cleaned_count, cleaned_size = self._cleanup_directory(cleanup_path, current_time)
                total_cleaned += cleaned_count
                total_size_cleaned += cleaned_size
            except Exception as e:
                ppt_logger.error(f"清理目录失败: {cleanup_path} - 错误: {str(e)}")
        
        if total_cleaned > 0:
            ppt_logger.info(f"文件清理完成 - 清理文件数: {total_cleaned} - 清理大小: {self._format_size(total_size_cleaned)}")
    
    def _cleanup_directory(self, directory_path, current_time):
        """清理指定目录"""
        cleaned_count = 0
        cleaned_size = 0
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # 只处理文件，跳过目录
            if not os.path.isfile(file_path):
                continue
            
            try:
                # 检查文件年龄
                file_mtime = os.path.getmtime(file_path)
                file_age = current_time - file_mtime
                
                if file_age > self.file_max_age:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned_count += 1
                    cleaned_size += file_size
                    ppt_logger.debug(f"清理过期文件: {file_path} - 年龄: {self._format_time(file_age)}")
                    
            except Exception as e:
                ppt_logger.warning(f"清理文件失败: {file_path} - 错误: {str(e)}")
        
        return cleaned_count, cleaned_size
    
    def cleanup_file(self, file_path):
        """清理指定文件"""
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            ppt_logger.log_file_operation('清理文件', file_path, 'success')
            ppt_logger.debug(f"手动清理文件: {file_path} - 大小: {self._format_size(file_size)}")
            return True
        except Exception as e:
            ppt_logger.log_file_operation('清理文件', file_path, 'failed', str(e))
            return False
    
    def cleanup_old_files_now(self, max_age_hours=1):
        """立即清理超过指定小时数的文件"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleanup_paths = [
            os.path.join(self.backend_root_path, 'temp', 'uploads'),
            os.path.join(self.backend_root_path, 'temp', 'generated')
        ]
        
        total_cleaned = 0
        total_size_cleaned = 0
        
        for cleanup_path in cleanup_paths:
            if not os.path.exists(cleanup_path):
                continue
            
            for filename in os.listdir(cleanup_path):
                file_path = os.path.join(cleanup_path, filename)
                
                if not os.path.isfile(file_path):
                    continue
                
                try:
                    file_mtime = os.path.getmtime(file_path)
                    file_age = current_time - file_mtime
                    
                    if file_age > max_age_seconds:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_cleaned += 1
                        total_size_cleaned += file_size
                        ppt_logger.debug(f"立即清理文件: {file_path}")
                        
                except Exception as e:
                    ppt_logger.warning(f"立即清理文件失败: {file_path} - 错误: {str(e)}")
        
        if total_cleaned > 0:
            ppt_logger.info(f"立即清理完成 - 清理文件数: {total_cleaned} - 清理大小: {self._format_size(total_size_cleaned)}")
        
        return total_cleaned, total_size_cleaned
    
    def get_temp_files_info(self):
        """获取临时文件信息"""
        if not self.backend_root_path:
            return {
                'uploads': {'count': 0, 'size': 0, 'files': []},
                'generated': {'count': 0, 'size': 0, 'files': []}
            }
            
        info = {
            'uploads': {'count': 0, 'size': 0, 'files': []},
            'generated': {'count': 0, 'size': 0, 'files': []}
        }
        
        temp_dirs = {
            'uploads': os.path.join(self.backend_root_path, 'temp', 'uploads'),
            'generated': os.path.join(self.backend_root_path, 'temp', 'generated')
        }
        
        for dir_type, dir_path in temp_dirs.items():
            if not os.path.exists(dir_path):
                continue
            
            for filename in os.listdir(dir_path):
                file_path = os.path.join(dir_path, filename)
                
                if os.path.isfile(file_path):
                    try:
                        file_size = os.path.getsize(file_path)
                        file_mtime = os.path.getmtime(file_path)
                        file_age = time.time() - file_mtime
                        
                        info[dir_type]['count'] += 1
                        info[dir_type]['size'] += file_size
                        info[dir_type]['files'].append({
                            'name': filename,
                            'size': file_size,
                            'age_hours': file_age / 3600,
                            'path': file_path
                        })
                    except Exception as e:
                        ppt_logger.warning(f"获取文件信息失败: {file_path} - 错误: {str(e)}")
        
        return info
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _format_time(self, seconds):
        """格式化时间"""
        if seconds < 60:
            return f"{int(seconds)}秒"
        elif seconds < 3600:
            return f"{int(seconds/60)}分钟"
        elif seconds < 86400:
            return f"{int(seconds/3600)}小时"
        else:
            return f"{int(seconds/86400)}天"

# 创建全局文件清理管理器实例
file_cleanup_manager = FileCleanupManager()