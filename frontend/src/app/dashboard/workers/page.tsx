'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';

export default function WorkersPage() {
  const { user } = useAuthStore();
  const [selectedWorker, setSelectedWorker] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');

  if (!user || user.role !== 'admin') {
    return (
      <div className="card bg-yellow-50 border border-yellow-200">
        <p className="text-yellow-800">This page is only available to administrators.</p>
      </div>
    );
  }

  // Mock data
  const workers = [
    {
      id: '1',
      name: 'John Smith',
      email: 'john@example.com',
      status: 'active',
      eligible: true,
      hoursWeek: 28,
      rating: 4.8,
      acceptanceRate: 0.97,
    },
    {
      id: '2',
      name: 'Jane Doe',
      email: 'jane@example.com',
      status: 'active',
      eligible: true,
      hoursWeek: 32,
      rating: 4.6,
      acceptanceRate: 0.95,
    },
    {
      id: '3',
      name: 'Mike Johnson',
      email: 'mike@example.com',
      status: 'suspended',
      eligible: false,
      hoursWeek: 15,
      rating: 3.2,
      acceptanceRate: 0.88,
    },
  ];

  const filteredWorkers = workers.filter((w) => {
    if (filter === 'eligible') return w.eligible;
    if (filter === 'suspended') return w.status === 'suspended';
    return true;
  });

  return (
    <div className="space-y-8">
      <div className="card">
        <h1 className="text-3xl font-bold mb-2">Worker Management</h1>
        <p className="text-gray-600">
          Monitor worker performance and manage eligibility status
        </p>
      </div>

      {/* Filters */}
      <div className="card">
        <label className="block text-gray-700 font-medium mb-2">Filter by Status:</label>
        <div className="flex space-x-4">
          {[
            { value: 'all', label: 'All Workers' },
            { value: 'eligible', label: 'Eligible Only' },
            { value: 'suspended', label: 'Suspended' },
          ].map((f) => (
            <button
              key={f.value}
              onClick={() => setFilter(f.value)}
              className={`px-4 py-2 rounded-lg transition ${
                filter === f.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Workers List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredWorkers.map((worker) => (
          <div
            key={worker.id}
            className="card cursor-pointer hover:shadow-lg transition"
            onClick={() => setSelectedWorker(worker.id)}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-bold text-gray-800">{worker.name}</h3>
                <p className="text-sm text-gray-600">{worker.email}</p>
              </div>
              <div className={`px-3 py-1 rounded text-xs font-semibold ${
                worker.eligible
                  ? 'bg-green-100 text-green-700'
                  : 'bg-red-100 text-red-700'
              }`}>
                {worker.status}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm">
              <StatRow label="Hours/Week" value={`${worker.hoursWeek}h`} />
              <StatRow label="Rating" value={`${worker.rating}/5`} />
              <StatRow label="Acceptance" value={`${(worker.acceptanceRate * 100).toFixed(0)}%`} />
              <StatRow label="Eligible" value={worker.eligible ? '✓ Yes' : '✗ No'} />
            </div>

            <button className="mt-4 w-full btn-secondary text-sm">
              View Details
            </button>
          </div>
        ))}
      </div>

      {/* Worker Detail Panel */}
      {selectedWorker && (
        <div className="card bg-blue-50 border-2 border-blue-300">
          <h2 className="text-xl font-bold text-gray-800 mb-4">
            Worker Actions for {workers.find((w) => w.id === selectedWorker)?.name}
          </h2>
          <div className="space-y-3">
            <button className="w-full btn-secondary">View Volatility Analysis</button>
            <button className="w-full btn-secondary">View Survey Responses</button>
            <button className="w-full btn-secondary">View Shift History</button>
            <button className="w-full btn-danger">
              Suspend Eligibility
            </button>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <SummaryCard label="Total Workers" value={workers.length} />
        <SummaryCard
          label="Eligible"
          value={workers.filter((w) => w.eligible).length}
        />
        <SummaryCard
          label="Suspended"
          value={workers.filter((w) => w.status === 'suspended').length}
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

function SummaryCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="card">
      <p className="text-gray-600 text-sm">{label}</p>
      <p className="text-3xl font-bold text-gray-800 mt-2">{value}</p>
    </div>
  );
}
