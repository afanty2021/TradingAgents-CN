"""
安全密钥管理器
提供API密钥的安全存储、轮换和审计功能
"""

import os
import json
import hashlib
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from tradingagents.exceptions import SecurityError, AuthenticationError
from tradingagents.utils.logging_init import get_logger

logger = get_logger(__name__)


@dataclass
class KeyMetadata:
    """密钥元数据"""
    key_id: str
    provider: str
    created_at: datetime
    last_rotated: Optional[datetime] = None
    rotation_interval_days: int = 90
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    status: str = "active"  # active, expired, revoked
    risk_level: str = "low"  # low, medium, high
    environment: str = "development"


@dataclass
class KeyAuditLog:
    """密钥审计日志"""
    timestamp: datetime
    key_id: str
    action: str  # created, accessed, rotated, revoked, deleted
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None


class SecureKeyManager:
    """安全密钥管理器"""

    def __init__(self, master_key_env: str = "MASTER_KEY",
                 keys_file: str = "keys.enc",
                 audit_log_file: str = "key_audit.log"):
        """
        初始化安全密钥管理器

        Args:
            master_key_env: 主密钥环境变量名
            keys_file: 加密密钥文件路径
            audit_log_file: 审计日志文件路径
        """
        self.master_key_env = master_key_env
        self.keys_file = keys_file
        self.audit_log_file = audit_log_file

        # 初始化加密器
        self.cipher = None
        self._initialize_cipher()

        # 加载密钥数据
        self.keys: Dict[str, Any] = {}
        self.key_metadata: Dict[str, KeyMetadata] = {}
        self.audit_logs: List[KeyAuditLog] = []

        # 加载现有数据
        self._load_keys()
        self._load_audit_logs()

        # 自动轮换检查
        self._auto_rotation_check()

        logger.info("🔐 安全密钥管理器初始化完成")

    def _initialize_cipher(self):
        """初始化加密器"""
        try:
            master_key = os.getenv(self.master_key_env)
            if not master_key:
                raise SecurityError("主密钥未设置", 'MASTER_KEY_NOT_SET')

            # 验证主密钥格式
            if not self._validate_master_key_format(master_key):
                raise SecurityError("主密钥格式无效", 'INVALID_MASTER_KEY')

            # 生成加密密钥
            key = base64.urlsafe_b64decode(master_key.encode())
            self.cipher = Fernet(key)

            logger.debug("✅ 加密器初始化成功")

        except Exception as e:
            logger.error(f"加密器初始化失败: {e}")
            raise SecurityError(f"加密器初始化失败: {e}", 'CIPHER_INIT_FAILED')

    def _validate_master_key_format(self, key: str) -> bool:
        """验证主密钥格式"""
        try:
            # 尝试base64解码
            decoded = base64.urlsafe_b64decode(key)

            # 检查长度（Fernet需要32字节密钥）
            return len(decoded) == 32

        except Exception:
            return False

    def store_key(self, provider: str, api_key: str,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        安全存储API密钥

        Args:
            provider: 提供商名称
            api_key: API密钥
            metadata: 额外的元数据

        Returns:
            bool: 是否存储成功
        """
        try:
            # 验证密钥格式
            if not self._validate_api_key_format(provider, api_key):
                raise SecurityError(f"无效的{provider} API密钥格式", 'INVALID_API_KEY_FORMAT')

            # 生成密钥ID
            key_id = self._generate_key_id(provider)

            # 评估风险级别
            risk_level = self._assess_key_risk(api_key, provider)

            # 创建元数据
            key_metadata = KeyMetadata(
                key_id=key_id,
                provider=provider,
                created_at=datetime.now(),
                rotation_interval_days=self._get_rotation_interval(provider),
                access_count=0,
                risk_level=risk_level,
                environment=os.getenv('ENVIRONMENT', 'development'),
                **(metadata or {})
            )

            # 加密存储密钥
            encrypted_key = self._encrypt_data(api_key)

            # 存储到内存
            self.keys[key_id] = {
                'encrypted_key': encrypted_key,
                'provider': provider,
                'created_at': datetime.now().isoformat()
            }
            self.key_metadata[key_id] = key_metadata

            # 持久化存储
            self._save_keys()

            # 记录审计日志
            self._log_key_action('created', key_id, success=True)

            logger.info(f"✅ API密钥已安全存储: {provider} (ID: {key_id})")
            return True

        except Exception as e:
            error_msg = f"存储{provider} API密钥失败: {e}"
            logger.error(error_msg)
            self._log_key_action('created', provider, success=False, error_message=error_msg)
            return False

    def get_key(self, provider: str, key_id: Optional[str] = None) -> Optional[str]:
        """
        安全获取API密钥

        Args:
            provider: 提供商名称
            key_id: 特定的密钥ID（可选）

        Returns:
            Optional[str]: API密钥或None
        """
        try:
            # 查找密钥
            key_id = key_id or self._find_key_by_provider(provider)
            if not key_id:
                self._log_key_action('accessed', provider, success=False,
                                 error_message=f"未找到{provider}的密钥")
                return None

            # 检查密钥状态
            metadata = self.key_metadata.get(key_id)
            if not metadata:
                self._log_key_action('accessed', key_id, success=False,
                                 error_message="密钥元数据缺失")
                return None

            # 检查是否过期
            if self._is_key_expired(metadata):
                self._log_key_action('accessed', key_id, success=False,
                                 error_message="密钥已过期")
                return None

            # 检查是否被撤销
            if metadata.status != "active":
                self._log_key_action('accessed', key_id, success=False,
                                 error_message=f"密钥状态: {metadata.status}")
                return None

            # 获取加密密钥
            key_data = self.keys.get(key_id)
            if not key_data:
                self._log_key_action('accessed', key_id, success=False,
                                 error_message="加密密钥数据缺失")
                return None

            # 解密密钥
            api_key = self._decrypt_data(key_data['encrypted_key'])

            # 更新访问统计
            metadata.access_count += 1
            metadata.last_accessed = datetime.now()
            self.key_metadata[key_id] = metadata

            # 记录审计日志
            self._log_key_action('accessed', key_id, success=True)

            logger.debug(f"🔑 API密钥已安全获取: {provider} (ID: {key_id})")
            return api_key

        except Exception as e:
            error_msg = f"获取{provider} API密钥失败: {e}"
            logger.error(error_msg)
            self._log_key_action('accessed', key_id or provider, success=False,
                             error_message=error_msg)
            return None

    def rotate_key(self, provider: str, new_api_key: str) -> bool:
        """
        轮换API密钥

        Args:
            provider: 提供商名称
            new_api_key: 新的API密钥

        Returns:
            bool: 是否轮换成功
        """
        try:
            # 查找现有密钥
            old_key_id = self._find_key_by_provider(provider)
            if not old_key_id:
                # 如果没有现有密钥，直接存储新密钥
                return self.store_key(provider, new_api_key)

            old_metadata = self.key_metadata.get(old_key_id)
            if not old_metadata:
                raise SecurityError(f"无法找到{provider}的密钥元数据", 'KEY_METADATA_NOT_FOUND')

            # 验证新密钥格式
            if not self._validate_api_key_format(provider, new_api_key):
                raise SecurityError(f"无效的{provider}新API密钥格式", 'INVALID_NEW_KEY_FORMAT')

            # 评估新密钥风险
            new_risk_level = self._assess_key_risk(new_api_key, provider)

            # 标记旧密钥为已轮换
            old_metadata.status = "rotated"
            old_metadata.last_rotated = datetime.now()
            self.key_metadata[old_key_id] = old_metadata

            # 创建新密钥条目
            new_key_id = self._generate_key_id(provider)
            new_metadata = KeyMetadata(
                key_id=new_key_id,
                provider=provider,
                created_at=datetime.now(),
                last_rotated=datetime.now(),
                rotation_interval_days=old_metadata.rotation_interval_days,
                access_count=0,
                risk_level=new_risk_level,
                environment=os.getenv('ENVIRONMENT', 'development')
            )

            # 加密存储新密钥
            encrypted_key = self._encrypt_data(new_api_key)

            # 更新数据结构
            self.keys[new_key_id] = {
                'encrypted_key': encrypted_key,
                'provider': provider,
                'created_at': datetime.now().isoformat(),
                'previous_key_id': old_key_id
            }
            self.key_metadata[new_key_id] = new_metadata

            # 持久化存储
            self._save_keys()

            # 记录审计日志
            self._log_key_action('rotated', new_key_id, success=True)
            self._log_key_action('rotated', old_key_id, success=True)

            logger.info(f"🔄 API密钥已轮换: {provider} (旧ID: {old_key_id}, 新ID: {new_key_id})")
            return True

        except Exception as e:
            error_msg = f"轮换{provider} API密钥失败: {e}"
            logger.error(error_msg)
            self._log_key_action('rotated', provider, success=False, error_message=error_msg)
            return False

    def revoke_key(self, key_id: str) -> bool:
        """
        撤销API密钥

        Args:
            key_id: 密钥ID

        Returns:
            bool: 是否撤销成功
        """
        try:
            metadata = self.key_metadata.get(key_id)
            if not metadata:
                raise SecurityError(f"密钥ID不存在: {key_id}", 'KEY_ID_NOT_FOUND')

            # 标记为已撤销
            metadata.status = "revoked"
            self.key_metadata[key_id] = metadata

            # 从活跃密钥中移除
            if key_id in self.keys:
                del self.keys[key_id]

            # 持久化存储
            self._save_keys()

            # 记录审计日志
            self._log_key_action('revoked', key_id, success=True)

            logger.info(f"🚫 API密钥已撤销: {key_id}")
            return True

        except Exception as e:
            error_msg = f"撤销密钥{key_id}失败: {e}"
            logger.error(error_msg)
            self._log_key_action('revoked', key_id, success=False, error_message=error_msg)
            return False

    def get_key_info(self, provider: str = None, key_id: str = None) -> List[Dict[str, Any]]:
        """
        获取密钥信息

        Args:
            provider: 提供商名称（可选）
            key_id: 密钥ID（可选）

        Returns:
            List[Dict[str, Any]]: 密钥信息列表
        """
        results = []

        for metadata in self.key_metadata.values():
            # 过滤条件
            if provider and metadata.provider != provider:
                continue
            if key_id and metadata.key_id != key_id:
                continue

            # 转换为字典
            info = asdict(metadata)
            info['is_expired'] = self._is_key_expired(metadata)
            info['needs_rotation'] = self._needs_rotation(metadata)

            results.append(info)

        return results

    def audit_keys(self) -> Dict[str, Any]:
        """
        审计所有密钥

        Returns:
            Dict[str, Any]: 审计结果
        """
        audit_result = {
            'timestamp': datetime.now().isoformat(),
            'total_keys': len(self.key_metadata),
            'active_keys': 0,
            'expired_keys': 0,
            'rotated_keys': 0,
            'revoked_keys': 0,
            'high_risk_keys': 0,
            'keys_needing_rotation': 0,
            'providers': {},
            'recommendations': []
        }

        for metadata in self.key_metadata.values():
            # 统计状态
            if metadata.status == "active":
                audit_result['active_keys'] += 1
            elif metadata.status == "expired":
                audit_result['expired_keys'] += 1
            elif metadata.status == "rotated":
                audit_result['rotated_keys'] += 1
            elif metadata.status == "revoked":
                audit_result['revoked_keys'] += 1

            # 统计风险
            if metadata.risk_level == "high":
                audit_result['high_risk_keys'] += 1

            # 检查是否需要轮换
            if self._needs_rotation(metadata):
                audit_result['keys_needing_rotation'] += 1

            # 按提供商统计
            provider = metadata.provider
            if provider not in audit_result['providers']:
                audit_result['providers'][provider] = {
                    'total': 0,
                    'active': 0,
                    'expired': 0,
                    'high_risk': 0
                }

            audit_result['providers'][provider]['total'] += 1
            if metadata.status == "active":
                audit_result['providers'][provider]['active'] += 1
            elif metadata.status == "expired":
                audit_result['providers'][provider]['expired'] += 1
            if metadata.risk_level == "high":
                audit_result['providers'][provider]['high_risk'] += 1

        # 生成建议
        audit_result['recommendations'] = self._generate_audit_recommendations(audit_result)

        return audit_result

    def _generate_key_id(self, provider: str) -> str:
        """生成密钥ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{provider}_{timestamp}_{hashlib.md5(provider.encode()).hexdigest()[:8]}"

    def _find_key_by_provider(self, provider: str) -> Optional[str]:
        """根据提供商查找密钥ID"""
        for key_id, metadata in self.key_metadata.items():
            if metadata.provider == provider and metadata.status == "active":
                return key_id
        return None

    def _validate_api_key_format(self, provider: str, api_key: str) -> bool:
        """验证API密钥格式"""
        # 基本格式检查
        if not api_key or len(api_key) < 10:
            return False

        # 提供商特定格式验证
        provider_formats = {
            'dashscope': lambda k: k.startswith('sk-') and len(k) == 51,
            'openai': lambda k: k.startswith('sk-') and len(k) == 51,
            'deepseek': lambda k: k.startswith('sk-') and len(k) == 56,
            'google': lambda k: len(k) >= 20 and k.replace('-', '').isalnum(),
            'finnhub': lambda k: len(k) == 32 and k.replace('-', '').isalnum(),
            'tushare': lambda k: len(k) >= 32 and k.replace('-', '').isalnum()
        }

        validator = provider_formats.get(provider.lower())
        if validator:
            return validator(api_key)

        # 通用验证：字母数字和基本特殊字符
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        return all(c in allowed_chars for c in api_key.upper())

    def _assess_key_risk(self, api_key: str, provider: str) -> str:
        """评估密钥风险级别"""
        risk_score = 0

        # 长度评分
        if len(api_key) < 20:
            risk_score += 3
        elif len(api_key) < 30:
            risk_score += 2
        elif len(api_key) < 40:
            risk_score += 1

        # 复杂度评分
        has_upper = any(c.isupper() for c in api_key)
        has_lower = any(c.islower() for c in api_key)
        has_digits = any(c.isdigit() for c in api_key)
        has_special = any(c in '-_' for c in api_key)

        complexity = sum([has_upper, has_lower, has_digits, has_special])
        if complexity < 3:
            risk_score += 2
        elif complexity < 4:
            risk_score += 1

        # 提供商风险
        high_risk_providers = ['openai', 'anthropic']
        if provider.lower() in high_risk_providers:
            risk_score += 1

        # 转换为风险级别
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"

    def _get_rotation_interval(self, provider: str) -> int:
        """获取密钥轮换间隔（天）"""
        intervals = {
            'dashscope': 90,
            'openai': 60,
            'deepseek': 90,
            'google': 90,
            'finnhub': 90,
            'tushare': 90
        }
        return intervals.get(provider.lower(), 90)

    def _is_key_expired(self, metadata: KeyMetadata) -> bool:
        """检查密钥是否过期"""
        if metadata.status in ["revoked", "expired"]:
            return True

        # 检查轮换过期
        if metadata.last_rotated:
            expiry_date = metadata.last_rotated + timedelta(days=metadata.rotation_interval_days)
            return datetime.now() > expiry_date

        return False

    def _needs_rotation(self, metadata: KeyMetadata) -> bool:
        """检查密钥是否需要轮换"""
        if metadata.status != "active":
            return False

        # 检查轮换窗口
        if metadata.last_rotated:
            rotation_window = metadata.last_rotated + timedelta(days=metadata.rotation_interval_days - 7)
            return datetime.now() > rotation_window

        # 检查创建时间
        creation_window = metadata.created_at + timedelta(days=metadata.rotation_interval_days - 7)
        return datetime.now() > creation_window

    def _encrypt_data(self, data: str) -> str:
        """加密数据"""
        if not self.cipher:
            raise SecurityError("加密器未初始化", 'CIPHER_NOT_INITIALIZED')

        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        if not self.cipher:
            raise SecurityError("加密器未初始化", 'CIPHER_NOT_INITIALIZED')

        return self.cipher.decrypt(encrypted_data.encode()).decode()

    def _load_keys(self):
        """加载密钥数据"""
        try:
            if not os.path.exists(self.keys_file):
                logger.info("📁 密钥文件不存在，将创建新文件")
                return

            with open(self.keys_file, 'r') as f:
                encrypted_data = json.load(f)

            # 解密数据
            if isinstance(encrypted_data, dict) and 'encrypted' in encrypted_data:
                decrypted_json = self._decrypt_data(encrypted_data['encrypted'])
                data = json.loads(decrypted_json)
            else:
                data = encrypted_data

            self.keys = data.get('keys', {})
            self.key_metadata = {
                key_id: KeyMetadata(**metadata)
                for key_id, metadata in data.get('metadata', {}).items()
            }

            logger.info(f"📁 已加载 {len(self.keys)} 个加密密钥")

        except Exception as e:
            logger.error(f"加载密钥失败: {e}")
            self.keys = {}
            self.key_metadata = {}

    def _save_keys(self):
        """保存密钥数据"""
        try:
            # 准备数据
            metadata_dict = {
                key_id: asdict(metadata)
                for key_id, metadata in self.key_metadata.items()
            }

            data = {
                'keys': self.keys,
                'metadata': metadata_dict,
                'saved_at': datetime.now().isoformat()
            }

            # 加密数据
            json_data = json.dumps(data, indent=2)
            encrypted_data = self._encrypt_data(json_data)

            # 保存到文件
            save_data = {
                'encrypted': encrypted_data,
                'version': '1.0'
            }

            with open(self.keys_file, 'w') as f:
                json.dump(save_data, f, indent=2)

            # 设置文件权限
            os.chmod(self.keys_file, 0o600)

            logger.debug(f"💾 已保存 {len(self.keys)} 个密钥到加密文件")

        except Exception as e:
            logger.error(f"保存密钥失败: {e}")
            raise SecurityError(f"保存密钥失败: {e}", 'KEY_SAVE_FAILED')

    def _load_audit_logs(self):
        """加载审计日志"""
        try:
            if os.path.exists(self.audit_log_file):
                with open(self.audit_log_file, 'r') as f:
                    logs = json.load(f)
                self.audit_logs = [
                    KeyAuditLog(**log) for log in logs
                ]
        except Exception as e:
            logger.debug(f"加载审计日志失败: {e}")
            self.audit_logs = []

    def _log_key_action(self, action: str, key_id: str, success: bool = True,
                      error_message: Optional[str] = None):
        """记录密钥操作日志"""
        try:
            log_entry = KeyAuditLog(
                timestamp=datetime.now(),
                key_id=key_id,
                action=action,
                success=success,
                error_message=error_message,
                user_id=os.getenv('USER_ID'),
                ip_address=os.getenv('REMOTE_ADDR')
            )

            self.audit_logs.append(log_entry)

            # 保持最近1000条记录
            if len(self.audit_logs) > 1000:
                self.audit_logs = self.audit_logs[-1000:]

            # 保存审计日志
            self._save_audit_logs()

        except Exception as e:
            logger.error(f"记录审计日志失败: {e}")

    def _save_audit_logs(self):
        """保存审计日志"""
        try:
            logs_data = [
                asdict(log) for log in self.audit_logs
            ]

            with open(self.audit_log_file, 'w') as f:
                json.dump(logs_data, f, indent=2, default=str)

            # 设置文件权限
            os.chmod(self.audit_log_file, 0o600)

        except Exception as e:
            logger.error(f"保存审计日志失败: {e}")

    def _auto_rotation_check(self):
        """自动轮换检查"""
        try:
            for key_id, metadata in self.key_metadata.items():
                if self._needs_rotation(metadata):
                    logger.warning(f"⚠️ 密钥需要轮换: {key_id} ({metadata.provider})")

                    # 可以在这里添加自动轮换逻辑
                    # 例如：如果配置了自动轮换，可以调用rotate_key

        except Exception as e:
            logger.error(f"自动轮换检查失败: {e}")

    def _generate_audit_recommendations(self, audit_result: Dict[str, Any]) -> List[str]:
        """生成审计建议"""
        recommendations = []

        if audit_result['high_risk_keys'] > 0:
            recommendations.append("发现高风险密钥，建议立即轮换")

        if audit_result['keys_needing_rotation'] > 0:
            recommendations.append(f"有 {audit_result['keys_needing_rotation']} 个密钥需要轮换")

        if audit_result['expired_keys'] > 0:
            recommendations.append(f"发现 {audit_result['expired_keys']} 个过期密钥")

        if audit_result['revoked_keys'] > audit_result['active_keys'] * 0.3:
            recommendations.append("已撤销密钥比例较高，建议清理")

        return recommendations

    def cleanup_expired_keys(self):
        """清理过期密钥"""
        try:
            expired_keys = []
            for key_id, metadata in self.key_metadata.items():
                if self._is_key_expired(metadata):
                    expired_keys.append(key_id)

            for key_id in expired_keys:
                self.revoke_key(key_id)

            logger.info(f"🧹 已清理 {len(expired_keys)} 个过期密钥")

        except Exception as e:
            logger.error(f"清理过期密钥失败: {e}")

    def export_keys_backup(self, backup_file: str, include_inactive: bool = False) -> bool:
        """导出密钥备份"""
        try:
            backup_data = {
                'exported_at': datetime.now().isoformat(),
                'include_inactive': include_inactive,
                'keys': {},
                'metadata': {},
                'audit_logs': []
            }

            for key_id, metadata in self.key_metadata.items():
                # 过滤条件
                if not include_inactive and metadata.status != "active":
                    continue

                # 只包含元数据，不包含实际密钥
                backup_data['metadata'][key_id] = asdict(metadata)

            # 包含最近的审计日志
            backup_data['audit_logs'] = [
                asdict(log) for log in self.audit_logs[-100:]
            ]

            # 加密备份
            json_data = json.dumps(backup_data, indent=2)
            encrypted_backup = self._encrypt_data(json_data)

            final_backup = {
                'encrypted': encrypted_backup,
                'version': '1.0',
                'metadata_only': True
            }

            with open(backup_file, 'w') as f:
                json.dump(final_backup, f, indent=2)

            os.chmod(backup_file, 0o600)
            logger.info(f"💾 密钥备份已导出到: {backup_file}")
            return True

        except Exception as e:
            logger.error(f"导出密钥备份失败: {e}")
            return False

    def import_keys_backup(self, backup_file: str, master_key: str) -> bool:
        """导入密钥备份"""
        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

            # 解密备份
            if 'encrypted' in backup_data:
                decrypted_backup = self._decrypt_data(backup_data['encrypted'])
                data = json.loads(decrypted_backup)
            else:
                data = backup_data

            # 验证备份格式
            if data.get('metadata_only', False):
                logger.info("📥 导入的是元数据备份，不包含实际密钥")

            # 合并数据（不覆盖现有数据）
            for key_id, metadata in data.get('metadata', {}).items():
                if key_id not in self.key_metadata:
                    self.key_metadata[key_id] = KeyMetadata(**metadata)

            self._save_keys()
            logger.info(f"📥 密钥备份已从 {backup_file} 导入")
            return True

        except Exception as e:
            logger.error(f"导入密钥备份失败: {e}")
            return False