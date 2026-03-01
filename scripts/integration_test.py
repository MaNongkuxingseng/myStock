#!/usr/bin/env python3
"""
myStock 1.1版本 - 集成测试脚本
测试完整的推送系统工作流程
"""

import sys
import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.data.collector import data_collector
from src.core.analysis.indicators import technical_indicators
from src.core.analysis.signals import signal_generator
from src.core.push.generator import content_generator
from src.core.push.executor import push_executor
from src.core.push.scheduler import PushTimePoint, push_scheduler

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def create_test_data():
    """创建测试数据"""
    print("📊 创建测试数据...")
    
    # 生成30天的测试数据
    dates = pd.date_range(start='2026-01-01', periods=30, freq='D')
    np.random.seed(42)  # 固定随机种子，确保可重复
    
    data = pd.DataFrame({
        'date': dates,
        'open': 10 + np.random.randn(30).cumsum() * 0.1,
        'high': 10.5 + np.random.randn(30).cumsum() * 0.1,
        'low': 9.5 + np.random.randn(30).cumsum() * 0.1,
        'close': 10 + np.random.randn(30).cumsum() * 0.1,
        'volume': 1000000 + np.random.randn(30).cumsum() * 10000
    })
    data.set_index('date', inplace=True)
    
    print(f"  数据形状: {data.shape}")
    print(f"  日期范围: {data.index[0].date()} 到 {data.index[-1].date()}")
    print(f"  最新收盘价: {data['close'].iloc[-1]:.2f}")
    
    return data

def test_data_collection():
    """测试数据采集模块"""
    print("\n" + "="*60)
    print("🧪 测试数据采集模块")
    print("="*60)
    
    # 使用模拟数据源
    from src.core.data.collector import MockDataSource, DataCollector
    mock_source = MockDataSource()
    collector = DataCollector(mock_source)
    
    # 测试历史数据采集
    print("1. 测试历史数据采集...")
    history_data = collector.get_stock_history("000001", days=10)
    if history_data is not None:
        print(f"   ✓ 历史数据获取成功")
        print(f"     数据形状: {history_data.shape}")
        print(f"     列名: {list(history_data.columns)}")
    else:
        print("   ✗ 历史数据获取失败")
    
    # 测试实时数据采集
    print("\n2. 测试实时数据采集...")
    realtime_data = collector.get_realtime_quotes(["000001", "600000"])
    print(f"   ✓ 实时数据获取成功")
    print(f"     股票数量: {len(realtime_data)}")
    for code, data in realtime_data.items():
        print(f"     {code}: 价格={data.get('current_price'):.2f}, 涨跌={data.get('change'):+.2f}")
    
    # 测试市场数据采集
    print("\n3. 测试市场数据采集...")
    market_data = collector.get_market_overview()
    print(f"   ✓ 市场数据获取成功")
    print(f"     上证指数: {market_data.get('shanghai_index', {}).get('current'):.2f}")
    print(f"     深证成指: {market_data.get('shenzhen_index', {}).get('current'):.2f}")
    
    return True

def test_technical_indicators(test_data):
    """测试技术指标模块"""
    print("\n" + "="*60)
    print("📈 测试技术指标模块")
    print("="*60)
    
    print("1. 测试单个指标计算...")
    
    # 测试MACD
    macd_result = technical_indicators.calculate_macd(test_data['close'])
    print(f"   ✓ MACD计算完成")
    print(f"     数据长度: {len(macd_result.values)}")
    print(f"     最新DIF值: {macd_result.values.iloc[-1] if not macd_result.values.empty else 'N/A'}")
    
    # 测试RSI
    rsi_result = technical_indicators.calculate_rsi(test_data['close'], period=14)
    print(f"   ✓ RSI计算完成")
    print(f"     最新RSI值: {rsi_result.values.iloc[-1] if not rsi_result.values.empty else 'N/A'}")
    print(f"     最新信号: {rsi_result.signals.iloc[-1] if rsi_result.signals is not None else 'N/A'}")
    
    print("\n2. 测试批量指标计算...")
    all_results = technical_indicators.calculate_all_indicators(test_data)
    print(f"   ✓ 批量计算完成")
    print(f"     计算指标数: {len(all_results)}")
    for name, result in all_results.items():
        print(f"     {name}: {result.type.value} - {len(result.values)}个数据点")
    
    print("\n3. 测试分析报告生成...")
    report = technical_indicators.generate_indicator_report(all_results)
    print(f"   ✓ 分析报告生成完成")
    print(f"     整体趋势: {report['summary']['overall_trend']}")
    print(f"     买入信号: {report['summary']['buy_signals']}个")
    print(f"     卖出信号: {report['summary']['sell_signals']}个")
    
    return True

def test_signal_generation(test_data):
    """测试信号生成模块"""
    print("\n" + "="*60)
    print("📢 测试信号生成模块")
    print("="*60)
    
    current_price = test_data['close'].iloc[-1]
    
    print("1. 计算技术指标...")
    indicator_results = technical_indicators.calculate_all_indicators(test_data)
    print(f"   ✓ 技术指标计算完成: {len(indicator_results)}个指标")
    
    print("\n2. 生成交易信号...")
    signals = signal_generator.analyze_indicators(indicator_results, current_price)
    print(f"   ✓ 交易信号生成完成")
    print(f"     信号数量: {len(signals)}")
    
    if signals:
        print(f"     信号详情:")
        for i, signal in enumerate(signals[:3], 1):  # 显示前3个信号
            print(f"     {i}. {signal.signal_type.value.upper()} ({signal.strength.value})")
            print(f"        置信度: {signal.confidence:.0%}")
            print(f"        指标: {', '.join(signal.indicators)}")
    
    print("\n3. 生成最终建议...")
    recommendation = signal_generator.generate_final_recommendation(signals)
    print(f"   ✓ 最终建议生成完成")
    print(f"     建议: {recommendation['recommendation']}")
    print(f"     置信度: {recommendation['confidence']:.0%}")
    print(f"     原因: {recommendation['reason']}")
    
    print("\n4. 生成完整分析报告...")
    full_report = signal_generator.generate_signal_report(test_data, current_price)
    print(f"   ✓ 完整报告生成完成")
    print(f"     风险等级: {full_report['risk_assessment']['level']}")
    print(f"     买入信号: {full_report['trading_signals']['buy']}个")
    print(f"     卖出信号: {full_report['trading_signals']['sell']}个")
    
    return True

def test_content_generation(test_data):
    """测试内容生成模块"""
    print("\n" + "="*60)
    print("📝 测试内容生成模块")
    print("="*60)
    
    current_price = test_data['close'].iloc[-1]
    
    # 测试各时间点内容生成
    time_points = [
        ("09:00", "早盘分析"),
        ("09:30", "开盘监控"),
        ("15:00", "收盘总结"),
        ("20:00", "晚间复盘")
    ]
    
    for time_point, description in time_points:
        print(f"\n{description} ({time_point}):")
        try:
            content = content_generator.generate_by_time_point(
                time_point, test_data, current_price
            )
            print(f"   ✓ 内容生成成功")
            print(f"     标题: {content.title}")
            print(f"     建议: {content.recommendation} ({content.confidence:.0%}置信度)")
            print(f"     信号数: {len(content.signals)}")
            print(f"     内容行数: {len(content.content.split('\\n'))}")
            
            # 显示内容预览
            preview = content.content.split('\n')[:3]
            for line in preview:
                print(f"       {line}")
            if len(content.content.split('\n')) > 3:
                print(f"       ...")
                
        except Exception as e:
            print(f"   ✗ 内容生成失败: {e}")
    
    return True

def test_push_execution(test_data):
    """测试推送执行模块"""
    print("\n" + "="*60)
    print("🚀 测试推送执行模块")
    print("="*60)
    
    current_price = test_data['close'].iloc[-1]
    
    print("1. 生成测试内容...")
    content = content_generator.generate_morning_analysis(test_data, current_price)
    print(f"   ✓ 内容生成完成: {content.title}")
    
    print("\n2. 测试消息格式化...")
    
    # 测试控制台格式
    console_msg = push_executor.format_for_console(content)
    print(f"   ✓ 控制台格式完成")
    print(f"     消息长度: {len(console_msg)}字符")
    
    # 测试飞书格式
    feishu_msg = push_executor.format_for_feishu(content)
    print(f"   ✓ 飞书格式完成")
    print(f"     卡片标题: {feishu_msg['header']['title']['content']}")
    print(f"     元素数量: {len(feishu_msg['elements'])}")
    
    # 测试JSON格式
    json_msg = push_executor.format_for_json(content)
    print(f"   ✓ JSON格式完成")
    print(f"     数据类型: {json_msg['type']}")
    print(f"     版本: {json_msg['version']}")
    
    print("\n3. 测试推送执行...")
    push_result = push_executor.execute_push(
        time_point="09:00",
        stock_data=test_data,
        current_price=current_price,
        channels=["console", "file"]
    )
    
    print(f"   ✓ 推送执行完成")
    print(f"     整体结果: {'成功' if push_result['success'] else '失败'}")
    print(f"     时间点: {push_result['time_point']}")
    
    for channel, result in push_result['channels'].items():
        status = "成功" if result['success'] else "失败"
        print(f"     • {channel}: {status}")
    
    print("\n4. 测试发送统计...")
    stats = push_executor.get_send_statistics()
    print(f"   ✓ 统计获取完成")
    print(f"     总发送数: {stats['total']}")
    print(f"     成功数: {stats['success']}")
    if stats['total'] > 0:
        print(f"     成功率: {stats.get('success_rate', 0):.1%}")
    
    return True

def test_push_scheduler():
    """测试推送调度模块"""
    print("\n" + "="*60)
    print("⏰ 测试推送调度模块")
    print("="*60)
    
    print("1. 测试调度器初始化...")
    push_scheduler.register_default_tasks()
    print(f"   ✓ 调度器初始化完成")
    print(f"     注册任务数: {len(push_scheduler.tasks)}")
    
    print("\n2. 测试任务信息...")
    status = push_scheduler.get_status()
    print(f"   ✓ 状态获取完成")
    print(f"     总任务数: {status['total_tasks']}")
    print(f"     启用任务: {status['enabled_tasks']}")
    print(f"     禁用任务: {status['disabled_tasks']}")
    
    print("\n3. 测试手动触发...")
    test_time_point = PushTimePoint.MORNING_ANALYSIS
    result = push_scheduler.trigger_manual_push(test_time_point)
    print(f"   ✓ 手动触发完成: {test_time_point.value}")
    print(f"     触发结果: {result['status']}")
    
    print("\n4. 显示任务详情...")
    for time_point, task in push_scheduler.tasks.items():
        info = task.get_info()
        print(f"     • {info['time_point']}: {info['name']}")
        print(f"       状态: {info['last_status']}, 启用: {info['enabled']}")
    
    return True

def run_full_integration_test():
    """运行完整的集成测试"""
    print("="*80)
    print("myStock 1.1版本 - 完整集成测试")
    print("="*80)
    
    setup_logging()
    
    # 创建测试数据
    test_data = create_test_data()
    
    # 运行各个模块测试
    test_results = []
    
    try:
        test_results.append(("数据采集", test_data_collection()))
    except Exception as e:
        print(f"数据采集测试失败: {e}")
        test_results.append(("数据采集", False))
    
    try:
        test_results.append(("技术指标", test_technical_indicators(test_data)))
    except Exception as e:
        print(f"技术指标测试失败: {e}")
        test_results.append(("技术指标", False))
    
    try:
        test_results.append(("信号生成", test_signal_generation(test_data)))
    except Exception as e:
        print(f"信号生成测试失败: {e}")
        test_results.append(("信号生成", False))
    
    try:
        test_results.append(("内容生成", test_content_generation(test_data)))
    except Exception as e:
        print(f"内容生成测试失败: {e}")
        test_results.append(("内容生成", False))
    
    try:
        test_results.append(("推送执行", test_push_execution(test_data)))
    except Exception as e:
        print(f"推送执行测试失败: {e}")
        test_results.append(("推送执行", False))
    
    try:
        test_results.append(("推送调度", test_push_scheduler()))
    except Exception as e:
        print(f"推送调度测试失败: {e}")
        test_results.append(("推送调度", False))
    
    # 输出测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    print(f"📈 通过率: {passed/total*100:.1f}%")
    
    print("\n详细结果:")
    for module, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {module:10} {status}")
    
    print("\n" + "="*80)
    
    if passed == total:
        print("🎉 所有测试通过！myStock 1.1版本推送系统功能完整。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = run_full_integration_test()
    sys.exit(0 if success else 1)