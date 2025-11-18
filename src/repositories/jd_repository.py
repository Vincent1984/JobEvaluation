"""JD数据访问层"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.database import JobDescriptionDB, JobCategoryDB
from src.models.schemas import JobDescription


class JDRepository:
    """JD数据访问类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, jd: JobDescription) -> JobDescriptionDB:
        """创建JD"""
        db_jd = JobDescriptionDB(
            id=jd.id,
            job_title=jd.job_title,
            department=jd.department,
            location=jd.location,
            responsibilities=jd.responsibilities,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills,
            qualifications=jd.qualifications,
            custom_fields=jd.custom_fields,
            raw_text=jd.raw_text,
            category_level1_id=jd.category_level1_id,
            category_level2_id=jd.category_level2_id,
            category_level3_id=jd.category_level3_id,
            created_at=jd.created_at,
            updated_at=jd.updated_at
        )
        self.db.add(db_jd)
        self.db.commit()
        self.db.refresh(db_jd)
        return db_jd
    
    def get_by_id(self, jd_id: str) -> Optional[JobDescriptionDB]:
        """根据ID获取JD"""
        return self.db.query(JobDescriptionDB).filter(JobDescriptionDB.id == jd_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[JobDescriptionDB]:
        """获取所有JD"""
        return self.db.query(JobDescriptionDB).order_by(desc(JobDescriptionDB.created_at)).offset(skip).limit(limit).all()
    
    def get_by_category(self, category_id: str, level: int = 3) -> List[JobDescriptionDB]:
        """根据分类获取JD"""
        if level == 1:
            return self.db.query(JobDescriptionDB).filter(JobDescriptionDB.category_level1_id == category_id).all()
        elif level == 2:
            return self.db.query(JobDescriptionDB).filter(JobDescriptionDB.category_level2_id == category_id).all()
        else:
            return self.db.query(JobDescriptionDB).filter(JobDescriptionDB.category_level3_id == category_id).all()
    
    def update_category(self, jd_id: str, category_level1_id: Optional[str] = None,
                       category_level2_id: Optional[str] = None,
                       category_level3_id: Optional[str] = None) -> Optional[JobDescriptionDB]:
        """更新JD分类"""
        db_jd = self.get_by_id(jd_id)
        if db_jd:
            if category_level1_id is not None:
                db_jd.category_level1_id = category_level1_id
            if category_level2_id is not None:
                db_jd.category_level2_id = category_level2_id
            if category_level3_id is not None:
                db_jd.category_level3_id = category_level3_id
            self.db.commit()
            self.db.refresh(db_jd)
        return db_jd
    
    def delete(self, jd_id: str) -> bool:
        """删除JD"""
        db_jd = self.get_by_id(jd_id)
        if db_jd:
            self.db.delete(db_jd)
            self.db.commit()
            return True
        return False
    
    def search(self, keyword: str, skip: int = 0, limit: int = 100) -> List[JobDescriptionDB]:
        """搜索JD"""
        return self.db.query(JobDescriptionDB).filter(
            JobDescriptionDB.job_title.contains(keyword) |
            JobDescriptionDB.raw_text.contains(keyword)
        ).offset(skip).limit(limit).all()


class CategoryRepository:
    """职位分类数据访问类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, category: JobCategoryDB) -> JobCategoryDB:
        """创建分类"""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category
    
    def get_by_id(self, category_id: str) -> Optional[JobCategoryDB]:
        """根据ID获取分类"""
        return self.db.query(JobCategoryDB).filter(JobCategoryDB.id == category_id).first()
    
    def get_all(self) -> List[JobCategoryDB]:
        """获取所有分类"""
        return self.db.query(JobCategoryDB).order_by(JobCategoryDB.level, JobCategoryDB.name).all()
    
    def get_by_level(self, level: int) -> List[JobCategoryDB]:
        """根据层级获取分类"""
        return self.db.query(JobCategoryDB).filter(JobCategoryDB.level == level).all()
    
    def get_children(self, parent_id: str) -> List[JobCategoryDB]:
        """获取子分类"""
        return self.db.query(JobCategoryDB).filter(JobCategoryDB.parent_id == parent_id).all()
    
    def update_sample_jds(self, category_id: str, sample_jd_ids: List[str]) -> Optional[JobCategoryDB]:
        """更新样本JD列表"""
        category = self.get_by_id(category_id)
        if category:
            # 验证：只有第三层级可以有样本JD，且最多2个
            if category.level != 3:
                raise ValueError("只有第三层级分类才能添加样本JD")
            if len(sample_jd_ids) > 2:
                raise ValueError("样本JD数量不能超过2个")
            
            category.sample_jd_ids = sample_jd_ids
            self.db.commit()
            self.db.refresh(category)
        return category
    
    def delete(self, category_id: str) -> bool:
        """删除分类"""
        category = self.get_by_id(category_id)
        if category:
            # 检查是否有子分类
            children = self.get_children(category_id)
            if children:
                raise ValueError("该分类下还有子分类，无法删除")
            
            self.db.delete(category)
            self.db.commit()
            return True
        return False
    
    def get_category_tree(self) -> List[dict]:
        """获取分类树结构"""
        # 获取所有一级分类
        level1_categories = self.get_by_level(1)
        
        tree = []
        for cat1 in level1_categories:
            cat1_dict = {
                "id": cat1.id,
                "name": cat1.name,
                "level": cat1.level,
                "description": cat1.description,
                "children": []
            }
            
            # 获取二级分类
            level2_categories = self.get_children(cat1.id)
            for cat2 in level2_categories:
                cat2_dict = {
                    "id": cat2.id,
                    "name": cat2.name,
                    "level": cat2.level,
                    "description": cat2.description,
                    "children": []
                }
                
                # 获取三级分类
                level3_categories = self.get_children(cat2.id)
                for cat3 in level3_categories:
                    cat3_dict = {
                        "id": cat3.id,
                        "name": cat3.name,
                        "level": cat3.level,
                        "description": cat3.description,
                        "sample_jd_ids": cat3.sample_jd_ids
                    }
                    cat2_dict["children"].append(cat3_dict)
                
                cat1_dict["children"].append(cat2_dict)
            
            tree.append(cat1_dict)
        
        return tree
