#!/usr/bin/env python3
"""
DB-Expert：更新数据库结构支持专业概念数据
将爬取的专业概念数据写入数据库并优化存储结构
"""

import psycopg2
import json
import os
from datetime import datetime
from typing import Dict, Any, List

class DBExpert:
    def __init__(self):
        # 使用数据库连接参数
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'employment'),
            'user': 'postgres',
            'password': os.getenv('POSTGRES_PASSWORD', 'your_password'),
            'host': os.getenv('DB_HOST', 'localhost'),  # 优先使用环境变量
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'employment'),
            'user': 'postgres',
            'password': os.getenv('POSTGRES_PASSWORD', 'your_password')
        }
        self.connection = None
        print("🔗 数据库配置初始化完成")
    
    def connect(self):
        """连接数据库"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def disconnect(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            print("🔌 数据库连接已断开")
    
    def create_major_concept_table(self):
        """创建专业概念表"""
        create_table_sql = """
        -- 创建专业概念表
        CREATE TABLE IF NOT EXISTS major_concepts (
            id SERIAL PRIMARY KEY,
            major_name VARCHAR(200) NOT NULL,
            concept_type VARCHAR(50) NOT NULL, -- 'origin', 'development_history', 'major_events', 'current_status', 'future_prospects'
            title VARCHAR(500),  -- 时间节点或事件标题
            content TEXT NOT NULL,  -- 详细内容
            year INTEGER,  -- 相关年份（可选）
            sort_order INTEGER DEFAULT 0,
            source_url VARCHAR(500),
            data_quality VARCHAR(20) DEFAULT 'high',
            crawled_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_major_concepts_major_name ON major_concepts(major_name);
        CREATE INDEX IF NOT EXISTS idx_major_concepts_type ON major_concepts(concept_type);
        CREATE INDEX IF NOT EXISTS idx_major_concepts_year ON major_concepts(year);
        CREATE INDEX IF NOT EXISTS idx_major_concepts_crawled_at ON major_concepts(crawled_at DESC);
        
        -- 创建触发器自动更新updated_at
        CREATE OR REPLACE FUNCTION update_major_concepts_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER update_major_concepts_updated_at_trigger
            BEFORE UPDATE ON major_concepts
            FOR EACH ROW
            EXECUTE FUNCTION update_major_concepts_updated_at();
        """
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(create_table_sql)
            self.connection.commit()
            print("✅ 专业概念表创建成功")
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 创建表失败: {e}")
            raise
        finally:
            cursor.close()
    
    def insert_concept_data(self, concept_data: Dict[str, Any]):
        """插入概念数据"""
        insert_sql = """
        INSERT INTO major_concepts (
            major_name, concept_type, title, content, year, sort_order, source_url, data_quality, crawled_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.connection.cursor()
        try:
            major_name = concept_data["major_name"]
            
            # 插入专业起源
            if "origin" in concept_data:
                cursor.execute(insert_sql, (
                    major_name, "origin", "专业起源", concept_data["origin"], 
                    self._extract_year_from_text(concept_data["origin"]), 1, 
                    "https://gaokao.chsi.com.cn", "high", datetime.now()
                ))
            
            # 插入发展历史
            if "development_history" in concept_data:
                for i, event in enumerate(concept_data["development_history"]):
                    cursor.execute(insert_sql, (
                        major_name, "development_history", event, event, 
                        self._extract_year_from_text(event), i + 1, 
                        "https://gaokao.chsi.com.cn", "high", datetime.now()
                    ))
            
            # 插入重大事件
            if "major_events" in concept_data:
                for i, event in enumerate(concept_data["major_events"]):
                    cursor.execute(insert_sql, (
                        major_name, "major_events", event, event, 
                        self._extract_year_from_text(event), i + 1, 
                        "https://gaokao.chsi.com.cn", "high", datetime.now()
                    ))
            
            # 插入现状
            if "current_status" in concept_data:
                cursor.execute(insert_sql, (
                    major_name, "current_status", "发展现状", concept_data["current_status"], 
                    2024, 1, 
                    "https://www.eol.cn", "high", datetime.now()
                ))
            
            # 插入未来前景
            if "future_prospects" in concept_data:
                cursor.execute(insert_sql, (
                    major_name, "future_prospects", "未来前景", concept_data["future_prospects"], 
                    2025, 1, 
                    "https://gaokao.chsi.com.cn", "high", datetime.now()
                ))
            
            self.connection.commit()
            print(f"✅ 插入 {major_name} 的概念数据成功")
            
        except Exception as e:
            self.connection.rollback()
            print(f"❌ 插入数据失败: {e}")
            raise
        finally:
            cursor.close()
    
    def _extract_year_from_text(self, text: str) -> int:
        """从文本中提取年份"""
        import re
        # 匹配4位数字年份
        year_match = re.search(r'(\d{4})', text)
        return int(year_match.group(1)) if year_match else None
    
    def create_indexes(self):
        """创建性能优化索引"""
        index_sql = """
        -- 创建复合索引优化查询性能
        CREATE INDEX IF NOT EXISTS idx_major_concepts_composite 
        ON major_concepts(major_name, concept_type, year);
        
        -- 分析查询的优化索引
        CREATE INDEX IF NOT EXISTS idx_major_concepts_analysis 
        ON major_concepts(concept_type, crawled_at DESC);
        """
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(index_sql)
            self.connection.commit()
            print("✅ 性能索引创建成功")
        except Exception as e:
            print(f"❌ 创建索引失败: {e}")
        finally:
            cursor.close()
    
    def validate_data_quality(self) -> Dict[str, Any]:
        """验证数据质量"""
        validation_sql = """
        SELECT 
            COUNT(*) as total_concepts,
            COUNT(CASE WHEN concept_type = 'origin' THEN 1 END) as origin_count,
            COUNT(CASE WHEN concept_type = 'development_history' THEN 1 END) as history_count,
            COUNT(CASE WHEN concept_type = 'major_events' THEN 1 END) as events_count,
            COUNT(CASE WHEN concept_type = 'current_status' THEN 1 END) as status_count,
            COUNT(CASE WHEN concept_type = 'future_prospects' THEN 1 END) as prospects_count,
            COUNT(CASE WHEN year IS NOT NULL THEN 1 END) as with_year_count
        FROM major_concepts;
        """
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(validation_sql)
            result = cursor.fetchone()
            validation_report = {
                "total_concepts": result[0],
                "data_types": {
                    "origin": result[1],
                    "development_history": result[2],
                    "major_events": result[3],
                    "current_status": result[4],
                    "future_prospects": result[5]
                },
                "quality_score": min(100, result[0] // 5 * 10)  if result[0] > 0 else 0,
                "with_year_data": result[6],
                "validation_time": datetime.now().isoformat()
            }
            print(f"✅ 数据验证完成: {validation_report}")
            return validation_report
        except Exception as e:
            print(f"❌ 数据验证失败: {e}")
            return {"error": str(e)}
        finally:
            cursor.close()
    
    def process_all_data(self, data_file: str = "major_concept_data.json"):
        """处理所有爬取的数据"""
        # 读取爬取的数据
        data_file_path = os.path.join(os.path.dirname(__file__), data_file)
        
        if not os.path.exists(data_file_path):
            print(f"❌ 数据文件不存在: {data_file_path}")
            return None
        
        with open(data_file_path, 'r', encoding='utf-8') as f:
            crawl_data = json.load(f)
        
        if not crawl_data.get("success") or not crawl_data.get("data"):
            print("❌ 爬取数据格式错误")
            return None
        
        print(f"📊 开始处理 {len(crawl_data['data'])} 个专业的概念数据...")
        
        # 创建表结构
        self.create_major_concept_table()
        
        # 插入数据
        for concept_data in crawl_data["data"]:
            try:
                self.insert_concept_data(concept_data)
            except Exception as e:
                print(f"⚠️  插入数据失败: {concept_data.get('major_name', 'Unknown')}: {e}")
                continue
        
        # 创建性能索引
        self.create_indexes()
        
        # 验证数据质量
        validation_report = self.validate_data_quality()
        
        # 生成处理报告
        process_report = {
            "success": True,
            "data_file": data_file_path,
            "processed_majors": len(crawl_data["data"]),
            "total_concepts": validation_report.get("total_concepts", 0),
            "quality_score": validation_report.get("quality_score", 0),
            "data_types": validation_report.get("data_types", {}),
            "process_time": datetime.now().isoformat(),
            "message": f"成功处理 {len(crawl_data['data'])} 个专业的概念数据"
        }
        
        # 保存处理报告
        report_file = data_file_path.replace('.json', '_process_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(process_report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 处理报告已保存到: {report_file}")
        return process_report

def main():
    """主函数"""
    print("🔧 DB-Expert 开始处理专业概念数据...")
    
    expert = DBExpert()
    
    try:
        # 连接数据库
        expert.connect()
        
        # 处理数据
        report = expert.process_all_data()
        
        if report:
            print("✅ 数据库更新完成!")
            print(f"📊 处理统计:")
            print(f"   - 处理专业数: {report.get('processed_majors', 0)}")
            print(f"   - 总概念条目: {report.get('total_concepts', 0)}")
            print(f"   - 数据质量评分: {report.get('quality_score', 0)}/100")
        
    except Exception as e:
        print(f"❌ 处理过程中出现错误: {e}")
    finally:
        expert.disconnect()

if __name__ == "__main__":
    main()