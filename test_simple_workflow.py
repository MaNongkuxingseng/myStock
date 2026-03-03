#!/usr/bin/env python3
"""
简化版工作流程测试
"""

import os
import json
import requests
from datetime import datetime
import subprocess

def test_complete_workflow():
    """测试完整工作流程"""
    print("="*70)
    print("简化版完整工作流程测试")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. 获取实时数据
    print("\n1. 获取实时数据...")
    holdings = [
        {'code': '600118', 'name': '中国卫星'},
        {'code': '600157', 'name': '永泰能源'},
        {'code': '000731', 'name': '四川美丰'}
    ]
    
    data = {}
    for stock in holdings:
        code = stock['code']
        try:
            if code.startswith('6'):
                market_code = f"sh{code}"
            else:
                market_code = f"sz{code}"
            
            url = f"http://qt.gtimg.cn/q={market_code}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                text = response.text.strip()
                if '=' in text:
                    data_part = text.split('=')[1].strip('"')
                    fields = data_part.split('~')
                    
                    if len(fields) >= 40:
                        data[code] = {
                            'name': stock['name'],
                            'price': float(fields[3]) if fields[3] else 0,
                            'pre_close': float(fields[4]) if fields[4] else 0,
                            'time': fields[30] if len(fields) > 30 else ''
                        }
                        print(f"  ✅ {stock['name']}: {data[code]['price']}元")
        except Exception as e:
            print(f"  ❌ {stock['name']}: 获取失败 - {e}")
    
    # 2. 分析数据
    print("\n2. 分析数据...")
    analysis = {}
    for code, stock_data in data.items():
        if stock_data['pre_close'] > 0:
            change_pct = (stock_data['price'] - stock_data['pre_close']) / stock_data['pre_close'] * 100
            analysis[code] = {
                'change_pct': change_pct,
                'signal': '上涨' if change_pct > 0 else '下跌'
            }
            print(f"  📊 {stock_data['name']}: {change_pct:+.2f}%")
    
    # 3. 生成报告
    print("\n3. 生成报告...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = f"""测试报告 - {timestamp}
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

持仓股实时数据:
"""
    
    for code, stock_data in data.items():
        if code in analysis:
            report += f"""
{stock_data['name']} ({code}):
• 当前价: {stock_data['price']:.2f}元
• 涨跌幅: {analysis[code]['change_pct']:+.2f}%
• 数据时间: {stock_data['time']}
"""
    
    report += f"""
========================================
工作流程测试完成
"""
    
    # 保存报告
    reports_dir = os.path.join(base_dir, 'reports', datetime.now().strftime('%Y%m%d'))
    os.makedirs(reports_dir, exist_ok=True)
    
    report_file = os.path.join(reports_dir, f"test_report_{timestamp}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"  ✅ 报告已保存: {report_file}")
    
    # 4. Git提交
    print("\n4. Git提交...")
    try:
        os.chdir(base_dir)
        
        # 添加文件
        rel_path = os.path.relpath(report_file, base_dir)
        subprocess.run(['git', 'add', rel_path], check=True)
        print(f"  ✅ 已添加: {rel_path}")
        
        # 提交
        commit_msg = f"test: 工作流程测试 {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        print(f"  ✅ 已提交: {commit_msg}")
        
        # 查看状态
        status = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True).stdout
        print(f"  📋 Git状态:\n{status}")
        
        git_success = True
        
    except Exception as e:
        print(f"  ❌ Git操作失败: {e}")
        git_success = False
    
    # 5. 生成追溯报告
    print("\n5. 生成追溯报告...")
    trace_report = {
        'test_time': datetime.now().isoformat(),
        'data_fetched': len(data),
        'report_file': report_file,
        'git_success': git_success,
        'workflow_steps': [
            '数据获取: 完成',
            '数据分析: 完成',
            '报告生成: 完成',
            'Git提交: ' + ('成功' if git_success else '失败'),
            '追溯报告: 完成'
        ]
    }
    
    trace_file = os.path.join(base_dir, 'git_logs', f"trace_test_{timestamp}.json")
    os.makedirs(os.path.dirname(trace_file), exist_ok=True)
    
    with open(trace_file, 'w', encoding='utf-8') as f:
        json.dump(trace_report, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ 追溯报告已保存: {trace_file}")
    
    # 6. 总结
    print("\n" + "="*70)
    print("工作流程测试总结")
    print("="*70)
    
    print(f"数据获取: {len(data)}/{len(holdings)} 成功")
    print(f"报告生成: ✅ 完成")
    print(f"Git提交: {'✅ 成功' if git_success else '❌ 失败'}")
    print(f"追溯报告: ✅ 完成")
    
    print(f"\n生成文件:")
    print(f"• 测试报告: {report_file}")
    print(f"• 追溯报告: {trace_file}")
    
    print(f"\n下一步:")
    print("1. 安装schedule模块: pip install schedule")
    print("2. 运行完整调度系统: python nine_point_scheduler.py")
    print("3. 配置9时间点自动执行")
    
    print("\n" + "="*70)
    print("简化版工作流程测试完成!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    test_complete_workflow()