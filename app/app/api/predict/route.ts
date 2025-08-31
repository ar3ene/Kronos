import { NextRequest, NextResponse } from 'next/server';
import { YahooFinanceService } from '@/lib/yahooFinance';
import { KronosService } from '@/lib/kronosService';

export async function POST(request: NextRequest) {
  try {
    const { symbol } = await request.json();

    if (!symbol) {
      return NextResponse.json(
        { error: 'Symbol is required' },
        { status: 400 }
      );
    }

    const yahooService = new YahooFinanceService();
    const kronosService = new KronosService();

    // Fetch weekly data
    const weeklyData = await yahooService.getWeeklyData(symbol);
    
    if (weeklyData.length < 20) {
      return NextResponse.json(
        { error: `Insufficient data for ${symbol}. Only ${weeklyData.length} weeks available.` },
        { status: 400 }
      );
    }

    // Fine-tune model
    const fineTuneResult = await kronosService.fineTuneModel(symbol, weeklyData);
    
    // Generate predictions
    const predictions = await kronosService.predict(symbol, weeklyData);

    return NextResponse.json({
      success: true,
      symbol,
      historicalData: weeklyData.slice(-20),
      predictions,
      metadata: fineTuneResult
    });

  } catch (error) {
    console.error('Prediction error:', error);
    return NextResponse.json(
      { 
        error: 'Prediction failed', 
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}