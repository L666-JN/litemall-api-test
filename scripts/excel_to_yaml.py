"""
Excel 测试用例 → YAML 转换脚本

读取 test_design/ 下的 Excel 文件，生成对应的 YAML 测试数据文件
输出到 tests/test_data/

用法: python scripts/excel_to_yaml.py [excel_file] [--output dir]
"""
import sys
import json
import re
from pathlib import Path

import openpyxl
import yaml


# 需要认证的 case_id（这些用例通过 authenticated_client 执行）
# Excel 中 "need_auth" 列为 "是" 的自动识别
# 额外标记为"手动设置假token"的，也加入需要特殊处理


def excel_to_yaml(excel_path: str, output_dir: str):
    """读取 Excel，按模块拆分生成 YAML 文件"""
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active  # 第一个 sheet = 用例数据

    # 读取表头
    headers = []
    for col in range(1, ws.max_column + 1):
        headers.append(ws.cell(1, col).value)

    # 解析所有用例行
    cases = []
    for row in range(2, ws.max_row + 1):
        case = {}
        for col, header in enumerate(headers, 1):
            val = ws.cell(row, col).value
            case[header] = val if val is not None else ""
        cases.append(case)

    # 按模块分组
    modules = {}
    for case in cases:
        mod = case.get("模块", "")
        if mod not in modules:
            modules[mod] = []
        modules[mod].append(case)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 模块 → YAML 文件名映射
    module_file_map = {
        "登录": "auth_login_data",
        "登出": "auth_logout_data",
        "用户信息": "auth_info_data",
        "注册": "auth_register_data",
        "密码重置": "auth_reset_data",
    }

    total_count = 0
    for mod_name, mod_cases in modules.items():
        yaml_data = {}
        for case in mod_cases:
            case_id = case["用例ID"]
            expected = {}

            # ── expected 字段 ──
            exp_errno = case["预期errno"]
            exp_errno_not = case["预期errno不为"]
            exp_errmsg = case["预期errmsg"]
            exp_errmsg_contains = case["预期errmsg包含"]
            exp_has_data = case["预期data有值"]
            exp_check_fields = case["预期data字段"]

            if exp_errno != "":
                expected["errno"] = int(exp_errno) if str(exp_errno).isdigit() else exp_errno
            if exp_errno_not != "":
                expected["errno_not"] = int(exp_errno_not) if str(exp_errno_not).isdigit() else exp_errno_not
            if exp_errmsg != "":
                expected["errmsg"] = str(exp_errmsg)
            if exp_errmsg_contains != "":
                expected["errmsg_contains"] = str(exp_errmsg_contains)
            if exp_has_data in ("是", "true", "True"):
                expected["has_data"] = True
            elif exp_has_data in ("否", "false", "False"):
                expected["has_data"] = False
            if exp_check_fields != "":
                expected["fields"] = [f.strip() for f in str(exp_check_fields).split(",") if f.strip()]

            # ── request 字段 ──
            req_body = case["请求体"]
            request = None
            if req_body and req_body.strip():
                try:
                    request = json.loads(req_body)
                except json.JSONDecodeError:
                    request = {"_raw": req_body}

            req_params = case["请求参数"]
            params = None
            if req_params and req_params.strip():
                params = str(req_params).strip()

            # ── 组装 YAML 节点 ──
            node = {
                "description": str(case["用例描述"]),
                "module": str(case["模块"]),
                "priority": str(case["优先级"]),
                "method": str(case["请求方法"]).upper(),
                "need_auth": str(case["需要认证"]) in ("是", "true", "True"),
                "endpoint": str(case["接口路径"]),
                "expected": expected,
            }

            if params:
                node["params"] = params

            if request:
                node["request"] = request

            yaml_data[case_id] = node

        # ── 写 YAML 文件 ──
        filename = module_file_map.get(mod_name)
        if filename is None:
            filename = re.sub(r'[^\w]', '_', mod_name).lower()
            # 去掉多余下划线
            filename = re.sub(r'_+', '_', filename).strip('_') + "_data"

        filepath = output_dir / f"{filename}.yaml"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Litemall {mod_name}模块 测试数据\n")
            f.write(f"# 由 scripts/excel_to_yaml.py 自动生成\n")
            f.write(f"# 来源: {excel_path}\n\n")

            for idx, (case_id, node) in enumerate(yaml_data.items()):
                dump = yaml.dump(
                    {case_id: node},
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    indent=2,
                    width=120,
                )
                f.write(dump)
                if idx < len(yaml_data) - 1:
                    f.write("\n")

        count = len(yaml_data)
        total_count += count
        print(f"  [OK] {mod_name}: {count} 个用例 → {filepath}")

    print(f"\n  共生成 {total_count} 个用例，{len(modules)} 个 YAML 文件")

    # ── 同时生成合并版 auth_data.yaml（兼容旧引用）──
    all_data = {}
    for mod_name, mod_cases in modules.items():
        for case in mod_cases:
            case_id = case["用例ID"]

            expected = {}
            if case["预期errno"] != "":
                expected["errno"] = int(case["预期errno"]) if str(case["预期errno"]).isdigit() else case["预期errno"]
            if case["预期errno不为"] != "":
                expected["errno_not"] = int(case["预期errno不为"]) if str(case["预期errno不为"]).isdigit() else case["预期errno不为"]
            if case["预期errmsg"] != "":
                expected["errmsg"] = str(case["预期errmsg"])
            if case["预期errmsg包含"] != "":
                expected["errmsg_contains"] = str(case["预期errmsg包含"])

            req_body = case["请求体"]
            request = None
            if req_body and req_body.strip():
                try:
                    request = json.loads(req_body)
                except json.JSONDecodeError:
                    request = {"_raw": req_body}

            node = {
                "description": str(case["用例描述"]),
                "module": str(case["模块"]),
                "priority": str(case["优先级"]),
                "method": str(case["请求方法"]).upper(),
                "need_auth": str(case["需要认证"]) in ("是", "true", "True"),
                "endpoint": str(case["接口路径"]),
                "expected": expected,
            }

            req_params = str(case["请求参数"])
            if req_params:
                node["params"] = req_params

            if request:
                node["request"] = request
            if str(case["预期data有值"]) in ("是", "true", "True"):
                node["expected"]["has_data"] = True
            if str(case["预期data字段"]):
                node["expected"]["fields"] = [f.strip() for f in str(case["预期data字段"]).split(",") if f.strip()]

            all_data[case_id] = node

    filepath_all = output_dir / "auth_data.yaml"
    with open(filepath_all, "w", encoding="utf-8") as f:
        f.write("# Litemall 认证模块 全部测试数据（合并版）\n")
        f.write("# 由 scripts/excel_to_yaml.py 自动生成\n\n")
        for idx, (case_id, node) in enumerate(all_data.items()):
            dump = yaml.dump({case_id: node}, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2, width=120)
            f.write(dump)
            if idx < len(all_data) - 1:
                f.write("\n")
    print(f"  [OK] 合并版: {total_count} 个用例 → {filepath_all}")


if __name__ == "__main__":
    args = sys.argv[1:]
    excel_file = args[0] if args else "test_design/auth_module_testcases.xlsx"
    output = args[1] if len(args) > 1 else "tests/test_data"

    excel_path = Path(excel_file)
    if not excel_path.is_absolute():
        excel_path = Path(__file__).parent.parent / excel_file

    if not excel_path.exists():
        print(f"[ERROR] Excel 文件不存在: {excel_path}")
        sys.exit(1)

    print(f"Excel: {excel_path}")
    print(f"Output: {output}")
    excel_to_yaml(str(excel_path), output)
