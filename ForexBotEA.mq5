#property strict
#property version "1.00"

int ma5Handle;
int ma40Handle;
int ma75Handle;
int rsiHandle;

datetime lastBarTime = 0;

int OnInit()
{
   ma5Handle = iMA(_Symbol, PERIOD_H1, 5, 0, MODE_SMA, PRICE_CLOSE);
   ma40Handle = iMA(_Symbol, PERIOD_H1, 40, 0, MODE_SMA, PRICE_CLOSE);
   ma75Handle = iMA(_Symbol, PERIOD_H1, 75, 0, MODE_SMA, PRICE_CLOSE);
   rsiHandle = iRSI(_Symbol, PERIOD_H1, 14, PRICE_CLOSE);

   if(ma5Handle == INVALID_HANDLE ||
      ma40Handle == INVALID_HANDLE ||
      ma75Handle == INVALID_HANDLE ||
      rsiHandle == INVALID_HANDLE)
   {
      Print("ERROR: Could not create indicator handles.");
      return(INIT_FAILED);
   }

   Print("ForexBotEA initialized.");
   Print("Strategy: MA 5/40/75 + RSI 14");
   Print("Signal-only mode: NO TRADES");

   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   IndicatorRelease(ma5Handle);
   IndicatorRelease(ma40Handle);
   IndicatorRelease(ma75Handle);
   IndicatorRelease(rsiHandle);
}

void OnTick()
{
   datetime currentBarTime = iTime(_Symbol, PERIOD_H1, 0);

   if(currentBarTime == lastBarTime)
      return;

   lastBarTime = currentBarTime;

   CheckSignal();
}

void CheckSignal()
{
   double ma5[];
   double ma40[];
   double ma75[];
   double rsi[];

   ArraySetAsSeries(ma5, true);
   ArraySetAsSeries(ma40, true);
   ArraySetAsSeries(ma75, true);
   ArraySetAsSeries(rsi, true);

   if(CopyBuffer(ma5Handle, 0, 0, 3, ma5) < 3)
      return;

   if(CopyBuffer(ma40Handle, 0, 0, 3, ma40) < 3)
      return;

   if(CopyBuffer(ma75Handle, 0, 0, 3, ma75) < 3)
      return;

   if(CopyBuffer(rsiHandle, 0, 0, 3, rsi) < 3)
      return;

   double current = iClose(_Symbol, PERIOD_H1, 1);
   double previous = iClose(_Symbol, PERIOD_H1, 2);

   double trendStrength = MathAbs(ma5[1] - ma75[1]);

   Print("MA5=", ma5[1],
         " MA40=", ma40[1],
         " MA75=", ma75[1],
         " RSI=", rsi[1],
         " Trend=", trendStrength);

   if(trendStrength < 0.0006)
   {
      Print("SIGNAL: HOLD - trend too weak");
      return;
   }

   bool bullish = ma5[1] > ma40[1] &&
                  ma40[1] > ma75[1];

   bool bearish = ma5[1] < ma40[1] &&
                  ma40[1] < ma75[1];

   bool bullishRecovery = previous <= ma5[2] &&
                          current > ma5[1];

   bool bearishRecovery = previous >= ma5[2] &&
                          current < ma5[1];

   if(bullish && bullishRecovery &&
      rsi[1] > 53 && rsi[1] < 60)
   {
      Print("SIGNAL: BUY");
      return;
   }

   if(bearish && bearishRecovery &&
      rsi[1] > 40 && rsi[1] < 50)
   {
      Print("SIGNAL: SELL");
      return;
   }

   Print("SIGNAL: HOLD");
}
