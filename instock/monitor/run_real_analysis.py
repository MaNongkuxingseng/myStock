#!/usr/bin/env python3
"""
运行实际持仓分析、消息推送和沟通测试
"""

import sys
import os

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('D:\\python_libs')

# Import the analysis class
from monitor.real_portfolio_analysis import RealPortfolioAnalysis

def main():
    """主函数"""
    print("="*70)
    print("myStock 实际持仓分析与消息推送测试")
    print("="*70)
    
    # 创建分析实例
    analyzer = RealPortfolioAnalysis()
    
    # 运行完整分析
    print("\n[阶段1] 持仓数据分析")
    print("-"*40)
    
    analysis = analyzer.analyze_holdings()
    
    print(f"✓ 分析持仓数量: {analysis['total_holdings']}")
    print(f"✓ 生成预警数量: {len(analysis['alerts'])}")
    print(f"✓ 生成建议数量: {len(analysis['recommendations'])}")
    
    # 显示分析结果
    print("\n[阶段2] 分析结果摘要")
    print("-"*40)
    
    for portfolio_name, portfolio_data in analysis['portfolios'].items():
        print(f"\n📊 {portfolio_name}:")
        print(f"  持仓数量: {portfolio_data['holdings_count']}只")
        print(f"  总市值: {portfolio_data['total_value']:,.0f}元")
        print(f"  总盈亏: {portfolio_data['total_profit']:+,.0f}元 ({portfolio_data['total_profit_rate']:+.1f}%)")
        
        # 显示持仓明细
        print(f"  持仓明细:")
        for holding in portfolio_data['holdings']:
            pl_emoji = "🟢" if holding['profit_loss_rate'] > 0 else "🔴"
            print(f"    {pl_emoji} {holding['code']} {holding['name']}: {holding['profit_loss_rate']:+.1f}%")
    
    # 显示预警
    if analysis['alerts']:
        print("\n[阶段3] 异动预警")
        print("-"*40)
        
        high_alerts = [a for a in analysis['alerts'] if a['level'] == 'HIGH']
        medium_alerts = [a for a in analysis['alerts'] if a['level'] == 'MEDIUM']
        
        if high_alerts:
            print("🔴 高风险预警:")
            for alert in high_alerts:
                print(f"  • {alert['code']} {alert['name']}: {alert['description']}")
        
        if medium_alerts:
            print("\n🟡 中等风险预警:")
            for alert in medium_alerts:
                print(f"  • {alert['code']} {alert['name']}: {alert['description']}")
    
    # 显示建议
    if analysis['recommendations']:
        print("\n[阶段4] 投资建议")
        print("-"*40)
        
        for rec in analysis['recommendations']:
            priority_emoji = "🔴" if rec['priority'] == 'HIGH' else "🟡"
            print(f"{priority_emoji} {rec['description']}")
    
    # 生成Feishu消息
    print("\n[阶段5] Feishu消息生成")
    print("-"*40)
    
    feishu_message = analyzer.generate_feishu_message(analysis)
    
    print("✓ 消息生成成功")
    print(f"✓ 消息长度: {len(feishu_message)} 字符")
    
    # 显示消息预览
    print("\n[阶段6] 消息预览（前500字符）")
    print("-"*40)
    print(feishu_message[:500] + "...")
    
    # 沟通内容测试
    print("\n[阶段7] 沟通内容测试")
    print("-"*40)
    
    communication_tests = analyzer.test_communication_content()
    print(f"✓ 测试了 {len(communication_tests)} 种沟通类型")
    
    # 保存消息到文件
    print("\n[阶段8] 保存测试结果")
    print("-"*40)
    
    output_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存Feishu消息
    message_file = os.path.join(output_dir, "feishu_message_test.md")
    with open(message_file, 'w', encoding='utf-8') as f:
        f.write(feishu_message)
    
    # 保存分析结果
    analysis_file = os.path.join(output_dir, "portfolio_analysis.json")
    import json
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Feishu消息保存到: {message_file}")
    print(f"✓ 分析结果保存到: {analysis_file}")
    
    # 显示下一步操作
    print("\n" + "="*70)
    print("测试完成！下一步操作：")
    print("="*70)
    
    print("\n1. 📋 查看完整Feishu消息：")
    print(f"   文件位置: {message_file}")
    
    print("\n2. 📊 查看详细分析结果：")
    print(f"   文件位置: {analysis_file}")
    
    print("\n3. 💬 测试消息推送：")
    print("   将Feishu消息复制到群组进行测试")
    print("   群组ID: oc_b99df765824c2e59b3fabf287e8d14a2")
    
    print("\n4. ⚙️ 配置自动推送：")
    print("   修改持仓数据后重新运行分析")
    print("   设置定时任务自动推送")
    
    print("\n5. 🔧 自定义配置：")
    print("   修改 real_portfolio_analysis.py 中的持仓数据")
    print("   调整预警阈值和监控规则")
    
    print("\n6. 📈 扩展功能：")
    print("   集成实时价格更新")
    print("   添加更多分析指标")
    print("   实现券商自动同步")
    
    print("\n" + "="*70)
    print("myStock 实际持仓分析系统已就绪！")
    print("="*70)
    
    return {
        'success': True,
        'message_file': message_file,
        'analysis_file': analysis_file,
        'feishu_message': feishu_message[:1000] + "..." if len(feishu_message) > 1000 else feishu_message
    }

if __name__ == "__main__":
    try:
        result = main()
        
        # 显示Feishu消息供复制
        print("\n" + "="*70)
        print("Feishu消息内容（供复制测试）：")
        print("="*70)
        
        analyzer = RealPortfolioAnalysis()
        analysis = analyzer.analyze_holdings()
        feishu_message = analyzer.generate_feishu_message(analysis)
        print(feishu_message)
        
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()