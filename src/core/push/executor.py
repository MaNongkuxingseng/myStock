"""
myStock 1.1版本 - 推送执行模块
负责推送内容的格式化和发送
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..utils.helpers import Timer, format_time
from .generator import PushContent, content_generator

logger = logging.getLogger("mystock.push.executor")

class PushExecutor:
    """推送执行器"""
    
    def __init__(self):
        self.sent_history: List[Dict[str, Any]] = []
        self.max_history_size = 50
        logger.info("推送执行器初始化完成")
    
    def format_for_feishu(self, content: PushContent) -> Dict[str, Any]:
        """格式化为飞书消息格式"""
        with Timer("格式化飞书消息"):
            # 创建消息卡片
            card = {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": content.title
                    },
                    "template": self._get_color_template(content.recommendation)
                },
                "elements": []
            }
            
            # 添加内容模块
            elements = []
            
            # 摘要模块
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📊 分析摘要**\n{content.summary}"
                }
            })
            
            # 分隔线
            elements.append({"tag": "hr"})
            
            # 详细内容
            content_lines = content.content.split('\n')
            for line in content_lines:
                if line.strip():
                    elements.append({
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": line
                        }
                    })
            
            # 信号统计
            if content.signals:
                elements.append({"tag": "hr"})
                signal_text = "**📈 交易信号统计**\n"
                for signal in content.signals[:3]:  # 显示前3个信号
                    signal_text += f"• {signal['signal'].upper()} - {signal['strength']}信号\n"
                if len(content.signals) > 3:
                    signal_text += f"• ... 共{len(content.signals)}个信号"
                
                elements.append({
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": signal_text
                    }
                })
            
            # 操作建议
            elements.append({"tag": "hr"})
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**🎯 操作建议**\n建议: **{content.recommendation}** (置信度: {content.confidence:.0%})"
                }
            })
            
            # 时间戳
            elements.append({
                "tag": "note",
                "elements": [{
                    "tag": "plain_text",
                    "content": f"生成时间: {format_time(content.timestamp.timestamp())}"
                }]
            })
            
            card["elements"] = elements
            
            logger.debug(f"飞书消息格式化完成: {content.title}")
            return card
    
    def format_for_console(self, content: PushContent) -> str:
        """格式化为控制台输出格式"""
        with Timer("格式化控制台消息"):
            output = []
            output.append("=" * 60)
            output.append(f"📱 {content.title}")
            output.append("=" * 60)
            output.append("")
            output.append(content.content)
            output.append("")
            output.append("-" * 40)
            output.append(f"📊 摘要: {content.summary}")
            output.append(f"🎯 建议: {content.recommendation} ({content.confidence:.0%}置信度)")
            output.append(f"📈 信号: 共{len(content.signals)}个交易信号")
            output.append(f"⏰ 时间: {format_time(content.timestamp.timestamp())}")
            output.append("=" * 60)
            
            return "\n".join(output)
    
    def format_for_json(self, content: PushContent) -> Dict[str, Any]:
        """格式化为JSON格式"""
        with Timer("格式化JSON消息"):
            return {
                "type": "stock_analysis",
                "version": "1.1",
                "timestamp": content.timestamp.isoformat(),
                "title": content.title,
                "summary": content.summary,
                "recommendation": content.recommendation,
                "confidence": content.confidence,
                "signal_count": len(content.signals),
                "signals": content.signals,
                "content": content.content,
                "metadata": {
                    "generated_by": "myStock 1.1",
                    "format": "json"
                }
            }
    
    def _get_color_template(self, recommendation: str) -> str:
        """根据建议类型获取颜色模板"""
        templates = {
            "BUY": "green",
            "SELL": "red", 
            "HOLD": "blue"
        }
        return templates.get(recommendation, "grey")
    
    def send_to_feishu(self, content: PushContent, 
                      target: Optional[str] = None) -> bool:
        """
        发送到飞书
        
        Args:
            content: 推送内容
            target: 目标用户或群组
        
        Returns:
            bool: 发送是否成功
        """
        with Timer("发送到飞书"):
            try:
                # 格式化为飞书消息
                feishu_message = self.format_for_feishu(content)
                
                # 这里实际应该调用飞书API
                # 暂时模拟发送成功
                logger.info(f"模拟发送飞书消息: {content.title}")
                logger.debug(f"消息内容: {json.dumps(feishu_message, ensure_ascii=False, indent=2)}")
                
                # 记录发送历史
                self._record_send_history(content, "feishu", True)
                
                return True
                
            except Exception as e:
                logger.error(f"发送飞书消息失败: {e}")
                self._record_send_history(content, "feishu", False, str(e))
                return False
    
    def send_to_console(self, content: PushContent) -> bool:
        """发送到控制台（测试用）"""
        with Timer("发送到控制台"):
            try:
                console_message = self.format_for_console(content)
                print(console_message)
                
                self._record_send_history(content, "console", True)
                return True
                
            except Exception as e:
                logger.error(f"发送控制台消息失败: {e}")
                self._record_send_history(content, "console", False, str(e))
                return False
    
    def save_to_file(self, content: PushContent, 
                    filepath: Optional[str] = None) -> bool:
        """保存到文件"""
        with Timer("保存到文件"):
            try:
                import os
                from pathlib import Path
                
                if filepath is None:
                    # 默认保存路径
                    base_dir = Path(__file__).parent.parent.parent.parent
                    logs_dir = base_dir / "logs" / "push"
                    logs_dir.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = content.timestamp.strftime("%Y%m%d_%H%M%S")
                    filepath = logs_dir / f"push_{timestamp}.json"
                
                # 格式化为JSON
                json_data = self.format_for_json(content)
                
                # 保存文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"推送内容已保存到文件: {filepath}")
                self._record_send_history(content, "file", True, str(filepath))
                return True
                
            except Exception as e:
                logger.error(f"保存到文件失败: {e}")
                self._record_send_history(content, "file", False, str(e))
                return False
    
    def _record_send_history(self, content: PushContent,
                           channel: str,
                           success: bool,
                           details: Optional[str] = None):
        """记录发送历史"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "content_title": content.title,
            "channel": channel,
            "success": success,
            "details": details,
            "recommendation": content.recommendation,
            "confidence": content.confidence
        }
        
        self.sent_history.append(history_entry)
        
        # 限制历史记录大小
        if len(self.sent_history) > self.max_history_size:
            self.sent_history = self.sent_history[-self.max_history_size:]
        
        logger.debug(f"记录发送历史: {content.title} -> {channel} ({'成功' if success else '失败'})")
    
    def get_send_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取发送历史"""
        return self.sent_history[-limit:] if self.sent_history else []
    
    def get_send_statistics(self) -> Dict[str, Any]:
        """获取发送统计"""
        if not self.sent_history:
            return {"total": 0, "success": 0, "failure": 0, "channels": {}}
        
        stats = {
            "total": len(self.sent_history),
            "success": 0,
            "failure": 0,
            "channels": {},
            "recommendations": {}
        }
        
        for entry in self.sent_history:
            # 统计成功失败
            if entry["success"]:
                stats["success"] += 1
            else:
                stats["failure"] += 1
            
            # 统计渠道
            channel = entry["channel"]
            if channel not in stats["channels"]:
                stats["channels"][channel] = 0
            stats["channels"][channel] += 1
            
            # 统计建议类型
            rec = entry["recommendation"]
            if rec not in stats["recommendations"]:
                stats["recommendations"][rec] = 0
            stats["recommendations"][rec] += 1
        
        # 计算成功率
        if stats["total"] > 0:
            stats["success_rate"] = stats["success"] / stats["total"]
        
        return stats
    
    def execute_push(self, time_point: str,
                    stock_data: pd.DataFrame,
                    current_price: float,
                    channels: List[str] = None) -> Dict[str, Any]:
        """
        执行推送
        
        Args:
            time_point: 时间点
            stock_data: 股票数据
            current_price: 当前价格
            channels: 推送渠道列表
        
        Returns:
            Dict[str, Any]: 推送执行结果
        """
        with Timer(f"执行推送: {time_point}"):
            # 默认渠道
            if channels is None:
                channels = ["console", "file"]  # 默认控制台和文件
            
            results = {
                "time_point": time_point,
                "timestamp": datetime.now().isoformat(),
                "channels": {},
                "success": False,
                "error": None
            }
            
            try:
                # 生成内容
                content = content_generator.generate_by_time_point(
                    time_point, stock_data, current_price
                )
                
                results["content"] = {
                    "title": content.title,
                    "recommendation": content.recommendation,
                    "confidence": content.confidence,
                    "signal_count": len(content.signals)
                }
                
                # 发送到各个渠道
                for channel in channels:
                    channel_result = {"success": False, "error": None}
                    
                    try:
                        if channel == "feishu":
                            success = self.send_to_feishu(content)
                        elif channel == "console":
                            success = self.send_to_console(content)
                        elif channel == "file":
                            success = self.save_to_file(content)
                        else:
                            channel_result["error"] = f"未知渠道: {channel}"
                            success = False
                        
                        channel_result["success"] = success
                        
                    except Exception as e:
                        channel_result["error"] = str(e)
                        channel_result["success"] = False
                    
                    results["channels"][channel] = channel_result
                
                # 检查是否至少有一个渠道成功
                results["success"] = any(
                    channel_result.get("success", False)
                    for channel_result in results["channels"].values()
                )
                
                logger.info(f"推送执行完成: {time_point} - {'成功' if results['success'] else '失败'}")
                
            except Exception as e:
                results["success"] = False
                results["error"] = str(e)
                logger.error(f"推送执行失败: {time_point} - {e}")
            
            return results

# 全局推送执行器实例
push_executor = PushExecutor()

def init_push_executor():
    """初始化推送执行器"""
    logger.info("推送执行器初始化完成")
    return push_executor

if __name__ == "__main__":
    # 测试推送执行模块
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    print("=== 推送执行模块测试 ===")
    
    # 初始化
    executor = init_push_executor()
    
    # 创建测试数据
    dates = pd.date_range(start='2026-01-01', periods=20, freq='D')
    np.random.seed(42)
    
    test_data = pd.DataFrame({
        'date': dates,
        'open': 10 + np.random.randn(20).cumsum() * 0.1,
        'high': 10.5 + np.random.randn(20).cumsum() * 0.1,
        'low': 9.5 + np.random.randn(20).cumsum() * 0.1,
        'close': 10 + np.random.randn(20).cumsum() * 0.1,
        'volume': 1000000 + np.random.randn(20).cumsum() * 10000
    })
    test_data.set_index('date', inplace=True)
    
    current_price = test_data['close'].iloc[-1]
    
    # 测试格式化功能
    print("\n测试消息格式化:")
    
    # 生成内容
    content = content_generator.generate_morning_analysis(test_data, current_price)
    
    # 测试不同格式
    print("1. 控制台格式:")
    console_msg = executor.format_for_console(content)
    print(console_msg[:200] + "..." if len(console_msg) > 200 else console_msg)
    
    print("\n2. 飞书格式 (预览):")
    feishu_msg = executor.format_for_feishu(content)
    print(f"   标题: {feishu_msg['header']['title']['content']}")
    print(f"   模板: {feishu_msg['header']['template']}")
    print(f"   元素数: {len(feishu_msg['elements'])}")
    
    print("\n3. JSON格式 (预览):")
    json_msg = executor.format_for_json(content)
    print(f"   类型: {json_msg['type']}")
    print(f"   建议: {json_msg['recommendation']}")
    print(f"   置信度: {json_msg['confidence']}")
    
    # 测试发送功能
    print("\n测试发送功能:")
    
    # 发送到控制台
    print("1. 发送到控制台:")
    console_success = executor.send_to_console(content)
    print(f"   结果: {'成功' if console_success else '失败'}")
    
    # 保存到文件
    print("\n2. 保存到文件:")
    file_success = executor.save_to_file(content)
    print(f"   结果: {'成功' if file_success else '失败'}")
    
    # 测试完整推送
    print("\n测试完整推送执行:")
    push_result = executor.execute_push(
        time_point="09:00",
        stock_data=test_data,
        current_price=current_price,
        channels=["console", "file"]
    )
    
    print(f"   时间点: {push_result['time_point']}")
    print(f"   整体结果: {'成功' if push_result['success'] else '失败'}")
    print(f"   内容标题: {push_result['content']['title']}")
    print(f"   渠道结果:")
    for channel, result in push_result['channels'].items():
        print(f"     • {channel}: {'成功' if result['success'] else '失败'}")
    
    # 测试统计功能
    print("\n测试统计功能:")
    stats = executor.get_send_statistics()
    print(f"   总发送数: {stats['total']}")
    print(f"   成功数: {stats['success']}")
    print(f"   失败数: {stats['failure']}")
    if stats['total'] > 0:
        print(f"   成功率: {stats.get('success_rate', 0):.1%}")
    
    print("\n" + "=" * 40)