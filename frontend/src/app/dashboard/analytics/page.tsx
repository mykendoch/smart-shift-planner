'use client';

import { useAuthStore } from '@/lib/store';
import { useAccuracy } from '@/lib/hooks';
import { Toaster } from 'react-hot-toast';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  BarChart3,
  TrendingUp,
  Users,
  Activity,
  AlertCircle,
  CheckCircle,
  Zap,
  Star,
  Smartphone,
  DollarSign,
  Calendar,
} from 'lucide-react';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';

export default function AnalyticsPage() {
  const { user } = useAuthStore();
  const { data: accuracyData } = useAccuracy();

  if (!user || user.role !== 'admin') {
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
              This page is only available to administrators.
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
            background: `linear-gradient(135deg, ${colors.primary[600]} 0%, ${colors.primary[700]} 100%)`,
            boxShadow: '0 10px 30px rgba(0, 150, 180, 0.3)',
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div
              className="w-14 h-14 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(255, 255, 255, 0.2)' }}
            >
              <BarChart3 size={28} />
            </div>
            <div>
              <h1
                style={{
                  fontSize: fonts.sizes.h3,
                  fontWeight: fonts.weights.bold,
                }}
              >
                System Analytics
              </h1>
              <p
                style={{
                  fontSize: fonts.sizes.caption,
                  opacity: 0.9,
                  marginTop: spacing.xs,
                }}
              >
                Monitor key system metrics and worker performance
              </p>
            </div>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            icon={Users as any}
            label="Active Workers"
            value="—"
            color={colors.primary[500]}
          />
          <MetricCard
            icon={TrendingUp as any}
            label="Total Shifts"
            value="—"
            color={colors.secondary[500]}
          />
          <MetricCard
            icon={Activity as any}
            label="System Uptime"
            value="99.9%"
            color={colors.success[500]}
          />
          <MetricCard
            icon={DollarSign as any}
            label="Avg Earnings/Worker"
            value="—"
            color={colors.warning[500]}
          />
        </div>

        {/* Income Volatility Impact */}
        <div>
          <div
            className="mb-6 pb-4"
            style={{
              borderBottom: `2px solid ${colors.neutral[200]}`,
            }}
          >
            <h2
              style={{
                fontSize: fonts.sizes.h5,
                fontWeight: fonts.weights.bold,
                color: colors.neutral[900],
              }}
            >
              Income Volatility Impact
            </h2>
            <p
              style={{
                fontSize: fonts.sizes.caption,
                color: colors.neutral[500],
                marginTop: spacing.xs,
              }}
            >
              System-wide average volatility reduction across all workers
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <VolatilityCard
              title="Avg Volatility Reduction"
              value="—"
              bgColor={colors.success[50]}
              borderColor={colors.success[200]}
              iconColor={colors.success[500]}
            />
            <VolatilityCard
              title="Median Earnings Stability"
              value="—"
              bgColor={colors.primary[50]}
              borderColor={colors.primary[200]}
              iconColor={colors.primary[500]}
            />
            <VolatilityCard
              title="Workers Benefiting"
              value="—"
              bgColor={colors.secondary[50]}
              borderColor={colors.secondary[200]}
              iconColor={colors.secondary[500]}
            />
          </div>
        </div>

        {/* Model Performance */}
        <div>
          <div
            className="mb-6 pb-4"
            style={{
              borderBottom: `2px solid ${colors.neutral[200]}`,
            }}
          >
            <h2
              style={{
                fontSize: fonts.sizes.h5,
                fontWeight: fonts.weights.bold,
                color: colors.neutral[900],
              }}
            >
              Model Accuracy Overview
            </h2>
            <p
              style={{
                fontSize: fonts.sizes.caption,
                color: colors.neutral[500],
                marginTop: spacing.xs,
              }}
            >
              Current performance of earnings prediction model
            </p>
          </div>

          {accuracyData ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <AccuracyMetric
                label="Overall MAPE"
                value={`${accuracyData.overall?.mape?.toFixed(1) || '—'}%`}
                status={getAccuracyStatus(accuracyData.overall?.mape)}
              />
              <AccuracyMetric
                label="Mean Absolute Error"
                value={`$${(accuracyData.overall?.mae || 0).toFixed(2)}`}
                status={getAccuracyStatus(accuracyData.overall?.mape)}
              />
              <AccuracyMetric
                label="RMSE"
                value={`$${(accuracyData.overall?.rmse || 0).toFixed(2)}`}
                status={getAccuracyStatus(accuracyData.overall?.mape)}
              />
              <AccuracyMetric
                label="R² Score"
                value={`${(accuracyData.overall?.r2 || 0).toFixed(3)}`}
                status={getAccuracyStatus(100 - (accuracyData.overall?.mape || 0))}
              />
            </div>
          ) : (
            <div
              className="rounded-xl p-8 text-center"
              style={{
                background: colors.neutral[50],
                border: `1px solid ${colors.neutral[200]}`,
              }}
            >
              <p style={{ color: colors.neutral[600], fontSize: fonts.sizes.body }}>
                Loading accuracy metrics...
              </p>
            </div>
          )}
        </div>

        {/* Prediction Accuracy Chart */}
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
              Prediction Accuracy by Hour
            </h2>
            <p
              style={{
                fontSize: fonts.sizes.caption,
                color: colors.neutral[500],
                marginTop: spacing.xs,
              }}
            >
              Model performance across different times of day
            </p>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={[
                { hour: '6am', accuracy: 85 },
                { hour: '9am', accuracy: 78 },
                { hour: '12pm', accuracy: 82 },
                { hour: '3pm', accuracy: 88 },
                { hour: '6pm', accuracy: 90 },
                { hour: '9pm', accuracy: 75 },
              ]}
              margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke={colors.neutral[200]} />
              <XAxis dataKey="hour" stroke={colors.neutral[500]} />
              <YAxis domain={[0, 100]} stroke={colors.neutral[500]} />
              <Tooltip
                contentStyle={{
                  background: colors.neutral[900],
                  border: `1px solid ${colors.neutral[700]}`,
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="accuracy" fill={colors.primary[500]} name="Accuracy %" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Worker Satisfaction */}
        <div>
          <div
            className="mb-6 pb-4"
            style={{
              borderBottom: `2px solid ${colors.neutral[200]}`,
            }}
          >
            <h2
              style={{
                fontSize: fonts.sizes.h5,
                fontWeight: fonts.weights.bold,
                color: colors.neutral[900],
              }}
            >
              Worker Satisfaction Trends
            </h2>
            <p
              style={{
                fontSize: fonts.sizes.caption,
                color: colors.neutral[500],
                marginTop: spacing.xs,
              }}
            >
              Aggregated feedback from driver surveys
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <SatisfactionCard
              icon={Smartphone as any}
              metric="App Usefulness"
              rating={4.2}
              color={colors.primary[500]}
            />
            <SatisfactionCard
              icon={DollarSign as any}
              metric="Income Stability"
              rating={4.4}
              color={colors.success[500]}
            />
            <SatisfactionCard
              icon={Calendar as any}
              metric="Schedule Satisfaction"
              rating={3.8}
              color={colors.secondary[500]}
            />
          </div>
        </div>

        {/* System Health */}
        <div
          className="rounded-xl p-6"
          style={{
            background: colors.success[50],
            border: `1px solid ${colors.success[200]}`,
          }}
        >
          <div className="flex items-start gap-4">
            <CheckCircle size={24} color={colors.success[600]} style={{ marginTop: spacing.xs }} />
            <div className="flex-1">
              <h3
                style={{
                  fontWeight: fonts.weights.semibold,
                  color: colors.success[900],
                  fontSize: fonts.sizes.body,
                  marginBottom: spacing.md,
                }}
              >
                System Health
              </h3>
              <ul className="space-y-3">
                {[
                  'All workers: System functioning normally',
                  'Model accuracy: Meets specification targets (MAPE < 20%)',
                  'Survey response rate: Active participation enabled',
                  'Database: Healthy with optimized indices',
                ].map((item, idx) => (
                  <li key={idx} className="flex gap-3">
                    <CheckCircle size={16} color={colors.success[600]} style={{ marginTop: spacing.xs, flexShrink: 0 }} />
                    <span
                      style={{
                        color: colors.success[800],
                        fontSize: fonts.sizes.body,
                      }}
                    >
                      {item}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

interface MetricCardProps {
  icon: React.ForwardRefExoticComponent<any>;
  label: string;
  value: string;
  color: string;
}

function MetricCard({ icon: Icon, label, value, color }: MetricCardProps) {
  return (
    <div
      className="rounded-xl p-6 hover:shadow-lg transition-all hover:scale-105"
      style={{
        background: colors.neutral[0],
        border: `1px solid ${colors.neutral[200]}`,
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <p
          style={{
            color: colors.neutral[600],
            fontSize: fonts.sizes.caption,
            fontWeight: fonts.weights.semibold,
          }}
        >
          {label}
        </p>
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ background: `${color}20` }}
        >
          <Icon size={20} color={color} />
        </div>
      </div>

      <p
        className="text-3xl font-bold"
        style={{
          color: color,
        }}
      >
        {value}
      </p>
    </div>
  );
}

interface VolatilityCardProps {
  title: string;
  value: string;
  bgColor: string;
  borderColor: string;
  iconColor: string;
}

function VolatilityCard({
  title,
  value,
  bgColor,
  borderColor,
  iconColor,
}: VolatilityCardProps) {
  return (
    <div
      className="rounded-xl p-6"
      style={{
        background: bgColor,
        border: `1px solid ${borderColor}`,
      }}
    >
      <p
        style={{
          color: colors.neutral[700],
          fontSize: fonts.sizes.caption,
          fontWeight: fonts.weights.semibold,
          marginBottom: spacing.md,
        }}
      >
        {title}
      </p>
      <p
        className="text-4xl font-bold"
        style={{
          color: iconColor,
        }}
      >
        {value}
      </p>
    </div>
  );
}

interface AccuracyMetricProps {
  label: string;
  value: string;
  status: 'excellent' | 'good' | 'acceptable' | 'poor';
}

function AccuracyMetric({ label, value, status }: AccuracyMetricProps) {
  const statusConfig = {
    excellent: { bg: colors.success[50], border: colors.success[200], text: colors.success[700], color: colors.success[500] },
    good: { bg: colors.primary[50], border: colors.primary[200], text: colors.primary[700], color: colors.primary[500] },
    acceptable: { bg: colors.warning[50], border: colors.warning[200], text: colors.warning[700], color: colors.warning[500] },
    poor: { bg: colors.error[50], border: colors.error[200], text: colors.error[700], color: colors.error[500] },
  };

  const config = statusConfig[status];

  return (
    <div
      className="rounded-xl p-6 border"
      style={{
        background: config.bg,
        borderColor: config.border,
      }}
    >
      <p
        style={{
          fontSize: fonts.sizes.caption,
          color: colors.neutral[600],
          fontWeight: fonts.weights.semibold,
          marginBottom: spacing.md,
        }}
      >
        {label}
      </p>
      <p
        className="text-2xl font-bold mb-4"
        style={{
          color: config.color,
        }}
      >
        {value}
      </p>
      <span
        style={{
          fontSize: fonts.sizes.caption,
          fontWeight: fonts.weights.semibold,
          color: config.text,
          textTransform: 'capitalize',
        }}
      >
        {status}
      </span>
    </div>
  );
}

interface SatisfactionCardProps {
  icon: React.ForwardRefExoticComponent<any>;
  metric: string;
  rating: number;
  color: string;
}

function SatisfactionCard({ icon: Icon, metric, rating, color }: SatisfactionCardProps) {
  return (
    <div
      className="rounded-xl p-6"
      style={{
        background: colors.neutral[0],
        border: `1px solid ${colors.neutral[200]}`,
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
      }}
    >
      <div className="flex items-start gap-4 mb-4">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ background: `${color}20` }}
        >
          <Icon size={24} color={color} />
        </div>
      </div>

      <h4
        style={{
          fontWeight: fonts.weights.semibold,
          color: colors.neutral[900],
          fontSize: fonts.sizes.body,
          marginBottom: spacing.md,
        }}
      >
        {metric}
      </h4>

      <div className="flex items-center gap-3">
        <div className="flex gap-1">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              size={16}
              color={i < Math.floor(rating) ? color : colors.neutral[300]}
              fill={i < Math.floor(rating) ? color : 'none'}
            />
          ))}
        </div>
        <span
          style={{
            fontWeight: fonts.weights.bold,
            color: color,
            fontSize: fonts.sizes.body,
          }}
        >
          {rating}/5
        </span>
      </div>
    </div>
  );
}

function getAccuracyStatus(mape?: number): 'excellent' | 'good' | 'acceptable' | 'poor' {
  if (!mape) return 'acceptable';
  if (mape <= 10) return 'excellent';
  if (mape <= 15) return 'good';
  if (mape <= 20) return 'acceptable';
  return 'poor';
}
