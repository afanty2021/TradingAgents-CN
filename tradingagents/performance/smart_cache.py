"""
智能缓存系统
提供多级缓存、智能决策和自动优化功能
"""

import time
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
from collections import OrderedDict
import math

from tradingagents.exceptions import CacheError
from tradingagents.utils.logging_init import get_logger

logger = get_logger(__name__)


class CacheLevel(Enum):
    """缓存级别"""
    MEMORY = "memory"      # 内存缓存 (最快)
    REDIS = "redis"        # Redis缓存 (较快)
    MONGODB = "mongodb"    # MongoDB缓存 (持久化)
    FILE = "file"          # 文件缓存 (最慢)


class CacheStrategy(Enum):
    """缓存策略"""
    LRU = "lru"              # 最近最少使用
    LFU = "lfu"              # 最少使用频率
    TTL = "ttl"              # 时间过期
    ADAPTIVE = "adaptive"      # 自适应策略


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    cost: float = 0.0  # 获取成本（时间）
    hit_count: int = 0  # 命中次数
    miss_count: int = 0  # 未命中次数

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)

    def update_access(self):
        """更新访问信息"""
        self.last_accessed = time.time()
        self.access_count += 1

    def calculate_score(self, current_time: float) -> float:
        """计算缓存分数（用于LRU/LFU策略）"""
        age = current_time - self.last_accessed
        frequency = self.access_count

        # 综合分数（新访问 + 高频率 = 高分数）
        return frequency * 1000 - age


@dataclass
class CacheStats:
    """缓存统计"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0
    avg_access_time_ms: float = 0.0
    hit_rate: float = 0.0

    def update_hit(self):
        """更新命中统计"""
        self.total_requests += 1
        self.cache_hits += 1
        self.hit_rate = (self.cache_hits / self.total_requests) * 100

    def update_miss(self):
        """更新未命中统计"""
        self.total_requests += 1
        self.cache_misses += 1
        self.hit_rate = (self.cache_hits / self.total_requests) * 100

    def update_eviction(self):
        """更新驱逐统计"""
        self.evictions += 1


class SmartCacheManager:
    """智能缓存管理器"""

    def __init__(self,
                 max_memory_size: int = 100 * 1024 * 1024,  # 100MB
                 max_entries: int = 10000,
                 strategy: CacheStrategy = CacheStrategy.ADAPTIVE,
                 enable_redis: bool = True,
                 enable_mongodb: bool = True):
        """
        初始化智能缓存管理器

        Args:
            max_memory_size: 最大内存使用量（字节）
            max_entries: 最大缓存条目数
            strategy: 缓存策略
            enable_redis: 是否启用Redis
            enable_mongodb: 是否启用MongoDB
        """
        self.max_memory_size = max_memory_size
        self.max_entries = max_entries
        self.strategy = strategy

        # 多级缓存
        self.memory_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.redis_cache = None
        self.mongodb_cache = None
        self.file_cache_path = "/tmp/tradingagents_cache.json"

        # 统计信息
        self.stats = CacheStats()
        self.lock = threading.RLock()

        # 初始化外部缓存
        if enable_redis:
            self._init_redis_cache()
        if enable_mongodb:
            self._init_mongodb_cache()

        logger.info(f"🚀 智能缓存管理器初始化完成 - 策略: {strategy.value}")

    def _init_redis_cache(self):
        """初始化Redis缓存"""
        try:
            import redis
            self.redis_cache = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # 测试连接
            self.redis_cache.ping()
            logger.info("✅ Redis缓存连接成功")
        except Exception as e:
            logger.warning(f"⚠️ Redis缓存连接失败: {e}")
            self.redis_cache = None

    def _init_mongodb_cache(self):
        """初始化MongoDB缓存"""
        try:
            from pymongo import MongoClient
            self.mongodb_cache = MongoClient(
                'mongodb://localhost:27017/',
                serverSelectionTimeoutMS=5000
            )
            # 测试连接
            self.mongodb_cache.admin.command('ping')
            self.mongodb_db = self.mongodb_cache.tradingagents_cache
            self.mongodb_collection = self.mongodb_db.cache_entries
            logger.info("✅ MongoDB缓存连接成功")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB缓存连接失败: {e}")
            self.mongodb_cache = None

    def get(self, key: str, default: Any = None,
            level: CacheLevel = CacheLevel.MEMORY) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值
            level: 优先使用的缓存级别

        Returns:
            缓存值或默认值
        """
        start_time = time.time()

        with self.lock:
            try:
                # 1. 尝试内存缓存
                if level == CacheLevel.MEMORY:
                    value = self._get_from_memory(key)
                    if value is not None:
                        self.stats.update_hit()
                        self._record_access_time(start_time)
                        return value

                # 2. 尝试Redis缓存
                if level in [CacheLevel.REDIS, CacheLevel.MEMORY] and self.redis_cache:
                    value = self._get_from_redis(key)
                    if value is not None:
                        self.stats.update_hit()
                        # 提升到内存缓存
                        if level == CacheLevel.REDIS:
                            self._set_to_memory(key, value, ttl=3600)
                        self._record_access_time(start_time)
                        return value

                # 3. 尝试MongoDB缓存
                if level in [CacheLevel.MONGODB, CacheLevel.REDIS, CacheLevel.MEMORY] and self.mongodb_cache:
                    value = self._get_from_mongodb(key)
                    if value is not None:
                        self.stats.update_hit()
                        # 提升到上级缓存
                        if level == CacheLevel.MONGODB:
                            self._set_to_memory(key, value, ttl=7200)
                            if self.redis_cache:
                                self._set_to_redis(key, value, ttl=7200)
                        self._record_access_time(start_time)
                        return value

                # 4. 尝试文件缓存
                value = self._get_from_file(key)
                if value is not None:
                    self.stats.update_hit()
                    # 提升到上级缓存
                    self._set_to_memory(key, value, ttl=14400)
                    if self.redis_cache:
                        self._set_to_redis(key, value, ttl=14400)
                    self._record_access_time(start_time)
                    return value

                # 5. 缓存未命中
                self.stats.update_miss()
                self._record_access_time(start_time)
                return default

            except Exception as e:
                logger.error(f"获取缓存失败 {key}: {e}")
                self.stats.update_miss()
                return default

    def set(self, key: str, value: Any, ttl: Optional[float] = None,
              levels: List[CacheLevel] = None) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 生存时间（秒）
            levels: 要设置的缓存级别列表

        Returns:
            是否设置成功
        """
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS, CacheLevel.MONGODB]

        try:
            with self.lock:
                success = True

                # 计算值大小
                value_size = self._calculate_size(value)

                # 检查是否需要驱逐
                if self._should_evict(key, value_size):
                    self._evict_entries(value_size)

                # 设置到指定级别
                for level in levels:
                    if level == CacheLevel.MEMORY:
                        success &= self._set_to_memory(key, value, ttl)
                    elif level == CacheLevel.REDIS and self.redis_cache:
                        success &= self._set_to_redis(key, value, ttl)
                    elif level == CacheLevel.MONGODB and self.mongodb_cache:
                        success &= self._set_to_mongodb(key, value, ttl)

                return success

        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False

    def delete(self, key: str, levels: List[CacheLevel] = None) -> bool:
        """
        删除缓存值

        Args:
            key: 缓存键
            levels: 要删除的缓存级别列表

        Returns:
            是否删除成功
        """
        if levels is None:
            levels = [CacheLevel.MEMORY, CacheLevel.REDIS, CacheLevel.MONGODB]

        try:
            with self.lock:
                success = True

                for level in levels:
                    if level == CacheLevel.MEMORY and key in self.memory_cache:
                        del self.memory_cache[key]
                    elif level == CacheLevel.REDIS and self.redis_cache:
                        self.redis_cache.delete(key)
                    elif level == CacheLevel.MONGODB and self.mongodb_cache:
                        self.mongodb_collection.delete_one({'key': key})

                return success

        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False

    def clear(self, level: Optional[CacheLevel] = None):
        """
        清空缓存

        Args:
            level: 要清空的缓存级别，None表示全部清空
        """
        try:
            with self.lock:
                if level is None or level == CacheLevel.MEMORY:
                    self.memory_cache.clear()
                    self.stats.memory_usage_bytes = 0

                if level is None or level == CacheLevel.REDIS and self.redis_cache:
                    self.redis_cache.flushdb()

                if level is None or level == CacheLevel.MONGODB and self.mongodb_cache:
                    self.mongodb_collection.delete_many({})

                logger.info(f"✅ 缓存已清空: {level.value if level else '全部'}")

        except Exception as e:
            logger.error(f"清空缓存失败: {e}")

    def _get_from_memory(self, key: str) -> Optional[Any]:
        """从内存缓存获取"""
        entry = self.memory_cache.get(key)
        if entry is None:
            return None

        if entry.is_expired():
            del self.memory_cache[key]
            return None

        entry.update_access()
        return entry.value

    def _get_from_redis(self, key: str) -> Optional[Any]:
        """从Redis缓存获取"""
        try:
            data = self.redis_cache.get(key)
            if data is None:
                return None

            cache_data = json.loads(data)
            if cache_data.get('ttl') and time.time() > cache_data['created_at'] + cache_data['ttl']:
                self.redis_cache.delete(key)
                return None

            return cache_data.get('value')
        except Exception as e:
            logger.debug(f"Redis获取失败 {key}: {e}")
            return None

    def _get_from_mongodb(self, key: str) -> Optional[Any]:
        """从MongoDB缓存获取"""
        try:
            doc = self.mongodb_collection.find_one({'key': key})
            if doc is None:
                return None

            if doc.get('ttl') and time.time() > doc['created_at'] + doc['ttl']:
                self.mongodb_collection.delete_one({'key': key})
                return None

            return doc.get('value')
        except Exception as e:
            logger.debug(f"MongoDB获取失败 {key}: {e}")
            return None

    def _get_from_file(self, key: str) -> Optional[Any]:
        """从文件缓存获取"""
        try:
            import os
            if not os.path.exists(self.file_cache_path):
                return None

            with open(self.file_cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            if key not in cache_data:
                return None

            entry_data = cache_data[key]
            if entry_data.get('ttl') and time.time() > entry_data['created_at'] + entry_data['ttl']:
                del cache_data[key]
                self._save_file_cache(cache_data)
                return None

            return entry_data.get('value')
        except Exception as e:
            logger.debug(f"文件缓存获取失败 {key}: {e}")
            return None

    def _set_to_memory(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置到内存缓存"""
        try:
            entry = CacheEntry(
                key=key,
                value=value,
                ttl=ttl,
                size_bytes=self._calculate_size(value)
            )

            self.memory_cache[key] = entry
            self._update_memory_usage()

            # 驱逐策略
            if len(self.memory_cache) > self.max_entries:
                self._evict_by_strategy()

            return True
        except Exception as e:
            logger.error(f"内存缓存设置失败 {key}: {e}")
            return False

    def _set_to_redis(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置到Redis缓存"""
        try:
            cache_data = {
                'value': value,
                'created_at': time.time(),
                'ttl': ttl
            }

            serialized = json.dumps(cache_data, default=str)
            if ttl:
                self.redis_cache.setex(key, int(ttl), serialized)
            else:
                self.redis_cache.set(key, serialized)

            return True
        except Exception as e:
            logger.error(f"Redis缓存设置失败 {key}: {e}")
            return False

    def _set_to_mongodb(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置到MongoDB缓存"""
        try:
            cache_data = {
                'key': key,
                'value': value,
                'created_at': time.time(),
                'ttl': ttl
            }

            # 如果有TTL，设置过期索引
            if ttl:
                cache_data['expire_at'] = time.time() + ttl

            self.mongodb_collection.replace_one(
                {'key': key},
                cache_data,
                upsert=True
            )

            return True
        except Exception as e:
            logger.error(f"MongoDB缓存设置失败 {key}: {e}")
            return False

    def _should_evict(self, new_key: str, new_size: int) -> bool:
        """判断是否需要驱逐"""
        # 检查条目数量限制
        if len(self.memory_cache) >= self.max_entries:
            return True

        # 检查内存大小限制
        if self.stats.memory_usage_bytes + new_size > self.max_memory_size:
            return True

        return False

    def _evict_entries(self, required_space: int):
        """驱逐缓存条目"""
        entries_to_evict = []

        # 计算需要释放的空间
        current_time = time.time()
        total_freed = 0

        # 根据策略选择驱逐条目
        if self.strategy == CacheStrategy.LRU:
            entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed
            )
        elif self.strategy == CacheStrategy.LFU:
            entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].access_count
            )
        else:  # ADAPTIVE
            entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].calculate_score(current_time)
            )

        # 选择要驱逐的条目
        for key, entry in entries:
            entries_to_evict.append(key)
            total_freed += entry.size_bytes

            if total_freed >= required_space:
                break

        # 执行驱逐
        for key in entries_to_evict:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                del self.memory_cache[key]
                self.stats.update_eviction()

        self._update_memory_usage()

    def _evict_by_strategy(self):
        """根据策略驱逐单个条目"""
        if not self.memory_cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # 移除最久未访问的
            oldest_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].last_accessed
            )
        elif self.strategy == CacheStrategy.LFU:
            # 移除最少使用的
            least_used_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].access_count
            )
        else:  # ADAPTIVE
            current_time = time.time()
            worst_key = min(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k].calculate_score(current_time)
            )
            oldest_key = worst_key

        if oldest_key in self.memory_cache:
            del self.memory_cache[oldest_key]
            self.stats.update_eviction()

    def _calculate_size(self, value: Any) -> int:
        """计算值的大小"""
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (dict, list)):
                return len(json.dumps(value, default=str).encode('utf-8'))
            elif isinstance(value, bytes):
                return len(value)
            else:
                # 其他类型的估算
                return len(str(value).encode('utf-8'))
        except Exception:
            return 1024  # 默认1KB

    def _update_memory_usage(self):
        """更新内存使用统计"""
        total_size = sum(
            entry.size_bytes for entry in self.memory_cache.values()
        )
        self.stats.memory_usage_bytes = total_size

    def _record_access_time(self, start_time: float):
        """记录访问时间"""
        access_time = (time.time() - start_time) * 1000  # 转换为毫秒
        if self.stats.total_requests > 0:
            # 计算移动平均
            alpha = 0.1  # 平滑因子
            self.stats.avg_access_time_ms = (
                alpha * access_time +
                (1 - alpha) * self.stats.avg_access_time_ms
            )
        else:
            self.stats.avg_access_time_ms = access_time

    def _save_file_cache(self, cache_data: Dict):
        """保存文件缓存"""
        try:
            import os
            os.makedirs(os.path.dirname(self.file_cache_path), exist_ok=True)
            with open(self.file_cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存文件缓存失败: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            'total_requests': self.stats.total_requests,
            'cache_hits': self.stats.cache_hits,
            'cache_misses': self.stats.cache_misses,
            'hit_rate': self.stats.hit_rate,
            'evictions': self.stats.evictions,
            'memory_usage_bytes': self.stats.memory_usage_bytes,
            'memory_usage_mb': self.stats.memory_usage_bytes / (1024 * 1024),
            'avg_access_time_ms': self.stats.avg_access_time_ms,
            'memory_entries': len(self.memory_cache),
            'strategy': self.strategy.value,
            'redis_available': self.redis_cache is not None,
            'mongodb_available': self.mongodb_cache is not None
        }

    def optimize(self):
        """优化缓存性能"""
        logger.info("🔧 开始缓存优化...")

        # 1. 清理过期条目
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.memory_cache[key]

        # 2. 重新排序（基于访问频率）
        if self.strategy == CacheStrategy.LFU:
            sorted_entries = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )
            self.memory_cache = OrderedDict(sorted_entries)

        # 3. 内存使用优化
        if self.stats.memory_usage_bytes > self.max_memory_size * 0.8:
            # 驱逐到80%以下
            target_size = int(self.max_memory_size * 0.7)
            self._evict_entries(self.stats.memory_usage_bytes - target_size)

        self._update_memory_usage()
        logger.info(f"✅ 缓存优化完成 - 清理过期: {len(expired_keys)} 条目")