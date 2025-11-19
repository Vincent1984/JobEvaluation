"""共享存储模块（MVP版本 - 内存存储）"""

from typing import Dict
from ..models.schemas import Company, JobCategory, CategoryTag

# 企业存储
company_storage: Dict[str, Company] = {}

# 分类存储
category_storage: Dict[str, JobCategory] = {}

# 标签存储
tag_storage: Dict[str, CategoryTag] = {}
