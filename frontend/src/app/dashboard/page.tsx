'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/store';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';
import {
  TrendingUp, BarChart3, FileText, Users, Activity, Clock,
  Settings, LogOut, Bell, User, Menu, ChevronDown, MapPin,
  CheckCircle, Shield, Calendar,
} from 'lucide-react';
import { useRouter } from 'next/navigation';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

/* ===== TYPE DEFINITIONS ===== */
interface Recommendation {
  location_key: string;
  location_name: string;
  region: string;
  zone: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  predicted_earnings: number;
  demand_score: number;
  difficulty: string;
  guarantee_eligible: boolean;
  base_hourly: number;
  region_demand: number;
  day_name: string;
}

interface CommittedShift {
  location_name: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  predicted_earnings: number;
  day_name: string;
  guarantee_eligible: boolean;
}

/* ===== MAIN PAGE ===== */
export default function DashboardPage() {
  const { user, logout, loadUserFromToken } = useAuthStore();
  const router = useRouter();
  const [pageReady, setPageReady] = useState(false);

  useEffect(() => {
    const init = async () => {
      if (!user) {
        await loadUserFromToken();
      }
      setPageReady(true);
    };
    init();
  }, []);

  const isAdmin = user?.role === 'admin';

  const handleLogout = () => {
    logout();
    router.push('/login');
    showToast.success('Logged out successfully');
  };

  if (!pageReady) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: colors.neutral[50] }}>
        <p style={{ color: colors.neutral[600], fontSize: fonts.sizes.body }}>Loading dashboard...</p>
      </div>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: colors.neutral[50], margin: 0, padding: 0 }}>
      {/* Header */}
      <header style={{
        backgroundColor: colors.primary[700], color: colors.neutral[0],
        padding: `${spacing.md}px ${spacing.lg}px`,
        boxShadow: '0 2px 4px rgba(255,87,34,0.1)', width: '100%', margin: 0,
      }}>
        <div style={{
          maxWidth: '1200px', margin: '0 auto',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        }}>
          <div>
            <h1 style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, margin: 0, color: colors.neutral[0] }}>
              {isAdmin ? '👤 Admin Dashboard' : '🚗 Driver Dashboard'}
            </h1>
            <p style={{ fontSize: fonts.sizes.caption, opacity: 0.9, margin: `${spacing.xs}px 0 0 0`, color: colors.neutral[0] }}>
              Welcome back, {user.full_name}
            </p>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
            <button style={{ background: 'none', border: 'none', color: colors.neutral[0], cursor: 'pointer', padding: spacing.sm, display: 'flex', alignItems: 'center', transition: 'opacity 0.3s' }}
              onMouseOver={(e) => (e.currentTarget.style.opacity = '0.7')}
              onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
            ><Bell size={20} /></button>
            <button style={{ background: 'none', border: 'none', color: colors.neutral[0], cursor: 'pointer', padding: spacing.sm, display: 'flex', alignItems: 'center', transition: 'opacity 0.3s' }}
              onMouseOver={(e) => (e.currentTarget.style.opacity = '0.7')}
              onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
            ><User size={20} /></button>
            <button style={{ background: 'none', border: 'none', color: colors.neutral[0], cursor: 'pointer', padding: spacing.sm, display: 'flex', alignItems: 'center', transition: 'opacity 0.3s' }}
              onMouseOver={(e) => (e.currentTarget.style.opacity = '0.7')}
              onMouseOut={(e) => (e.currentTarget.style.opacity = '1')}
            ><Menu size={20} /></button>
            <button onClick={handleLogout} style={{
              display: 'flex', alignItems: 'center', gap: `${spacing.xs}px`,
              backgroundColor: colors.primary[600], color: colors.neutral[0],
              border: 'none', padding: `${spacing.sm}px ${spacing.md}px`,
              borderRadius: '6px', cursor: 'pointer',
              fontSize: fonts.sizes.button, fontWeight: fonts.weights.semibold,
              transition: 'background-color 0.3s',
            }}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = colors.primary[800])}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = colors.primary[600])}
            ><LogOut size={16} />Logout</button>
          </div>
        </div>
      </header>

      <main style={{ maxWidth: '1200px', margin: '0 auto', padding: spacing.lg }}>
        {isAdmin ? <AdminDashboard /> : <DriverDashboard />}
      </main>
    </div>
  );
}

/* ===== DRIVER DASHBOARD (FUNCTIONAL - Connected to API) ===== */
function DriverDashboard() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [committedShifts, setCommittedShifts] = useState<CommittedShift[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    if (!user) return;
    try {
      setLoading(true);
      setApiError(null);
      const res = await fetch(`${API_BASE}/shifts/recommendations/${user.id}?limit=10`);
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
      } else {
        setApiError('Failed to load shift recommendations');
      }
    } catch (err) {
      setApiError('Could not connect to server. Ensure backend is running on port 8000.');
      console.error('Recommendations fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCommitToShift = async (rec: Recommendation) => {
    // Persist commitment via backend API
    try {
      const res = await fetch(`${API_BASE}/guarantee/commit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          driver_id: user?.id ?? 4,
          location_name: rec.location_name,
          region: rec.region,
          zone: rec.zone,
          shift_type: rec.shift_type,
          start_time: rec.start_time,
          end_time: rec.end_time,
          predicted_earnings: rec.predicted_earnings,
          demand_score: rec.demand_score,
          guarantee_eligible: rec.guarantee_eligible,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to commit shift');
      }
    } catch (err: any) {
      console.error('Commit API error (falling back to client state):', err);
    }

    const newCommitted: CommittedShift = {
      location_name: rec.location_name,
      shift_type: rec.shift_type,
      start_time: rec.start_time,
      end_time: rec.end_time,
      predicted_earnings: rec.predicted_earnings,
      day_name: rec.day_name,
      guarantee_eligible: rec.guarantee_eligible,
    };
    setCommittedShifts(prev => [...prev, newCommitted]);
    setRecommendations(prev => prev.filter(r => r !== rec));
    showToast.success(`Committed to ${rec.shift_type} at ${rec.location_name}`);
  };

  // Calculate dynamic stats from real data
  const totalPredictedEarnings = committedShifts.length > 0
    ? committedShifts.reduce((sum, s) => sum + s.predicted_earnings, 0)
    : recommendations.slice(0, 5).reduce((sum, r) => sum + r.predicted_earnings, 0);

  const totalHours = committedShifts.length > 0
    ? committedShifts.reduce((sum, s) => {
        const h = (new Date(s.end_time).getTime() - new Date(s.start_time).getTime()) / 3600000;
        return sum + h;
      }, 0)
    : recommendations.slice(0, 5).reduce((sum, r) => {
        const h = (new Date(r.end_time).getTime() - new Date(r.start_time).getTime()) / 3600000;
        return sum + h;
      }, 0);

  const avgDemand = recommendations.length > 0
    ? Math.round(recommendations.reduce((sum, r) => sum + r.demand_score, 0) / recommendations.length)
    : 0;

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      {/* Welcome Section */}
      <section style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px',
        padding: spacing.lg, borderLeft: `4px solid ${colors.primary[700]}`,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}>
        <h2 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          Driver Dashboard
        </h2>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[600], margin: `${spacing.sm}px 0 0 0` }}>
          View recommended shifts, commit to earning windows, and track your income guarantee.
        </p>
      </section>

      {/* Quick Stats - Dynamic from API */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: spacing.md }}>
        <ClickableStatCard
          icon={<Activity size={24} />}
          label="Committed Shifts"
          value={loading ? '...' : String(committedShifts.length)}
          color={colors.success[600]}
          sectionId="active-shifts"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
        <ClickableStatCard
          icon={<TrendingUp size={24} />}
          label={committedShifts.length > 0 ? 'Predicted Earnings' : 'Top Earnings Potential'}
          value={loading ? '...' : `£${totalPredictedEarnings.toFixed(2)}`}
          color={colors.primary[700]}
          sectionId="earnings"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
        <ClickableStatCard
          icon={<Clock size={24} />}
          label={committedShifts.length > 0 ? 'Committed Hours' : 'Peak Hours Available'}
          value={loading ? '...' : `${Math.round(totalHours)} hrs`}
          color={colors.warning[600]}
          sectionId="hours"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
        <ClickableStatCard
          icon={<BarChart3 size={24} />}
          label="Avg Demand Score"
          value={loading ? '...' : `${avgDemand}%`}
          color={colors.secondary[600]}
          sectionId="stability"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
      </div>

      {/* Navigation Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.md }}>
        <ClickableNavCard
          title="Shift Recommendations"
          description="AI-powered shift suggestions"
          icon={<MapPin size={20} />}
          sectionId="shifts"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
        <div
          onClick={() => router.push('/dashboard/guarantee')}
          style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: `1px solid ${colors.neutral[200]}`,
            cursor: 'pointer', transition: 'all 0.3s',
            display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
          }}
          onMouseOver={(e) => { e.currentTarget.style.borderColor = colors.primary[700]; e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,87,34,0.15)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
          onMouseOut={(e) => { e.currentTarget.style.borderColor = colors.neutral[200]; e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'translateY(0)'; }}
        >
          <div style={{ color: colors.primary[700], marginBottom: spacing.sm }}><Shield size={20} /></div>
          <h3 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>Income Guarantee</h3>
          <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>Guarantee eligibility & details</p>
        </div>
        <ClickableNavCard
          title="Analytics"
          description="Performance & volatility metrics"
          icon={<BarChart3 size={20} />}
          sectionId="analytics"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
        <ClickableNavCard
          title="Profile"
          description="Your account information"
          icon={<Settings size={20} />}
          sectionId="profile"
          expandedSection={expandedSection}
          setExpandedSection={setExpandedSection}
        />
      </div>

      {/* Expanded Content - Functional Sections */}
      {expandedSection && (
        <DriverExpandedSection
          sectionId={expandedSection}
          recommendations={recommendations}
          committedShifts={committedShifts}
          user={user}
          loading={loading}
          apiError={apiError}
          onCommit={handleCommitToShift}
          onClose={() => setExpandedSection(null)}
        />
      )}
    </div>
  );
}

/* ===== DRIVER EXPANDED SECTIONS (FUNCTIONAL) ===== */
interface DriverExpandedSectionProps {
  sectionId: string;
  recommendations: Recommendation[];
  committedShifts: CommittedShift[];
  user: any;
  loading: boolean;
  apiError: string | null;
  onCommit: (rec: Recommendation) => void;
  onClose: () => void;
}

function DriverExpandedSection({
  sectionId, recommendations, committedShifts, user, loading, apiError, onCommit, onClose,
}: DriverExpandedSectionProps) {

  const getContent = (): { title: string; subtitle: string; content: React.ReactNode } => {
    switch (sectionId) {

      /* FR5 + FR6: Shift Recommendations with Location */
      case 'shifts': {
        return {
          title: 'AI Shift Recommendations',
          subtitle: 'Smart recommendations based on UK demand patterns, location data, and predicted earnings. Commit to a shift to activate income guarantee.',
          content: (
            <div>
              {loading && (
                <p style={{ color: colors.neutral[500], padding: spacing.md }}>Loading recommendations from AI engine...</p>
              )}
              {apiError && (
                <div style={{ padding: spacing.md, backgroundColor: colors.error[50], borderRadius: '6px', color: colors.error[700], marginBottom: spacing.md }}>
                  {apiError}
                </div>
              )}
              {!loading && !apiError && recommendations.length === 0 && (
                <div style={{ padding: spacing.lg, textAlign: 'center', color: colors.neutral[500] }}>
                  <CheckCircle size={40} style={{ marginBottom: spacing.sm, color: colors.success[400] }} />
                  <p style={{ fontWeight: fonts.weights.bold }}>All available shifts committed!</p>
                  <p style={{ fontSize: fonts.sizes.caption }}>Check your Committed Shifts for details.</p>
                </div>
              )}
              {recommendations.map((rec, i) => (
                <div key={i} style={{
                  borderRadius: '8px', padding: spacing.md,
                  border: `1px solid ${rec.guarantee_eligible ? colors.success[200] : colors.neutral[200]}`,
                  backgroundColor: rec.guarantee_eligible ? `${colors.success[50]}40` : colors.neutral[0],
                  marginBottom: spacing.md,
                  transition: 'box-shadow 0.2s',
                }}
                  onMouseOver={(e) => (e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)')}
                  onMouseOut={(e) => (e.currentTarget.style.boxShadow = 'none')}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: spacing.sm }}>
                    {/* Left: Shift details */}
                    <div style={{ flex: 1, minWidth: '220px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, marginBottom: spacing.xs, flexWrap: 'wrap' }}>
                        <MapPin size={16} color={colors.primary[700]} />
                        <h4 style={{ margin: 0, fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[900] }}>
                          {rec.location_name}
                        </h4>
                        {rec.guarantee_eligible && (
                          <span style={{
                            padding: `2px ${spacing.sm}px`, borderRadius: '12px',
                            backgroundColor: colors.success[100], color: colors.success[700],
                            fontSize: '11px', fontWeight: fonts.weights.semibold,
                          }}>
                            <Shield size={10} style={{ verticalAlign: 'middle', marginRight: 2 }} />
                            Guarantee Eligible
                          </span>
                        )}
                      </div>
                      <p style={{ margin: 0, fontSize: fonts.sizes.caption, color: colors.neutral[600] }}>
                        {rec.region} · {rec.zone} · {rec.shift_type}
                      </p>
                      <p style={{ margin: `${spacing.xs}px 0 0 0`, fontSize: fonts.sizes.caption, color: colors.neutral[700] }}>
                        <Calendar size={12} style={{ verticalAlign: 'middle', marginRight: 4 }} />
                        {rec.day_name} · {new Date(rec.start_time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} – {new Date(rec.end_time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      <p style={{ margin: `${spacing.xs}px 0 0 0`, fontSize: fonts.sizes.caption, color: colors.neutral[500] }}>
                        Difficulty: {rec.difficulty} · Base: £{rec.base_hourly.toFixed(2)}/hr
                      </p>
                    </div>

                    {/* Right: Earnings + Demand + Commit */}
                    <div style={{ textAlign: 'right', minWidth: '170px' }}>
                      {/* FR3: Earnings Estimation */}
                      <p style={{ margin: 0, fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.success[700] }}>
                        £{rec.predicted_earnings.toFixed(2)}
                      </p>
                      <p style={{ margin: '2px 0', fontSize: fonts.sizes.caption, color: colors.neutral[600] }}>
                        predicted earnings
                      </p>

                      {/* FR4: Confidence / Demand Indicator */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs, justifyContent: 'flex-end', marginTop: spacing.xs }}>
                        <span style={{ fontSize: '11px', color: colors.neutral[600] }}>Demand</span>
                        <div style={{ width: 80, height: 6, backgroundColor: colors.neutral[200], borderRadius: 3 }}>
                          <div style={{
                            width: `${rec.demand_score}%`, height: '100%', borderRadius: 3,
                            backgroundColor: rec.demand_score >= 70 ? colors.success[500]
                              : rec.demand_score >= 40 ? colors.warning[500]
                              : colors.error[500],
                          }} />
                        </div>
                        <span style={{ fontSize: '11px', fontWeight: fonts.weights.bold, color: colors.neutral[700] }}>
                          {rec.demand_score}%
                        </span>
                      </div>

                      {/* FR7: Shift Commitment Button */}
                      <button
                        onClick={(e) => { e.stopPropagation(); onCommit(rec); }}
                        style={{
                          marginTop: spacing.sm,
                          padding: `${spacing.sm}px ${spacing.md}px`,
                          backgroundColor: colors.primary[700],
                          color: colors.neutral[0],
                          border: 'none', borderRadius: '6px',
                          cursor: 'pointer', fontWeight: fonts.weights.bold,
                          fontSize: fonts.sizes.caption,
                          transition: 'background-color 0.2s',
                          display: 'inline-flex', alignItems: 'center', gap: '4px',
                        }}
                        onMouseOver={(e) => (e.currentTarget.style.backgroundColor = colors.primary[800])}
                        onMouseOut={(e) => (e.currentTarget.style.backgroundColor = colors.primary[700])}
                      >
                        <CheckCircle size={14} />
                        Commit to Shift
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ),
        };
      }

      /* FR7 + FR10: Active / Committed Shifts */
      case 'active-shifts': {
        return {
          title: 'Committed Shifts',
          subtitle: committedShifts.length > 0
            ? `You have committed to ${committedShifts.length} shift(s). Income guarantee is active for eligible shifts.`
            : 'No shifts committed yet. Browse Shift Recommendations to find and commit to high-earning shifts.',
          content: (
            <div>
              {committedShifts.length === 0 ? (
                <div style={{ padding: spacing.lg, textAlign: 'center', color: colors.neutral[500] }}>
                  <Clock size={40} style={{ marginBottom: spacing.sm, opacity: 0.5 }} />
                  <p style={{ fontWeight: fonts.weights.bold, margin: `${spacing.sm}px 0` }}>No committed shifts yet</p>
                  <p style={{ fontSize: fonts.sizes.caption }}>
                    Go to <strong>Shift Recommendations</strong> to find AI-recommended shifts and commit to them.
                  </p>
                </div>
              ) : (
                committedShifts.map((s, i) => (
                  <div key={i} style={{
                    padding: spacing.md, borderRadius: '8px',
                    border: `1px solid ${colors.success[200]}`,
                    backgroundColor: colors.success[50],
                    marginBottom: spacing.sm,
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: spacing.sm,
                  }}>
                    <div>
                      <p style={{ margin: 0, fontWeight: fonts.weights.bold, color: colors.neutral[900] }}>
                        📍 {s.location_name} – {s.shift_type}
                      </p>
                      <p style={{ margin: `${spacing.xs}px 0 0 0`, fontSize: fonts.sizes.caption, color: colors.neutral[600] }}>
                        {s.day_name} · {new Date(s.start_time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })} – {new Date(s.end_time).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <p style={{ margin: 0, fontWeight: fonts.weights.bold, color: colors.success[700], fontSize: fonts.sizes.body }}>
                        £{s.predicted_earnings.toFixed(2)}
                      </p>
                      <div style={{ display: 'flex', gap: spacing.xs, justifyContent: 'flex-end', marginTop: spacing.xs }}>
                        <span style={{
                          padding: `2px ${spacing.sm}px`, borderRadius: '12px',
                          backgroundColor: colors.success[100], color: colors.success[700],
                          fontSize: '11px', fontWeight: fonts.weights.semibold,
                        }}>Committed ✓</span>
                        {s.guarantee_eligible && (
                          <span style={{
                            padding: `2px ${spacing.sm}px`, borderRadius: '12px',
                            backgroundColor: colors.primary[100], color: colors.primary[700],
                            fontSize: '11px', fontWeight: fonts.weights.semibold,
                          }}>Guaranteed</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          ),
        };
      }

      /* FR3 + FR8 + FR11 + FR12: Earnings & Guarantee */
      case 'earnings': {
        const totalEarnings = committedShifts.reduce((sum, s) => sum + s.predicted_earnings, 0);
        const guaranteeThreshold = totalEarnings * 0.9;
        return {
          title: 'Earnings Overview',
          subtitle: 'Your predicted earnings breakdown and income guarantee details.',
          content: (
            <div>
              {committedShifts.length === 0 ? (
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px', borderLeft: `4px solid ${colors.warning[600]}` }}>
                  <p style={{ margin: 0, color: colors.warning[700] }}>
                    <strong>No committed shifts yet.</strong> Commit to shifts via Shift Recommendations to see earnings predictions and guarantee eligibility.
                  </p>
                </div>
              ) : (
                <>
                  <div style={{ padding: spacing.md, backgroundColor: colors.success[50], borderRadius: '6px', marginBottom: spacing.md }}>
                    <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                      <strong>Total Predicted Earnings:</strong> £{totalEarnings.toFixed(2)}
                    </p>
                    <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                      <strong>Income Guarantee Threshold (90%):</strong> £{guaranteeThreshold.toFixed(2)}
                    </p>
                    <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                      <strong>Committed Shifts:</strong> {committedShifts.length}
                    </p>
                    <p style={{
                      margin: `${spacing.md}px 0 0 0`, fontSize: fonts.sizes.h5,
                      fontWeight: fonts.weights.bold, color: colors.success[700],
                    }}>
                      Guaranteed Minimum: £{guaranteeThreshold.toFixed(2)}
                    </p>
                  </div>
                  {/* FR12: Top-up Explanation */}
                  <div style={{ padding: spacing.md, backgroundColor: colors.neutral[100], borderRadius: '6px' }}>
                    <p style={{ margin: 0, fontSize: fonts.sizes.caption, color: colors.neutral[600], fontWeight: fonts.weights.bold }}>
                      How the Income Guarantee Works:
                    </p>
                    <ul style={{ margin: `${spacing.sm}px 0 0 0`, paddingLeft: spacing.lg, color: colors.neutral[700], fontSize: fonts.sizes.caption, lineHeight: 1.8 }}>
                      <li>Commit to a recommended shift window before it starts</li>
                      <li>Work the shift and your actual earnings are tracked automatically</li>
                      <li>If your actual earnings fall below 90% of the predicted amount, you receive a top-up</li>
                      <li><strong>Top-Up = Guaranteed Minimum − Actual Earnings</strong></li>
                      <li>Eligibility requires meeting minimum active hours and acceptance rate</li>
                    </ul>
                  </div>
                </>
              )}
            </div>
          ),
        };
      }

      /* Hours Breakdown */
      case 'hours': {
        const hoursBreakdown = committedShifts.map(s => {
          const hours = (new Date(s.end_time).getTime() - new Date(s.start_time).getTime()) / 3600000;
          return { day: s.day_name, location: s.location_name, shift: s.shift_type, hours };
        });
        const totalH = hoursBreakdown.reduce((sum, h) => sum + h.hours, 0);
        return {
          title: 'Hours Overview',
          subtitle: committedShifts.length > 0
            ? `${Math.round(totalH)} hours across ${committedShifts.length} committed shift(s).`
            : 'Commit to shifts to see your hours breakdown.',
          content: (
            <div>
              {committedShifts.length === 0 ? (
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px', borderLeft: `4px solid ${colors.warning[600]}` }}>
                  <p style={{ margin: 0, color: colors.warning[700] }}>No committed shifts yet. Browse Shift Recommendations to plan your week.</p>
                </div>
              ) : (
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px' }}>
                  {hoursBreakdown.map((h, i) => (
                    <p key={i} style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                      <strong>{h.day}:</strong> {h.hours} hours — {h.location} ({h.shift})
                    </p>
                  ))}
                  <p style={{ margin: `${spacing.md}px 0 0 0`, fontWeight: fonts.weights.bold, color: colors.neutral[900], fontSize: fonts.sizes.body, borderTop: `1px solid ${colors.warning[200]}`, paddingTop: spacing.sm }}>
                    Total: {Math.round(totalH)} hours
                  </p>
                </div>
              )}
            </div>
          ),
        };
      }

      /* FR14: Demand & Stability / Volatility Analysis */
      case 'stability': {
        const avgDemandScore = recommendations.length > 0
          ? Math.round(recommendations.reduce((s, r) => s + r.demand_score, 0) / recommendations.length)
          : 0;
        return {
          title: 'Demand & Stability Analysis',
          subtitle: 'UK demand patterns, income stability metrics, and volatility analysis.',
          content: (
            <div>
              <div style={{ padding: spacing.md, backgroundColor: colors.secondary[50], borderRadius: '6px', marginBottom: spacing.md }}>
                <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                  📊 <strong>Average Demand Score:</strong> {avgDemandScore}/100
                </p>
                <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                  🕐 <strong>Peak Hours:</strong> 7–9 AM (Morning Rush) &amp; 5–8 PM (Evening Rush)
                </p>
                <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                  📅 <strong>Best Days:</strong> Saturday (+35%), Sunday (+25%), Friday (+15%)
                </p>
                <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[700] }}>
                  📍 <strong>Top Earning Location:</strong> London Heathrow (£28.00/hr base rate)
                </p>
              </div>
              <div style={{ padding: spacing.md, backgroundColor: colors.neutral[100], borderRadius: '6px' }}>
                <p style={{ margin: 0, fontSize: fonts.sizes.caption, color: colors.neutral[600], fontWeight: fonts.weights.bold }}>
                  Income Stability Tips:
                </p>
                <ul style={{ margin: `${spacing.sm}px 0 0 0`, paddingLeft: spacing.lg, color: colors.neutral[700], fontSize: fonts.sizes.caption, lineHeight: 1.8 }}>
                  <li>Commit to peak-hour shifts for highest earnings consistency</li>
                  <li>Saturday evening shifts offer the best demand (2.3× multiplier)</li>
                  <li>Airport zones have higher base rates but vary by flight schedules</li>
                  <li>Use the income guarantee on committed shifts for earnings protection</li>
                  <li>Diversify across locations to reduce income volatility</li>
                </ul>
              </div>
            </div>
          ),
        };
      }

      /* FR8 + FR9: Income Guarantee Details */
      case 'guarantee': {
        const eligibleCount = recommendations.filter(r => r.guarantee_eligible).length;
        const committedGuaranteed = committedShifts.filter(s => s.guarantee_eligible).length;
        const totalGuaranteedEarnings = committedShifts
          .filter(s => s.guarantee_eligible)
          .reduce((sum, s) => sum + s.predicted_earnings, 0);
        return {
          title: 'Income Guarantee Window',
          subtitle: 'Your income protection details, eligibility status, and guarantee conditions.',
          content: (
            <div>
              {/* How it works */}
              <div style={{ padding: spacing.md, backgroundColor: colors.success[50], borderRadius: '6px', borderLeft: `4px solid ${colors.success[600]}`, marginBottom: spacing.md }}>
                <h4 style={{ margin: `0 0 ${spacing.sm}px 0`, color: colors.success[700], fontSize: fonts.sizes.body }}>
                  <Shield size={18} style={{ verticalAlign: 'middle', marginRight: 6 }} />
                  How the Income Guarantee Works
                </h4>
                <ol style={{ margin: 0, paddingLeft: spacing.lg, color: colors.neutral[700], fontSize: fonts.sizes.caption, lineHeight: 2 }}>
                  <li><strong>Browse Recommendations</strong> — View AI-powered shift suggestions</li>
                  <li><strong>Commit to a Shift</strong> — Click &quot;Commit to Shift&quot; on an eligible recommendation</li>
                  <li><strong>Work the Shift</strong> — Complete the committed shift as planned</li>
                  <li><strong>Earnings Compared</strong> — System compares actual vs predicted earnings</li>
                  <li><strong>Top-Up Applied</strong> — If actual &lt; 90% of predicted, you receive the difference</li>
                </ol>
              </div>

              {/* FR9: Eligibility Conditions */}
              <div style={{ padding: spacing.md, backgroundColor: colors.primary[50], borderRadius: '6px', borderLeft: `4px solid ${colors.primary[600]}`, marginBottom: spacing.md }}>
                <h4 style={{ margin: `0 0 ${spacing.sm}px 0`, color: colors.primary[700], fontSize: fonts.sizes.body }}>
                  Eligibility Requirements
                </h4>
                <ul style={{ margin: 0, paddingLeft: spacing.lg, color: colors.neutral[700], fontSize: fonts.sizes.caption, lineHeight: 1.8 }}>
                  <li>Minimum 20 active hours per week</li>
                  <li>Acceptance rate ≥ 95%</li>
                  <li>Cancellation rate ≤ 5%</li>
                  <li>Shift must be committed <strong>before</strong> it starts</li>
                </ul>
              </div>

              {/* Stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: spacing.md }}>
                <div style={{ padding: spacing.md, backgroundColor: colors.primary[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: 0 }}>
                    {eligibleCount}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Eligible Recommendations
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.success[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[700], margin: 0 }}>
                    {committedGuaranteed}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Committed (Protected)
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.warning[700], margin: 0 }}>
                    £{(totalGuaranteedEarnings * 0.9).toFixed(0)}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Guaranteed Minimum
                  </p>
                </div>
              </div>
            </div>
          ),
        };
      }

      /* FR14 + FR15: Performance Analytics */
      case 'analytics': {
        const topEarning = recommendations.length > 0
          ? Math.max(...recommendations.map(r => r.predicted_earnings))
          : 0;
        const lowestEarning = recommendations.length > 0
          ? Math.min(...recommendations.map(r => r.predicted_earnings))
          : 0;
        const avgEarning = recommendations.length > 0
          ? recommendations.reduce((s, r) => s + r.predicted_earnings, 0) / recommendations.length
          : 0;
        return {
          title: 'Performance Analytics',
          subtitle: 'Earnings performance metrics, volatility analysis, and stability reports.',
          content: (
            <div>
              {/* Stats grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: spacing.md, marginBottom: spacing.md }}>
                <div style={{ padding: spacing.md, backgroundColor: colors.success[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.success[700], margin: 0 }}>
                    £{topEarning.toFixed(2)}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Highest Predicted Shift
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.primary[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: 0 }}>
                    £{avgEarning.toFixed(2)}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Average Shift Earnings
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.warning[700], margin: 0 }}>
                    {recommendations.length}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Available Shifts
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.secondary[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.secondary[700], margin: 0 }}>
                    {committedShifts.length}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Shifts Committed
                  </p>
                </div>
              </div>
              {/* FR14: Earnings Volatility */}
              <div style={{ padding: spacing.md, backgroundColor: colors.neutral[100], borderRadius: '6px' }}>
                <p style={{ margin: 0, fontSize: fonts.sizes.caption, color: colors.neutral[600], fontWeight: fonts.weights.bold }}>
                  Earnings Volatility Analysis (FR14):
                </p>
                <p style={{ margin: `${spacing.sm}px 0 0 0`, fontSize: fonts.sizes.caption, color: colors.neutral[700] }}>
                  Based on {recommendations.length + committedShifts.length} analysed shifts, earnings range from
                  <strong> £{lowestEarning.toFixed(2)}</strong> to <strong>£{topEarning.toFixed(2)}</strong> per shift.
                  Committing to guarantee-eligible shifts reduces income volatility and provides earnings protection.
                </p>
              </div>
            </div>
          ),
        };
      }

      /* Profile */
      case 'profile': {
        return {
          title: 'Driver Profile',
          subtitle: 'Your account information and settings.',
          content: (
            <div>
              <div style={{ padding: spacing.md, backgroundColor: colors.neutral[100], borderRadius: '6px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: `${spacing.sm}px ${spacing.md}px`, fontSize: fonts.sizes.body }}>
                  <p style={{ margin: `${spacing.sm}px 0`, fontWeight: fonts.weights.bold, color: colors.neutral[600] }}>Name:</p>
                  <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[900] }}>{user?.full_name || 'N/A'}</p>
                  <p style={{ margin: `${spacing.sm}px 0`, fontWeight: fonts.weights.bold, color: colors.neutral[600] }}>Email:</p>
                  <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[900] }}>{user?.email || 'N/A'}</p>
                  <p style={{ margin: `${spacing.sm}px 0`, fontWeight: fonts.weights.bold, color: colors.neutral[600] }}>Role:</p>
                  <p style={{ margin: `${spacing.sm}px 0`, color: colors.neutral[900] }}>
                    {user?.role === 'driver' ? 'Driver' : user?.role === 'admin' ? 'Administrator' : user?.role || 'N/A'}
                  </p>
                  <p style={{ margin: `${spacing.sm}px 0`, fontWeight: fonts.weights.bold, color: colors.neutral[600] }}>Status:</p>
                  <p style={{ margin: `${spacing.sm}px 0` }}>
                    <span style={{
                      padding: `2px ${spacing.sm}px`, borderRadius: '12px',
                      backgroundColor: user?.is_active ? colors.success[100] : colors.error[100],
                      color: user?.is_active ? colors.success[700] : colors.error[700],
                      fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold,
                    }}>
                      {user?.is_active ? '● Active' : '● Inactive'}
                    </span>
                  </p>
                </div>
              </div>
            </div>
          ),
        };
      }

      default:
        return { title: 'Section', subtitle: '', content: null };
    }
  };

  const { title, subtitle, content } = getContent();

  return (
    <section style={{
      backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
      borderLeft: `4px solid ${colors.primary[700]}`,
      boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm }}>
        <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          {title}
        </h3>
        <button onClick={onClose} style={{
          background: 'none', border: 'none', color: colors.neutral[600],
          cursor: 'pointer', fontSize: '24px', padding: 0,
        }}>✕</button>
      </div>
      {subtitle && (
        <p style={{ color: colors.neutral[600], margin: `0 0 ${spacing.md}px 0`, fontSize: fonts.sizes.caption }}>{subtitle}</p>
      )}
      {content}
    </section>
  );
}

/* ===== ADMIN DASHBOARD (Real API Data + Navigation) ===== */
function AdminDashboard() {
  const router = useRouter();
  const [summary, setSummary] = useState<any>(null);
  const [drivers, setDrivers] = useState<any[]>([]);
  const [guaranteeOverview, setGuaranteeOverview] = useState<any>(null);
  const [shiftsOverview, setShiftsOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      try {
        const [sumRes, drvRes, guaRes, shfRes] = await Promise.all([
          fetch(`${API_BASE}/admin/dashboard-summary`),
          fetch(`${API_BASE}/admin/drivers`),
          fetch(`${API_BASE}/admin/guarantee-overview`),
          fetch(`${API_BASE}/admin/shifts-overview`),
        ]);
        if (sumRes.ok) setSummary(await sumRes.json());
        if (drvRes.ok) setDrivers(await drvRes.json());
        if (guaRes.ok) setGuaranteeOverview(await guaRes.json());
        if (shfRes.ok) setShiftsOverview(await shfRes.json());
      } catch (err) {
        setApiError('Could not connect to backend. Ensure server is running on port 8000.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, []);

  const handleSuspendDriver = async (driverId: number) => {
    setActionLoading(driverId);
    try {
      const res = await fetch(`${API_BASE}/admin/drivers/${driverId}/suspend`, { method: 'POST' });
      if (res.ok) {
        setDrivers(prev => prev.map(d => d.id === driverId ? { ...d, is_active: false } : d));
        showToast.success('Driver suspended');
      }
    } catch { showToast.error('Failed to suspend driver'); }
    finally { setActionLoading(null); }
  };

  const handleReactivateDriver = async (driverId: number) => {
    setActionLoading(driverId);
    try {
      const res = await fetch(`${API_BASE}/admin/drivers/${driverId}/reactivate`, { method: 'POST' });
      if (res.ok) {
        setDrivers(prev => prev.map(d => d.id === driverId ? { ...d, is_active: true } : d));
        showToast.success('Driver reactivated');
      }
    } catch { showToast.error('Failed to reactivate driver'); }
    finally { setActionLoading(null); }
  };

  const s = summary; // shorthand

  return (
    <div style={{ display: 'grid', gap: spacing.lg }}>
      {/* Header */}
      <section style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px',
        padding: spacing.lg, borderLeft: `4px solid ${colors.primary[700]}`,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}>
        <h2 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
          Admin Control Centre
        </h2>
        <p style={{ fontSize: fonts.sizes.body, color: colors.neutral[600], margin: `${spacing.sm}px 0 0 0` }}>
          Manage drivers, monitor platform performance, oversee income guarantees, and review model accuracy.
        </p>
      </section>

      {apiError && (
        <div style={{ padding: spacing.md, backgroundColor: colors.error[50], borderRadius: '6px', color: colors.error[700] }}>
          {apiError}
        </div>
      )}

      {/* KPI Summary Cards — Real Data */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: spacing.md }}>
        <AdminStatCard
          icon={<Users size={24} />}
          label="Active Drivers"
          value={loading ? '...' : `${s?.drivers?.active ?? 0}`}
          sub={loading ? '' : `${s?.drivers?.suspended ?? 0} suspended`}
          color={colors.primary[700]}
          onClick={() => setExpandedSection(expandedSection === 'drivers' ? null : 'drivers')}
        />
        <AdminStatCard
          icon={<Shield size={24} />}
          label="Guarantee Activations"
          value={loading ? '...' : `${s?.guarantee?.activations ?? 0}`}
          sub={loading ? '' : `${s?.guarantee?.activation_rate ?? 0}% activation rate`}
          color={colors.success[600]}
          onClick={() => setExpandedSection(expandedSection === 'guarantee' ? null : 'guarantee')}
        />
        <AdminStatCard
          icon={<TrendingUp size={24} />}
          label="Total Top-ups Paid"
          value={loading ? '...' : `£${(s?.guarantee?.total_topups_paid ?? 0).toFixed(2)}`}
          sub={loading ? '' : `${s?.shifts?.committed_completed ?? 0} shifts completed`}
          color={colors.warning[600]}
          onClick={() => setExpandedSection(expandedSection === 'guarantee' ? null : 'guarantee')}
        />
        <AdminStatCard
          icon={<BarChart3 size={24} />}
          label="Survey Responses"
          value={loading ? '...' : `${s?.surveys?.total_responses ?? 0}`}
          sub={loading ? '' : s?.surveys?.avg_satisfaction ? `Avg satisfaction: ${s.surveys.avg_satisfaction}/5` : 'No ratings yet'}
          color={colors.secondary[600]}
          onClick={() => router.push('/dashboard/survey-admin')}
        />
      </div>

      {/* Navigation Cards — Link to dedicated admin pages */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: spacing.md }}>
        <AdminNavCard
          title="Worker Management"
          description="View, suspend, reactivate drivers (FR9)"
          icon={<Users size={20} />}
          color={colors.primary[700]}
          onClick={() => setExpandedSection(expandedSection === 'drivers' ? null : 'drivers')}
          active={expandedSection === 'drivers'}
        />
        <AdminNavCard
          title="Model Performance"
          description="Prediction accuracy monitoring (NFR3)"
          icon={<Activity size={20} />}
          color={colors.success[600]}
          onClick={() => router.push('/dashboard/accuracy')}
        />
        <AdminNavCard
          title="Survey Reports"
          description="Aggregated driver feedback (FR16)"
          icon={<FileText size={20} />}
          color={colors.secondary[600]}
          onClick={() => router.push('/dashboard/survey-admin')}
        />
        <AdminNavCard
          title="Guarantee Overview"
          description="Platform-wide guarantee stats"
          icon={<Shield size={20} />}
          color={colors.warning[600]}
          onClick={() => setExpandedSection(expandedSection === 'guarantee' ? null : 'guarantee')}
          active={expandedSection === 'guarantee'}
        />
        <AdminNavCard
          title="Shifts Breakdown"
          description="Shift types, locations, status"
          icon={<Clock size={20} />}
          color={colors.primary[600]}
          onClick={() => setExpandedSection(expandedSection === 'shifts' ? null : 'shifts')}
          active={expandedSection === 'shifts'}
        />
        <AdminNavCard
          title="System Analytics"
          description="Earnings analytics & reports"
          icon={<BarChart3 size={20} />}
          color={colors.neutral[700]}
          onClick={() => router.push('/dashboard/analytics')}
        />
      </div>

      {/* Expanded Inline Sections */}
      {expandedSection === 'drivers' && (
        <section style={{
          backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
          borderLeft: `4px solid ${colors.primary[700]}`, boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
            <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
              Driver Management (FR9)
            </h3>
            <button onClick={() => setExpandedSection(null)} style={{ background: 'none', border: 'none', color: colors.neutral[600], cursor: 'pointer', fontSize: '24px', padding: 0 }}>✕</button>
          </div>
          <p style={{ color: colors.neutral[600], margin: `0 0 ${spacing.md}px 0`, fontSize: fonts.sizes.caption }}>
            {drivers.length} driver account(s). Suspend or reactivate as needed. Click &quot;Manage&quot; in the Workers page for full eligibility controls.
          </p>

          {drivers.length === 0 ? (
            <div style={{ padding: spacing.lg, textAlign: 'center', color: colors.neutral[500] }}>
              <Users size={40} style={{ marginBottom: spacing.sm, opacity: 0.5 }} />
              <p>No driver accounts found. Drivers register via the sign-up page.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: fonts.sizes.body }}>
                <thead>
                  <tr style={{ borderBottom: `2px solid ${colors.primary[700]}`, backgroundColor: colors.primary[50] }}>
                    <th style={{ padding: spacing.md, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>ID</th>
                    <th style={{ padding: spacing.md, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Name</th>
                    <th style={{ padding: spacing.md, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Email</th>
                    <th style={{ padding: spacing.md, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Phone</th>
                    <th style={{ padding: spacing.md, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Status</th>
                    <th style={{ padding: spacing.md, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Joined</th>
                    <th style={{ padding: spacing.md, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {drivers.map((d) => (
                    <tr key={d.id} style={{ borderBottom: `1px solid ${colors.neutral[200]}` }}>
                      <td style={{ padding: spacing.md, color: colors.neutral[500], fontSize: fonts.sizes.caption }}>#{d.id}</td>
                      <td style={{ padding: spacing.md, color: colors.neutral[900], fontWeight: fonts.weights.semibold }}>{d.full_name}</td>
                      <td style={{ padding: spacing.md, color: colors.neutral[700] }}>{d.email}</td>
                      <td style={{ padding: spacing.md, color: colors.neutral[700] }}>{d.phone || '—'}</td>
                      <td style={{ padding: spacing.md, textAlign: 'center' }}>
                        <span style={{
                          display: 'inline-block', padding: `${spacing.xs}px ${spacing.sm}px`,
                          backgroundColor: d.is_active ? colors.success[100] : colors.error[100],
                          color: d.is_active ? colors.success[700] : colors.error[700],
                          borderRadius: '4px', fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold,
                        }}>
                          {d.is_active ? 'Active' : 'Suspended'}
                        </span>
                      </td>
                      <td style={{ padding: spacing.md, textAlign: 'center', color: colors.neutral[600], fontSize: fonts.sizes.caption }}>
                        {d.created_at ? new Date(d.created_at).toLocaleDateString('en-GB') : '—'}
                      </td>
                      <td style={{ padding: spacing.md, textAlign: 'center' }}>
                        {d.is_active ? (
                          <button
                            disabled={actionLoading === d.id}
                            onClick={() => handleSuspendDriver(d.id)}
                            style={{
                              padding: `${spacing.xs}px ${spacing.sm}px`, backgroundColor: 'transparent',
                              color: colors.error[700], border: `1px solid ${colors.error[700]}`,
                              borderRadius: '4px', cursor: actionLoading === d.id ? 'wait' : 'pointer',
                              fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold,
                              opacity: actionLoading === d.id ? 0.6 : 1,
                            }}
                          >
                            {actionLoading === d.id ? 'Suspending...' : 'Suspend'}
                          </button>
                        ) : (
                          <button
                            disabled={actionLoading === d.id}
                            onClick={() => handleReactivateDriver(d.id)}
                            style={{
                              padding: `${spacing.xs}px ${spacing.sm}px`, backgroundColor: 'transparent',
                              color: colors.success[700], border: `1px solid ${colors.success[700]}`,
                              borderRadius: '4px', cursor: actionLoading === d.id ? 'wait' : 'pointer',
                              fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold,
                              opacity: actionLoading === d.id ? 0.6 : 1,
                            }}
                          >
                            {actionLoading === d.id ? 'Reactivating...' : 'Reactivate'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Link to full Workers management page */}
          <div style={{ marginTop: spacing.md, textAlign: 'center' }}>
            <button
              onClick={() => router.push('/dashboard/workers')}
              style={{
                padding: `${spacing.sm}px ${spacing.lg}px`, backgroundColor: colors.primary[700],
                color: colors.neutral[0], border: 'none', borderRadius: '6px', cursor: 'pointer',
                fontWeight: fonts.weights.semibold, fontSize: fonts.sizes.body,
              }}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = colors.primary[800])}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = colors.primary[700])}
            >
              Open Full Worker Management (FR9)
            </button>
          </div>
        </section>
      )}

      {expandedSection === 'guarantee' && (
        <section style={{
          backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
          borderLeft: `4px solid ${colors.success[600]}`, boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
            <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
              Platform Guarantee Overview
            </h3>
            <button onClick={() => setExpandedSection(null)} style={{ background: 'none', border: 'none', color: colors.neutral[600], cursor: 'pointer', fontSize: '24px', padding: 0 }}>✕</button>
          </div>
          <p style={{ color: colors.neutral[600], margin: `0 0 ${spacing.md}px 0`, fontSize: fonts.sizes.caption }}>
            System-wide income guarantee statistics across all drivers. Shows guarantee usage, top-up costs, and per-driver breakdown.
          </p>

          {!guaranteeOverview ? (
            <p style={{ color: colors.neutral[500], padding: spacing.md }}>Loading guarantee data...</p>
          ) : (
            <>
              {/* Summary stats */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: spacing.md, marginBottom: spacing.lg }}>
                <div style={{ padding: spacing.md, backgroundColor: colors.success[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.success[700], margin: 0 }}>
                    {guaranteeOverview.total_completed}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Completed Shifts
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.warning[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.warning[700], margin: 0 }}>
                    {guaranteeOverview.guarantee_triggered}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Guarantees Triggered
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.primary[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.primary[700], margin: 0 }}>
                    £{guaranteeOverview.total_topups.toFixed(2)}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Total Top-ups Paid
                  </p>
                </div>
                <div style={{ padding: spacing.md, backgroundColor: colors.secondary[50], borderRadius: '6px', textAlign: 'center' }}>
                  <p style={{ fontSize: fonts.sizes.h3, fontWeight: fonts.weights.bold, color: colors.secondary[700], margin: 0 }}>
                    £{guaranteeOverview.avg_topup.toFixed(2)}
                  </p>
                  <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>
                    Avg Top-up Amount
                  </p>
                </div>
              </div>

              {/* Per-driver breakdown */}
              {guaranteeOverview.per_driver && guaranteeOverview.per_driver.length > 0 && (
                <>
                  <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.sm}px 0` }}>
                    Per-Driver Breakdown
                  </h4>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: fonts.sizes.caption }}>
                      <thead>
                        <tr style={{ borderBottom: `2px solid ${colors.success[600]}`, backgroundColor: colors.success[50] }}>
                          <th style={{ padding: spacing.sm, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.success[700] }}>Driver</th>
                          <th style={{ padding: spacing.sm, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.success[700] }}>Completed</th>
                          <th style={{ padding: spacing.sm, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.success[700] }}>Guarantees</th>
                          <th style={{ padding: spacing.sm, textAlign: 'right', fontWeight: fonts.weights.bold, color: colors.success[700] }}>Total Top-up</th>
                        </tr>
                      </thead>
                      <tbody>
                        {guaranteeOverview.per_driver.map((pd: any) => (
                          <tr key={pd.driver_id} style={{ borderBottom: `1px solid ${colors.neutral[200]}` }}>
                            <td style={{ padding: spacing.sm, color: colors.neutral[900] }}>{pd.driver_name}</td>
                            <td style={{ padding: spacing.sm, textAlign: 'center', color: colors.neutral[700] }}>{pd.completed_shifts}</td>
                            <td style={{ padding: spacing.sm, textAlign: 'center' }}>
                              <span style={{
                                padding: `2px 8px`, borderRadius: '12px', fontSize: '11px', fontWeight: fonts.weights.semibold,
                                backgroundColor: pd.guarantees_triggered > 0 ? colors.warning[100] : colors.neutral[100],
                                color: pd.guarantees_triggered > 0 ? colors.warning[700] : colors.neutral[600],
                              }}>
                                {pd.guarantees_triggered}
                              </span>
                            </td>
                            <td style={{ padding: spacing.sm, textAlign: 'right', color: colors.neutral[900], fontWeight: fonts.weights.semibold }}>
                              £{pd.total_topup.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </>
          )}
        </section>
      )}

      {expandedSection === 'shifts' && (
        <section style={{
          backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.lg,
          borderLeft: `4px solid ${colors.primary[600]}`, boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.md }}>
            <h3 style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>
              Shifts Breakdown
            </h3>
            <button onClick={() => setExpandedSection(null)} style={{ background: 'none', border: 'none', color: colors.neutral[600], cursor: 'pointer', fontSize: '24px', padding: 0 }}>✕</button>
          </div>

          {!shiftsOverview ? (
            <p style={{ color: colors.neutral[500], padding: spacing.md }}>Loading shift data...</p>
          ) : (
            <>
              {/* Status Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: spacing.md, marginBottom: spacing.lg }}>
                {Object.entries(shiftsOverview.by_status || {}).map(([status, count]: [string, any]) => (
                  <div key={status} style={{
                    padding: spacing.md, borderRadius: '6px', textAlign: 'center',
                    backgroundColor: status === 'completed' ? colors.success[50]
                      : status === 'committed' ? colors.primary[50]
                      : status === 'cancelled' ? colors.error[50]
                      : colors.neutral[100],
                  }}>
                    <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, margin: 0,
                      color: status === 'completed' ? colors.success[700]
                        : status === 'committed' ? colors.primary[700]
                        : status === 'cancelled' ? colors.error[700]
                        : colors.neutral[700],
                    }}>{count}</p>
                    <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0`, textTransform: 'capitalize' }}>
                      {status}
                    </p>
                  </div>
                ))}
              </div>

              {/* By Shift Type */}
              {shiftsOverview.by_type && shiftsOverview.by_type.length > 0 && (
                <>
                  <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.sm}px 0` }}>
                    By Shift Type
                  </h4>
                  <div style={{ overflowX: 'auto', marginBottom: spacing.md }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: fonts.sizes.caption }}>
                      <thead>
                        <tr style={{ borderBottom: `2px solid ${colors.primary[600]}`, backgroundColor: colors.primary[50] }}>
                          <th style={{ padding: spacing.sm, textAlign: 'left', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Type</th>
                          <th style={{ padding: spacing.sm, textAlign: 'center', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Count</th>
                          <th style={{ padding: spacing.sm, textAlign: 'right', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Total Predicted</th>
                          <th style={{ padding: spacing.sm, textAlign: 'right', fontWeight: fonts.weights.bold, color: colors.primary[700] }}>Total Actual</th>
                        </tr>
                      </thead>
                      <tbody>
                        {shiftsOverview.by_type.map((t: any) => (
                          <tr key={t.shift_type} style={{ borderBottom: `1px solid ${colors.neutral[200]}` }}>
                            <td style={{ padding: spacing.sm, color: colors.neutral[900], fontWeight: fonts.weights.semibold }}>{t.shift_type}</td>
                            <td style={{ padding: spacing.sm, textAlign: 'center', color: colors.neutral[700] }}>{t.count}</td>
                            <td style={{ padding: spacing.sm, textAlign: 'right', color: colors.neutral[700] }}>£{t.total_predicted.toFixed(2)}</td>
                            <td style={{ padding: spacing.sm, textAlign: 'right', color: colors.neutral[700] }}>£{t.total_actual.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}

              {/* By Location */}
              {shiftsOverview.by_location && shiftsOverview.by_location.length > 0 && (
                <>
                  <h4 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `0 0 ${spacing.sm}px 0` }}>
                    By Location
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: spacing.sm }}>
                    {shiftsOverview.by_location.map((loc: any) => (
                      <div key={loc.location} style={{
                        padding: spacing.sm, borderRadius: '6px', border: `1px solid ${colors.neutral[200]}`,
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      }}>
                        <div>
                          <p style={{ margin: 0, fontSize: fonts.sizes.caption, fontWeight: fonts.weights.semibold, color: colors.neutral[900] }}>{loc.location}</p>
                          <p style={{ margin: 0, fontSize: '11px', color: colors.neutral[500] }}>{loc.count} shift(s)</p>
                        </div>
                        <p style={{ margin: 0, fontSize: fonts.sizes.caption, fontWeight: fonts.weights.bold, color: colors.primary[700] }}>
                          £{loc.total_predicted.toFixed(0)}
                        </p>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </>
          )}
        </section>
      )}

      {/* Quick Audit Info (Nice-to-have) */}
      {!loading && s && (
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: spacing.md,
        }}>
          <div style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: `3px solid ${colors.neutral[400]}`,
          }}>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Audit Log Entries (NFR11)</p>
            <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `${spacing.xs}px 0 0 0` }}>
              {s.audit_log_entries}
            </p>
            <p style={{ fontSize: '11px', color: colors.neutral[500], margin: `${spacing.xs}px 0 0 0` }}>
              Guarantee commitments, earnings recordings, and cancellations are all logged for auditability.
            </p>
          </div>
          <div style={{
            backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: `3px solid ${colors.neutral[400]}`,
          }}>
            <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[500], margin: 0 }}>Prediction Accuracy Records</p>
            <p style={{ fontSize: fonts.sizes.h4, fontWeight: fonts.weights.bold, color: colors.neutral[800], margin: `${spacing.xs}px 0 0 0` }}>
              {s.accuracy?.records ?? 0} {s.accuracy?.avg_mape != null ? `(MAPE: ${s.accuracy.avg_mape}%)` : ''}
            </p>
            <p style={{ fontSize: '11px', color: colors.neutral[500], margin: `${spacing.xs}px 0 0 0` }}>
              Model performance tracked via NFR3 accuracy monitoring. Click &quot;Model Performance&quot; for details.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

/* Admin-specific card components */
function AdminStatCard({ icon, label, value, sub, color, onClick }: {
  icon: React.ReactNode; label: string; value: string; sub: string; color: string; onClick: () => void;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderTop: `3px solid ${color}`,
        transition: 'transform 0.2s, box-shadow 0.2s', cursor: 'pointer',
      }}
      onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; }}
      onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'; }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
        <div style={{ color, opacity: 0.8 }}>{icon}</div>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>{label}</p>
          <p style={{ fontSize: fonts.sizes.h5, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: `${spacing.xs}px 0 0 0` }}>{value}</p>
          {sub && <p style={{ fontSize: '11px', color: colors.neutral[500], margin: `2px 0 0 0` }}>{sub}</p>}
        </div>
      </div>
    </div>
  );
}

function AdminNavCard({ title, description, icon, color, onClick, active }: {
  title: string; description: string; icon: React.ReactNode; color: string; onClick: () => void; active?: boolean;
}) {
  return (
    <div
      onClick={onClick}
      style={{
        backgroundColor: active ? `${color}10` : colors.neutral[0], borderRadius: '8px', padding: spacing.md,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: `2px solid ${active ? color : `${color}20`}`,
        cursor: 'pointer', transition: 'all 0.3s',
        display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
      }}
      onMouseOver={(e) => { e.currentTarget.style.borderColor = color; e.currentTarget.style.boxShadow = `0 4px 12px ${color}25`; e.currentTarget.style.transform = 'translateY(-4px)'; }}
      onMouseOut={(e) => { if (!active) e.currentTarget.style.borderColor = `${color}20`; e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'translateY(0)'; }}
    >
      <div style={{ color, marginBottom: spacing.sm }}>{icon}</div>
      <h3 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>{title}</h3>
      <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>{description}</p>
    </div>
  );
}

/* ===== REUSABLE CARD COMPONENTS ===== */
interface ClickableStatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
  sectionId: string;
  expandedSection: string | null;
  setExpandedSection: (id: string | null) => void;
}

function ClickableStatCard({ icon, label, value, color, sectionId, expandedSection, setExpandedSection }: ClickableStatCardProps) {
  const isExpanded = expandedSection === sectionId;
  return (
    <div
      onClick={() => setExpandedSection(isExpanded ? null : sectionId)}
      style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderTop: `3px solid ${color}`,
        transition: 'transform 0.2s, box-shadow 0.2s', cursor: 'pointer',
      }}
      onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; }}
      onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'; }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
        <div style={{ color, opacity: 0.8 }}>{icon}</div>
        <div style={{ flex: 1 }}>
          <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: 0 }}>{label}</p>
          <p style={{ fontSize: fonts.sizes.h5, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: `${spacing.xs}px 0 0 0` }}>{value}</p>
        </div>
        <ChevronDown size={20} style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.3s' }} />
      </div>
    </div>
  );
}

interface ClickableNavCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  sectionId: string;
  expandedSection: string | null;
  setExpandedSection: (id: string | null) => void;
}

function ClickableNavCard({ title, description, icon, sectionId, expandedSection, setExpandedSection }: ClickableNavCardProps) {
  return (
    <div
      onClick={() => setExpandedSection(expandedSection === sectionId ? null : sectionId)}
      style={{
        backgroundColor: colors.neutral[0], borderRadius: '8px', padding: spacing.md,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: `1px solid ${colors.neutral[200]}`,
        cursor: 'pointer', transition: 'all 0.3s',
        display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center',
      }}
      onMouseOver={(e) => { e.currentTarget.style.borderColor = colors.primary[700]; e.currentTarget.style.boxShadow = '0 4px 12px rgba(255,87,34,0.15)'; e.currentTarget.style.transform = 'translateY(-4px)'; }}
      onMouseOut={(e) => { e.currentTarget.style.borderColor = colors.neutral[200]; e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)'; e.currentTarget.style.transform = 'translateY(0)'; }}
    >
      <div style={{ color: colors.primary[700], marginBottom: spacing.sm }}>{icon}</div>
      <h3 style={{ fontSize: fonts.sizes.body, fontWeight: fonts.weights.bold, color: colors.neutral[900], margin: 0 }}>{title}</h3>
      <p style={{ fontSize: fonts.sizes.caption, color: colors.neutral[600], margin: `${spacing.xs}px 0 0 0` }}>{description}</p>
    </div>
  );
}


