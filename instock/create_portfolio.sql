-- 持仓管理表
CREATE TABLE IF NOT EXISTS `portfolio_holdings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `portfolio_name` VARCHAR(50) NOT NULL COMMENT '组合名称',
    `code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `name` VARCHAR(50) NOT NULL COMMENT '股票名称',
    `quantity` INT NOT NULL DEFAULT 0 COMMENT '持仓数量',
    `cost_price` DECIMAL(10,2) NOT NULL COMMENT '成本价',
    `current_price` DECIMAL(10,2) COMMENT '当前价',
    `market_value` DECIMAL(12,2) COMMENT '市值',
    `profit_loss` DECIMAL(12,2) COMMENT '盈亏金额',
    `profit_loss_rate` DECIMAL(8,2) COMMENT '盈亏比例',
    `weight` DECIMAL(8,2) COMMENT '仓位权重',
    `industry` VARCHAR(50) COMMENT '行业',
    `risk_level` VARCHAR(20) COMMENT '风险等级',
    `notes` TEXT COMMENT '备注',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否有效',
    UNIQUE KEY `uniq_portfolio_code` (`portfolio_name`, `code`),
    INDEX `idx_code` (`code`),
    INDEX `idx_portfolio` (`portfolio_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓管理表';

-- 持仓异动记录表
CREATE TABLE IF NOT EXISTS `portfolio_alerts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `portfolio_name` VARCHAR(50) NOT NULL,
    `code` VARCHAR(10) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `alert_type` VARCHAR(50) NOT NULL COMMENT '预警类型',
    `alert_level` VARCHAR(20) NOT NULL COMMENT '预警级别',
    `current_value` DECIMAL(12,2) COMMENT '当前值',
    `threshold_value` DECIMAL(12,2) COMMENT '阈值',
    `change_rate` DECIMAL(8,2) COMMENT '变化率',
    `description` TEXT COMMENT '描述',
    `suggested_action` TEXT COMMENT '建议操作',
    `alert_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `is_acknowledged` TINYINT(1) DEFAULT 0 COMMENT '是否已确认',
    `acknowledged_at` TIMESTAMP NULL,
    `acknowledged_by` VARCHAR(50),
    INDEX `idx_alert_time` (`alert_time`),
    INDEX `idx_portfolio_code` (`portfolio_name`, `code`),
    INDEX `idx_alert_type` (`alert_type`),
    INDEX `idx_is_acknowledged` (`is_acknowledged`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓异动记录表';

-- 持仓分析报告表
CREATE TABLE IF NOT EXISTS `portfolio_reports` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `portfolio_name` VARCHAR(50) NOT NULL,
    `report_date` DATE NOT NULL COMMENT '报告日期',
    `report_type` VARCHAR(20) NOT NULL COMMENT '报告类型',
    `total_value` DECIMAL(14,2) COMMENT '总市值',
    `total_cost` DECIMAL(14,2) COMMENT '总成本',
    `total_profit_loss` DECIMAL(14,2) COMMENT '总盈亏',
    `total_profit_loss_rate` DECIMAL(8,2) COMMENT '总盈亏率',
    `position_count` INT COMMENT '持仓数量',
    `winning_count` INT COMMENT '盈利数量',
    `losing_count` INT COMMENT '亏损数量',
    `max_profit_rate` DECIMAL(8,2) COMMENT '最大盈利比例',
    `max_loss_rate` DECIMAL(8,2) COMMENT '最大亏损比例',
    `industry_distribution` JSON COMMENT '行业分布',
    `risk_analysis` TEXT COMMENT '风险分析',
    `recommendations` TEXT COMMENT '操作建议',
    `report_content` TEXT COMMENT '报告内容',
    `generated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uniq_portfolio_date_type` (`portfolio_name`, `report_date`, `report_type`),
    INDEX `idx_report_date` (`report_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓分析报告表';

-- 持仓同步记录表（为后续券商对接准备）
CREATE TABLE IF NOT EXISTS `portfolio_sync_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `broker_name` VARCHAR(50) COMMENT '券商名称',
    `sync_type` VARCHAR(20) NOT NULL COMMENT '同步类型',
    `sync_status` VARCHAR(20) NOT NULL COMMENT '同步状态',
    `records_fetched` INT COMMENT '获取记录数',
    `records_updated` INT COMMENT '更新记录数',
    `sync_start_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `sync_end_time` TIMESTAMP NULL,
    `error_message` TEXT COMMENT '错误信息',
    `sync_details` JSON COMMENT '同步详情',
    INDEX `idx_sync_time` (`sync_start_time`),
    INDEX `idx_sync_status` (`sync_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='持仓同步记录表';

-- 插入示例持仓数据
INSERT INTO `portfolio_holdings` 
(`portfolio_name`, `code`, `name`, `quantity`, `cost_price`, `industry`, `risk_level`, `notes`) VALUES
('主力组合', '000001', '平安银行', 1000, 12.50, '银行', '中等', '核心持仓'),
('主力组合', '000858', '五粮液', 500, 150.00, '白酒', '中高', '消费龙头'),
('主力组合', '600519', '贵州茅台', 100, 1800.00, '白酒', '高', '价值投资'),
('主力组合', '000002', '万科A', 2000, 20.00, '房地产', '中高', '地产龙头'),
('主力组合', '300750', '宁德时代', 300, 200.00, '新能源', '高', '成长股'),
('稳健组合', '601318', '中国平安', 800, 45.00, '保险', '中等', '保险龙头'),
('稳健组合', '600036', '招商银行', 1200, 35.00, '银行', '中等', '零售银行'),
('稳健组合', '000333', '美的集团', 600, 55.00, '家电', '中等', '家电龙头');

-- 创建视图：持仓概览
CREATE OR REPLACE VIEW `portfolio_overview` AS
SELECT 
    portfolio_name,
    COUNT(*) as holding_count,
    SUM(quantity * cost_price) as total_cost,
    SUM(quantity * IFNULL(current_price, cost_price)) as total_value,
    SUM(quantity * IFNULL(current_price, cost_price) - quantity * cost_price) as total_profit_loss,
    ROUND(SUM(quantity * IFNULL(current_price, cost_price) - quantity * cost_price) / SUM(quantity * cost_price) * 100, 2) as total_profit_loss_rate,
    GROUP_CONCAT(DISTINCT industry) as industries
FROM portfolio_holdings 
WHERE is_active = 1
GROUP BY portfolio_name;

-- 创建视图：行业分布
CREATE OR REPLACE VIEW `portfolio_industry_distribution` AS
SELECT 
    portfolio_name,
    industry,
    COUNT(*) as stock_count,
    SUM(quantity) as total_quantity,
    SUM(quantity * IFNULL(current_price, cost_price)) as industry_value,
    ROUND(SUM(quantity * IFNULL(current_price, cost_price)) / 
          (SELECT SUM(quantity * IFNULL(current_price, cost_price)) 
           FROM portfolio_holdings ph2 
           WHERE ph2.portfolio_name = ph.portfolio_name AND ph2.is_active = 1) * 100, 2) as weight_percentage
FROM portfolio_holdings ph
WHERE is_active = 1
GROUP BY portfolio_name, industry
ORDER BY portfolio_name, industry_value DESC;

-- 创建视图：风险分析
CREATE OR REPLACE VIEW `portfolio_risk_analysis` AS
SELECT 
    portfolio_name,
    risk_level,
    COUNT(*) as stock_count,
    SUM(quantity * IFNULL(current_price, cost_price)) as risk_value,
    ROUND(SUM(quantity * IFNULL(current_price, cost_price)) / 
          (SELECT SUM(quantity * IFNULL(current_price, cost_price)) 
           FROM portfolio_holdings ph2 
           WHERE ph2.portfolio_name = ph.portfolio_name AND ph2.is_active = 1) * 100, 2) as risk_weight
FROM portfolio_holdings ph
WHERE is_active = 1
GROUP BY portfolio_name, risk_level
ORDER BY portfolio_name, 
    CASE risk_level 
        WHEN '高' THEN 1 
        WHEN '中高' THEN 2 
        WHEN '中等' THEN 3 
        WHEN '中低' THEN 4 
        WHEN '低' THEN 5 
        ELSE 6 
    END;

-- 触发器：自动计算市值和盈亏
DELIMITER //
CREATE TRIGGER `update_portfolio_values` 
BEFORE UPDATE ON `portfolio_holdings`
FOR EACH ROW
BEGIN
    IF NEW.current_price IS NOT NULL THEN
        SET NEW.market_value = NEW.quantity * NEW.current_price;
        SET NEW.profit_loss = NEW.market_value - (NEW.quantity * NEW.cost_price);
        SET NEW.profit_loss_rate = ROUND((NEW.profit_loss / (NEW.quantity * NEW.cost_price)) * 100, 2);
    END IF;
END//
DELIMITER ;

-- 存储过程：生成持仓报告
DELIMITER //
CREATE PROCEDURE `generate_portfolio_report`(
    IN p_portfolio_name VARCHAR(50),
    IN p_report_date DATE
)
BEGIN
    DECLARE v_total_value DECIMAL(14,2);
    DECLARE v_total_cost DECIMAL(14,2);
    DECLARE v_total_pl DECIMAL(14,2);
    DECLARE v_total_pl_rate DECIMAL(8,2);
    DECLARE v_position_count INT;
    DECLARE v_winning_count INT;
    DECLARE v_losing_count INT;
    
    -- 计算基础数据
    SELECT 
        SUM(quantity * IFNULL(current_price, cost_price)),
        SUM(quantity * cost_price),
        SUM(quantity * IFNULL(current_price, cost_price) - quantity * cost_price),
        ROUND(SUM(quantity * IFNULL(current_price, cost_price) - quantity * cost_price) / SUM(quantity * cost_price) * 100, 2),
        COUNT(*),
        SUM(CASE WHEN (quantity * IFNULL(current_price, cost_price) - quantity * cost_price) > 0 THEN 1 ELSE 0 END),
        SUM(CASE WHEN (quantity * IFNULL(current_price, cost_price) - quantity * cost_price) < 0 THEN 1 ELSE 0 END)
    INTO v_total_value, v_total_cost, v_total_pl, v_total_pl_rate, v_position_count, v_winning_count, v_losing_count
    FROM portfolio_holdings 
    WHERE portfolio_name = p_portfolio_name AND is_active = 1;
    
    -- 插入报告
    INSERT INTO portfolio_reports (
        portfolio_name, report_date, report_type,
        total_value, total_cost, total_profit_loss, total_profit_loss_rate,
        position_count, winning_count, losing_count,
        industry_distribution, risk_analysis, recommendations, report_content
    )
    SELECT 
        p_portfolio_name,
        p_report_date,
        'daily',
        v_total_value,
        v_total_cost,
        v_total_pl,
        v_total_pl_rate,
        v_position_count,
        v_winning_count,
        v_losing_count,
        JSON_OBJECTAGG(industry, industry_value),
        (SELECT GROUP_CONCAT(CONCAT(risk_level, ':', risk_weight, '%') SEPARATOR '; ') 
         FROM portfolio_risk_analysis 
         WHERE portfolio_name = p_portfolio_name),
        CASE 
            WHEN v_total_pl_rate > 5 THEN '考虑部分获利了结'
            WHEN v_total_pl_rate < -5 THEN '考虑止损或补仓'
            ELSE '持仓观察'
        END,
        CONCAT('持仓分析报告：', p_portfolio_name, '，日期：', p_report_date)
    FROM portfolio_industry_distribution 
    WHERE portfolio_name = p_portfolio_name;
    
END//
DELIMITER ;

-- 事件：每日自动生成报告
CREATE EVENT IF NOT EXISTS `daily_portfolio_report`
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_portfolio_name VARCHAR(50);
    DECLARE cur CURSOR FOR SELECT DISTINCT portfolio_name FROM portfolio_holdings WHERE is_active = 1;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO v_portfolio_name;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        CALL generate_portfolio_report(v_portfolio_name, CURDATE());
    END LOOP;
    
    CLOSE cur;
END;

-- 启用事件调度器
SET GLOBAL event_scheduler = ON;

SELECT 'Portfolio management system created successfully!' as message;