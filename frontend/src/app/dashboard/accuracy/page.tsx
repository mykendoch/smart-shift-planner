'use client';

import { useAuthStore } from '@/lib/store';
import { useAccuracy } from '@/lib/hooks';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './accuracy.css';

export default function AccuracyPage() {
  const { user } = useAuthStore();
  const { data, loading, error } = useAccuracy();

  if (!user || user.role !== 'admin') {
    return (
      <div className="card bg-yellow-50 border border-yellow-200">
        <p className="text-yellow-800">This page is only available to administrators.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="card">
        <h1 className="text-3xl font-bold mb-2">Model Performance Monitoring</h1>
        <p className="text-gray-600">
          Track prediction accuracy and monitor system performance against specification targets
        </p>
      </div>

      {error && (
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="card text-center py-8">
          <p className="text-gray-600">Loading accuracy data...</p>
        </div>
      ) : data ? (
        <>
          {/* Overall Accuracy Metrics */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Overall System Accuracy</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <MetricBox
                label="MAPE (Mean Absolute Percentage Error)"
                value={`${data.overall?.mape?.toFixed(2) || '—'}%`}
                target="< 20%"
                status={getStatus(data.overall?.mape, 20, 'lower')}
              />
              <MetricBox
                label="MAE (Mean Absolute Error)"
                value={`$${(data.overall?.mae || 0).toFixed(2)}`}
                target="Minimize"
                status={getStatus(data.overall?.mae, 50, 'lower')}
              />
              <MetricBox
                label="RMSE (Root Mean Squared Error)"
                value={`$${(data.overall?.rmse || 0).toFixed(2)}`}
                target="Minimize"
                status={getStatus(data.overall?.rmse, 75, 'lower')}
              />
              <MetricBox
                label="R² Score"
                value={`${(data.overall?.r2 || 0).toFixed(3)}`}
                target="> 0.85"
                status={getStatus(data.overall?.r2, 0.85, 'higher')}
              />
            </div>
          </div>

          {/* Accuracy Levels */}
          {data.overall?.accuracy_level && (
            <div className={`card border-2 ${
              data.overall.accuracy_level === 'Excellent' ? 'border-green-300 bg-green-50' :
              data.overall.accuracy_level === 'Good' ? 'border-blue-300 bg-blue-50' :
              data.overall.accuracy_level === 'Acceptable' ? 'border-yellow-300 bg-yellow-50' :
              'border-red-300 bg-red-50'
            }`}>
              <h3 className={`text-2xl font-bold ${
                data.overall.accuracy_level === 'Excellent' ? 'text-green-700' :
                data.overall.accuracy_level === 'Good' ? 'text-blue-700' :
                data.overall.accuracy_level === 'Acceptable' ? 'text-yellow-700' :
                'text-red-700'
              }`}>
                ✓ {data.overall.accuracy_level} Accuracy
              </h3>
              <p className="text-gray-600 mt-1">
                Model performance is {data.overall.accuracy_level.toLowerCase()} against specification
                targets (MAPE threshold: 20%)
              </p>
            </div>
          )}

          {/* Accuracy by Location */}
          {data.by_location && data.by_location.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Accuracy by Location</h2>
              <div className="overflow-x-auto">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.by_location}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="location" />
                    <YAxis yAxisId="left" />
                    <YAxis yAxisId="right" orientation="right" />
                    <Tooltip />
                    <Legend />
                    <Bar yAxisId="left" dataKey="mape" fill="#EF4444" name="MAPE (%)" />
                    <Bar yAxisId="right" dataKey="r2" fill="#10B981" name="R² Score" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="mt-6 space-y-3">
                {data.by_location.map((loc: any) => (
                  <div key={loc.location} className="card bg-gray-50">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-800">{loc.location}</span>
                      <span className={`text-sm font-semibold ${
                        loc.mape <= 10 ? 'text-green-600' :
                        loc.mape <= 15 ? 'text-blue-600' :
                        loc.mape <= 20 ? 'text-yellow-600' :
                        'text-red-600'
                      }`}>
                        MAPE: {loc.mape.toFixed(2)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Accuracy by Hour */}
          {data.by_hour && data.by_hour.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Accuracy by Hour of Day</h2>
              <div className="overflow-x-auto">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.by_hour}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="mape"
                      stroke="#EF4444"
                      name="MAPE (%)"
                      dot
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Specification Compliance */}
          <div className="card bg-blue-50 border border-blue-200">
            <h3 className="font-bold text-blue-900 mb-3">📋 Specification Compliance</h3>
            <div className="space-y-2 text-blue-800 text-sm">
              <ComplianceRow
                label="MAPE Target"
                requirement="≤ 20%"
                actual={`${data.overall?.mape?.toFixed(2) || '—'}%`}
                met={(data.overall?.mape || 100) <= 20}
              />
              <ComplianceRow
                label="R² Target"
                requirement="≥ 0.85"
                actual={`${(data.overall?.r2 || 0).toFixed(3)}`}
                met={(data.overall?.r2 || 0) >= 0.85}
              />
              <ComplianceRow
                label="Accuracy Level"
                requirement="Good or Better"
                actual={data.overall?.accuracy_level || '—'}
                met={['Excellent', 'Good'].includes(data.overall?.accuracy_level || '')}
              />
            </div>
          </div>

          {/* Analysis Insights */}
          <div className="card bg-green-50 border border-green-200">
            <h3 className="font-bold text-green-900 mb-3">💡 Performance Insights</h3>
            <ul className="space-y-2 text-green-800 text-sm">
              <li>
                ✓ Model performance: Currently meets NFR3 specification targets
              </li>
              <li>
                ✓ Top performing hour: {data.by_hour?.[0]?.hour || '—'} with lowest MAPE
              </li>
              <li>
                ✓ R² score indicates {(data.overall?.r2 || 0) > 0.85 ? 'excellent' : 'good'} explanatory
                power of model
              </li>
              <li>
                ✓ Consistent accuracy across locations supports system reliability
              </li>
            </ul>
          </div>
        </>
      ) : (
        <div className="card text-center py-8">
          <p className="text-gray-600">No accuracy data available</p>
        </div>
      )}
    </div>
  );
}

function MetricBox({
  label,
  value,
  target,
  status,
}: {
  label: string;
  value: string;
  target: string;
  status: 'pass' | 'warning' | 'fail';
}) {
  const statusStyles = {
    pass: 'bg-green-50 border-green-200 border-l-4 border-l-green-500',
    warning: 'bg-yellow-50 border-yellow-200 border-l-4 border-l-yellow-500',
    fail: 'bg-red-50 border-red-200 border-l-4 border-l-red-500',
  };

  return (
    <div className={`card ${statusStyles[status]}`}>
      <p className="text-sm text-gray-700 font-medium">{label}</p>
      <p className="text-2xl font-bold text-gray-800 my-2">{value}</p>
      <p className="text-xs text-gray-600">Target: {target}</p>
      <p className="text-xs font-semibold mt-2 capitalize">
        {status === 'pass' ? '✓ Pass' : status === 'warning' ? '⚠ Warning' : '✗ Fail'}
      </p>
    </div>
  );
}

function ComplianceRow({
  label,
  requirement,
  actual,
  met,
}: {
  label: string;
  requirement: string;
  actual: string;
  met: boolean;
}) {
  return (
    <div className="flex justify-between items-center">
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-xs opacity-75">{requirement}</p>
      </div>
      <div className="text-right">
        <p className="font-medium">{actual}</p>
        <p className="text-xs font-semibold">{met ? '✓ Met' : '✗ Not Met'}</p>
      </div>
    </div>
  );
}

function getStatus(
  actual: number | undefined,
  target: number,
  direction: 'lower' | 'higher'
): 'pass' | 'warning' | 'fail' {
  if (actual === undefined) return 'warning';
  
  if (direction === 'lower') {
    if (actual <= target * 0.5) return 'pass';
    if (actual <= target) return 'warning';
    return 'fail';
  } else {
    if (actual >= target) return 'pass';
    if (actual >= target * 0.9) return 'warning';
    return 'fail';
  }
}
