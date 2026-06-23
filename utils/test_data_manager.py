# utils/test_data_manager.py
"""
测试数据管理模块 - 读取和管理测试数据
"""
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from config.settings import get_settings
from utils.logger import get_logger


logger = get_logger(__name__)


class TestDataManager:
    """测试数据管理器"""

    def __init__(self):
        """初始化测试数据管理器"""
        self.data_dir = get_settings().get_test_data_path()

    def load_json(self, filename: str) -> Any:
        """
        加载 JSON 格式的测试数据

        Args:
            filename: 文件名（不需要 .json 后缀）

        Returns:
            解析后的数据
        """
        file_path = self.data_dir / f"{filename}.json"
        return self._load_file(file_path, self._parse_json)

    def load_yaml(self, filename: str) -> Any:
        """
        加载 YAML 格式的测试数据

        Args:
            filename: 文件名（不需要 .yaml 后缀）

        Returns:
            解析后的数据
        """
        file_path = self.data_dir / f"{filename}.yaml"
        return self._load_file(file_path, self._parse_yaml)

    def load_env_data(self, env: Optional[str] = None) -> Dict[str, Any]:
        """
        加载环境相关的测试数据

        Args:
            env: 环境名称，默认使用配置中的 ENV

        Returns:
            环境测试数据
        """
        env = env or get_settings().ENV
        return self.load_yaml(f"{env}_data")

    def _load_file(self, file_path: Path, parser) -> Any:
        """
        通用文件加载方法

        Args:
            file_path: 文件路径
            parser: 解析器函数

        Returns:
            解析后的数据
        """
        if not file_path.exists():
            logger.warning(f"文件不存在: {file_path}")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = parser(f)
                logger.info(f"成功加载测试数据: {file_path.name}")
                return data
        except Exception as e:
            logger.error(f"加载文件失败: {file_path}, 错误: {e}")
            raise

    @staticmethod
    def _parse_json(file) -> Dict[str, Any]:
        """解析 JSON 文件"""
        return json.load(file)

    @staticmethod
    def _parse_yaml(file) -> Dict[str, Any]:
        """解析 YAML 文件"""
        return yaml.safe_load(file) or {}

    def save_json(self, filename: str, data: Any) -> None:
        """
        保存数据为 JSON 文件

        Args:
            filename: 文件名
            data: 要保存的数据
        """
        file_path = self.data_dir / f"{filename}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"数据已保存: {file_path.name}")
        except Exception as e:
            logger.error(f"保存数据失败: {file_path}, 错误: {e}")
            raise

    def get_test_case(self, module: str, case_name: str) -> Dict[str, Any]:
        """
        获取指定的测试用例数据

        Args:
            module: 模块名称
            case_name: 用例名称

        Returns:
            测试用例数据
        """
        test_data = self.load_yaml(module)
        return test_data.get('test_cases', {}).get(case_name, {})


# 全局测试数据管理器实例
test_data_manager = TestDataManager()


def get_test_data_manager() -> TestDataManager:
    """获取测试数据管理器实例"""
    return test_data_manager