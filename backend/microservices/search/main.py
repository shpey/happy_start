from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import asyncio
import json
import logging
from datetime import datetime, timedelta
import uuid
import numpy as np
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import redis.asyncio as redis
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import jieba
import re
from collections import defaultdict, Counter
import pickle
import hashlib
import asyncpg
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据模型
class SearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"  # semantic, keyword, hybrid, multimodal
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    offset: int = 0
    user_id: Optional[str] = None
    include_score: bool = True

class SearchResult(BaseModel):
    id: str
    content: str
    title: str
    type: str
    score: float
    source: str
    metadata: Dict[str, Any]
    created_at: datetime
    relevance_reason: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query_time: float
    search_type: str
    suggestions: List[str]
    facets: Dict[str, List[Dict[str, Any]]]

class IndexRequest(BaseModel):
    documents: List[Dict[str, Any]]
    index_name: str = "thinking_documents"

class RecommendationRequest(BaseModel):
    user_id: str
    item_type: str = "thinking"
    limit: int = 5
    context: Optional[Dict[str, Any]] = None

class RecommendationResult(BaseModel):
    id: str
    title: str
    content: str
    score: float
    reason: str
    type: str

# 搜索引擎类
class AISearchEngine:
    def __init__(self):
        self.es = None
        self.chroma_client = None
        self.redis_client = None
        self.db_pool = None
        self.sentence_transformer = None
        self.tfidf_vectorizer = None
        self.lda_model = None
        self.user_profiles = {}
        self.item_features = {}
        
    async def initialize(self):
        """初始化所有组件"""
        try:
            # 初始化Elasticsearch
            self.es = AsyncElasticsearch([{"host": "localhost", "port": 9200}])
            
            # 初始化ChromaDB
            self.chroma_client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="./chroma_db"
            ))
            
            # 初始化Redis
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # 初始化数据库连接池
            self.db_pool = await asyncpg.create_pool(
                host="localhost",
                port=5432,
                user="postgres",
                password="password",
                database="intelligent_thinking"
            )
            
            # 初始化机器学习模型
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            self.tfidf_vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            self.lda_model = LatentDirichletAllocation(n_components=10, random_state=42)
            
            # 创建Elasticsearch索引
            await self._create_elasticsearch_indices()
            
            # 初始化ChromaDB集合
            await self._create_chroma_collections()
            
            # 加载用户画像和推荐模型
            await self._load_recommendation_models()
            
            logger.info("AI搜索引擎初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    async def _create_elasticsearch_indices(self):
        """创建Elasticsearch索引"""
        indices = {
            "thinking_documents": {
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "ik_max_word"},
                        "content": {"type": "text", "analyzer": "ik_max_word"},
                        "summary": {"type": "text", "analyzer": "ik_max_word"},
                        "type": {"type": "keyword"},
                        "user_id": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"},
                        "view_count": {"type": "integer"},
                        "like_count": {"type": "integer"},
                        "embedding": {"type": "dense_vector", "dims": 384},
                        "location": {"type": "geo_point"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "ik_max_word": {
                                "type": "custom",
                                "tokenizer": "ik_max_word"
                            }
                        }
                    }
                }
            },
            "user_behavior": {
                "mappings": {
                    "properties": {
                        "user_id": {"type": "keyword"},
                        "action": {"type": "keyword"},
                        "item_id": {"type": "keyword"},
                        "item_type": {"type": "keyword"},
                        "timestamp": {"type": "date"},
                        "session_id": {"type": "keyword"},
                        "metadata": {"type": "object"}
                    }
                }
            }
        }
        
        for index_name, index_config in indices.items():
            if not await self.es.indices.exists(index=index_name):
                await self.es.indices.create(index=index_name, body=index_config)
                logger.info(f"创建索引: {index_name}")
    
    async def _create_chroma_collections(self):
        """创建ChromaDB集合"""
        try:
            self.thinking_collection = self.chroma_client.create_collection(
                name="thinking_embeddings",
                metadata={"hnsw:space": "cosine"}
            )
            self.user_collection = self.chroma_client.create_collection(
                name="user_profiles",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            # 如果集合已存在，获取现有集合
            self.thinking_collection = self.chroma_client.get_collection("thinking_embeddings")
            self.user_collection = self.chroma_client.get_collection("user_profiles")
    
    async def _load_recommendation_models(self):
        """加载推荐模型"""
        try:
            # 从Redis加载用户画像
            user_keys = await self.redis_client.keys("user_profile:*")
            for key in user_keys:
                user_id = key.split(":")[-1]
                profile_data = await self.redis_client.get(key)
                if profile_data:
                    self.user_profiles[user_id] = json.loads(profile_data)
            
            logger.info(f"加载了 {len(self.user_profiles)} 个用户画像")
            
        except Exception as e:
            logger.error(f"加载推荐模型失败: {e}")
    
    async def semantic_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """语义搜索"""
        try:
            # 生成查询向量
            query_embedding = self.sentence_transformer.encode([query])[0]
            
            # 在ChromaDB中搜索
            results = self.thinking_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=limit,
                where=filters or {}
            )
            
            # 格式化结果
            formatted_results = []
            for i, (id, distance, metadata) in enumerate(zip(
                results['ids'][0], results['distances'][0], results['metadatas'][0]
            )):
                formatted_results.append({
                    'id': id,
                    'score': 1 - distance,  # 转换为相似度分数
                    'content': results['documents'][0][i],
                    'metadata': metadata,
                    'search_type': 'semantic'
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            return []
    
    async def keyword_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """关键词搜索"""
        try:
            # 构建Elasticsearch查询
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^3", "content^2", "summary", "tags^2"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {"fragment_size": 150, "number_of_fragments": 3},
                        "summary": {}
                    }
                },
                "size": limit
            }
            
            # 添加过滤器
            if filters:
                es_query["query"]["bool"]["filter"] = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        es_query["query"]["bool"]["filter"].append({
                            "terms": {key: value}
                        })
                    else:
                        es_query["query"]["bool"]["filter"].append({
                            "term": {key: value}
                        })
            
            # 执行搜索
            response = await self.es.search(
                index="thinking_documents",
                body=es_query
            )
            
            # 格式化结果
            formatted_results = []
            for hit in response['hits']['hits']:
                formatted_results.append({
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'content': hit['_source']['content'],
                    'title': hit['_source']['title'],
                    'metadata': hit['_source'],
                    'highlights': hit.get('highlight', {}),
                    'search_type': 'keyword'
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"关键词搜索失败: {e}")
            return []
    
    async def hybrid_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """混合搜索（语义+关键词）"""
        try:
            # 并行执行语义搜索和关键词搜索
            semantic_results, keyword_results = await asyncio.gather(
                self.semantic_search(query, limit, filters),
                self.keyword_search(query, limit, filters)
            )
            
            # 合并和重新排序结果
            combined_results = {}
            
            # 处理语义搜索结果
            for result in semantic_results:
                result_id = result['id']
                combined_results[result_id] = result
                combined_results[result_id]['semantic_score'] = result['score']
                combined_results[result_id]['keyword_score'] = 0.0
            
            # 处理关键词搜索结果
            for result in keyword_results:
                result_id = result['id']
                if result_id in combined_results:
                    combined_results[result_id]['keyword_score'] = result['score']
                    combined_results[result_id]['highlights'] = result.get('highlights', {})
                else:
                    combined_results[result_id] = result
                    combined_results[result_id]['semantic_score'] = 0.0
                    combined_results[result_id]['keyword_score'] = result['score']
            
            # 计算混合分数
            for result_id, result in combined_results.items():
                semantic_score = result.get('semantic_score', 0.0)
                keyword_score = result.get('keyword_score', 0.0)
                
                # 归一化分数
                normalized_semantic = semantic_score / (1.0 if semantic_score == 0 else max(1.0, semantic_score))
                normalized_keyword = keyword_score / (1.0 if keyword_score == 0 else max(1.0, keyword_score))
                
                # 加权混合分数
                combined_results[result_id]['score'] = 0.6 * normalized_semantic + 0.4 * normalized_keyword
                combined_results[result_id]['search_type'] = 'hybrid'
            
            # 按分数排序
            sorted_results = sorted(combined_results.values(), key=lambda x: x['score'], reverse=True)
            
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"混合搜索失败: {e}")
            return []
    
    async def multimodal_search(self, query: str, limit: int = 10, filters: Dict = None) -> List[Dict]:
        """多模态搜索"""
        try:
            # 这里可以集成图像搜索、音频搜索等
            # 目前先实现文本搜索的增强版本
            
            # 查询扩展
            expanded_query = await self._expand_query(query)
            
            # 执行混合搜索
            results = await self.hybrid_search(expanded_query, limit, filters)
            
            # 添加多模态相关信息
            for result in results:
                result['search_type'] = 'multimodal'
                result['expanded_query'] = expanded_query
            
            return results
            
        except Exception as e:
            logger.error(f"多模态搜索失败: {e}")
            return []
    
    async def _expand_query(self, query: str) -> str:
        """查询扩展"""
        try:
            # 使用同义词扩展
            synonyms = await self._get_synonyms(query)
            
            # 使用相关术语扩展
            related_terms = await self._get_related_terms(query)
            
            # 组合扩展查询
            expanded_parts = [query]
            if synonyms:
                expanded_parts.extend(synonyms[:3])
            if related_terms:
                expanded_parts.extend(related_terms[:3])
            
            return " ".join(expanded_parts)
            
        except Exception as e:
            logger.error(f"查询扩展失败: {e}")
            return query
    
    async def _get_synonyms(self, query: str) -> List[str]:
        """获取同义词"""
        # 这里可以集成词典API或训练好的同义词模型
        # 目前返回简单的同义词映射
        synonym_map = {
            "思考": ["思维", "分析", "推理"],
            "学习": ["学习", "教育", "培训"],
            "创新": ["创造", "发明", "革新"],
            "合作": ["协作", "配合", "团队"],
            "分析": ["分解", "解析", "研究"]
        }
        
        synonyms = []
        for word in jieba.cut(query):
            if word in synonym_map:
                synonyms.extend(synonym_map[word])
        
        return list(set(synonyms))
    
    async def _get_related_terms(self, query: str) -> List[str]:
        """获取相关术语"""
        try:
            # 使用词向量模型找相关术语
            query_embedding = self.sentence_transformer.encode([query])[0]
            
            # 从ChromaDB中查找相似文档的关键词
            results = self.thinking_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=5
            )
            
            related_terms = []
            for doc in results['documents'][0]:
                # 提取关键词
                keywords = self._extract_keywords(doc)
                related_terms.extend(keywords[:2])
            
            return list(set(related_terms))[:5]
            
        except Exception as e:
            logger.error(f"获取相关术语失败: {e}")
            return []
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 使用TF-IDF提取关键词
        try:
            # 分词
            words = jieba.cut(text)
            filtered_words = [word for word in words if len(word) > 1 and word.isalpha()]
            
            # 词频统计
            word_freq = Counter(filtered_words)
            
            # 返回高频词
            return [word for word, freq in word_freq.most_common(10)]
            
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            return []
    
    async def get_recommendations(self, user_id: str, item_type: str = "thinking", limit: int = 5) -> List[Dict]:
        """获取个性化推荐"""
        try:
            # 获取用户画像
            user_profile = self.user_profiles.get(user_id, {})
            
            # 基于协同过滤的推荐
            collaborative_recs = await self._collaborative_filtering(user_id, item_type, limit)
            
            # 基于内容的推荐
            content_recs = await self._content_based_filtering(user_id, item_type, limit)
            
            # 混合推荐
            hybrid_recs = await self._hybrid_recommendations(
                collaborative_recs, content_recs, user_profile, limit
            )
            
            return hybrid_recs
            
        except Exception as e:
            logger.error(f"获取推荐失败: {e}")
            return []
    
    async def _collaborative_filtering(self, user_id: str, item_type: str, limit: int) -> List[Dict]:
        """协同过滤推荐"""
        try:
            # 获取用户行为数据
            user_behavior = await self._get_user_behavior(user_id)
            
            # 找相似用户
            similar_users = await self._find_similar_users(user_id, user_behavior)
            
            # 基于相似用户的推荐
            recommendations = []
            for similar_user_id, similarity in similar_users:
                similar_user_items = await self._get_user_items(similar_user_id, item_type)
                
                for item in similar_user_items:
                    if item['id'] not in [i['id'] for i in recommendations]:
                        recommendations.append({
                            'id': item['id'],
                            'title': item['title'],
                            'content': item['content'],
                            'score': similarity * item['rating'],
                            'reason': f"喜欢类似内容的用户也喜欢这个",
                            'type': item_type
                        })
            
            return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"协同过滤失败: {e}")
            return []
    
    async def _content_based_filtering(self, user_id: str, item_type: str, limit: int) -> List[Dict]:
        """基于内容的推荐"""
        try:
            # 获取用户偏好
            user_preferences = await self._get_user_preferences(user_id)
            
            # 获取候选项目
            candidate_items = await self._get_candidate_items(item_type)
            
            # 计算相似度
            recommendations = []
            for item in candidate_items:
                similarity = self._calculate_content_similarity(user_preferences, item)
                
                if similarity > 0.5:  # 阈值过滤
                    recommendations.append({
                        'id': item['id'],
                        'title': item['title'],
                        'content': item['content'],
                        'score': similarity,
                        'reason': f"基于您的兴趣偏好",
                        'type': item_type
                    })
            
            return sorted(recommendations, key=lambda x: x['score'], reverse=True)[:limit]
            
        except Exception as e:
            logger.error(f"基于内容的推荐失败: {e}")
            return []
    
    async def _hybrid_recommendations(self, collaborative_recs: List[Dict], 
                                    content_recs: List[Dict], 
                                    user_profile: Dict, 
                                    limit: int) -> List[Dict]:
        """混合推荐"""
        try:
            # 合并推荐结果
            combined_recs = {}
            
            # 处理协同过滤结果
            for rec in collaborative_recs:
                rec_id = rec['id']
                combined_recs[rec_id] = rec
                combined_recs[rec_id]['collaborative_score'] = rec['score']
                combined_recs[rec_id]['content_score'] = 0.0
            
            # 处理基于内容的结果
            for rec in content_recs:
                rec_id = rec['id']
                if rec_id in combined_recs:
                    combined_recs[rec_id]['content_score'] = rec['score']
                else:
                    combined_recs[rec_id] = rec
                    combined_recs[rec_id]['collaborative_score'] = 0.0
                    combined_recs[rec_id]['content_score'] = rec['score']
            
            # 计算混合分数
            for rec_id, rec in combined_recs.items():
                collaborative_score = rec.get('collaborative_score', 0.0)
                content_score = rec.get('content_score', 0.0)
                
                # 加权组合
                rec['score'] = 0.7 * collaborative_score + 0.3 * content_score
                rec['reason'] = "基于协同过滤和内容分析的综合推荐"
            
            # 按分数排序
            sorted_recs = sorted(combined_recs.values(), key=lambda x: x['score'], reverse=True)
            
            return sorted_recs[:limit]
            
        except Exception as e:
            logger.error(f"混合推荐失败: {e}")
            return []
    
    async def _get_user_behavior(self, user_id: str) -> List[Dict]:
        """获取用户行为数据"""
        try:
            # 从Elasticsearch获取用户行为
            query = {
                "query": {
                    "term": {"user_id": user_id}
                },
                "sort": [{"timestamp": {"order": "desc"}}],
                "size": 1000
            }
            
            response = await self.es.search(index="user_behavior", body=query)
            
            behaviors = []
            for hit in response['hits']['hits']:
                behaviors.append(hit['_source'])
            
            return behaviors
            
        except Exception as e:
            logger.error(f"获取用户行为失败: {e}")
            return []
    
    async def _find_similar_users(self, user_id: str, user_behavior: List[Dict]) -> List[tuple]:
        """找相似用户"""
        try:
            # 简化的相似用户查找
            # 实际应用中可以使用更复杂的算法
            similar_users = []
            
            # 获取用户的物品评分向量
            user_items = {b['item_id']: 1 for b in user_behavior if b['action'] == 'like'}
            
            # 这里应该实现更复杂的相似度计算
            # 目前返回模拟数据
            return [("user_2", 0.8), ("user_3", 0.7), ("user_4", 0.6)]
            
        except Exception as e:
            logger.error(f"查找相似用户失败: {e}")
            return []
    
    async def _get_user_items(self, user_id: str, item_type: str) -> List[Dict]:
        """获取用户的物品"""
        try:
            # 模拟数据
            return [
                {
                    'id': 'item_1',
                    'title': '深度学习思考',
                    'content': '关于深度学习的思考内容',
                    'rating': 0.9
                }
            ]
            
        except Exception as e:
            logger.error(f"获取用户物品失败: {e}")
            return []
    
    async def _get_user_preferences(self, user_id: str) -> Dict:
        """获取用户偏好"""
        try:
            # 从用户画像中获取偏好
            user_profile = self.user_profiles.get(user_id, {})
            return user_profile.get('preferences', {})
            
        except Exception as e:
            logger.error(f"获取用户偏好失败: {e}")
            return {}
    
    async def _get_candidate_items(self, item_type: str) -> List[Dict]:
        """获取候选项目"""
        try:
            # 从Elasticsearch获取候选项目
            query = {
                "query": {
                    "term": {"type": item_type}
                },
                "size": 100
            }
            
            response = await self.es.search(index="thinking_documents", body=query)
            
            items = []
            for hit in response['hits']['hits']:
                items.append({
                    'id': hit['_id'],
                    'title': hit['_source']['title'],
                    'content': hit['_source']['content'],
                    'metadata': hit['_source']
                })
            
            return items
            
        except Exception as e:
            logger.error(f"获取候选项目失败: {e}")
            return []
    
    def _calculate_content_similarity(self, user_preferences: Dict, item: Dict) -> float:
        """计算内容相似度"""
        try:
            # 简化的相似度计算
            # 实际应用中应该使用更复杂的算法
            
            # 基于标签的相似度
            user_tags = set(user_preferences.get('tags', []))
            item_tags = set(item.get('metadata', {}).get('tags', []))
            
            if not user_tags or not item_tags:
                return 0.0
            
            intersection = len(user_tags & item_tags)
            union = len(user_tags | item_tags)
            
            jaccard_similarity = intersection / union if union > 0 else 0.0
            
            return jaccard_similarity
            
        except Exception as e:
            logger.error(f"计算内容相似度失败: {e}")
            return 0.0
    
    async def index_documents(self, documents: List[Dict], index_name: str = "thinking_documents"):
        """索引文档"""
        try:
            # 准备批量索引数据
            actions = []
            embeddings = []
            
            for doc in documents:
                # 生成向量
                content = f"{doc.get('title', '')} {doc.get('content', '')}"
                embedding = self.sentence_transformer.encode([content])[0]
                
                # 添加到Elasticsearch
                doc_copy = doc.copy()
                doc_copy['embedding'] = embedding.tolist()
                doc_copy['created_at'] = datetime.now().isoformat()
                
                actions.append({
                    "_index": index_name,
                    "_id": doc.get('id', str(uuid.uuid4())),
                    "_source": doc_copy
                })
                
                # 添加到ChromaDB
                embeddings.append({
                    'id': doc.get('id', str(uuid.uuid4())),
                    'embedding': embedding.tolist(),
                    'document': content,
                    'metadata': doc
                })
            
            # 批量索引到Elasticsearch
            await async_bulk(self.es, actions)
            
            # 批量添加到ChromaDB
            if embeddings:
                self.thinking_collection.add(
                    embeddings=[e['embedding'] for e in embeddings],
                    documents=[e['document'] for e in embeddings],
                    metadatas=[e['metadata'] for e in embeddings],
                    ids=[e['id'] for e in embeddings]
                )
            
            logger.info(f"成功索引 {len(documents)} 个文档")
            
        except Exception as e:
            logger.error(f"索引文档失败: {e}")
            raise
    
    async def update_user_behavior(self, user_id: str, action: str, item_id: str, item_type: str):
        """更新用户行为"""
        try:
            behavior_data = {
                "user_id": user_id,
                "action": action,
                "item_id": item_id,
                "item_type": item_type,
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4())
            }
            
            # 索引到Elasticsearch
            await self.es.index(
                index="user_behavior",
                body=behavior_data
            )
            
            # 更新用户画像
            await self._update_user_profile(user_id, behavior_data)
            
        except Exception as e:
            logger.error(f"更新用户行为失败: {e}")
    
    async def _update_user_profile(self, user_id: str, behavior_data: Dict):
        """更新用户画像"""
        try:
            # 获取现有画像
            profile_key = f"user_profile:{user_id}"
            existing_profile = await self.redis_client.get(profile_key)
            
            if existing_profile:
                profile = json.loads(existing_profile)
            else:
                profile = {
                    "user_id": user_id,
                    "preferences": {"tags": []},
                    "behavior_count": defaultdict(int),
                    "last_active": datetime.now().isoformat()
                }
            
            # 更新行为计数
            profile["behavior_count"][behavior_data["action"]] += 1
            profile["last_active"] = datetime.now().isoformat()
            
            # 保存到Redis
            await self.redis_client.set(
                profile_key,
                json.dumps(profile, default=str),
                ex=86400 * 30  # 30天过期
            )
            
            # 更新内存中的画像
            self.user_profiles[user_id] = profile
            
        except Exception as e:
            logger.error(f"更新用户画像失败: {e}")
    
    async def get_search_suggestions(self, query: str, limit: int = 5) -> List[str]:
        """获取搜索建议"""
        try:
            # 基于历史查询的建议
            suggestions = []
            
            # 从Redis获取热门搜索
            hot_searches = await self.redis_client.zrevrange("hot_searches", 0, limit-1)
            
            # 过滤相关的搜索
            for search_term in hot_searches:
                if query.lower() in search_term.lower() or search_term.lower() in query.lower():
                    suggestions.append(search_term)
            
            # 如果建议不够，添加基于分词的建议
            if len(suggestions) < limit:
                words = list(jieba.cut(query))
                for word in words:
                    if len(word) > 1:
                        suggestions.append(f"{word} 相关")
            
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"获取搜索建议失败: {e}")
            return []
    
    async def get_search_facets(self, query: str) -> Dict[str, List[Dict]]:
        """获取搜索分面"""
        try:
            # 执行聚合查询
            agg_query = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "content", "summary"]
                    }
                },
                "aggs": {
                    "types": {
                        "terms": {"field": "type", "size": 10}
                    },
                    "tags": {
                        "terms": {"field": "tags", "size": 10}
                    },
                    "date_histogram": {
                        "date_histogram": {
                            "field": "created_at",
                            "calendar_interval": "month"
                        }
                    }
                },
                "size": 0
            }
            
            response = await self.es.search(index="thinking_documents", body=agg_query)
            
            facets = {}
            
            # 处理聚合结果
            for agg_name, agg_result in response['aggregations'].items():
                facets[agg_name] = []
                
                if 'buckets' in agg_result:
                    for bucket in agg_result['buckets']:
                        facets[agg_name].append({
                            'key': bucket['key'],
                            'count': bucket['doc_count']
                        })
            
            return facets
            
        except Exception as e:
            logger.error(f"获取搜索分面失败: {e}")
            return {}
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.es:
                await self.es.close()
            if self.redis_client:
                await self.redis_client.close()
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("搜索引擎资源清理完成")
            
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

# 全局搜索引擎实例
search_engine = AISearchEngine()

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await search_engine.initialize()
    yield
    # 关闭时清理
    await search_engine.cleanup()

# 创建FastAPI应用
app = FastAPI(
    title="AI搜索引擎",
    description="智能搜索和推荐系统",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # 这里应该验证JWT token
    # 目前返回模拟用户
    return {"user_id": "test_user", "username": "test"}

# API端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """搜索文档"""
    try:
        start_time = asyncio.get_event_loop().time()
        
        # 更新搜索历史
        await search_engine.redis_client.zincrby("hot_searches", 1, request.query)
        
        # 根据搜索类型执行搜索
        if request.search_type == "semantic":
            results = await search_engine.semantic_search(
                request.query, request.limit, request.filters
            )
        elif request.search_type == "keyword":
            results = await search_engine.keyword_search(
                request.query, request.limit, request.filters
            )
        elif request.search_type == "multimodal":
            results = await search_engine.multimodal_search(
                request.query, request.limit, request.filters
            )
        else:  # hybrid
            results = await search_engine.hybrid_search(
                request.query, request.limit, request.filters
            )
        
        # 记录用户搜索行为
        if request.user_id:
            await search_engine.update_user_behavior(
                request.user_id, "search", request.query, "query"
            )
        
        # 获取搜索建议和分面
        suggestions = await search_engine.get_search_suggestions(request.query)
        facets = await search_engine.get_search_facets(request.query)
        
        # 格式化结果
        formatted_results = []
        for result in results:
            formatted_results.append(SearchResult(
                id=result['id'],
                content=result['content'],
                title=result.get('title', ''),
                type=result.get('metadata', {}).get('type', 'unknown'),
                score=result['score'],
                source=result.get('search_type', 'unknown'),
                metadata=result.get('metadata', {}),
                created_at=datetime.now(),
                relevance_reason=result.get('highlights', {}).get('content', [''])[0] if result.get('highlights') else ''
            ))
        
        query_time = asyncio.get_event_loop().time() - start_time
        
        return SearchResponse(
            results=formatted_results,
            total=len(formatted_results),
            query_time=query_time,
            search_type=request.search_type,
            suggestions=suggestions,
            facets=facets
        )
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index")
async def index_documents(
    request: IndexRequest,
    current_user: dict = Depends(get_current_user)
):
    """索引文档"""
    try:
        await search_engine.index_documents(request.documents, request.index_name)
        return {"message": f"成功索引 {len(request.documents)} 个文档"}
        
    except Exception as e:
        logger.error(f"索引失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend", response_model=List[RecommendationResult])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: dict = Depends(get_current_user)
):
    """获取推荐"""
    try:
        recommendations = await search_engine.get_recommendations(
            request.user_id, request.item_type, request.limit
        )
        
        formatted_recommendations = []
        for rec in recommendations:
            formatted_recommendations.append(RecommendationResult(
                id=rec['id'],
                title=rec['title'],
                content=rec['content'],
                score=rec['score'],
                reason=rec['reason'],
                type=rec['type']
            ))
        
        return formatted_recommendations
        
    except Exception as e:
        logger.error(f"获取推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/behavior")
async def update_user_behavior(
    user_id: str,
    action: str,
    item_id: str,
    item_type: str,
    current_user: dict = Depends(get_current_user)
):
    """更新用户行为"""
    try:
        await search_engine.update_user_behavior(user_id, action, item_id, item_type)
        return {"message": "用户行为更新成功"}
        
    except Exception as e:
        logger.error(f"更新用户行为失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggestions")
async def get_search_suggestions(
    query: str,
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """获取搜索建议"""
    try:
        suggestions = await search_engine.get_search_suggestions(query, limit)
        return {"suggestions": suggestions}
        
    except Exception as e:
        logger.error(f"获取搜索建议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_search_stats(current_user: dict = Depends(get_current_user)):
    """获取搜索统计"""
    try:
        # 获取热门搜索
        hot_searches = await search_engine.redis_client.zrevrange("hot_searches", 0, 9, withscores=True)
        
        # 获取文档统计
        doc_stats = await search_engine.es.count(index="thinking_documents")
        
        return {
            "hot_searches": [{"query": term, "count": int(score)} for term, score in hot_searches],
            "total_documents": doc_stats['count'],
            "total_users": len(search_engine.user_profiles)
        }
        
    except Exception as e:
        logger.error(f"获取搜索统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8087) 