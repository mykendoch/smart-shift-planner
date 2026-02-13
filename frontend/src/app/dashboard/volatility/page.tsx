'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { useVolatility } from '@/lib/hooks';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function VolatilityPage() {
  const { user } = useAuthStore();
  const [days, setDays] = useState(30);
  const { data, loading, error } = useVolatility(user?.id || '', days);

  if (!user || user.role !== 'driver') {
    return (
      <div className="card bg-yellow-50 border border-yellow-200">
        <p className="text-yellow-800">This page is only available to drivers.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="card">
        <h1 className="text-3xl font-bold mb-2">Income Insights</h1>
        <p className="text-gray-600">
          Analyze how guaranteed shifts help stabilize your earnings
        </p>
      </div>

      {/* Controls */}
      <div className="card">
        <label className="block text-gray-700 font-medium mb-2">
          Analysis Period (days):
        </label>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="input-field max-w-xs"
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {error && (
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="card text-center py-8">
          <p className="text-gray-600">Loading income insights...</p>
        </div>
      ) : data ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <SummaryCard
              title="Volatility Reduction"
              value={`${(data.impact?.volatility_reduction_percent || 0).toFixed(1)}%`}
              subtitle="Income variance reduction with guarantee"
              color="bg-green-50"
            />
            <SummaryCard
              title="Earnings Stability"
              value={data.with_guarantee?.cv?.toFixed(2) || 'N/A'}
              subtitle="Coefficient of variation (lower is better)"
              color="bg-blue-50"
            />
            <SummaryCard
              title="Average Daily Earnings"
              value={`$${(data.without_guarantee?.mean || 0).toFixed(2)}`}
              subtitle="Based on shift history"
              color="bg-purple-50"
            />
          </div>

          {/* Earnings Comparison */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Earnings Comparison</h2>
            <div className="overflow-x-auto">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[data.without_guarantee, data.with_guarantee]} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="mean" fill="#3B82F6" name="Average Earnings" />
                  <Bar dataKey="std" fill="#EF4444" name="Std Deviation" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Detailed Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <StatisticsCard
              title="Without Guarantee"
              stats={data.without_guarantee}
            />
            <StatisticsCard
              title="With Guarantee"
              stats={data.with_guarantee}
            />
          </div>

          {/* Insights */}
          <div className="card bg-blue-50 border border-blue-200">
            <h3 className="font-bold text-blue-900 mb-2">💡 Key Insights</h3>
            <ul className="space-y-2 text-blue-800 text-sm">
              <li>
                ✓ Your income is {(data.impact?.volatility_reduction_percent || 0).toFixed(1)}% more
                stable with guaranteed shifts
              </li>
              <li>
                ✓ Standard deviation reduced from ${(data.without_guarantee?.std || 0).toFixed(2)} to $
                {(data.with_guarantee?.std || 0).toFixed(2)}
              </li>
              <li>
                ✓ Better predictability helps with budgeting and financial planning
              </li>
            </ul>
          </div>
        </>
      ) : (
        <div className="card text-center py-8">
          <p className="text-gray-600">No data available for the selected period</p>
        </div>
      )}
    </div>
  );
}

function SummaryCard({
  title,
  value,
  subtitle,
  color,
}: {
  title: string;
  value: string;
  subtitle: string;
  color: string;
}) {
  return (
    <div className={`card ${color}`}>
      <p className="text-gray-600 text-sm">{title}</p>
      <p className="text-3xl font-bold text-gray-800 my-1">{value}</p>
      <p className="text-xs text-gray-600">{subtitle}</p>
    </div>
  );
}

function StatisticsCard({
  title,
  stats,
}: {
  title: string;
  stats: {
    mean?: number;
    std?: number;
    variance?: number;
    cv?: number;
    min?: number;
    max?: number;
    q1?: number;
    median?: number;
    q3?: number;
    iqr?: number;
  };
}) {
  return (
    <div className="card">
      <h3 className="font-bold text-gray-800 mb-4">{title}</h3>
      <div className="space-y-3 text-sm">
        <StatRow label="Mean (μ)" value={`$${(stats.mean || 0).toFixed(2)}`} />
        <StatRow
          label="Std Deviation (σ)"
          value={`$${(stats.std || 0).toFixed(2)}`}
        />
        <StatRow
          label="Coefficient of Variation"
          value={`${(stats.cv || 0).toFixed(2)}%`}
        />
        <StatRow
          label="Min Earnings"
          value={`$${(stats.min || 0).toFixed(2)}`}
        />
        <StatRow
          label="Max Earnings"
          value={`$${(stats.max || 0).toFixed(2)}`}
        />
        <StatRow
          label="Median (Q2)"
          value={`$${(stats.median || 0).toFixed(2)}`}
        />
        <StatRow label="Q1 (25%)" value={`$${(stats.q1 || 0).toFixed(2)}`} />
        <StatRow label="Q3 (75%)" value={`$${(stats.q3 || 0).toFixed(2)}`} />
        <StatRow
          label="Interquartile Range"
          value={`$${(stats.iqr || 0).toFixed(2)}`}
        />
      </div>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-gray-600">{label}:</span>
      <span className="font-semibold text-gray-800">{value}</span>
    </div>
  );
}
