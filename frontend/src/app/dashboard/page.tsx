'use client';

import { useAuthStore } from '@/lib/store';

export default function DashboardPage() {
  const { user } = useAuthStore();

  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <div className="card bg-gradient-to-r from-blue-500 to-green-500 text-white">
        <h1 className="text-4xl font-bold mb-2">
          Welcome, {user?.full_name}! 👋
        </h1>
        <p className="text-lg opacity-90">
          {user?.role === 'driver'
            ? 'Monitor your earnings, income stability, and access guaranteed shift information'
            : 'Manage workers, monitor system performance, and analyze survey feedback'}
        </p>
      </div>

      {user?.role === 'driver' ? (
        <DriverDashboard />
      ) : (
        <AdminDashboard />
      )}
    </div>
  );
}

function DriverDashboard() {
  const stats = [
    {
      label: 'Quick Links',
      items: [
        { name: 'View Income Insights', href: '/dashboard/volatility', icon: '📊' },
        { name: 'Submit Feedback', href: '/dashboard/surveys', icon: '📝' },
        { name: 'Check Eligibility', href: '/dashboard/eligibility', icon: '✅' },
      ],
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {stats.map((group) => (
        <div key={group.label} className="col-span-full">
          <h2 className="text-xl font-bold mb-4">{group.label}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {group.items.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="card hover:shadow-lg transition cursor-pointer"
              >
                <div className="text-4xl mb-2">{item.icon}</div>
                <h3 className="font-semibold text-gray-800">{item.name}</h3>
              </a>
            ))}
          </div>
        </div>
      ))}

      {/* Information cards */}
      <div className="col-span-full">
        <h2 className="text-xl font-bold mb-4">System Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <InfoCard
            title="Income Guarantee"
            description="Transparent pricing with guaranteed earnings protection"
          />
          <InfoCard
            title="Income Insights"
            description="See how shifts stabilize your earnings volatility"
          />
          <InfoCard
            title="Feedback & Impact"
            description="Share your experience and influence system improvements"
          />
          <InfoCard
            title="Eligibility Status"
            description="Stay informed about your shift guarantee eligibility"
          />
        </div>
      </div>
    </div>
  );
}

function AdminDashboard() {
  const stats = [
    {
      label: 'Monitoring & Management',
      items: [
        { name: 'System Analytics', href: '/dashboard/analytics', icon: '📈' },
        { name: 'Model Performance', href: '/dashboard/accuracy', icon: '🎯' },
        { name: 'Survey Reports', href: '/dashboard/surveys', icon: '📊' },
        { name: 'Manage Workers', href: '/dashboard/workers', icon: '👥' },
      ],
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      {stats.map((group) => (
        <div key={group.label} className="col-span-full">
          <h2 className="text-xl font-bold mb-4">{group.label}</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {group.items.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="card hover:shadow-lg transition cursor-pointer"
              >
                <div className="text-4xl mb-2">{item.icon}</div>
                <h3 className="font-semibold text-gray-800 text-sm">{item.name}</h3>
              </a>
            ))}
          </div>
        </div>
      ))}

      {/* Key metrics */}
      <div className="col-span-full mt-6">
        <h2 className="text-xl font-bold mb-4">System Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Active Workers" value="—" subtitle="View on Analytics" />
          <MetricCard
            label="Model Accuracy"
            value="—"
            subtitle="View on Performance"
          />
          <MetricCard label="Surveys Submitted" value="—" subtitle="View Reports" />
        </div>
      </div>
    </div>
  );
}

function InfoCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="card">
      <h3 className="font-semibold text-gray-800 mb-1">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function MetricCard({
  label,
  value,
  subtitle,
}: {
  label: string;
  value: string;
  subtitle: string;
}) {
  return (
    <div className="card">
      <p className="text-gray-600 text-sm">{label}</p>
      <p className="text-3xl font-bold text-gray-800 my-2">{value}</p>
      <p className="text-xs text-blue-600">{subtitle}</p>
    </div>
  );
}
