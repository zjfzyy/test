import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import time

class StockScreener:
    def __init__(self):
        # 使用您的 tushare token
        self.ts_token = "30lin8c994239486bd9f0f430d3da0f3a670baa1789b376641e9f470"
        ts.set_token(self.ts_token)
        self.pro = ts.pro_api()
        
    def get_stock_list(self):
        """获取所有A股列表"""
        stocks = self.pro.stock_basic(exchange='', list_status='L')
        # 返回股票代码和名称的DataFrame
        return stocks[['ts_code', 'name']]
    
    def get_latest_trade_date(self):
        """获取最近的交易日期"""
        try:
            # 获取从当前日期往前20个交易日的数据
            today = datetime.now()
            start_date = (today - timedelta(days=20)).strftime('%Y%m%d')
            end_date = today.strftime('%Y%m%d')
            
            df = self.pro.trade_cal(exchange='SSE', 
                                  start_date=start_date,
                                  end_date=end_date,
                                  is_open='1')
            
            if not df.empty:
                # 按日期降序排序并获取最新的交易日
                df = df.sort_values('cal_date', ascending=False)
                latest_trade_date = df['cal_date'].iloc[0]
                return latest_trade_date
            return None
        except Exception as e:
            print(f"获取最新交易日期时出错: {str(e)}")
            return None
    
    def check_turnover_rate(self, stock_code):
        """检查换手率是否大于3%"""
        try:
            trade_date = self.get_latest_trade_date()
            if not trade_date:
                return False
            
            # 获取最近的交易日数据
            df = self.pro.daily_basic(ts_code=stock_code, 
                                    trade_date=trade_date)
            if df.empty:
                return False
            
            turnover_rate = df['turnover_rate'].iloc[0]
            #print(f"{stock_code} 换手率: {turnover_rate}%")  # 添加详细信息输出
            return turnover_rate > 3
        except:
            return False
    
    def check_volume_ratio(self, stock_code):
        """检查量比是否大于1.2"""
        try:
            trade_date = self.get_latest_trade_date()
            if not trade_date:
                return False
            
            df = self.pro.daily_basic(ts_code=stock_code, 
                                    trade_date=trade_date)
            if df.empty:
                return False
            
            volume_ratio = df['volume_ratio'].iloc[0]
            #print(f"{stock_code} 量比: {volume_ratio}")  # 添加详细信息输出
            return volume_ratio > 1.2
        except:
            return False
            
    def check_annual_forecast(self, stock_code):
        """检查是否年报预增"""
        try:
            # 获取当前年度
            current_year = datetime.now().year
            period = f"{current_year}1231"  # 年报期末
            
            # 获取最新的业绩预告
            df = self.pro.forecast(ts_code=stock_code, period=period)
            if df.empty:
                return False
            
            forecast_type = df['type'].iloc[0]
            #print(f"{stock_code} 业绩预告类型: {forecast_type}")  # 添加详细信息输出
            return forecast_type in ['预增', '续盈', '略增']
        except:
            return False
    
    def screen_stocks(self):
        """执行选股，返回所有满足条件的股票"""
        result = []
        stocks_df = self.get_stock_list()
        
        # 获取最近交易日期并显示
        trade_date = self.get_latest_trade_date()
        if trade_date:
            print(f"\n正在获取 {trade_date} 的交易数据\n")
        else:
            print("无法获取最近交易日期")
            return []
        
        for _, row in stocks_df.iterrows():
            try:
                stock = row['ts_code']
                #print(f"\n正在检查股票: {stock} ({row['name']})")
                # 分别检查每个条件并存储结果
                turnover_rate = self.check_turnover_rate(stock)
                volume_ratio = self.check_volume_ratio(stock)
                
                # 检查换手率和量比两个条件
                if turnover_rate and volume_ratio:
                    print(f"股票 {stock} ({row['name']}) 符合条件！")
                    result.append({'股票代码': stock, '股票名称': row['name']})
                
                # 避免频繁请求导致被限制
                time.sleep(0.01)
            except Exception as e:
                print(f"处理股票 {stock} 时出错: {str(e)}")
                continue
                
        return result

def main():
    screener = StockScreener()
    selected_stocks = screener.screen_stocks()
    
    if selected_stocks:
        print("\n找到以下符合条件的股票：")
        for stock in selected_stocks:
            print(f"{stock['股票代码']} ({stock['股票名称']})")
        
        # 保存结果到CSV文件
        df = pd.DataFrame(selected_stocks)
        df.to_csv('selected_stocks.csv', index=False, encoding='utf-8-sig')
        print(f"\n共找到 {len(selected_stocks)} 只股票")
        print("结果已保存到 selected_stocks.csv")
    else:
        print("\n未找到符合条件的股票")

if __name__ == "__main__":
    main()