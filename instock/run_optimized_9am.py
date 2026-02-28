#!/usr/bin/env python3
"""
运行优化版分析并生成9点报告
"""

import sys
import os
from optimized_analysis import OptimizedPortfolioAnalyzer, HOLDINGS

def main():
    """主函数"""
    print("="*70)
    print("myStock早上9点优化分析")
    print("="*70)
    
    # 创建分析器
    analyzer = OptimizedPortfolioAnalyzer(HOLDINGS)
    
    # 运行分析
    print("\n📊 运行优化分析...")
    result = analyzer.run_analysis()
    
    # 生成报告
    print("\n📝 生成分析报告...")
    report = analyzer.generate_report(result)
    
    print(f"✅ 报告生成完成，长度: {len(report)} 字符")
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    report_file = os.path.join(output_dir, f"9am_optimized_{result['analysis_date']}.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 报告保存到: {report_file}")
    
    # 显示报告摘要
    print("\n" + "="*70)
    print("报告摘要:")
    print("="*70)
    
    metrics = result['metrics']
    print(f"总市值: {metrics['total_value']:,.2f}元")
    print(f"总盈亏: {metrics['total_profit']:+,.2f}元 ({metrics['total_profit_rate']:+.2f}%)")
    
    print("\n持仓分析:")
    for h in metrics['holdings']:
        status = "盈利" if h['profit_loss_rate'] > 0 else "亏损"
        print(f"  {h['code']} {h['name']}: {status} {abs(h['profit_loss_rate']):.2f}% | 技术评分: {h['tech_indicators']['technical_score']}/100")
    
    print("\n" + "="*70)
    print("✅ 优化分析完成，准备定时推送！")
    print("="*70)
    
    # 返回报告内容（用于推送）
    return report

if __name__ == "__main__":
    try:
        report = main()
        
        # 提供配置建议
        print("\n💡 定时任务配置:")
        print("1. 创建Windows任务计划")
        print("2. 名称: myStock早上9点优化分析")
        print("3. 触发器: 每天 09:00")
        print("4. 操作: python run_optimized_9am.py")
        print("5. 起始于: G:\\openclaw\\workspace\\_system\\agent-home\\myStock\\instock")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()