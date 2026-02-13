'use client';

import { useAuthStore } from '@/lib/store';
import { useEligibility } from '@/lib/hooks';

export default function EligibilityPage() {
  const { user } = useAuthStore();
  const { data, loading, error } = useEligibility(user?.id || '');

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
        <h1 className="text-3xl font-bold mb-2">Guarantee Eligibility Status</h1>
        <p className="text-gray-600">
          Check your current eligibility for income guarantee protection
        </p>
      </div>

      {error && (
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {loading ? (
        <div className="card text-center py-8">
          <p className="text-gray-600">Loading eligibility data...</p>
        </div>
      ) : data ? (
        <>
          {/* Overall Status */}
          <div
            className={`card border-2 ${
              data.is_eligible
                ? 'bg-green-50 border-green-300'
                : 'bg-orange-50 border-orange-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h2 className={`text-2xl font-bold ${
                  data.is_eligible ? 'text-green-700' : 'text-orange-700'
                }`}>
                  {data.is_eligible ? '✓ Eligible' : '⚠ Not Currently Eligible'}
                </h2>
                <p className={`${
                  data.is_eligible ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {data.is_eligible
                    ? 'You can access all income guarantee benefits'
                    : 'You need to meet specific requirements'}
                </p>
              </div>
            </div>
          </div>

          {/* Detailed Checks */}
          <div className="space-y-4">
            <h3 className="text-xl font-bold">Eligibility Criteria</h3>

            <EligibilityCheck
              label="Active Hours per Week"
              status={data.checks?.active_hours_check}
              requirement="Minimum 20 hours"
              current={`${data.active_hours_week} hours`}
            />

            <EligibilityCheck
              label="Acceptance Rate"
              status={data.checks?.acceptance_rate_check}
              requirement="At least 95%"
              current={`${(data.acceptance_rate * 100).toFixed(1)}%`}
            />

            <EligibilityCheck
              label="Cancellation Rate"
              status={data.checks?.cancellation_rate_check}
              requirement="Less than 5%"
              current={`${(data.cancellation_rate * 100).toFixed(1)}%`}
            />

            <EligibilityCheck
              label="Average Rating"
              status={data.checks?.rating_check}
              requirement="At least 4.0 stars"
              current={`${data.avg_rating?.toFixed(1) || 'N/A'} stars`}
            />
          </div>

          {/* Status Badge */}
          {data.status && (
            <div className="card">
              <p className="text-sm text-gray-600 mb-2">Current Status:</p>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  data.status === 'active'
                    ? 'bg-green-500'
                    : data.status === 'suspended'
                    ? 'bg-red-500'
                    : 'bg-yellow-500'
                }`} />
                <span className="font-semibold text-gray-800 capitalize">
                  {data.status === 'active'
                    ? 'Active & Eligible'
                    : data.status === 'suspended'
                    ? 'Account Suspended'
                    : 'Pending Review'}
                </span>
              </div>
            </div>
          )}

          {/* Help Section */}
          <div className="card bg-blue-50 border border-blue-200">
            <h3 className="font-bold text-blue-900 mb-3">💡 How to Maintain Eligibility</h3>
            <ul className="space-y-2 text-blue-800 text-sm">
              <li>
                ✓ <strong>Active Hours:</strong> Complete at least 20 hours of shifts weekly
              </li>
              <li>
                ✓ <strong>Acceptance:</strong> Accept at least 95% of offered shifts
              </li>
              <li>
                ✓ <strong>Reliability:</strong> Cancel fewer than 5% of accepted shifts
              </li>
              <li>
                ✓ <strong>Quality:</strong> Maintain an excellent rating from customers
              </li>
              <li>
                ✓ <strong>Consistency:</strong> Meet all criteria on an ongoing basis
              </li>
            </ul>
          </div>

          {!data.is_eligible && (
            <div className="card bg-orange-50 border border-orange-200">
              <h3 className="font-bold text-orange-900 mb-3">⚠️ What to Do</h3>
              <p className="text-orange-800 text-sm mb-3">
                Your account currently doesn't meet all eligibility requirements. Focus on
                improving the criteria where you're falling short.
              </p>
              <p className="text-orange-800 text-sm">
                Need help? Contact support or consult our FAQ for tips on improving your metrics.
              </p>
            </div>
          )}
        </>
      ) : (
        <div className="card text-center py-8">
          <p className="text-gray-600">No eligibility data available</p>
        </div>
      )}
    </div>
  );
}

function EligibilityCheck({
  label,
  status,
  requirement,
  current,
}: {
  label: string;
  status?: boolean;
  requirement: string;
  current: string;
}) {
  return (
    <div className={`card ${
      status ? 'border-l-4 border-green-500 bg-green-50' :
      status === false ? 'border-l-4 border-red-500 bg-red-50' :
      'border-l-4 border-gray-300 bg-gray-50'
    }`}>
      <div className="flex items-start justify-between">
        <div>
          <h4 className="font-semibold text-gray-800 flex items-center space-x-2">
            <span>
              {status ? '✓' : status === false ? '✗' : '○'}
            </span>
            <span>{label}</span>
          </h4>
          <p className="text-sm text-gray-600 mt-1">Requirement: {requirement}</p>
        </div>
      </div>
      <div className="mt-3 flex justify-between items-center">
        <span className="text-sm text-gray-600">Current:</span>
        <span className={`font-semibold ${
          status ? 'text-green-700' : status === false ? 'text-red-700' : 'text-gray-700'
        }`}>
          {current}
        </span>
      </div>
    </div>
  );
}
