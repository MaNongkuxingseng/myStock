#!/usr/bin/env python3
"""
运行实际持仓的早上9点报告
"""

import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

from monitor.real_holdings_analysis import RealHoldingsAnalyzer

def main():
    """主函数"""
    print("="*70)
    print("myStock早上9点实际持仓报告")
    print("="*70)
    
    analyzer = RealHoldingsAnalyzer()
    
    # 运行分析
    print("\n📊 分析实际持仓...")
    analysis = analyzer.run_analysis()
    
    print(f"\n✅ 分析完成:")
    print(f"   持仓数量: {analysis['holdings_count']}只")
    print(f"   总市值: {analysis['total_value']:,.2f}元")
    print(f"   总盈亏: {analysis['total_profit']:+,.2f}元 ({analysis['total_profit_rate']:+.2f}%)")
    
    # 生成报告
    print("\n📝 生成早上9点报告...")
    report = analyzer.generate_9am_report(analysis)
    
    print(f"✅ 报告生成完成，长度: {len(report)} 字符")
    
    # 显示报告
    print("\n" + "="*70)
    print("早上9点报告内容：")
    print("="*70)
    print(report)
    
    # 保存报告
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    report_file = os.path.join(output_dir, "9am_real_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 报告已保存到: {report_file}")
    
    # 操作指南
    print("\n" + "="*70)
    print("操作指南：")
    print("="*70)
    print("1. 📋 复制上面的报告内容")
    print("2. 📱 粘贴到Feishu群组发送")
    print("3. 🎯 群组ID: oc_b99df765824c2e59b3fabf287e8d14a2")
    print("4. ✅ 测试消息格式和显示效果")
    print("5. ⏰ 配置明天09:00自动推送")
    print("="*70)
    
    # 显示关键数据
    print("\n📈 关键数据摘要：")
    print("-"*40)
    
    for result in analysis['analysis_results']:
        h = result['holding']
        tech = result['tech_analysis']
        
        pl_emoji = "🟢" if h['profit_loss_rate'] > 0 else "🔴"
        trend_emoji = "📈" if tech['trend'] == 'bullish' else "📉" if tech['trend'] == 'bearish' else "➡️"
        
        print(f"{trend_emoji} {h['code']} {h['name']}")
        print(f"  {pl_emoji} 盈亏: {h['profit_loss_rate']:+.2f}% | 权重: {h['weight']:.1f}%")
        print(f"  技术评分: {tech['score']}/100 | 行业: {h['industry']}")
        
        if tech['signals']:
            print(f"  信号: {', '.join(tech['signals'][:2])}")
    
    print("\n" + "="*70)
    print("✅ 系统就绪，可以开始早上9点定时推送！")
    print("="*70)
    
    return report

if __name__ == "__main__":
    try:
        report = main()
        
        # 提供复制建议
        print("\n💡 提示：")
        print("1. 此报告已集成myStock技术指标分析")
        print("2. 包含盈亏分析、技术评分、操作建议")
        print("3. 支持定时自动推送")
        print("4. 可配置预警规则和监控阈值")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()