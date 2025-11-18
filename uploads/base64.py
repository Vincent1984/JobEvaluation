# 确保正确导入
try:
    import base64
    print("Base64模块导入成功")
    
    # 测试编码
    data = b"Hello, World!"
    encoded_data = base64.b64encode(data)
    print("编码结果:", encoded_data.decode('utf-8'))
    
    # 测试解码
    decoded_data = base64.b64decode(encoded_data)
    print("解码结果:", decoded_data.decode('utf-8'))
    
except ImportError as e:
    print(f"导入错误: {e}")
except AttributeError as e:
    print(f"属性错误: {e}")