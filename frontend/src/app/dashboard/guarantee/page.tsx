'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';
import {
  Shield, TrendingUp, TrendingDown, ArrowLeft, CheckCircle, XCircle,
  Clock, MapPin, DollarSign, BarChart3, AlertTriangle, Activity,
  ChevronDown, FileText, PoundSterling,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/* ===== TYPE DEFINITIONS ===== */

interface GuaranteeSummary {
  driver_id: number;
  total_committed: number;
  total_completed: number;
  total_cancelled: number;
  total_in_progress: number;
  total_predicted_earnings: number;
  total_actual_earnings: number;
  total_guaranteed_minimum: number;
  total_topup_paid: number;
  guarantee_activation_rate: number;
  avg_predicted_per_shift: number;
  avg_actual_per_shift: number;
  earnings_accuracy_pct: number;
  income_improvement_pct: number;
  guarantee_threshold: string;
  shifts: ShiftDetail[];
}

interface ShiftDetail {
  id: number;
  location_name: string;
  shift_type: string;
  day_name: string;
  start_time: string;
  end_time: string;
  predicted_earnings: number;
  actual_earnings: number | null;
  guaranteed_minimum: number;
  topup_amount: number;
  guarantee_activated: boolean;
  guarantee_eligible: boolean;
  status: string;
  duration_hours: number;
  commitment_time: string;
  completed_at: string | null;
}

interface VolatilityData {
  driver_id: number;
  num_shifts: number;
  without_guarantee: StatBlock;
  with_guarantee: StatBlock;
  impact: {
    volatility_reduction_pct: number;
    cv_reduction_pct: number;
    earnings_floor_without: number;
    earnings_floor_with: number;
    total_topup_paid: number;
    interpretation: string;
  };
}

interface StatBlock {
  mean: number;
  std_dev: number;
  cv: number;
  min: number;
  max: number;
  range: number;
  sample_size: number;
}

interface PerformanceReport {
  driver_id: number;
  report_period: { from: string; to: string; total_shifts: number; total_hours: number };
  earnings_summary: {
    total_actual: number;
    total_topups: number;
    total_with_guarantee: number;
    avg_per_shift: number;
    avg_hourly: number;
    income_boost_pct: number;
  };
  earnings_trend: EarningsTrendItem[];
  best_locations: BestLocation[];
  best_shift_types: BestShiftType[];
}

interface EarningsTrendItem {
  date: string;
  day: string;
  location: string;
  shift_type: string;
  predicted: number;
  actual: number;
  topup: number;
  total_with_guarantee: number;
  hours: number;
  hourly_rate: number;
}

interface BestLocation {
  location: string;
  avg_earnings: number;
  total_earnings: number;
  shifts_worked: number;
  total_hours: number;
  avg_hourly: number;
}

interface BestShiftType {
  shift_type: string;
  avg_earnings: number;
  total_earnings: number;
  shifts_worked: number;
}

interface AuditLog {
  id: number;
  event_type: string;
  description: string;
  predicted_earnings: number | null;
  actual_earnings: number | null;
  guaranteed_minimum: number | null;
  topup_amount: number | null;
  was_eligible: boolean | null;
  timestamp: string;
}

/* ===== MAIN PAGE ===== */
export default function GuaranteeWindowPage() {
  const { user, loadUserFromToken } = useAuthStore();
  const router = useRouter();
  const [pageReady, setPageReady] = useState(false);

  // Data states
  const [summary, setSummary] = useState<GuaranteeSummary | null>(null);
  const [volatility, setVolatility] = useState<VolatilityData | null>(null);
  const [performance, setPerformance] = useState<PerformanceReport | null>(null);
  const [auditLog, setAuditLog] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI states
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [earningsInputs, setEarningsInputs] = useState<Record<number, string>>({});

  useEffect(() => {
    const init = async () => {
      if (!user) await loadUserFromToken();
      setPageReady(true);
    };
    init();
  }, []);

  useEffect(() => {
    if (pageReady && user) fetchAllData();
  }, [pageReady, user]);

  const fetchAllData = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);

    try {
      const [sumRes, volRes, perfRes, logRes] = await Promise.all([
        fetch(`${API_BASE}/guarantee/driver/${user.id}/summary`),
        fetch(`${API_BASE}/guarantee/driver/${user.id}/volatility`),
        fetch(`${API_BASE}/guarantee/driver/${user.id}/performance`),
        fetch(`${API_BASE}/guarantee/driver/${user.id}/history?limit=50`),
      ]);

      if (sumRes.ok) setSummary(await sumRes.json());
      if (volRes.ok) setVolatility(await volRes.json());
      if (perfRes.ok) setPerformance(await perfRes.json());
      if (logRes.ok) setAuditLog(await logRes.json());
    } catch {
      setError('Could not connect to backend. Ensure server is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  /* Record actual earnings for a committed shift */
  const handleRecordEarnings = async (shiftId: number) => {
    const val = earningsInputs[shiftId];
    if (!val || isNaN(parseFloat(val)) || parseFloat(val) < 0) {
      showToast.error('Please enter a valid earnings amount');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/guarantee/shifts/${shiftId}/actual-earnings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actual_earnings: parseFloat(val), driver_id: user!.id }),
      });

      if (res.ok) {
        const data = await res.json();
        showToast.success(data.message);
        setEarningsInputs(prev => { const n = { ...prev }; delete n[shiftId]; return n; });
        fetchAllData(); // Refresh all data
      } else {
        const err = await res.json();
        showToast.error(err.detail || 'Failed to record earnings');
      }
    } catch {
      showToast.error('Could not connect to server');
    }
  };

  /* Cancel a committed shift */
  const handleCancelShift = async (shiftId: number) => {
    try {
      const res = await fetch(
        `${API_BASE}/guarantee/shifts/${shiftId}/cancel?driver_id=${user!.id}`,
        { method: 'POST' }
      );
      if (res.ok) {
        showToast.success('Shift cancelled');
        fetchAllData();
      } else {
        const err = await res.json();
        showToast.error(err.detail || 'Failed to cancel shift');
      }
    } catch {
      showToast.error('Could not connect to server');
    }
  };

  if (!pageReady) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: colors.neutral[50] }}>
        <p style={{ color: colors.neutral[600], fontSize: fonts.sizes.body }}>Loading...</p>
      </div>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  /* ===== TABS CONFIG ===== */
  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Shield size={16} /> },
    { id: 'shifts', label: 'My Shifts', icon: <Clock size={16} /> },
    { id: 'comparison', label: 'Earnings Comparison', icon: <BarChart3 size={16} /> },
    { id: 'volatility', label: 'Volatility Analysis', icon: <Activity size={16} /> },
    { id: 'performance', label: 'Performance Report', icon: <TrendingUp size={16} /> },
    { id: 'audit', label: 'Audit Log', icon: <FileText size={16} /> },
  ];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.neutral[50] }}>
      {/* Header */}
      <header style={{
        backgroundColor: colors.primary[700], color: colors.neutral[0],
        padding: `${spacing.md} ${spacing.lg}`,
        boxShadow: '0 2px 4px rgba(255,87,34,0.1)',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
            <button
              onClick={() => router.push('/dashboard')}
              style={{
                background: 'none', border: 'none', color: colors.neutral[0],
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: spacing.xs,
                fontSize: fonts.sizes.body, fontWeight: fonts.weights.semibold,
              }}
            >
              <ArrowLeft size={18} /> Dashboard
            </button>
            <div style={{ width: '1px', height: '24px', backgroundColor: 'rgba(255,255,255,0.3)' }} />
            <div>
              <h1 style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, margin: 0, color: colors.neutral[0] }}>
                <Shield size={22} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
                Income Guarantee Window
              </h1>
              <p style={{ fontSize: fonts.sizes.caption, opacity: 0.9, margin: `${spacing.xs} 0 0 0`, color: colors.neutral[0] }}>
                Priority 2 — Earnings protection and income stability for {user.full_name}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div style={{
        backgroundColor: colors.neutral[0], borderBottom: `1px solid ${colors.neutral[200]}`,
        boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', gap: 0, overflowX: 'auto' }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex', alignItems: 'center', gap: spacing.xs,
                padding: `${spacing.md} ${spacing.lg}`,
                border: 'none', cursor: 'pointer',
                backgroundColor: activeTab === tab.id ? colors.primary[50] : 'transparent',
                color: activeTab === tab.id ? colors.primary[700] : colors.neutral[600],
                borderBottom: activeTab === tab.id ? `2px solid ${colors.primary[700]}` : '2px solid transparent',
                fontSize: fonts.sizes.body, fontWeight: activeTab === tab.id ? fonts.weights.bold : fonts.weights.regular,
                transition: 'all 0.2s',
                whiteSpace: 'nowrap',
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: spacing.lg }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: spacing.xl5, color: colors.neutral[500] }}>
            <Activity size={32} style={{ marginBottom: spacing.md, animation: 'spin 2s linear infinite' }} />
            <p>Loading guarantee data...</p>
          </div>
        ) : error ? (
          <div style={{ padding: spacing.lg, backgroundColor: colors.error[50], borderRadius: '8px', color: colors.error[700], border: `1px solid ${colors.error[200]}` }}>
            <AlertTriangle size={20} style={{ verticalAlign: 'middle', marginRight: spacing.sm }} />
            {error}
          </div>
        ) : (
          <>
            {activeTab === 'overview' && <OverviewTab summary={summary} volatility={volatility} />}
            {activeTab === 'shifts' && (
              <ShiftsTab
                summary={summary}
                earningsInputs={earningsInputs}
                setEarningsInputs={setEarningsInputs}
                onRecordEarnings={handleRecordEarnings}
                onCancelShift={handleCancelShift}
              />
            )}
            {activeTab === 'comparison' && <ComparisonTab summary={summary} />}
            {activeTab === 'volatility' && <VolatilityTab volatility={volatility} />}
            {activeTab === 'performance' && <PerformanceTab performance={performance} />}
            {activeTab === 'audit' && <AuditTab logs={auditLog} />}
          </>
        )}
      </main>
    </div>
  );
}


/* ===================================================================
   TAB 1: OVERVIEW — Summary Stats + How It Works
   =================================================================== */

function OverviewTab({ summary, volatility }: { summary: GuaranteeSummary | null; volatility: VolatilityData | null }) {
  if (!summary) return <EmptyState message="No guarantee data available yet." />;

  const s = summary;

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      {/* Summary stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: spacing.md }}>
        <StatCard label="Total Completed Shifts" value={String(s.total_completed)} icon={<CheckCircle size={22} />} color={colors.success[600]} />
        <StatCard label="Total top-up Paid" value={`£${s.total_topup_paid.toFixed(2)}`} icon={<Shield size={22} />} color={colors.primary[700]} />
        <StatCard label="Guarantee Activation Rate" value={`${s.guarantee_activation_rate}%`} icon={<Activity size={22} />} color={colors.warning[600]} />
        <StatCard label="Earnings Accuracy" value={`${s.earnings_accuracy_pct}%`} icon={<TrendingUp size={22} />} color={colors.secondary[600]} />
      </div>

      {/* Earnings overview panel */}
      <div style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
        border: `1px solid ${colors.neutral[200]}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      }}>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: `0 0 ${spacing.md} 0` }}>
          Earnings Overview
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.lg }}>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Total Predicted</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `${spacing.xs} 0 0 0` }}>
              £{s.total_predicted_earnings.toFixed(2)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Total Actual</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `${spacing.xs} 0 0 0` }}>
              £{s.total_actual_earnings.toFixed(2)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Guaranteed Minimum</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: `${spacing.xs} 0 0 0` }}>
              £{s.total_guaranteed_minimum.toFixed(2)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Total Top-Up Paid</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[600], margin: `${spacing.xs} 0 0 0` }}>
              £{s.total_topup_paid.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Income Guarantee Impact */}
      {volatility && volatility.impact && (
        <div style={{
          backgroundColor: colors.primary[50], borderRadius: '8px', padding: spacing.lg,
          border: `1px solid ${colors.primary[200]}`,
        }}>
          <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.primary[800], margin: `0 0 ${spacing.md} 0` }}>
            <Shield size={18} style={{ verticalAlign: 'middle', marginRight: spacing.xs }} />
            Income Guarantee Impact
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.md }}>
            <div style={impactCardStyle}>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Volatility Reduction</p>
              <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[600], margin: `${spacing.xs} 0 0 0` }}>
                {volatility.impact.volatility_reduction_pct}%
              </p>
            </div>
            <div style={impactCardStyle}>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Earnings Floor (Without)</p>
              <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.error[600], margin: `${spacing.xs} 0 0 0` }}>
                £{volatility.impact.earnings_floor_without.toFixed(2)}
              </p>
            </div>
            <div style={impactCardStyle}>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Earnings Floor (With Guarantee)</p>
              <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[600], margin: `${spacing.xs} 0 0 0` }}>
                £{volatility.impact.earnings_floor_with.toFixed(2)}
              </p>
            </div>
            <div style={impactCardStyle}>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Income Improvement</p>
              <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: `${spacing.xs} 0 0 0` }}>
                {s.income_improvement_pct}%
              </p>
            </div>
          </div>
          <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[700], marginTop: spacing.md, lineHeight: '1.6' }}>
            {volatility.impact.interpretation}
          </p>
        </div>
      )}

      {/* How It Works */}
      <div style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
        border: `1px solid ${colors.neutral[200]}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      }}>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: `0 0 ${spacing.md} 0` }}>
          How the Income Guarantee Works
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.md }}>
          {[
            { step: '1', title: 'View Recommendations', desc: 'AI suggests optimal shifts based on UK demand patterns and historical data.' },
            { step: '2', title: 'Commit to a Shift', desc: 'Accept a recommended shift. The system locks in your predicted earnings.' },
            { step: '3', title: 'Work the Shift', desc: 'Complete the shift and record your actual earnings in the system.' },
            { step: '4', title: 'Receive Top-Up', desc: 'If actual earnings < 90% of predicted, the difference is paid as a top-up.' },
          ].map(item => (
            <div key={item.step} style={{
              padding: spacing.md, borderRadius: '8px',
              backgroundColor: colors.neutral[50], border: `1px solid ${colors.neutral[200]}`,
            }}>
              <div style={{
                width: '28px', height: '28px', borderRadius: '50%',
                backgroundColor: colors.primary[700], color: colors.neutral[0],
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: fonts.weights.bold, fontSize: fonts.sizes.body, marginBottom: spacing.sm,
              }}>
                {item.step}
              </div>
              <p style={{ fontWeight: fonts.weights.bold, fontSize: fonts.sizes.body, color: colors.neutral[800], margin: `0 0 ${spacing.xs} 0` }}>{item.title}</p>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0, lineHeight: '1.5' }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Pending shifts reminder */}
      {s.total_committed > 0 && (
        <div style={{
          backgroundColor: colors.warning[50], borderRadius: '8px', padding: spacing.md,
          border: `1px solid ${colors.warning[200]}`, display: 'flex', alignItems: 'center', gap: spacing.md,
        }}>
          <AlertTriangle size={20} color={colors.warning[600]} />
          <div>
            <p style={{ fontWeight: fonts.weights.bold, color: colors.warning[800], margin: 0, fontSize: fonts.sizes.body }}>
              {s.total_committed} Pending Shift{s.total_committed > 1 ? 's' : ''}
            </p>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.warning[700], margin: `${spacing.xs} 0 0 0` }}>
              You have committed shifts awaiting completion. Record your actual earnings after each shift to activate the income guarantee.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}


/* ===================================================================
   TAB 2: SHIFTS — All Committed Shifts with Earnings Entry
   =================================================================== */

function ShiftsTab({
  summary, earningsInputs, setEarningsInputs, onRecordEarnings, onCancelShift,
}: {
  summary: GuaranteeSummary | null;
  earningsInputs: Record<number, string>;
  setEarningsInputs: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  onRecordEarnings: (id: number) => void;
  onCancelShift: (id: number) => void;
}) {
  if (!summary || summary.shifts.length === 0) return <EmptyState message="No committed shifts yet. Go to your dashboard to commit to recommended shifts." />;

  const statusOrder: Record<string, number> = { committed: 0, in_progress: 1, completed: 2, cancelled: 3 };
  const sorted = [...summary.shifts].sort((a, b) => (statusOrder[a.status] ?? 4) - (statusOrder[b.status] ?? 4));

  return (
    <div style={{ display: 'grid', gap: spacing.md }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm }}>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          All Committed Shifts ({summary.shifts.length})
        </h3>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <StatusBadge status="committed" />
          <StatusBadge status="completed" />
          <StatusBadge status="cancelled" />
        </div>
      </div>

      {sorted.map(shift => (
        <div
          key={shift.id}
          style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
            border: `1px solid ${
              shift.status === 'committed' ? colors.warning[200]
              : shift.status === 'completed' && shift.guarantee_activated ? colors.primary[200]
              : shift.status === 'completed' ? colors.success[200]
              : colors.neutral[200]
            }`,
            boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
          }}
        >
          {/* Shift header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: spacing.sm }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, flexWrap: 'wrap' }}>
                <MapPin size={16} color={colors.primary[700]} />
                <h4 style={{ margin: 0, fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[900] }}>
                  {shift.location_name}
                </h4>
                <StatusBadge status={shift.status} />
                {shift.guarantee_activated && (
                  <span style={{
                    padding: `2px ${spacing.sm}`, borderRadius: '12px',
                    backgroundColor: colors.primary[100], color: colors.primary[700],
                    fontSize: '11px', fontWeight: fonts.weights.semibold,
                  }}>
                    <Shield size={10} style={{ verticalAlign: 'middle', marginRight: 2 }} />
                    Top-Up Applied
                  </span>
                )}
              </div>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs} 0 0 0` }}>
                {shift.shift_type} · {shift.day_name} · {shift.duration_hours}h
              </p>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: `${spacing.xs} 0 0 0` }}>
                {new Date(shift.start_time).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' })} — {new Date(shift.end_time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>

            {/* Earnings column */}
            <div style={{ textAlign: 'right', minWidth: '160px' }}>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Predicted</p>
              <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: 0 }}>
                £{shift.predicted_earnings.toFixed(2)}
              </p>
              <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: `${spacing.xs} 0 0 0` }}>
                Guaranteed min: £{shift.guaranteed_minimum.toFixed(2)}
              </p>

              {shift.status === 'completed' && (
                <div style={{ marginTop: spacing.sm }}>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Actual</p>
                  <p style={{
                    fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, margin: 0,
                    color: (shift.actual_earnings ?? 0) >= shift.guaranteed_minimum ? colors.success[600] : colors.error[600],
                  }}>
                    £{(shift.actual_earnings ?? 0).toFixed(2)}
                  </p>
                  {shift.guarantee_activated && (
                    <p style={{ fontSize: fonts.sizes.caption, color: colors.primary[700], fontWeight: fonts.weights.semibold, margin: `${spacing.xs} 0 0 0` }}>
                      + £{shift.topup_amount.toFixed(2)} top-up
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Action area for committed shifts — record earnings or cancel */}
          {shift.status === 'committed' && (
            <div style={{
              marginTop: spacing.md, paddingTop: spacing.md,
              borderTop: `1px solid ${colors.neutral[200]}`,
              display: 'flex', alignItems: 'center', gap: spacing.md, flexWrap: 'wrap',
            }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <label style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], display: 'block', marginBottom: spacing.xs }}>
                  Record Actual Earnings (£)
                </label>
                <div style={{ display: 'flex', gap: spacing.sm }}>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="e.g. 125.50"
                    value={earningsInputs[shift.id] || ''}
                    onChange={(e) => setEarningsInputs(prev => ({ ...prev, [shift.id]: e.target.value }))}
                    style={{
                      flex: 1, padding: `${spacing.sm} ${spacing.md}`,
                      border: `1px solid ${colors.neutral[300]}`, borderRadius: '6px',
                      fontSize: fonts.sizes.body, outline: 'none',
                    }}
                    onFocus={(e) => e.target.style.borderColor = colors.primary[500]}
                    onBlur={(e) => e.target.style.borderColor = colors.neutral[300]}
                  />
                  <button
                    onClick={() => onRecordEarnings(shift.id)}
                    style={{
                      padding: `${spacing.sm} ${spacing.lg}`,
                      backgroundColor: colors.success[600], color: colors.neutral[0],
                      border: 'none', borderRadius: '6px', cursor: 'pointer',
                      fontSize: fonts.sizes.body, fontWeight: fonts.weights.semibold,
                      transition: 'background-color 0.2s',
                    }}
                    onMouseOver={(e) => (e.currentTarget.style.backgroundColor = colors.success[700])}
                    onMouseOut={(e) => (e.currentTarget.style.backgroundColor = colors.success[600])}
                  >
                    <CheckCircle size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                    Submit
                  </button>
                </div>
              </div>
              <button
                onClick={() => onCancelShift(shift.id)}
                style={{
                  padding: `${spacing.sm} ${spacing.md}`,
                  backgroundColor: 'transparent', color: colors.error[600],
                  border: `1px solid ${colors.error[300]}`, borderRadius: '6px',
                  cursor: 'pointer', fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold,
                  transition: 'all 0.2s',
                }}
                onMouseOver={(e) => { e.currentTarget.style.backgroundColor = colors.error[50]; }}
                onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'transparent'; }}
              >
                <XCircle size={14} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                Cancel Shift
              </button>
            </div>
          )}

          {/* Guarantee bar for completed shifts */}
          {shift.status === 'completed' && (
            <div style={{ marginTop: spacing.md }}>
              <GuaranteeBar
                predicted={shift.predicted_earnings}
                guaranteed={shift.guaranteed_minimum}
                actual={shift.actual_earnings ?? 0}
                topup={shift.topup_amount}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}


/* ===================================================================
   TAB 3: EARNINGS COMPARISON — Predicted vs Actual per shift
   =================================================================== */

function ComparisonTab({ summary }: { summary: GuaranteeSummary | null }) {
  if (!summary) return <EmptyState message="No data available." />;

  const completed = summary.shifts.filter(s => s.status === 'completed');
  if (completed.length === 0) return <EmptyState message="No completed shifts to compare." />;

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
        Earnings Comparison — Predicted vs Actual (FR11)
      </h3>

      {/* Summary row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: spacing.md }}>
        <StatCard label="Avg Predicted/Shift" value={`£${summary.avg_predicted_per_shift.toFixed(2)}`} icon={<TrendingUp size={20} />} color={colors.neutral[700]} />
        <StatCard label="Avg Actual/Shift" value={`£${summary.avg_actual_per_shift.toFixed(2)}`} icon={<TrendingDown size={20} />} color={colors.neutral[700]} />
        <StatCard label="Total Top-Ups" value={`£${summary.total_topup_paid.toFixed(2)}`} icon={<Shield size={20} />} color={colors.primary[700]} />
        <StatCard label="Income Boost" value={`${summary.income_improvement_pct}%`} icon={<Activity size={20} />} color={colors.success[600]} />
      </div>

      {/* Comparison table */}
      <div style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px',
        border: `1px solid ${colors.neutral[200]}`, overflow: 'hidden',
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: colors.neutral[50] }}>
              {['Location', 'Shift Type', 'Day', 'Predicted', 'Actual', 'Guaranteed Min', 'Top-Up', 'Status'].map(h => (
                <th key={h} style={{
                  padding: `${spacing.md} ${spacing.md}`,
                  textAlign: 'left', fontSize: fonts.sizes.caption,
                  color: colors.neutral[600], fontWeight: fonts.weights.bold,
                  borderBottom: `1px solid ${colors.neutral[200]}`,
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {completed.map(shift => (
              <tr key={shift.id} style={{ borderBottom: `1px solid ${colors.neutral[100]}` }}>
                <td style={tdStyle}>{shift.location_name}</td>
                <td style={tdStyle}>{shift.shift_type}</td>
                <td style={tdStyle}>{shift.day_name}</td>
                <td style={tdStyle}>£{shift.predicted_earnings.toFixed(2)}</td>
                <td style={{
                  ...tdStyle,
                  color: (shift.actual_earnings ?? 0) >= shift.guaranteed_minimum ? colors.success[600] : colors.error[600],
                  fontWeight: fonts.weights.semibold,
                }}>
                  £{(shift.actual_earnings ?? 0).toFixed(2)}
                </td>
                <td style={tdStyle}>£{shift.guaranteed_minimum.toFixed(2)}</td>
                <td style={{
                  ...tdStyle,
                  color: shift.topup_amount > 0 ? colors.primary[700] : colors.neutral[400],
                  fontWeight: shift.topup_amount > 0 ? fonts.weights.bold : fonts.weights.regular,
                }}>
                  {shift.topup_amount > 0 ? `+£${shift.topup_amount.toFixed(2)}` : '—'}
                </td>
                <td style={tdStyle}>
                  {shift.guarantee_activated ? (
                    <span style={{ color: colors.primary[700], fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold }}>
                      <Shield size={12} style={{ verticalAlign: 'middle', marginRight: 2 }} />
                      Protected
                    </span>
                  ) : (
                    <span style={{ color: colors.success[600], fontSize: fonts.sizes.caption }}>
                      <CheckCircle size={12} style={{ verticalAlign: 'middle', marginRight: 2 }} />
                      Met
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Top-up explanation */}
      <div style={{
        backgroundColor: colors.neutral[50], borderRadius: '8px', padding: spacing.lg,
        border: `1px solid ${colors.neutral[200]}`,
      }}>
        <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.sm} 0` }}>
          Top-Up Calculation Formula (FR12)
        </h4>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[700], margin: 0, lineHeight: '1.6', fontFamily: 'monospace' }}>
          top_up = max(0, predicted_earnings × {summary.guarantee_threshold} − actual_earnings)
        </p>
        <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], marginTop: spacing.sm, lineHeight: '1.5' }}>
          Example: If predicted = £135.00 and actual = £102.50 → guaranteed min = £135 × 90% = £121.50 → top-up = £121.50 − £102.50 = <strong>£19.00</strong>
        </p>
      </div>
    </div>
  );
}


/* ===================================================================
   TAB 4: VOLATILITY ANALYSIS (FR14)
   =================================================================== */

function VolatilityTab({ volatility }: { volatility: VolatilityData | null }) {
  if (!volatility || !volatility.without_guarantee?.sample_size)
    return <EmptyState message="Need at least 2 completed shifts for volatility analysis." />;

  const v = volatility;

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      <div>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          Earnings Volatility Analysis (FR14)
        </h3>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[600], margin: `${spacing.xs} 0 0 0` }}>
          Research Question 2: &ldquo;To what extent does an income guarantee mechanism reduce income volatility?&rdquo;
        </p>
      </div>

      {/* Side-by-side comparison */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
        {/* Without guarantee */}
        <div style={{
          backgroundColor: colors.error[50], borderRadius: '8px', padding: spacing.lg,
          border: `1px solid ${colors.error[200]}`,
        }}>
          <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.error[700], margin: `0 0 ${spacing.md} 0` }}>
            <XCircle size={16} style={{ verticalAlign: 'middle', marginRight: spacing.xs }} />
            Without Guarantee
          </h4>
          <StatGrid stats={v.without_guarantee} color={colors.error[700]} />
        </div>

        {/* With guarantee */}
        <div style={{
          backgroundColor: colors.success[50], borderRadius: '8px', padding: spacing.lg,
          border: `1px solid ${colors.success[200]}`,
        }}>
          <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.success[700], margin: `0 0 ${spacing.md} 0` }}>
            <CheckCircle size={16} style={{ verticalAlign: 'middle', marginRight: spacing.xs }} />
            With Guarantee
          </h4>
          <StatGrid stats={v.with_guarantee} color={colors.success[700]} />
        </div>
      </div>

      {/* Impact summary */}
      <div style={{
        backgroundColor: colors.primary[50], borderRadius: '8px', padding: spacing.lg,
        border: `1px solid ${colors.primary[200]}`,
      }}>
        <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.primary[800], margin: `0 0 ${spacing.md} 0` }}>
          Impact Assessment
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: spacing.md }}>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Volatility Reduction</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[600], margin: `${spacing.xs} 0 0 0` }}>
              {v.impact.volatility_reduction_pct}%
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>CV Reduction</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[600], margin: `${spacing.xs} 0 0 0` }}>
              {v.impact.cv_reduction_pct}%
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Earnings Floor Raised</p>
            <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: `${spacing.xs} 0 0 0` }}>
              £{v.impact.earnings_floor_without.toFixed(2)} → £{v.impact.earnings_floor_with.toFixed(2)}
            </p>
          </div>
          <div>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>Total Top-Ups</p>
            <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: `${spacing.xs} 0 0 0` }}>
              £{v.impact.total_topup_paid.toFixed(2)}
            </p>
          </div>
        </div>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[700], marginTop: spacing.md, lineHeight: '1.6' }}>
          {v.impact.interpretation}
        </p>
      </div>

      {/* Methodology note */}
      <div style={{
        backgroundColor: colors.neutral[50], borderRadius: '8px', padding: spacing.md,
        border: `1px solid ${colors.neutral[200]}`,
      }}>
        <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0, lineHeight: '1.6' }}>
          <strong>Methodology:</strong> Coefficient of Variation (CV) = Standard Deviation ÷ Mean × 100.
          Lower CV indicates more stable income. The analysis compares raw earnings against earnings
          after top-up protection is applied, demonstrating the stabilising effect of the income guarantee.
          Sample size: {v.num_shifts} completed shifts.
        </p>
      </div>
    </div>
  );
}


/* ===================================================================
   TAB 5: PERFORMANCE REPORT (FR15)
   =================================================================== */

function PerformanceTab({ performance }: { performance: PerformanceReport | null }) {
  if (!performance || !performance.earnings_trend?.length)
    return <EmptyState message="No completed shifts to generate a performance report." />;

  const p = performance;

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      <div>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          Performance Report (FR15)
        </h3>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[600], margin: `${spacing.xs} 0 0 0` }}>
          Period: {p.report_period.from} to {p.report_period.to} · {p.report_period.total_shifts} shifts · {p.report_period.total_hours}h total
        </p>
      </div>

      {/* Summary stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: spacing.md }}>
        <StatCard label="Total Actual Earnings" value={`£${p.earnings_summary.total_actual.toFixed(2)}`} icon={<TrendingUp size={20} />} color={colors.neutral[800]} />
        <StatCard label="Total with Guarantee" value={`£${p.earnings_summary.total_with_guarantee.toFixed(2)}`} icon={<Shield size={20} />} color={colors.success[600]} />
        <StatCard label="Avg per Shift" value={`£${p.earnings_summary.avg_per_shift.toFixed(2)}`} icon={<BarChart3 size={20} />} color={colors.primary[700]} />
        <StatCard label="Avg Hourly Rate" value={`£${p.earnings_summary.avg_hourly.toFixed(2)}/hr`} icon={<Clock size={20} />} color={colors.secondary[600]} />
      </div>

      {/* Earnings trend table */}
      <div style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px',
        border: `1px solid ${colors.neutral[200]}`, overflow: 'hidden',
      }}>
        <h4 style={{ padding: `${spacing.md} ${spacing.lg}`, margin: 0, fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], borderBottom: `1px solid ${colors.neutral[200]}` }}>
          Earnings Trend
        </h4>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: colors.neutral[50] }}>
              {['Date', 'Day', 'Location', 'Type', 'Hours', 'Predicted', 'Actual', 'Top-Up', 'Total', 'Hourly Rate'].map(h => (
                <th key={h} style={{
                  padding: `${spacing.sm} ${spacing.md}`, textAlign: 'left',
                  fontSize: '11px', color: colors.neutral[600], fontWeight: fonts.weights.bold,
                  borderBottom: `1px solid ${colors.neutral[200]}`,
                }}>
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {p.earnings_trend.map((item, i) => (
              <tr key={i} style={{ borderBottom: `1px solid ${colors.neutral[100]}` }}>
                <td style={tdSmStyle}>{item.date}</td>
                <td style={tdSmStyle}>{item.day}</td>
                <td style={tdSmStyle}>{item.location}</td>
                <td style={tdSmStyle}>{item.shift_type}</td>
                <td style={tdSmStyle}>{item.hours}h</td>
                <td style={tdSmStyle}>£{item.predicted.toFixed(2)}</td>
                <td style={{
                  ...tdSmStyle,
                  color: item.actual >= item.predicted * 0.9 ? colors.success[600] : colors.error[600],
                  fontWeight: fonts.weights.semibold,
                }}>
                  £{item.actual.toFixed(2)}
                </td>
                <td style={{
                  ...tdSmStyle,
                  color: item.topup > 0 ? colors.primary[700] : colors.neutral[400],
                  fontWeight: item.topup > 0 ? fonts.weights.bold : fonts.weights.regular,
                }}>
                  {item.topup > 0 ? `+£${item.topup.toFixed(2)}` : '—'}
                </td>
                <td style={{ ...tdSmStyle, fontWeight: fonts.weights.semibold }}>£{item.total_with_guarantee.toFixed(2)}</td>
                <td style={tdSmStyle}>£{item.hourly_rate.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Best locations */}
      {p.best_locations.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
          <div style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
            border: `1px solid ${colors.neutral[200]}`,
          }}>
            <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.md} 0` }}>
              <MapPin size={16} style={{ verticalAlign: 'middle', marginRight: spacing.xs }} />
              Best Locations
            </h4>
            {p.best_locations.map((loc, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: `${spacing.sm} 0`,
                borderBottom: i < p.best_locations.length - 1 ? `1px solid ${colors.neutral[100]}` : 'none',
              }}>
                <div>
                  <p style={{ fontWeight: fonts.weights.semibold, fontSize: fonts.sizes.body, color: colors.neutral[800], margin: 0 }}>{loc.location}</p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>
                    {loc.shifts_worked} shifts · {loc.total_hours}h
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontWeight: fonts.weights.bold, fontSize: fonts.sizes.body, color: colors.success[600], margin: 0 }}>
                    £{loc.avg_earnings.toFixed(2)}/shift
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>
                    £{loc.avg_hourly.toFixed(2)}/hr
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
            border: `1px solid ${colors.neutral[200]}`,
          }}>
            <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.md} 0` }}>
              <Clock size={16} style={{ verticalAlign: 'middle', marginRight: spacing.xs }} />
              Best Shift Types
            </h4>
            {p.best_shift_types.map((st, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: `${spacing.sm} 0`,
                borderBottom: i < p.best_shift_types.length - 1 ? `1px solid ${colors.neutral[100]}` : 'none',
              }}>
                <div>
                  <p style={{ fontWeight: fonts.weights.semibold, fontSize: fonts.sizes.body, color: colors.neutral[800], margin: 0 }}>{st.shift_type}</p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>
                    {st.shifts_worked} shifts
                  </p>
                </div>
                <p style={{ fontWeight: fonts.weights.bold, fontSize: fonts.sizes.body, color: colors.success[600], margin: 0 }}>
                  £{st.avg_earnings.toFixed(2)}/shift
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}


/* ===================================================================
   TAB 6: AUDIT LOG (FR13 + NFR11)
   =================================================================== */

function AuditTab({ logs }: { logs: AuditLog[] }) {
  if (logs.length === 0) return <EmptyState message="No guarantee events logged yet." />;

  const eventColors: Record<string, string> = {
    commitment: colors.warning[600],
    earnings_recorded: colors.neutral[600],
    guarantee_activated: colors.primary[700],
    cancellation: colors.error[600],
  };

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      <div>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          Guarantee Audit Log (FR13 + NFR11)
        </h3>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[600], margin: `${spacing.xs} 0 0 0` }}>
          All predictions, commitments, and guarantee calculations logged for review and research evaluation.
        </p>
      </div>

      <div style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px',
        border: `1px solid ${colors.neutral[200]}`, overflow: 'hidden',
      }}>
        {logs.map((log, i) => (
          <div
            key={log.id}
            style={{
              padding: `${spacing.md} ${spacing.lg}`,
              borderBottom: i < logs.length - 1 ? `1px solid ${colors.neutral[100]}` : 'none',
              display: 'flex', gap: spacing.md, alignItems: 'flex-start',
            }}
          >
            {/* Event type indicator */}
            <div style={{
              width: '8px', height: '8px', borderRadius: '50%', marginTop: '6px', flexShrink: 0,
              backgroundColor: eventColors[log.event_type] || colors.neutral[400],
            }} />

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span style={{
                    fontSize: fonts.sizes.caption, fontWeight: fonts.weights.bold,
                    color: eventColors[log.event_type] || colors.neutral[600],
                    textTransform: 'uppercase',
                  }}>
                    {log.event_type.replace('_', ' ')}
                  </span>
                  <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[700], margin: `${spacing.xs} 0 0 0`, lineHeight: '1.5' }}>
                    {log.description}
                  </p>
                </div>
                <span style={{ fontSize: fonts.sizes.caption, color: colors.neutral[400], whiteSpace: 'nowrap', marginLeft: spacing.md }}>
                  {log.timestamp ? new Date(log.timestamp).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) : ''}
                </span>
              </div>

              {/* Financial details */}
              {(log.predicted_earnings || log.actual_earnings || log.topup_amount) && (
                <div style={{ display: 'flex', gap: spacing.lg, marginTop: spacing.sm, flexWrap: 'wrap' }}>
                  {log.predicted_earnings != null && (
                    <span style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500] }}>
                      Predicted: <strong>£{log.predicted_earnings.toFixed(2)}</strong>
                    </span>
                  )}
                  {log.actual_earnings != null && (
                    <span style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500] }}>
                      Actual: <strong>£{log.actual_earnings.toFixed(2)}</strong>
                    </span>
                  )}
                  {log.guaranteed_minimum != null && (
                    <span style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500] }}>
                      Guaranteed: <strong>£{log.guaranteed_minimum.toFixed(2)}</strong>
                    </span>
                  )}
                  {log.topup_amount != null && log.topup_amount > 0 && (
                    <span style={{ fontSize: fonts.sizes.caption, color: colors.primary[700], fontWeight: fonts.weights.bold }}>
                      Top-up: +£{log.topup_amount.toFixed(2)}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


/* ===================================================================
   SHARED COMPONENTS
   =================================================================== */

function StatCard({ label, value, icon, color }: { label: string; value: string; icon: React.ReactNode; color: string }) {
  return (
    <div style={{
      backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
      border: `1px solid ${colors.neutral[200]}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      display: 'flex', alignItems: 'center', gap: spacing.md,
    }}>
      <div style={{
        width: '44px', height: '44px', borderRadius: '10px',
        backgroundColor: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
        color,
      }}>
        {icon}
      </div>
      <div>
        <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>{label}</p>
        <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: `${spacing.xs} 0 0 0` }}>{value}</p>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    committed: { bg: colors.warning[100], text: colors.warning[700], label: 'Committed' },
    in_progress: { bg: colors.semanticInfo + '20', text: colors.semanticInfo, label: 'In Progress' },
    completed: { bg: colors.success[100], text: colors.success[700], label: 'Completed' },
    cancelled: { bg: colors.error[100], text: colors.error[700], label: 'Cancelled' },
  };
  const c = config[status] || config.committed;
  return (
    <span style={{
      padding: `2px ${spacing.sm}`, borderRadius: '12px',
      backgroundColor: c.bg, color: c.text,
      fontSize: '11px', fontWeight: fonts.weights.semibold,
    }}>
      {c.label}
    </span>
  );
}

function GuaranteeBar({ predicted, guaranteed, actual, topup }: {
  predicted: number; guaranteed: number; actual: number; topup: number;
}) {
  const max = Math.max(predicted, actual + topup, guaranteed) * 1.1;
  const predPct = (predicted / max) * 100;
  const guarPct = (guaranteed / max) * 100;
  const actPct = (actual / max) * 100;
  const topPct = (topup / max) * 100;

  return (
    <div style={{ paddingTop: spacing.sm }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: fonts.sizes.caption, color: colors.neutral[500], marginBottom: spacing.xs }}>
        <span>£0</span>
        <span>£{Math.ceil(max)}</span>
      </div>
      <div style={{ position: 'relative', height: '24px', backgroundColor: colors.neutral[100], borderRadius: '4px', overflow: 'hidden' }}>
        {/* Actual earnings bar */}
        <div style={{
          position: 'absolute', left: 0, top: 0, height: '100%',
          width: `${actPct}%`,
          backgroundColor: actual >= guaranteed ? colors.success[400] : colors.error[400],
          borderRadius: '4px 0 0 4px',
        }} />
        {/* Top-up bar */}
        {topup > 0 && (
          <div style={{
            position: 'absolute', left: `${actPct}%`, top: 0, height: '100%',
            width: `${topPct}%`,
            backgroundColor: colors.primary[400],
            opacity: 0.7,
          }} />
        )}
        {/* Guaranteed minimum line */}
        <div style={{
          position: 'absolute', left: `${guarPct}%`, top: 0, height: '100%',
          width: '2px', backgroundColor: colors.primary[700],
        }} />
        {/* Predicted line */}
        <div style={{
          position: 'absolute', left: `${predPct}%`, top: 0, height: '100%',
          width: '2px', backgroundColor: colors.neutral[600], opacity: 0.5,
        }} />
      </div>
      <div style={{ display: 'flex', gap: spacing.lg, marginTop: spacing.xs, fontSize: '10px', color: colors.neutral[500], flexWrap: 'wrap' }}>
        <span><span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '2px', backgroundColor: actual >= guaranteed ? colors.success[400] : colors.error[400], marginRight: '3px', verticalAlign: 'middle' }} />Actual: £{actual.toFixed(2)}</span>
        {topup > 0 && <span><span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '2px', backgroundColor: colors.primary[400], marginRight: '3px', verticalAlign: 'middle' }} />Top-up: £{topup.toFixed(2)}</span>}
        <span><span style={{ display: 'inline-block', width: '2px', height: '8px', backgroundColor: colors.primary[700], marginRight: '3px', verticalAlign: 'middle' }} />Guaranteed: £{guaranteed.toFixed(2)}</span>
        <span><span style={{ display: 'inline-block', width: '2px', height: '8px', backgroundColor: colors.neutral[600], marginRight: '3px', verticalAlign: 'middle', opacity: 0.5 }} />Predicted: £{predicted.toFixed(2)}</span>
      </div>
    </div>
  );
}

function StatGrid({ stats, color }: { stats: StatBlock; color: string }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm }}>
      {[
        { label: 'Mean', value: `£${stats.mean.toFixed(2)}` },
        { label: 'Std Dev', value: `£${stats.std_dev.toFixed(2)}` },
        { label: 'CV', value: `${stats.cv}%` },
        { label: 'Min', value: `£${stats.min.toFixed(2)}` },
        { label: 'Max', value: `£${stats.max.toFixed(2)}` },
        { label: 'Range', value: `£${stats.range.toFixed(2)}` },
      ].map(item => (
        <div key={item.label}>
          <p style={{ fontSize: '11px', color: colors.neutral[500], margin: 0 }}>{item.label}</p>
          <p style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color, margin: `2px 0 0 0` }}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div style={{
      textAlign: 'center', padding: spacing.xl5, color: colors.neutral[500],
      backgroundColor: colors.neutral[0], borderRadius: '8px',
      border: `1px solid ${colors.neutral[200]}`,
    }}>
      <Shield size={40} style={{ marginBottom: spacing.md, color: colors.neutral[300] }} />
      <p style={{ fontSize: fonts.sizes.body, margin: 0 }}>{message}</p>
    </div>
  );
}

/* ===== STYLE HELPERS ===== */

const tdStyle: React.CSSProperties = {
  padding: '10px 12px',
  fontSize: '13px',
  color: '#374151',
};

const tdSmStyle: React.CSSProperties = {
  padding: '8px 10px',
  fontSize: '12px',
  color: '#374151',
};

const impactCardStyle: React.CSSProperties = {
  padding: '12px',
  borderRadius: '8px',
  backgroundColor: '#ffffff',
  border: '1px solid #e5e7eb',
};
