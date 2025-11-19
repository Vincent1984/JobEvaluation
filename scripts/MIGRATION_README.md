# 数据库迁移说明

## 概述

此迁移脚本将数据库升级到支持企业管理和分类标签的新schema。

## 新增功能

### 1. 企业管理（Companies）
- 新增 `companies` 表
- 支持创建和管理多个企业
- 每个企业拥有独立的职位分类体系

### 2. 分类标签（Category Tags）
- 新增 `category_tags` 表
- 支持为第三层级分类添加标签
- 标签类型包括：战略重要性、业务价值、技能稀缺性、市场竞争度、发展潜力、风险等级

### 3. 职位分类增强
- `job_categories` 表新增 `company_id` 字段
- 分类现在关联到特定企业
- 新增 `updated_at` 字段用于跟踪更新时间

### 4. 评估结果增强
- `evaluation_results` 表新增以下字段：
  - `company_value`: 企业价值评级（高价值/中价值/低价值）
  - `is_core_position`: 是否核心岗位（布尔值）
  - `dimension_contributions`: 三个维度的贡献度百分比（JSON）
  - `is_manually_modified`: 是否手动修改过（布尔值）
  - `manual_modifications`: 修改历史记录（JSON数组）
  - `updated_at`: 更新时间

### 5. 索引优化
新增以下索引以提升查询性能：
- `idx_categories_company`: 按企业查询分类
- `idx_categories_level`: 按层级查询分类
- `idx_categories_parent`: 按父级查询分类
- `idx_tags_category`: 按分类查询标签
- `idx_evaluation_jd`: 按JD查询评估结果
- `idx_evaluation_company_value`: 按企业价值查询评估结果
- `idx_evaluation_core_position`: 按核心岗位查询评估结果

## 使用方法

### 执行迁移

```bash
# 使用默认数据库路径
python scripts/migrate_db.py

# 指定数据库路径
python scripts/migrate_db.py --db-path /path/to/database.db
```

### 查看帮助

```bash
python scripts/migrate_db.py --help
```

### 回滚迁移（仅用于开发测试）

```bash
python scripts/migrate_db.py --rollback --db-path /path/to/database.db
```

**警告**: 回滚操作将删除新添加的表和数据，请谨慎使用！

## 迁移过程

迁移脚本会自动执行以下步骤：

1. **创建新表**
   - 创建 `companies` 表
   - 创建 `category_tags` 表

2. **更新现有数据**
   - 创建"默认企业"
   - 将所有现有分类关联到默认企业
   - 为 `job_categories` 表添加 `company_id` 和 `updated_at` 字段

3. **更新评估结果表**
   - 为 `evaluation_results` 表添加综合评估相关字段

4. **创建索引**
   - 创建所有必要的索引以优化查询性能

## 数据兼容性

- **现有分类**: 所有现有的职位分类会自动关联到"默认企业"
- **现有JD**: 所有现有的JD数据保持不变
- **现有评估结果**: 所有现有的评估结果保持不变，新字段默认为NULL或默认值

## 迁移后操作

迁移完成后，您可以：

1. 通过企业管理页面创建新企业
2. 为第三层级分类添加标签
3. 使用综合评估功能（整合JD内容、评估模板、分类标签三个维度）
4. 手动修改评估结果并记录修改历史

## 测试

运行测试脚本验证迁移：

```bash
python test_database_migration.py
```

测试脚本会验证：
- 企业表创建和管理
- 分类标签表创建和管理
- 职位分类关联企业
- 评估结果综合评估字段
- 评估结果手动修改支持
- 关系和级联删除
- 索引创建

## 故障排除

### 问题：迁移失败

**解决方案**:
1. 检查数据库文件路径是否正确
2. 确保数据库文件没有被其他进程占用
3. 检查是否有足够的磁盘空间
4. 查看错误信息并根据提示操作

### 问题：索引创建失败

**解决方案**:
- 索引可能已经存在，这是正常的
- 脚本会自动跳过已存在的索引

### 问题：列已存在错误

**解决方案**:
- 脚本会检查列是否存在，自动跳过已存在的列
- 如果仍然出错，可能是数据库已经部分迁移，可以安全忽略

## 备份建议

在执行迁移前，建议备份数据库文件：

```bash
# Linux/Mac
cp data/jd_analyzer.db data/jd_analyzer.db.backup

# Windows
copy data\jd_analyzer.db data\jd_analyzer.db.backup
```

## 相关需求

此迁移实现了以下需求：
- 需求 3.1-3.10: 企业管理
- 需求 4.1-4.14: 职位分类体系管理和分类标签
- 需求 2.29-2.33: 评估结果手动修改支持

## 版本信息

- **迁移版本**: 1.0
- **创建日期**: 2025-01-18
- **兼容性**: SQLite 3.x
