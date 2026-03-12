import React from 'react';

interface RiskItem {
  id: string;
  name: string;
  probability: number; // 1 to 5
  consequence: string; // A to E
}

interface RiskHeatMapProps {
  items?: RiskItem[];
}

const CONSEQUENCES = ['A', 'B', 'C', 'D', 'E'];
const PROBABILITIES = [5, 4, 3, 2, 1];

export const RiskHeatMap: React.FC<RiskHeatMapProps> = ({ items = [] }) => {
  
  // Helper to get color based on coordinates (Standard RBI 581 Matrix)
  const getCellColor = (prob: number, cons: string) => {
    const consIdx = CONSEQUENCES.indexOf(cons) + 1; // 1 to 5
    
    // Sum-based approach for risk levels (Approximation of ISO 17776 / API 581)
    const riskScore = prob + consIdx;
    
    if (riskScore <= 3) return 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 border-emerald-200';
    if (riskScore <= 5) return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 border-yellow-200';
    if (riskScore <= 7) return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 border-orange-200';
    if (riskScore <= 9) return 'bg-red-100 dark:bg-red-900/30 text-red-700 border-red-200';
    return 'bg-rose-600 text-white border-rose-700';
  };

  const getItemsInCell = (prob: number, cons: string) => {
    return items.filter(item => item.probability === prob && item.consequence === cons);
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-800 w-full max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center">
          Risk Matrix <span className="ml-2 text-xs font-normal text-slate-400">API 581 Standard</span>
        </h3>
        <div className="flex space-x-2">
           <div className="flex items-center space-x-1">
             <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
             <span className="text-[10px] text-slate-500">Low</span>
           </div>
           <div className="flex items-center space-x-1">
             <div className="w-3 h-3 rounded-full bg-red-500"></div>
             <span className="text-[10px] text-slate-500">High</span>
           </div>
        </div>
      </div>

      <div className="grid grid-cols-6 gap-2">
        {/* Empty top-left cell */}
        <div className="flex items-center justify-center text-[10px] font-bold text-slate-400">Prob \ Cons</div>
        
        {/* Consequence Headers */}
        {CONSEQUENCES.map(c => (
          <div key={c} className="flex items-center justify-center font-bold text-slate-500 dark:text-slate-400 p-2">
            {c}
          </div>
        ))}

        {/* Matrix Rows */}
        {PROBABILITIES.map(p => (
          <React.Fragment key={p}>
            {/* Probability Header */}
            <div className="flex items-center justify-center font-bold text-slate-500 dark:text-slate-400 p-2 border-r border-slate-100 dark:border-slate-800">
              {p}
            </div>
            
            {/* Cells */}
            {CONSEQUENCES.map(c => {
              const cellItems = getItemsInCell(p, c);
              return (
                <div 
                  key={`${p}-${c}`} 
                  className={`aspect-square rounded-lg border flex flex-wrap gap-1 p-1 items-center justify-center transition-all hover:scale-105 cursor-pointer relative ${getCellColor(p, c)}`}
                >
                  {cellItems.length > 0 && (
                    <div className="w-6 h-6 rounded-full bg-white/80 dark:bg-black/30 flex items-center justify-center text-[10px] font-bold shadow-sm animate-pulse">
                      {cellItems.length}
                    </div>
                  )}
                  <span className="absolute bottom-0 right-1 text-[8px] opacity-20 font-bold">{p}{c}</span>
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
      
      <div className="mt-4 flex justify-center space-x-4 text-[10px] text-slate-400 uppercase tracking-widest font-bold">
        <span>Consequence →</span>
      </div>
    </div>
  );
};
