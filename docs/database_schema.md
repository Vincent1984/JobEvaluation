# 数据库Schema文档

## 概述

岗位JD分析器使用SQLite数据库（通过aiosqlite异步驱动）存储所有数据。数据库采用SQLAlchemy ORM进行管理，支持完整的关系映射和数据验证。

## 数据库配置

- **数据库类型**: SQLite
- **驱动**: aiosqlite (异步)
- **ORM**: SQLAlchemy 2.0+
- **数据库文件**: `./data/jd_analyzer.db`
- **连接字符串**: `sqlite+aiosqlite:///./data/jd_analyzer.db`

## 表结构

### 1. job_categories (职位分类表)

支持3层级的职位分类体系，用于组织和管理职位JD。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 分类唯一标识 |
| name | String(200) | NOT NULL | 分类名称 |
| level | Integer | NOT NULL | 分类层级 (1-3) |
| parent_id | String(50) | FOREIGN KEY | 父级分类ID，指向job_categories.id |
| description | Text | NULLABLE | 分类描述 |
| sample_jd_ids | JSON | DEFAULT [] | 样本JD的ID列表（仅第三层级，1-2个） |
| created_at | DateTime | DEFAULT now() | 创建时间 |

**关系**:
- 自引用关系：parent_id -> job_categories.id
- 一对多关系：一个分类可以有多个子分类

**业务规则**:
- 一级分类：parent_id 必须为 NULL
- 二级分类：parent_id 必须指向一级分类
- 三级分类：parent_id 必须指向二级分类，可以包含1-2个样本JD
- 样本JD仅用于第三层级分类，用于提高自动分类的准确性

**示例数据**:
```sql
-- 一级分类
INSERT INTO job_categories (id, name, level, parent_id, description) 
VALUES ('cat_tech', '技术类', 1, NULL, '技术相关职位');

-- 二级分类
INSERT INTO job_categories (id, name, level, parent_id, description) 
VALUES ('cat_dev', '研发', 2, 'cat_tech', '软件研发相关职位');

-- 三级分类（带样本JD）
INSERT INTO job_categories (id, name, level, parent_id, description, sample_jd_ids) 
VALUES ('cat_backend', '后端工程师', 3, 'cat_dev', '后端开发工程师', '["jd_001", "jd_002"]');
```

### 2. job_descriptions (岗位JD表)

存储职位描述的完整信息，包括结构化数据和原始文本。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | JD唯一标识 |
| job_title | String(200) | NOT NULL | 职位标题 |
| department | String(200) | NULLABLE | 部门 |
| location | String(200) | NULLABLE | 工作地点 |
| responsibilities | JSON | DEFAULT [] | 职责列表 |
| required_skills | JSON | DEFAULT [] | 必备技能列表 |
| preferred_skills | JSON | DEFAULT [] | 优选技能列表 |
| qualifications | JSON | DEFAULT [] | 任职资格列表 |
| custom_fields | JSON | DEFAULT {} | 自定义字段 |
| raw_text | Text | NOT NULL | 原始JD文本 |
| category_level1_id | String(50) | FOREIGN KEY | 一级分类ID |
| category_level2_id | String(50) | FOREIGN KEY | 二级分类ID |
| category_level3_id | String(50) | FOREIGN KEY | 三级分类ID |
| created_at | DateTime | DEFAULT now() | 创建时间 |
| updated_at | DateTime | DEFAULT now() | 更新时间 |

**关系**:
- 多对一关系：category_level1_id -> job_categories.id
- 多对一关系：category_level2_id -> job_categories.id
- 多对一关系：category_level3_id -> job_categories.id
- 一对多关系：一个JD可以有多个评估结果、问卷、匹配结果

### 3. evaluation_results (评估结果表)

存储JD质量评估的结果。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 评估结果唯一标识 |
| jd_id | String(50) | FOREIGN KEY, NOT NULL | 关联的JD ID |
| evaluation_model_type | String(50) | NOT NULL | 评估模型类型 |
| overall_score | Float | NOT NULL | 综合质量分数 (0-100) |
| completeness | Float | NOT NULL | 完整性分数 (0-100) |
| clarity | Float | NOT NULL | 清晰度分数 (0-100) |
| professionalism | Float | NOT NULL | 专业性分数 (0-100) |
| issues | JSON | DEFAULT [] | 质量问题列表 |
| position_value | JSON | NULLABLE | 岗位价值评估 |
| recommendations | JSON | DEFAULT [] | 优化建议列表 |
| created_at | DateTime | DEFAULT now() | 创建时间 |

**关系**:
- 多对一关系：jd_id -> job_descriptions.id

**评估模型类型**:
- `standard`: 标准评估
- `mercer_ipe`: 美世国际职位评估法
- `factor_comparison`: 因素比较法

### 4. questionnaires (问卷表)

存储基于JD生成的评估问卷。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 问卷唯一标识 |
| jd_id | String(50) | FOREIGN KEY, NOT NULL | 关联的JD ID |
| title | String(500) | NOT NULL | 问卷标题 |
| description | Text | NULLABLE | 问卷描述 |
| questions | JSON | DEFAULT [] | 问题列表 |
| evaluation_model | String(50) | NOT NULL | 评估模型 |
| share_link | String(500) | NULLABLE | 分享链接 |
| created_at | DateTime | DEFAULT now() | 创建时间 |

**关系**:
- 多对一关系：jd_id -> job_descriptions.id
- 一对多关系：一个问卷可以有多个回答

### 5. questionnaire_responses (问卷回答表)

存储候选人或在职员工填写的问卷回答。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 回答唯一标识 |
| questionnaire_id | String(50) | FOREIGN KEY, NOT NULL | 关联的问卷ID |
| respondent_name | String(200) | NULLABLE | 填写人姓名 |
| answers | JSON | DEFAULT {} | 答案字典 (question_id -> answer) |
| submitted_at | DateTime | DEFAULT now() | 提交时间 |

**关系**:
- 多对一关系：questionnaire_id -> questionnaires.id
- 一对多关系：一个回答可以有多个匹配结果

### 6. match_results (匹配结果表)

存储候选人与岗位的匹配度评估结果。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 匹配结果唯一标识 |
| jd_id | String(50) | FOREIGN KEY, NOT NULL | 关联的JD ID |
| response_id | String(50) | FOREIGN KEY, NOT NULL | 关联的问卷回答ID |
| overall_score | Float | NOT NULL | 综合匹配度分数 (0-100) |
| dimension_scores | JSON | DEFAULT {} | 各维度得分 |
| strengths | JSON | DEFAULT [] | 优势列表 |
| gaps | JSON | DEFAULT [] | 差距列表 |
| recommendations | JSON | DEFAULT [] | 建议列表 |
| created_at | DateTime | DEFAULT now() | 创建时间 |

**关系**:
- 多对一关系：jd_id -> job_descriptions.id
- 多对一关系：response_id -> questionnaire_responses.id

### 7. custom_templates (自定义模板表)

存储用户自定义的解析、评估和问卷模板。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | String(50) | PRIMARY KEY | 模板唯一标识 |
| name | String(200) | NOT NULL | 模板名称 |
| template_type | String(50) | NOT NULL | 模板类型 |
| config | JSON | DEFAULT {} | 模板配置 |
| created_at | DateTime | DEFAULT now() | 创建时间 |

**模板类型**:
- `parsing`: 解析模板
- `evaluation`: 评估模板
- `questionnaire`: 问卷模板

## 关系图

```
job_categories (自引用)
    ↓ (parent_id)
job_categories
    ↓ (category_level1_id, category_level2_id, category_level3_id)
job_descriptions
    ↓ (jd_id)
    ├── evaluation_results
    ├── questionnaires
    │       ↓ (questionnaire_id)
    │   questionnaire_responses
    │       ↓ (response_id)
    └── match_results
```

## 初始化和管理

### 初始化数据库

```bash
# 使用初始化脚本
python scripts/init_db.py

# 选项：
# 1. 初始化数据库（创建表）
# 2. 重置数据库（删除并重建所有表）
# 3. 创建示例数据
```

### 验证数据库Schema

```bash
# 运行验证脚本
python scripts/verify_db_schema.py
```

### 编程方式使用

```python
from src.core.database import init_db, get_db
from src.models.database import JobDescriptionDB

# 初始化数据库
await init_db()

# 使用数据库会话
async with get_db() as db:
    # 创建JD
    jd = JobDescriptionDB(
        id="jd_001",
        job_title="Python工程师",
        raw_text="招聘Python工程师...",
        # ... 其他字段
    )
    db.add(jd)
    await db.commit()
```

## 索引建议

为提高查询性能，建议在以下字段上创建索引：

```sql
-- JD表索引
CREATE INDEX idx_jd_category_l1 ON job_descriptions(category_level1_id);
CREATE INDEX idx_jd_category_l2 ON job_descriptions(category_level2_id);
CREATE INDEX idx_jd_category_l3 ON job_descriptions(category_level3_id);
CREATE INDEX idx_jd_created_at ON job_descriptions(created_at);

-- 分类表索引
CREATE INDEX idx_category_parent ON job_categories(parent_id);
CREATE INDEX idx_category_level ON job_categories(level);

-- 评估结果索引
CREATE INDEX idx_eval_jd ON evaluation_results(jd_id);
CREATE INDEX idx_eval_created_at ON evaluation_results(created_at);

-- 问卷索引
CREATE INDEX idx_quest_jd ON questionnaires(jd_id);

-- 匹配结果索引
CREATE INDEX idx_match_jd ON match_results(jd_id);
CREATE INDEX idx_match_response ON match_results(response_id);
```

## 数据迁移

当需要修改数据库结构时，建议使用Alembic进行版本管理：

```bash
# 安装Alembic
pip install alembic

# 初始化Alembic
alembic init alembic

# 创建迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 备份和恢复

```bash
# 备份数据库
cp data/jd_analyzer.db data/jd_analyzer_backup_$(date +%Y%m%d).db

# 恢复数据库
cp data/jd_analyzer_backup_20240101.db data/jd_analyzer.db
```

## 注意事项

1. **JSON字段**: SQLite的JSON字段存储为TEXT，查询时需要使用JSON函数
2. **外键约束**: SQLite默认不启用外键约束，需要在连接时启用：`PRAGMA foreign_keys = ON`
3. **并发**: SQLite支持多读单写，高并发场景建议使用PostgreSQL或MySQL
4. **事务**: 所有写操作应在事务中进行，确保数据一致性
5. **样本JD**: 第三层级分类的样本JD数量限制为1-2个，用于提高自动分类准确性
