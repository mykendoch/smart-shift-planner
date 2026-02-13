'use client';

import { useAuthStore } from '@/lib/store';
import { useEligibility } from '@/lib/hooks';
import { Toaster } from 'react-hot-toast';
import {
  AlertCircle,
  CheckCircle,
  Clock,
  Hand,
  Star,
  Zap,
  TrendingUp,
  Info,
} from 'lucide-react';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';

export default function EligibilityPage() {
  const { user } = useAuthStore();
  const { data, loading, error } = useEligibility(user?.id || '');

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
            background: `linear-gradient(135deg, ${colors.warning[600]} 0%, ${colors.warning[700]} 100%)`,
            boxShadow: '0 10px 30px rgba(245, 158, 11, 0.3)',
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div
              className="w-14 h-14 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(255, 255, 255, 0.2)' }}
            >
              <CheckCircle size={28} />
            </div>
            <div>
              <h1
                style={{
                  fontSize: fonts.sizes.h3,
                  fontWeight: fonts.weights.bold,
                }}
              >
                Eligibility Status
              </h1>
              <p
                style={{
                  fontSize: fonts.sizes.caption,
                  opacity: 0.9,
                  marginTop: spacing.xs,
                }}
              >
                Check your income guarantee eligibility requirements
              </p>
            </div>
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
                  borderTopColor: colors.warning[500],
                  borderRightColor: colors.warning[500],
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
              Checking your eligibility...
            </p>
          </div>
        )}

        {/* Main Content */}
        {data && !loading && (
          <>
            {/* Overall Status Card */}
            <div
              className="rounded-xl p-8 text-white overflow-hidden relative"
              style={{
                background: data.is_eligible
                  ? `linear-gradient(135deg, ${colors.success[600]} 0%, ${colors.success[700]} 100%)`
                  : `linear-gradient(135deg, ${colors.warning[600]} 0%, ${colors.warning[700]} 100%)`,
                boxShadow: data.is_eligible
                  ? '0 10px 30px rgba(34, 197, 94, 0.3)'
                  : '0 10px 30px rgba(245, 158, 11, 0.3)',
              }}
            >
              <div className="flex items-center gap-6">
                <div
                  className="w-20 h-20 rounded-full flex items-center justify-center"
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                  }}
                >
                  {data.is_eligible ? (
                    <CheckCircle size={40} />
                  ) : (
                    <AlertCircle size={40} />
                  )}
                </div>
                <div>
                  <h2
                    style={{
                      fontSize: fonts.sizes.h4,
                      fontWeight: fonts.weights.bold,
                      marginBottom: spacing.xs,
                    }}
                  >
                    {data.is_eligible ? '✓ You Are Eligible' : '⚠ Not Currently Eligible'}
                  </h2>
                  <p
                    style={{
                      fontSize: fonts.sizes.body,
                      opacity: 0.95,
                    }}
                  >
                    {data.is_eligible
                      ? 'You can access all income guarantee benefits for your shifts.'
                      : 'You need to meet specific requirements to access income guarantees.'}
                  </p>
                </div>
              </div>
            </div>

            {/* Eligibility Criteria */}
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
                  Eligibility Criteria
                </h2>
                <p
                  style={{
                    fontSize: fonts.sizes.caption,
                    color: colors.neutral[500],
                    marginTop: spacing.xs,
                  }}
                >
                  You must meet all criteria to maintain eligibility
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <EligibilityCheck
                  icon={Clock}
                  label="Active Hours per Week"
                  status={data.checks?.active_hours_check}
                  requirement="Minimum 20 hours"
                  current={`${data.active_hours_week} hours`}
                />

                <EligibilityCheck
                  icon={Hand}
                  label="Acceptance Rate"
                  status={data.checks?.acceptance_rate_check}
                  requirement="At least 95%"
                  current={`${(data.acceptance_rate * 100).toFixed(1)}%`}
                />

                <EligibilityCheck
                  icon={TrendingUp}
                  label="Cancellation Rate"
                  status={data.checks?.cancellation_rate_check}
                  requirement="Less than 5%"
                  current={`${(data.cancellation_rate * 100).toFixed(1)}%`}
                />

                <EligibilityCheck
                  icon={Star}
                  label="Average Rating"
                  status={data.checks?.rating_check}
                  requirement="At least 4.0 stars"
                  current={`${data.avg_rating?.toFixed(1) || 'N/A'} stars`}
                />
              </div>
            </div>

            {/* Status Badge */}
            {data.status && (
              <div
                className="rounded-xl p-6"
                style={{
                  background: colors.neutral[0],
                  border: `1px solid ${colors.neutral[200]}`,
                }}
              >
                <p
                  style={{
                    fontSize: fonts.sizes.caption,
                    color: colors.neutral[600],
                    marginBottom: spacing.md,
                  }}
                >
                  Account Status
                </p>
                <div className="flex items-center gap-3">
                  <div
                    className="w-4 h-4 rounded-full animate-pulse"
                    style={{
                      background:
                        data.status === 'active'
                          ? colors.success[500]
                          : data.status === 'suspended'
                          ? colors.error[500]
                          : colors.warning[500],
                    }}
                  ></div>
                  <span
                    style={{
                      fontWeight: fonts.weights.semibold,
                      color: colors.neutral[800],
                      fontSize: fonts.sizes.body,
                      textTransform: 'capitalize',
                    }}
                  >
                    {data.status === 'active'
                      ? 'Active & Eligible'
                      : data.status === 'suspended'
                      ? 'Account Suspended'
                      : 'Pending Review'}
                  </span>
                </div>
              </div>
            )}

            {/* How to Maintain Eligibility */}
            <div
              className="rounded-xl p-6"
              style={{
                background: colors.success[50],
                border: `1px solid ${colors.success[200]}`,
              }}
            >
              <div className="flex items-start gap-4">
                <Zap size={24} color={colors.success[600]} style={{ marginTop: spacing.xs }} />
                <div className="flex-1">
                  <h3
                    style={{
                      fontWeight: fonts.weights.semibold,
                      color: colors.success[900],
                      fontSize: fonts.sizes.body,
                      marginBottom: spacing.md,
                    }}
                  >
                    How to Maintain Eligibility
                  </h3>
                  <ul className="space-y-3">
                    {[
                      {
                        title: 'Active Hours',
                        desc: 'Complete at least 20 hours of shifts weekly',
                      },
                      {
                        title: 'Acceptance',
                        desc: 'Accept at least 95% of offered shifts',
                      },
                      {
                        title: 'Reliability',
                        desc: 'Cancel fewer than 5% of accepted shifts',
                      },
                      {
                        title: 'Quality',
                        desc: 'Maintain an excellent rating from customers',
                      },
                      {
                        title: 'Consistency',
                        desc: 'Meet all criteria on an ongoing basis',
                      },
                    ].map((item, idx) => (
                      <li key={idx} className="flex gap-3">
                        <CheckCircle size={18} color={colors.success[600]} style={{ marginTop: spacing.xs, flexShrink: 0 }} />
                        <div>
                          <p
                            style={{
                              fontWeight: fonts.weights.semibold,
                              color: colors.success[900],
                              fontSize: fonts.sizes.body,
                            }}
                          >
                            {item.title}
                          </p>
                          <p
                            style={{
                              color: colors.success[700],
                              fontSize: fonts.sizes.caption,
                              marginTop: spacing.xs,
                            }}
                          >
                            {item.desc}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            {/* Action Required for Ineligible */}
            {!data.is_eligible && (
              <div
                className="rounded-xl p-6"
                style={{
                  background: colors.warning[50],
                  border: `1px solid ${colors.warning[200]}`,
                }}
              >
                <div className="flex items-start gap-4">
                  <AlertCircle size={24} color={colors.warning[600]} style={{ marginTop: spacing.xs }} />
                  <div>
                    <h3
                      style={{
                        fontWeight: fonts.weights.semibold,
                        color: colors.warning[900],
                        fontSize: fonts.sizes.body,
                        marginBottom: spacing.md,
                      }}
                    >
                      What to Do Next
                    </h3>
                    <p
                      style={{
                        color: colors.warning[800],
                        fontSize: fonts.sizes.body,
                        lineHeight: 1.6,
                        marginBottom: spacing.md,
                      }}
                    >
                      Your account currently doesn't meet all eligibility requirements. Focus on
                      improving the criteria where you're falling short.
                    </p>
                    <p
                      style={{
                        color: colors.warning[700],
                        fontSize: fonts.sizes.caption,
                      }}
                    >
                      Need help? Contact support or check our FAQ for tips on improving your metrics.
                    </p>
                  </div>
                </div>
              </div>
            )}
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
              No eligibility data available
            </p>
          </div>
        )}
      </div>
    </>
  );
}

interface EligibilityCheckProps {
  icon: React.ForwardRefExoticComponent<any>;
  label: string;
  status?: boolean;
  requirement: string;
  current: string;
}

function EligibilityCheck({
  icon: Icon,
  label,
  status,
  requirement,
  current,
}: EligibilityCheckProps) {
  let bgColor = colors.neutral[50];
  let borderColor = colors.neutral[300];
  let accentColor = colors.neutral[400];
  let statusIcon = '○';

  if (status === true) {
    bgColor = colors.success[50];
    borderColor = colors.success[300];
    accentColor = colors.success[500];
    statusIcon = '✓';
  } else if (status === false) {
    bgColor = colors.error[50];
    borderColor = colors.error[300];
    accentColor = colors.error[500];
    statusIcon = '✗';
  }

  return (
    <div
      className="rounded-xl p-6 border-l-4"
      style={{
        background: bgColor,
        borderColor: borderColor,
        borderLeftColor: accentColor,
      }}
    >
      <div className="flex items-start gap-4 mb-4">
        <div
          className="w-12 h-12 rounded-lg flex items-center justify-center"
          style={{ background: `${accentColor}20` }}
        >
          <Icon size={24} color={accentColor} />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span
              style={{
                fontWeight: fonts.weights.bold,
                color: accentColor,
                fontSize: fonts.sizes.body,
              }}
            >
              {statusIcon}
            </span>
            <h4
              style={{
                fontWeight: fonts.weights.semibold,
                color: colors.neutral[900],
                fontSize: fonts.sizes.body,
              }}
            >
              {label}
            </h4>
          </div>
          <p
            style={{
              fontSize: fonts.sizes.caption,
              color: colors.neutral[600],
            }}
          >
            Requirement: {requirement}
          </p>
        </div>
      </div>

      <div className="flex justify-between items-center pt-4" style={{ borderTop: `1px solid ${borderColor}` }}>
        <span
          style={{
            fontSize: fonts.sizes.caption,
            color: colors.neutral[600],
          }}
        >
          Current:
        </span>
        <span
          style={{
            fontWeight: fonts.weights.bold,
            color: accentColor,
            fontSize: fonts.sizes.body,
          }}
        >
          {current}
        </span>
      </div>
    </div>
  );
}
