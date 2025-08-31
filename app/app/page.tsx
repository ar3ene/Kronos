'use client';

import { useState, useEffect } from 'react';

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
}

interface Prediction {
  success: boolean;
  symbol: string;
  historicalData?: {
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }[];
  predictions?: {
    week: number;
    predictedPrice: number;
    confidence: number;
  }[];
  metadata?: any;
  error?: string;
}

export default function Home() {
  const [userType, setUserType] = useState<'free' | 'premium'>('free');
  const [cryptos, setCryptos] = useState<Stock[]>([]);
  const [customSymbol, setCustomSymbol] = useState('');
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [dailyTests, setDailyTests] = useState(0);

  useEffect(() => {
    fetchCryptos();
    
    const today = new Date().toDateString();
    const lastReset = localStorage.getItem('lastReset');
    
    if (lastReset !== today) {
      setDailyTests(0);
      localStorage.setItem('lastReset', today);
    }
  }, []);

  const fetchCryptos = async () => {
    try {
      const response = await fetch('/api/cryptos');
      const data = await response.json();
      if (data.success) {
        setCryptos(data.cryptos);
      }
    } catch (error) {
      console.error('Failed to fetch cryptos:', error);
    }
  };

  const getRandomStocks = () => 
    [...cryptos].sort(() => Math.random() - 0.5).slice(0, 3);

  const handlePredict = async (symbol: string) => {
    if (userType === 'free' && dailyTests >= 1) {
      alert('免费用户每日只能测试1次');
      return;
    }
    
    if (userType === 'premium' && dailyTests >= 3) {
      alert('今日测试次数已用完');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol })
      });

      if (!response.ok) throw new Error('Prediction failed');
      
      const result = await response.json();
      setPrediction(result);
      setDailyTests(prev => prev + 1);
    } catch (error) {
      alert('预测失败，请重试');
    }
    setLoading(false);
  };

  const randomStocks = getRandomStocks();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-700 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Kronos Predictor</h1>
          <p className="text-blue-100">AI驱动加密货币预测</p>
        </div>

        <div className="bg-white rounded-xl p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-semibold">
                {userType === 'free' ? '免费版' : '高级版'}
              </h2>
              <p className="text-gray-600">
                今日剩余: {userType === 'free' ? 1 - dailyTests : 3 - dailyTests}次
              </p>
            </div>
            <button
              onClick={() => setUserType(userType === 'free' ? 'premium' : 'free')}
              className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition"
            >
              {userType === 'free' ? '升级' : '降级'}
            </button>
          </div>

          {userType === 'free' && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">随机推荐</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {randomStocks.map((stock) => (
                  <div key={stock.symbol} className="border rounded-lg p-4 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold">{stock.symbol}</h4>
                        <p className="text-sm text-gray-600">{stock.name}</p>
                      </div>
                      <span className={`text-sm font-semibold ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-2xl font-bold">${stock.price.toFixed(2)}</p>
                    <button
                      onClick={() => handlePredict(stock.symbol)}
                      disabled={loading || dailyTests >= 1}
                      className="w-full mt-3 bg-blue-500 text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      预测
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {userType === 'premium' && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">精选加密货币</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {cryptos.map((stock) => (
                  <div key={stock.symbol} className="border rounded-lg p-4 hover:shadow-md transition">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold">{stock.symbol}</h4>
                        <p className="text-sm text-gray-600">{stock.name}</p>
                      </div>
                      <span className={`text-sm font-semibold ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-2xl font-bold">${stock.price.toFixed(2)}</p>
                    <button
                      onClick={() => handlePredict(stock.symbol)}
                      disabled={loading || dailyTests >= 3}
                      className="w-full mt-3 bg-green-500 text-white py-2 rounded hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      预测
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">自定义测试</h3>
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="输入加密货币代码 (如: BTC-USD)"
                value={customSymbol}
                onChange={(e) => setCustomSymbol(e.target.value.toUpperCase())}
                className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={() => handlePredict(customSymbol)}
                disabled={loading || !customSymbol || (userType === 'free' && dailyTests >= 1) || (userType === 'premium' && dailyTests >= 3)}
                className="bg-purple-500 text-white px-6 py-2 rounded-lg hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                预测
              </button>
            </div>
          </div>
        </div>

        {loading && (
          <div className="bg-white rounded-xl p-6 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
            <p className="mt-4 text-gray-600">AI正在分析预测中...</p>
          </div>
        )}

        {prediction && !loading && (
          <div className="bg-white rounded-xl p-6">
            <h3 className="text-xl font-semibold mb-4">{prediction.symbol} 预测结果</h3>
            
            {prediction.predictions && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {prediction.predictions.map((pred, index) => (
                  <div key={index} className="text-center p-4 bg-gray-50 rounded">
                    <p className="text-sm text-gray-600">第{pred.week}周</p>
                    <p className="text-lg font-bold">${pred.predictedPrice.toFixed(2)}</p>
                    <p className="text-sm text-blue-600">置信度: {(pred.confidence * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            )}

            {prediction.error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600">{prediction.error}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}