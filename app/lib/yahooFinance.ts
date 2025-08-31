import axios from 'axios';

export interface WeeklyData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export class YahooFinanceService {
  private baseURL = 'https://query1.finance.yahoo.com/v8/finance/chart';

  async getWeeklyData(symbol: string, period: string = '2y'): Promise<WeeklyData[]> {
    try {
      const url = `${this.baseURL}/${symbol}?range=${period}&interval=1wk`;
      const response = await axios.get(url);
      
      const result = response.data.chart.result[0];
      const timestamps = result.timestamp;
      const quotes = result.indicators.quote[0];
      
      return timestamps.map((timestamp: number, index: number) => ({
        timestamp: new Date(timestamp * 1000).toISOString(),
        open: quotes.open[index],
        high: quotes.high[index],
        low: quotes.low[index],
        close: quotes.close[index],
        volume: quotes.volume[index]
      })).filter((data: WeeklyData) => 
        data.open && data.high && data.low && data.close
      );
    } catch (error) {
      console.error(`Error fetching data for ${symbol}:`, error);
      throw error;
    }
  }
}