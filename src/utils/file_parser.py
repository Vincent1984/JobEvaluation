"""文件解析工具"""

import io
import asyncio
import logging
from typing import Optional, List, Tuple, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class FileParserService:
    """
    文件解析服务 - 支持多种格式的JD文件解析（优化版）
    
    支持的格式：
    - TXT: 支持UTF-8、GBK、GB2312等编码
    - PDF: 使用PyPDF2解析
    - DOCX: 使用python-docx解析
    - DOC: 使用textract解析（可选）
    
    优化特性：
    - 并行文件解析
    - 线程池复用
    - 内存优化
    """
    
    # 支持的文件格式映射
    SUPPORTED_FORMATS = {
        '.txt': 'parse_txt',
        '.pdf': 'parse_pdf',
        '.docx': 'parse_docx',
        '.doc': 'parse_doc'
    }
    
    # 文件大小限制
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_BATCH_SIZE = 20  # 最多20个文件
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 总计100MB
    
    # 线程池（用于CPU密集型解析任务）
    _executor = ThreadPoolExecutor(max_workers=4)
    
    @staticmethod
    def parse_txt(file_content: bytes) -> str:
        """
        解析TXT文件 - 支持多种编码
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            解析后的文本内容
            
        Raises:
            ValueError: 无法识别文件编码
        """
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        
        for encoding in encodings:
            try:
                return file_content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        raise ValueError("无法识别文件编码")
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """
        解析PDF文件
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            解析后的文本内容
            
        Raises:
            ImportError: PyPDF2未安装
            ValueError: PDF解析失败
        """
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("需要安装PyPDF2库: pip install PyPDF2")
        
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF解析失败: {str(e)}")
    
    @staticmethod
    def parse_docx(file_content: bytes) -> str:
        """
        解析DOCX文件
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            解析后的文本内容
            
        Raises:
            ImportError: python-docx未安装
            ValueError: DOCX解析失败
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError("需要安装python-docx库: pip install python-docx")
        
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX解析失败: {str(e)}")
    
    @staticmethod
    def parse_doc(file_content: bytes) -> str:
        """
        解析DOC文件（旧版Word）- 可选功能
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            解析后的文本内容
            
        Raises:
            ImportError: textract未安装
            ValueError: DOC解析失败
        """
        try:
            import textract
        except ImportError:
            raise ImportError("需要安装textract库: pip install textract")
        
        try:
            text = textract.process(io.BytesIO(file_content))
            return text.decode('utf-8')
        except Exception as e:
            raise ValueError(f"DOC解析失败: {str(e)}")
    
    @classmethod
    def parse_file(cls, file_content: bytes, filename: str) -> str:
        """
        根据文件扩展名自动选择解析方法
        
        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            
        Returns:
            解析后的文本内容
            
        Raises:
            ValueError: 不支持的文件格式或解析失败
        """
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的文件格式: {file_ext}。"
                f"支持的格式: {', '.join(cls.SUPPORTED_FORMATS.keys())}"
            )
        
        parser_method = getattr(cls, cls.SUPPORTED_FORMATS[file_ext])
        return parser_method(file_content)
    
    @classmethod
    async def parse_file_async(cls, file_content: bytes, filename: str) -> str:
        """
        异步解析文件（使用线程池避免阻塞）
        
        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            
        Returns:
            解析后的文本内容
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            cls._executor,
            cls.parse_file,
            file_content,
            filename
        )
    
    @classmethod
    async def parse_files_parallel(
        cls,
        files: List[Tuple[bytes, str]],
        max_concurrent: int = 4
    ) -> List[Dict[str, Any]]:
        """
        并行解析多个文件
        
        Args:
            files: 文件列表 [(file_content, filename), ...]
            max_concurrent: 最大并发数
            
        Returns:
            解析结果列表 [{"filename": str, "text": str, "success": bool}, ...]
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def parse_with_semaphore(file_content: bytes, filename: str):
            async with semaphore:
                try:
                    text = await cls.parse_file_async(file_content, filename)
                    return {
                        "filename": filename,
                        "text": text,
                        "success": True
                    }
                except Exception as e:
                    logger.error(f"文件解析失败: {filename}, {e}")
                    return {
                        "filename": filename,
                        "error": str(e),
                        "success": False
                    }
        
        tasks = [
            parse_with_semaphore(content, name)
            for content, name in files
        ]
        
        return await asyncio.gather(*tasks)
    
    @classmethod
    def validate_file(cls, file_size: int, filename: str) -> Tuple[bool, str]:
        """
        验证单个文件
        
        Args:
            file_size: 文件大小（字节）
            filename: 文件名
            
        Returns:
            (是否验证通过, 错误信息或"验证通过")
        """
        # 检查文件大小
        if file_size > cls.MAX_FILE_SIZE:
            max_size_mb = cls.MAX_FILE_SIZE / 1024 / 1024
            return False, f"文件大小超过限制({max_size_mb}MB)"
        
        # 检查文件格式
        file_ext = Path(filename).suffix.lower()
        if file_ext not in cls.SUPPORTED_FORMATS:
            supported = ', '.join(cls.SUPPORTED_FORMATS.keys())
            return False, f"不支持的文件格式: {file_ext}。支持的格式: {supported}"
        
        return True, "验证通过"
    
    @classmethod
    def validate_batch(cls, files: List[Tuple[int, str]]) -> Tuple[bool, str]:
        """
        验证批量上传
        
        Args:
            files: 文件列表，每个元素为 (文件大小, 文件名)
            
        Returns:
            (是否验证通过, 错误信息或"验证通过")
        """
        # 检查文件数量
        if len(files) > cls.MAX_BATCH_SIZE:
            return False, f"文件数量超过限制({cls.MAX_BATCH_SIZE}个)"
        
        # 检查总大小
        total_size = sum(size for size, _ in files)
        if total_size > cls.MAX_TOTAL_SIZE:
            max_total_mb = cls.MAX_TOTAL_SIZE / 1024 / 1024
            return False, f"总文件大小超过限制({max_total_mb}MB)"
        
        # 检查每个文件
        for file_size, filename in files:
            is_valid, error_msg = cls.validate_file(file_size, filename)
            if not is_valid:
                return False, f"文件 '{filename}': {error_msg}"
        
        return True, "验证通过"
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """
        获取支持的文件格式列表
        
        Returns:
            支持的文件扩展名列表
        """
        return list(cls.SUPPORTED_FORMATS.keys())
    
    @classmethod
    def is_format_supported(cls, filename: str) -> bool:
        """
        检查文件格式是否支持
        
        Args:
            filename: 文件名
            
        Returns:
            是否支持该格式
        """
        file_ext = Path(filename).suffix.lower()
        return file_ext in cls.SUPPORTED_FORMATS


# 向后兼容的别名
class FileParser(FileParserService):
    """向后兼容的别名"""
    pass


# 全局文件解析器实例
file_parser = FileParserService()
