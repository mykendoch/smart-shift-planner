'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { useVolatility } from '@/lib/hooks';
import { Toaster } from 'react-hot-toast';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  TrendingUp,
  AlertCircle,
  CheckCircle,
  BarChart3,
  PieChart,
  DollarSign,
  Info,
  ChevronDown,
} from 'lucide-react';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';

export default function VolatilityPage() {
  const { user } = useAuthStore();
  const [days, setDays] = useState(30);
  const { data, loading, error } = useVolatility(user?.id || '', days);

  const handlePeriodChange = (newDays: number) => {
    setDays(newDays);
    showToast.info(`Analyzing last ${newDays} days...`);
  };

  if (!user || user.role !== 'driver') {
    return (
      <>
        <Toaster />
        <div
          className="rounded-xl p-6 flex items-start gap-4"
          style={{
            background: colors.warning[50],
            border: `1px solid ${colors.warning[200]}`,
          }}
        >
          <AlertCircle size={24} color={colors.warning[600]} style={{ marginTop: spacing.xs }} />
          <div>
            <p
              style={{
                color: colors.warning[900],
                fontWeight: fonts.weights.semibold,
              }}
            >
              Access Restricted
            </p>
            <p
              style={{
                color: colors.warning[700],
                fontSize: fonts.sizes.caption,
                marginTop: spacing.xs,
              }}
            >
              This page is only available to drivers.
            </p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Toaster />
      <div className="space-y-8">
        {/* Page Header */}
        <div
          className="rounded-xl p-8 text-white overflow-hidden"
          style={{
            background: `linear-gradient(135deg, ${colors.secondary[600]} 0%, ${colors.secondary[700]} 100%)`,
            boxShadow: '0 10px 30px rgba(168, 85, 247, 0.3)',
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div
              className="w-14 h-14 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(255, 255, 255, 0.2)' }}
            >
              <TrendingUp size={28} />
            </div>
            <div>
              <h1
                style={{
                  fontSize: fonts.sizes.h3,
                  fontWeight: fonts.weights.bold,
                }}
              >
                Shift Insights
              </h1>
              <p
                style={{
                  fontSize: fonts.sizes.caption,
                  opacity: 0.9,
                  marginTop: spacing.xs,
                }}
              >
                Income stability analysis with guaranteed shifts
              </p>
            </div>
          </div>
        </div>

        {/* Period Selector */}
        <div
          className="rounded-xl p-6"
          style={{
            background: colors.neutral[0],
            border: `1px solid ${colors.neutral[200]}`,
          }}
        >
          <label
            style={{
              display: 'block',
              color: colors.neutral[700],
              fontWeight: fonts.weights.semibold,
              marginBottom: spacing.md,
              fontSize: fonts.sizes.body,
            }}
          >
            Analysis Period
          </label>
          <div className="flex flex-wrap gap-3">
            {[
              { days: 7, label: 'Last 7 days' },
              { days: 14, label: 'Last 14 days' },
              { days: 30, label: 'Last 30 days' },
              { days: 90, label: 'Last 90 days' },
            ].map(({ days: d, label }) => (
              <button
                key={d}
                onClick={() => handlePeriodChange(d)}
                className="px-6 py-3 rounded-lg font-medium transition-all hover:scale-105"
                style={{
                  background: days === d ? colors.secondary[600] : colors.neutral[100],
                  color: days === d ? 'white' : colors.neutral[700],
                  border: `1px solid ${days === d ? colors.secondary[600] : colors.neutral[200]}`,
                  fontSize: fonts.sizes.body,
                  fontWeight: fonts.weights.semibold,
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div
            className="rounded-xl p-6 flex items-start gap-4"
            style={{
              background: colors.error[50],
              border: `1px solid ${colors.error[200]}`,
            }}
          >
            <AlertCircle size={24} color={colors.error[600]} style={{ marginTop: spacing.xs }} />
            <div>
              <p
                style={{
                  color: colors.error[900],
                  fontWeight: fonts.weights.semibold,
                }}
              >
                Error Loading Data
              </p>
              <p
                style={{
                  color: colors.error[700],
                  fontSize: fonts.sizes.caption,
                  marginTop: spacing.xs,
                }}
              >
                {error}
              </p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div
            className="rounded-xl p-8 text-center"
            style={{
              background: colors.neutral[50],
              border: `1px solid ${colors.neutral[200]}`,
            }}
          >
            <div className="inline-block">
              <div
                className="w-12 h-12 rounded-full border-4 border-transparent animate-spin mb-4"
                style={{
                  borderTopColor: colors.secondary[500],
                  borderRightColor: colors.secondary[500],
                }}
              ></div>
            </div>
            <p
              style={{
                color: colors.neutral[600],
                fontWeight: fonts.weights.semibold,
                fontSize: fonts.sizes.body,
              }}
            >
              Analyzing your income patterns...
            </p>
          </div>
        )}

        {/* Data Display */}
        {data && !loading && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                icon={TrendingUp}
                title="Stability Boost"
                value={`${(data.impact?.volatility_reduction_percent || 0).toFixed(1)}%`}
                subtitle="Income variance reduction"
                color={colors.success[500]}
                bgColor={colors.success[50]}
              />
              <MetricCard
                icon={BarChart3}
                title="Earnings Consistency"
                value={data.with_guarantee?.cv?.toFixed(2) || 'N/A'}
                subtitle="Coefficient of variation (lower is better)"
                color={colors.secondary[500]}
                bgColor={colors.secondary[50]}
              />
              <MetricCard
                icon={DollarSign}
                title="Average Daily Earnings"
                value={`$${(data.without_guarantee?.mean || 0).toFixed(2)}`}
                subtitle="Based on your shift history"
                color={colors.primary[500]}
                bgColor={colors.primary[50]}
              />
            </div>

            {/* Earnings Comparison Chart */}
            <div
              className="rounded-xl p-6"
              style={{
                background: colors.neutral[0],
                border: `1px solid ${colors.neutral[200]}`,
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
              }}
            >
              <div className="mb-6">
                <h2
                  style={{
                    fontSize: fonts.sizes.h5,
                    fontWeight: fonts.weights.bold,
                    color: colors.neutral[900],
                  }}
                >
                  Earnings Comparison
                </h2>
                <p
                  style={{
                    fontSize: fonts.sizes.caption,
                    color: colors.neutral[500],
                    marginTop: spacing.xs,
                  }}
                >
                  Earnings stability with vs without guaranteed shifts
                </p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={[data.without_guarantee, data.with_guarantee]}
                  margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.neutral[200]} />
                  <XAxis dataKey="name" stroke={colors.neutral[500]} />
                  <YAxis stroke={colors.neutral[500]} />
                  <Tooltip
                    contentStyle={{
                      background: colors.neutral[900],
                      border: `1px solid ${colors.neutral[700]}`,
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Legend />
                  <Bar dataKey="mean" fill={colors.primary[500]} name="Average Earnings" />
                  <Bar dataKey="std" fill={colors.error[500]} name="Std Deviation" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StatisticsCard
                title="Without Guarantee"
                stats={data.without_guarantee}
                color={colors.error}
              />
              <StatisticsCard
                title="With Guarantee"
                stats={data.with_guarantee}
                color={colors.success}
              />
            </div>

            {/* Key Insights */}
            <div
              className="rounded-xl p-6"
              style={{
                background: colors.success[50],
                border: `1px solid ${colors.success[200]}`,
              }}
            >
              <div className="flex items-start gap-4">
                <div style={{ marginTop: spacing.xs }}>
                  <CheckCircle size={24} color={colors.success[600]} />
                </div>
                <div className="flex-1">
                  <h3
                    style={{
                      fontWeight: fonts.weights.semibold,
                      color: colors.success[900],
                      fontSize: fonts.sizes.body,
                      marginBottom: spacing.md,
                    }}
                  >
                    Key Insights
                  </h3>
                  <ul className="space-y-3">
                    <InsightItem
                      text={`Your income is ${(data.impact?.volatility_reduction_percent || 0).toFixed(1)}% more stable with guaranteed shifts`}
                    />
                    <InsightItem
                      text={`Standard deviation reduced from $${(data.without_guarantee?.std || 0).toFixed(2)} to $${(data.with_guarantee?.std || 0).toFixed(2)}`}
                    />
                    <InsightItem text="Better predictability helps with budgeting and financial planning" />
                    <InsightItem text="Guaranteed shifts provide reliable income security" />
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {!data && !loading && !error && (
          <div
            className="rounded-xl p-8 text-center"
            style={{
              background: colors.neutral[50],
              border: `1px solid ${colors.neutral[200]}`,
            }}
          >
            <Info size={48} color={colors.neutral[400]} className="mx-auto mb-4" />
            <p
              style={{
                color: colors.neutral[600],
                fontSize: fonts.sizes.body,
              }}
            >
              No data available for the selected period
            </p>
          </div>
        )}
      </div>
    </>
  );
}

interface MetricCardProps {
  icon: React.ForwardRefExoticComponent<any>;
  title: string;
  value: string;
  subtitle: string;
  color: string;
  bgColor: string;
}

function MetricCard({ icon: Icon, title, value, subtitle, color, bgColor }: MetricCardProps) {
  return (
    <div
      className="rounded-xl p-6 hover:shadow-lg transition-all hover:scale-105"
      style={{
        background: bgColor,
        border: `1px solid ${color}20`,
      }}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ background: `${color}20` }}
        >
          <Icon size={24} color={color} />
        </div>
      </div>

      <p
        style={{
          color: colors.neutral[600],
          fontSize: fonts.sizes.caption,
          fontWeight: fonts.weights.semibold,
          marginBottom: spacing.xs,
        }}
      >
        {title}
      </p>

      <p
        className="text-3xl font-bold mb-2"
        style={{
          color: color,
        }}
      >
        {value}
      </p>

      <p
        style={{
          color: colors.neutral[600],
          fontSize: fonts.sizes.caption,
          lineHeight: 1.5,
        }}
      >
        {subtitle}
      </p>
    </div>
  );
}

interface StatisticsCardProps {
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
  color: Record<string, string>;
}

function StatisticsCard({ title, stats, color }: StatisticsCardProps) {
  return (
    <div
      className="rounded-xl p-6"
      style={{
        background: colors.neutral[0],
        border: `1px solid ${colors.neutral[200]}`,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
      }}
    >
      <div className="flex items-center gap-3 mb-6 pb-4" style={{ borderBottom: `1px solid ${colors.neutral[200]}` }}>
        <div
          className="w-3 h-3 rounded-full"
          style={{ background: color[500] }}
        ></div>
        <h3
          style={{
            fontWeight: fonts.weights.bold,
            color: colors.neutral[900],
            fontSize: fonts.sizes.body,
          }}
        >
          {title}
        </h3>
      </div>

      <div className="space-y-3">
        <StatRow label="Mean (μ)" value={`$${(stats.mean || 0).toFixed(2)}`} />
        <StatRow label="Std Deviation (σ)" value={`$${(stats.std || 0).toFixed(2)}`} />
        <StatRow label="Coefficient of Variation" value={`${(stats.cv || 0).toFixed(2)}%`} />
        <StatRow label="Min Earnings" value={`$${(stats.min || 0).toFixed(2)}`} />
        <StatRow label="Max Earnings" value={`$${(stats.max || 0).toFixed(2)}`} />
        <StatRow label="Median (Q2)" value={`$${(stats.median || 0).toFixed(2)}`} />
        <StatRow label="Q1 (25%)" value={`$${(stats.q1 || 0).toFixed(2)}`} />
        <StatRow label="Q3 (75%)" value={`$${(stats.q3 || 0).toFixed(2)}`} />
        <StatRow label="Interquartile Range" value={`$${(stats.iqr || 0).toFixed(2)}`} />
      </div>
    </div>
  );
}

function StatRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2">
      <span
        style={{
          color: colors.neutral[600],
          fontSize: fonts.sizes.body,
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontWeight: fonts.weights.semibold,
          color: colors.neutral[900],
          fontSize: fonts.sizes.body,
        }}
      >
        {value}
      </span>
    </div>
  );
}

function InsightItem({ text }: { text: string }) {
  return (
    <div className="flex gap-3">
      <CheckCircle size={18} color={colors.success[600]} style={{ marginTop: spacing.xs, flexShrink: 0 }} />
      <span
        style={{
          color: colors.success[800],
          fontSize: fonts.sizes.body,
          lineHeight: 1.5,
        }}
      >
        {text}
      </span>
    </div>
  );
}
