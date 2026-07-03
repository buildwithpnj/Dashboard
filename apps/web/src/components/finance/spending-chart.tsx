'use client';

import { useDashboard } from '@/hooks/use-finance';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { formatCurrency } from '@/lib/utils';

export function SpendingChart() {
  const { data: summary } = useDashboard();

  if (!summary || summary.spending_by_category.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <p className="text-sm text-muted-foreground">No spending data yet</p>
      </div>
    );
  }

  const data = summary.spending_by_category;

  return (
    <div>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={2}
            dataKey="amount"
            nameKey="category"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.color} stroke="transparent" />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload?.length) {
                const item = payload[0].payload;
                return (
                  <div className="rounded-md border border-border bg-popover px-3 py-2 shadow-lg">
                    <p className="text-[13px] font-medium text-foreground">{item.category}</p>
                    <p className="text-2xs text-muted-foreground">{formatCurrency(item.amount)}</p>
                  </div>
                );
              }
              return null;
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-3 space-y-1.5">
        {data.map((item, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-[13px] text-foreground">{item.category}</span>
            </div>
            <span className="text-[13px] font-mono text-muted-foreground tabular-nums">
              {formatCurrency(item.amount)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
