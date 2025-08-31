import { NextResponse } from 'next/server';

const CRYPTO_LIST = [
  'BTC-USD',  // Bitcoin
  'ETH-USD',  // Ethereum  
  'BNB-USD',  // Binance Coin
  'SOL-USD',  // Solana
  'XRP-USD',  // Ripple
  'ADA-USD',  // Cardano
  'DOGE-USD', // Dogecoin
  'DOT-USD',  // Polkadot
  'AVAX-USD', // Avalanche
  'LINK-USD'  // Chainlink
];

export async function GET() {
  return NextResponse.json({
    success: true,
    cryptos: CRYPTO_LIST.map(symbol => ({
      symbol,
      name: symbol.split('-')[0],
      price: Math.random() * 1000 + 50,
      change: (Math.random() - 0.5) * 10
    }))
  });
}