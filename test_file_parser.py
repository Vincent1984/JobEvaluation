"""测试文件解析服务"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.file_parser import FileParserService


def test_txt_parsing():
    """测试TXT文件解析"""
    print("测试TXT文件解析...")
    
    # UTF-8编码
    content_utf8 = "这是一个测试JD\n职位：Python开发工程师".encode('utf-8')
    result = FileParserService.parse_txt(content_utf8)
    assert "Python开发工程师" in result
    print("✓ UTF-8编码解析成功")
    
    # GBK编码
    content_gbk = "这是一个测试JD\n职位：Java开发工程师".encode('gbk')
    result = FileParserService.parse_txt(content_gbk)
    assert "Java开发工程师" in result
    print("✓ GBK编码解析成功")


def test_file_validation():
    """测试文件验证"""
    print("\n测试文件验证...")
    
    # 测试正常文件
    is_valid, msg = FileParserService.validate_file(1024, "test.txt")
    assert is_valid
    print(f"✓ 正常文件验证: {msg}")
    
    # 测试超大文件
    is_valid, msg = FileParserService.validate_file(20 * 1024 * 1024, "large.txt")
    assert not is_valid
    print(f"✓ 超大文件验证: {msg}")
    
    # 测试不支持的格式
    is_valid, msg = FileParserService.validate_file(1024, "test.xlsx")
    assert not is_valid
    print(f"✓ 不支持格式验证: {msg}")


def test_batch_validation():
    """测试批量验证"""
    print("\n测试批量验证...")
    
    # 测试正常批量
    files = [(1024, "test1.txt"), (2048, "test2.pdf"), (3072, "test3.docx")]
    is_valid, msg = FileParserService.validate_batch(files)
    assert is_valid
    print(f"✓ 正常批量验证: {msg}")
    
    # 测试超过数量限制
    files = [(1024, f"test{i}.txt") for i in range(25)]
    is_valid, msg = FileParserService.validate_batch(files)
    assert not is_valid
    print(f"✓ 超过数量限制验证: {msg}")
    
    # 测试超过总大小限制
    files = [(60 * 1024 * 1024, "large1.pdf"), (60 * 1024 * 1024, "large2.pdf")]
    is_valid, msg = FileParserService.validate_batch(files)
    assert not is_valid
    print(f"✓ 超过总大小限制验证: {msg}")


def test_format_support():
    """测试格式支持检查"""
    print("\n测试格式支持检查...")
    
    assert FileParserService.is_format_supported("test.txt")
    assert FileParserService.is_format_supported("test.pdf")
    assert FileParserService.is_format_supported("test.docx")
    assert FileParserService.is_format_supported("test.doc")
    assert not FileParserService.is_format_supported("test.xlsx")
    
    print("✓ 格式支持检查成功")
    
    supported = FileParserService.get_supported_formats()
    print(f"✓ 支持的格式: {', '.join(supported)}")


def test_parse_file_auto():
    """测试自动格式识别"""
    print("\n测试自动格式识别...")
    
    # 测试TXT
    content = "测试内容".encode('utf-8')
    result = FileParserService.parse_file(content, "test.txt")
    assert "测试内容" in result
    print("✓ TXT自动识别成功")
    
    # 测试不支持的格式
    try:
        FileParserService.parse_file(content, "test.xlsx")
        assert False, "应该抛出异常"
    except ValueError as e:
        print(f"✓ 不支持格式异常: {e}")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("文件解析服务测试")
    print("=" * 60)
    
    try:
        test_txt_parsing()
        test_file_validation()
        test_batch_validation()
        test_format_support()
        test_parse_file_auto()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
