#!/usr/bin/env python3
# Knowledge Base for SQL Expert System

class SchemaKnowledge:
    def __init__(self):
        self.tables = {}
        self.relationships = []
        self.indices = {}
        self.best_practices = []
        self.anomaly_rules = []
    
    def add_table(self, table_name, columns):
        self.tables[table_name] = {
             'columns': columns,
             'constraints': [],
             'indexes': []
         }
    
    def get_table(self, name):
        return self.tables.get(name)
    
    def get_relationships(self):
        return self.relationships
    
    def get_best_practices(self):
        return self.best_practices


class BestPracticesDB:
    def __init__(self):
        self.practices = []
    
    def add(self, desc):
        self.practices.append(desc)
    
    def get_all(self):
        return self.practices


class SchemaOptimizer:
    def check_full_table(self, query):
        if 'UPDATE' in query.upper() and 'WHERE' not in query.upper():
            return {"warning": "UPDATE needs WHERE", "severity": "HIGH"}
        elif 'DELETE FROM' in query.upper() and 'WHERE' not in query.upper():
            return {"warning": "DELETE needs WHERE", "severity": "CRITICAL"}
        return None
    
    def analyze(self, query):
        warnings = []
        if self.check_full_table(query):
            warnings.append("Full table operation")
        return {"warnings": warnings, "safe": len(warnings) == 0}


# Knowledge Base + Multi-DB Integration

class KnowledgeMultiDB:
    """
    Knowledge Base integrated with Multi-DB
    SchemaKnowledge + UnifiedDatabase
     """
    
    def __init__(self, db_uri):
        self.db = UnifiedDatabase(db_uri)
        self.kb = SchemaKnowledge()
        self.optimized = SchemaOptimizer(self.kb)
    
    def load_schema(self):
        """Load schema from database"""
        self.db.connect()
        schemas = self.db.get_schemas()
        
        for table in schemas:
            self.kb.add_table(
                table['name'],
                table['columns'],
                table.get('constraints', [])
            )
        
        return self.kb
    
    def query_with_kb(self, query):
        """Execute query with Knowledge Base optimization"""
        result = self.db.execute(query)
        
        # Analyze with KB
        analysis = self.optimized.analyze(query)
        
        return {
            'success': True,
            'query': query,
            'rows': result,
            'optimization': analysis,
            'schema': self.kb.tables
         }
    
    def close(self):
        """Close database"""
        self.db.close()
    
    def __enter__(self):
        self.load_schema()
        return self
    
    def __exit__(self, *args):
        self.close()
