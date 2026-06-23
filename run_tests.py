#!/usr/bin/env python
"""
Litemall API 自动化测试 — 主入口

用法:
    python run_tests.py                      # 全部测试
    python run_tests.py -m smoke             # 冒烟测试
    python run_tests.py -k auth              # 认证模块
    python run_tests.py -k shopping          # 业务流
    python run_tests.py -m smoke -n 4        # 4 线程并行冒烟
    python run_tests.py --cov               # 带覆盖率
    python run_tests.py --no-report         # 不生成 HTML 报告
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).parent
from config.settings import get_settings

settings = get_settings()


def check_server() -> bool:
    """检查 Litemall 后端是否可达"""
    url = f"{settings.get_base_url()}/wx/home/index"
    print(f"🔍  检查后端连通性: {url}")
    try:
        resp = requests.get(url, timeout=5)
        print(f"    响应: HTTP {resp.status_code}  | errno={resp.json().get('errno', '?')}")
        return True
    except requests.ConnectionError:
        print(f"❌  无法连接后端，请确认 Litemall 已启动在 {settings.get_base_url()}")
        return False
    except requests.Timeout:
        print(f"❌  后端连接超时")
        return False


def build_args(args: argparse.Namespace) -> list[str]:
    """根据命令行参数构建 pytest 参数列表"""
    pytest_args = ["-v"]

    # 测试目标
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
    if args.marker:
        pytest_args.extend(["-m", args.marker])
    if args.test_file:
        pytest_args.append(str(ROOT / "tests" / args.test_file))

    # 报告
    if not args.no_report:
        pytest_args.extend(["--html", str(ROOT / "reports" / "report.html"), "--self-contained-html"])

    # 覆盖率
    if args.cov:
        pytest_args.extend(["--cov=tests", "--cov-report=html", "--cov-report=term"])

    # 并行
    if args.parallel:
        pytest_args.extend(["-n", str(args.parallel)])
    elif args.parallel_auto:
        pytest_args.append("-n auto")

    # 输出
    if args.quiet:
        pytest_args = [a for a in pytest_args if a != "-v"]
    if args.tb:
        pytest_args.extend(["--tb", args.tb])

    # 透传
    if args.pytest_args:
        pytest_args.extend(args.pytest_args)

    return pytest_args


def main():
    parser = argparse.ArgumentParser(
        description="Litemall API 自动化测试入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py                        全部测试
  python run_tests.py -k auth                认证模块
  python run_tests.py -k shopping            下单业务流
  python run_tests.py -m smoke               冒烟测试
  python run_tests.py -m smoke -n 4          4 线程并行冒烟
  python run_tests.py --cov                  带覆盖率
  python run_tests.py --no-report            不生成 HTML 报告
  python run_tests.py --tb=long              详细回溯
        """,
    )

    # 测试选择
    group = parser.add_argument_group("测试选择")
    group.add_argument("-k", "--keyword", help="按关键字过滤测试（如 auth、shopping、login）")
    group.add_argument("-m", "--marker", choices=["smoke", "regression", "api", "slow"], help="按标记过滤")
    group.add_argument("-f", "--test-file", help="指定测试文件（如 test_litemall_auth.py）")

    # 执行方式
    group = parser.add_argument_group("执行方式")
    group.add_argument("-n", "--parallel", type=int, default=0, help="并行线程数（如 -n 4）")
    group.add_argument("--parallel-auto", action="store_true", help="自动并行（pytest -n auto）")
    group.add_argument("--cov", action="store_true", help="生成覆盖率报告（htmlcov/）")

    # 输出控制
    group = parser.add_argument_group("输出控制")
    group.add_argument("-q", "--quiet", action="store_true", help="安静模式")
    group.add_argument("--tb", choices=["auto", "long", "short", "line", "native", "no"], default="short", help="回溯模式（默认 short）")
    group.add_argument("--no-report", action="store_true", help="不生成 HTML 报告")

    # 透传
    group = parser.add_argument_group("其他")
    group.add_argument("--no-check", action="store_true", help="跳过服务连通性检查")
    group.add_argument("pytest_args", nargs="*", help="透传给 pytest 的额外参数")

    args = parser.parse_args()

    # ── 前置检查 ──
    if not args.no_check:
        if not check_server():
            sys.exit(1)
        print()

    # ── 构建 pytest 命令 ──
    pytest_args = build_args(args)
    cmd = ["python", "-m", "pytest"] + pytest_args

    print(f"🚀  执行: {' '.join(cmd)}")
    print("-" * 60)
    start = time.time()

    result = subprocess.run(cmd, cwd=str(ROOT))

    elapsed = time.time() - start
    print("-" * 60)
    status = "✅  PASSED" if result.returncode == 0 else "❌  FAILED"
    print(f"{status}  耗时 {elapsed:.1f}s  | 退出码 {result.returncode}")

    if not args.no_report and result.returncode == 0:
        report = ROOT / "reports" / "report.html"
        if report.exists():
            print(f"📊  HTML 报告: file:///{report}")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
