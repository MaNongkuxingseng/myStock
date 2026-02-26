# 买卖参考看板字段说明（myStock）

> 目标：打开网页后，优先看哪些字段，怎么组合判断。

## 一、先看趋势（方向）
- `change_rate`：当日涨跌幅
- `changerate_3days / 5days / 10days`：短中期趋势
- `upnday / downnday`：连涨连跌强弱

**建议**：3日与5日同向更可靠；连涨过长需防回撤。

## 二、再看资金（确认）
- `net_inflow`：当日主力净流入
- `netinflow_3days / 5days`：持续性资金方向
- `ddx / ddx_3d / ddx_5d`：筹码迁移方向

**建议**：价格上行 + 3/5日净流入为正 + DDX转正，信号质量更高。

## 三、看量价配合（真假突破）
- `volume_ratio`：量比
- `turnoverrate`：换手率
- `breakup_ma_20days / breakup_ma_60days`：关键均线突破
- `long_avg_array / short_avg_array`：均线多空排列

**建议**：放量突破（量比>1）比无量上涨更可信。

## 四、看风险与估值（防踩雷）
- `pe9 / pbnewmrq`：估值
- `debt_asset_ratio`：杠杆风险
- `high_funds_outflow`：高位资金撤退
- `is_issue_break / is_bps_break`：破发/破净标签

**建议**：高估值+资金流出并存时，优先风控。

## 五、实战判定模板（简版）
### 偏买入候选
1) 3/5日涨幅为正；
2) `netinflow_3days` 与 `ddx_3d` 为正；
3) `breakup_ma_20days=1` 或 `long_avg_array=1`；
4) 量比 >= 1。

### 偏减仓候选
1) 3/5日转弱；
2) `netinflow_3days` 与 `ddx_3d` 为负；
3) `high_funds_outflow=1` 或跌破关键均线；
4) 放量下跌。

## 六、当前限制（必须知晓）
若 `cn_stock_indicators*` / `cn_stock_pattern` 缺失或当天行数为0，
则“技术信号可信度下降”，应提高资金面与风控权重。
