"""
Neo4j 知识图谱数据库连接管理
"""

from typing import Any, Dict, List, Optional
import asyncio

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from loguru import logger

from .config import settings


class Neo4jClient:
    """Neo4j客户端管理器"""
    
    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.connected = False
    
    async def connect(self) -> None:
        """建立Neo4j连接"""
        try:
            # 创建异步驱动
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_acquisition_timeout=60
            )
            
            # 测试连接
            await self.driver.verify_connectivity()
            self.connected = True
            
            logger.info(f"✅ Neo4j连接成功: {settings.NEO4J_URI}")
            
        except Exception as e:
            logger.error(f"❌ Neo4j连接失败: {e}")
            raise
    
    async def disconnect(self) -> None:
        """关闭Neo4j连接"""
        try:
            if self.driver:
                await self.driver.close()
                self.connected = False
            logger.info("✅ Neo4j连接已关闭")
        except Exception as e:
            logger.error(f"❌ 关闭Neo4j连接失败: {e}")
    
    async def health_check(self) -> bool:
        """Neo4j健康检查"""
        try:
            if self.driver and self.connected:
                await self.driver.verify_connectivity()
                return True
            return False
        except Exception as e:
            logger.error(f"Neo4j健康检查失败: {e}")
            return False
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        if not self.driver:
            raise Exception("Neo4j驱动未初始化")
        return self.driver.session()
    
    async def get_database_info(self) -> Dict[str, Any]:
        """获取数据库信息"""
        try:
            async with self.get_session() as session:
                # 获取数据库版本
                result = await session.run("CALL dbms.components() YIELD name, versions, edition")
                components = await result.data()
                
                # 获取节点和关系统计
                stats_result = await session.run("""
                    MATCH (n) 
                    OPTIONAL MATCH ()-[r]->() 
                    RETURN count(DISTINCT n) as nodes, count(r) as relationships
                """)
                stats = await stats_result.single()
                
                return {
                    "components": components,
                    "nodes_count": stats["nodes"],
                    "relationships_count": stats["relationships"],
                    "status": "connected"
                }
                
        except Exception as e:
            logger.error(f"获取Neo4j信息失败: {e}")
            return {"status": "error", "message": str(e)}


class KnowledgeGraphManager:
    """知识图谱管理器"""
    
    def __init__(self, neo4j_client: Neo4jClient):
        self.neo4j_client = neo4j_client
    
    async def create_node(
        self, 
        label: str, 
        properties: Dict[str, Any],
        unique_property: str = "id"
    ) -> Optional[str]:
        """创建节点"""
        try:
            async with self.neo4j_client.get_session() as session:
                query = f"""
                MERGE (n:{label} {{{unique_property}: $unique_value}})
                SET n += $properties
                RETURN elementId(n) as node_id
                """
                
                result = await session.run(
                    query,
                    unique_value=properties.get(unique_property),
                    properties=properties
                )
                
                record = await result.single()
                return record["node_id"] if record else None
                
        except Exception as e:
            logger.error(f"创建节点失败: {e}")
            return None
    
    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> bool:
        """创建关系"""
        try:
            async with self.neo4j_client.get_session() as session:
                properties = properties or {}
                
                query = """
                MATCH (a), (b)
                WHERE elementId(a) = $from_id AND elementId(b) = $to_id
                MERGE (a)-[r:%s]->(b)
                SET r += $properties
                RETURN r
                """ % relationship_type
                
                result = await session.run(
                    query,
                    from_id=from_node_id,
                    to_id=to_node_id,
                    properties=properties
                )
                
                record = await result.single()
                return record is not None
                
        except Exception as e:
            logger.error(f"创建关系失败: {e}")
            return False
    
    async def find_nodes(
        self,
        label: str = None,
        properties: Dict[str, Any] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查找节点"""
        try:
            async with self.neo4j_client.get_session() as session:
                # 构建查询
                if label:
                    match_clause = f"MATCH (n:{label})"
                else:
                    match_clause = "MATCH (n)"
                
                where_clauses = []
                params = {"limit": limit}
                
                if properties:
                    for key, value in properties.items():
                        where_clauses.append(f"n.{key} = ${key}")
                        params[key] = value
                
                where_clause = " AND ".join(where_clauses)
                if where_clause:
                    where_clause = f"WHERE {where_clause}"
                
                query = f"""
                {match_clause}
                {where_clause}
                RETURN n, elementId(n) as node_id, labels(n) as labels
                LIMIT $limit
                """
                
                result = await session.run(query, **params)
                records = await result.data()
                
                return [
                    {
                        "id": record["node_id"],
                        "labels": record["labels"],
                        "properties": dict(record["n"])
                    }
                    for record in records
                ]
                
        except Exception as e:
            logger.error(f"查找节点失败: {e}")
            return []
    
    async def find_relationships(
        self,
        from_node_id: str = None,
        to_node_id: str = None,
        relationship_type: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """查找关系"""
        try:
            async with self.neo4j_client.get_session() as session:
                # 构建查询
                where_clauses = []
                params = {"limit": limit}
                
                if relationship_type:
                    match_clause = f"MATCH (a)-[r:{relationship_type}]->(b)"
                else:
                    match_clause = "MATCH (a)-[r]->(b)"
                
                if from_node_id:
                    where_clauses.append("elementId(a) = $from_id")
                    params["from_id"] = from_node_id
                
                if to_node_id:
                    where_clauses.append("elementId(b) = $to_id")
                    params["to_id"] = to_node_id
                
                where_clause = " AND ".join(where_clauses)
                if where_clause:
                    where_clause = f"WHERE {where_clause}"
                
                query = f"""
                {match_clause}
                {where_clause}
                RETURN a, r, b, 
                       elementId(a) as from_id, 
                       elementId(b) as to_id,
                       elementId(r) as rel_id,
                       type(r) as rel_type
                LIMIT $limit
                """
                
                result = await session.run(query, **params)
                records = await result.data()
                
                return [
                    {
                        "id": record["rel_id"],
                        "type": record["rel_type"],
                        "from_node": {
                            "id": record["from_id"],
                            "properties": dict(record["a"])
                        },
                        "to_node": {
                            "id": record["to_id"],
                            "properties": dict(record["b"])
                        },
                        "properties": dict(record["r"])
                    }
                    for record in records
                ]
                
        except Exception as e:
            logger.error(f"查找关系失败: {e}")
            return []
    
    async def delete_node(self, node_id: str) -> bool:
        """删除节点"""
        try:
            async with self.neo4j_client.get_session() as session:
                query = """
                MATCH (n)
                WHERE elementId(n) = $node_id
                DETACH DELETE n
                """
                
                await session.run(query, node_id=node_id)
                return True
                
        except Exception as e:
            logger.error(f"删除节点失败: {e}")
            return False
    
    async def execute_cypher(
        self, 
        query: str, 
        parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """执行自定义Cypher查询"""
        try:
            async with self.neo4j_client.get_session() as session:
                result = await session.run(query, parameters or {})
                return await result.data()
                
        except Exception as e:
            logger.error(f"执行Cypher查询失败: {e}")
            return []
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """获取图数据库统计信息"""
        try:
            async with self.neo4j_client.get_session() as session:
                # 节点标签统计
                labels_result = await session.run("""
                    CALL db.labels() YIELD label
                    CALL apoc.cypher.run('MATCH (:`' + label + '`) RETURN count(*) as count', {})
                    YIELD value
                    RETURN label, value.count as count
                """)
                labels_stats = await labels_result.data()
                
                # 关系类型统计
                relationships_result = await session.run("""
                    CALL db.relationshipTypes() YIELD relationshipType
                    CALL apoc.cypher.run('MATCH ()-[:`' + relationshipType + '`]->() RETURN count(*) as count', {})
                    YIELD value
                    RETURN relationshipType, value.count as count
                """)
                relationships_stats = await relationships_result.data()
                
                # 总体统计
                total_result = await session.run("""
                    MATCH (n)
                    OPTIONAL MATCH ()-[r]->()
                    RETURN count(DISTINCT n) as total_nodes, count(r) as total_relationships
                """)
                total_stats = await total_result.single()
                
                return {
                    "total_nodes": total_stats["total_nodes"],
                    "total_relationships": total_stats["total_relationships"],
                    "node_labels": {item["label"]: item["count"] for item in labels_stats},
                    "relationship_types": {item["relationshipType"]: item["count"] for item in relationships_stats}
                }
                
        except Exception as e:
            logger.error(f"获取图统计信息失败: {e}")
            return {
                "total_nodes": 0,
                "total_relationships": 0,
                "node_labels": {},
                "relationship_types": {}
            }


# 全局Neo4j客户端实例
neo4j_client = Neo4jClient()
knowledge_graph_manager = KnowledgeGraphManager(neo4j_client)


async def init_neo4j() -> None:
    """初始化Neo4j连接"""
    await neo4j_client.connect()


async def close_neo4j() -> None:
    """关闭Neo4j连接"""
    await neo4j_client.disconnect() 