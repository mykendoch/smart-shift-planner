'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { useSubmitSurvey, useMysurveys } from '@/lib/hooks';
import { SurveySubmission } from '@/lib/api';

export default function SurveysPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'submit' | 'history'>('submit');
  const [submitting, setSubmitting] = useState(false);

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
        <h1 className="text-3xl font-bold mb-2">Your Feedback Matters</h1>
        <p className="text-gray-600">
          Help us improve by sharing your experience with the smart shift system
        </p>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('submit')}
            className={`px-4 py-2 font-medium border-b-2 transition ${
              activeTab === 'submit'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            Submit Survey
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium border-b-2 transition ${
              activeTab === 'history'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            My Responses
          </button>
        </div>
      </div>

      {activeTab === 'submit' && (
        <SurveyForm setSubmitting={setSubmitting} submitting={submitting} />
      )}
      {activeTab === 'history' && <SurveyHistory />}
    </div>
  );
}

function SurveyForm({
  setSubmitting,
  submitting,
}: {
  setSubmitting: (val: boolean) => void;
  submitting: boolean;
}) {
  const { submit, loading, error } = useSubmitSurvey();
  const [formData, setFormData] = useState<SurveySubmission>({
    income_stress_level: 3,
    schedule_satisfaction: 3,
    app_usefulness: 3,
    decision_making_improvement: 3,
    shift_planning_ease: 3,
    earnings_stability: 3,
    feedback: '',
  });
  const [successMessage, setSuccessMessage] = useState('');

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'feedback' ? value : Number(value),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage('');

    const success = await submit(formData);
    if (success) {
      setSuccessMessage('✓ Survey submitted successfully!');
      setFormData({
        income_stress_level: 3,
        schedule_satisfaction: 3,
        app_usefulness: 3,
        decision_making_improvement: 3,
        shift_planning_ease: 3,
        earnings_stability: 3,
        feedback: '',
      });
      setTimeout(() => setSuccessMessage(''), 3000);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="card bg-red-50 border border-red-200">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {successMessage && (
        <div className="card bg-green-50 border border-green-200">
          <p className="text-green-800">{successMessage}</p>
        </div>
      )}

      {/* Survey Questions */}
      <div className="space-y-6">
        <SurveyQuestion
          label="How financially stressed do you feel about income?"
          description="1 = Very stressed, 5 = Not stressed at all"
          name="income_stress_level"
          value={formData.income_stress_level}
          onChange={handleChange}
        />

        <SurveyQuestion
          label="How satisfied are you with your schedule flexibility?"
          description="1 = Very unsatisfied, 5 = Very satisfied"
          name="schedule_satisfaction"
          value={formData.schedule_satisfaction}
          onChange={handleChange}
        />

        <SurveyQuestion
          label="How useful is the app for your shift planning?"
          description="1 = Not useful, 5 = Very useful"
          name="app_usefulness"
          value={formData.app_usefulness}
          onChange={handleChange}
        />

        <SurveyQuestion
          label="Has the system improved your decision-making?"
          description="1 = Not at all, 5 = Greatly improved"
          name="decision_making_improvement"
          value={formData.decision_making_improvement}
          onChange={handleChange}
        />

        <SurveyQuestion
          label="How easy is it to plan shifts ahead?"
          description="1 = Very difficult, 5 = Very easy"
          name="shift_planning_ease"
          value={formData.shift_planning_ease}
          onChange={handleChange}
        />

        <SurveyQuestion
          label="How stable is your earnings now?"
          description="1 = Highly unpredictable, 5 = Very predictable"
          name="earnings_stability"
          value={formData.earnings_stability}
          onChange={handleChange}
        />

        {/* Open feedback */}
        <div className="card">
          <label className="block text-gray-700 font-medium mb-2">
            Additional Feedback
          </label>
          <p className="text-sm text-gray-600 mb-3">
            Please share any other thoughts about your experience (optional)
          </p>
          <textarea
            name="feedback"
            value={formData.feedback}
            onChange={handleChange}
            placeholder="What's on your mind?"
            className="input-field h-24"
            disabled={loading}
          />
        </div>
      </div>

      <div className="card">
        <button
          type="submit"
          disabled={loading}
          className="btn-primary disabled:opacity-50"
        >
          {loading ? 'Submitting...' : 'Submit Survey'}
        </button>
        <p className="text-xs text-gray-500 mt-2">
          Your honest feedback helps us improve the system for everyone.
        </p>
      </div>
    </form>
  );
}

function SurveyQuestion({
  label,
  description,
  name,
  value,
  onChange,
}: {
  label: string;
  description: string;
  name: string;
  value: number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
}) {
  return (
    <div className="card">
      <label className="block text-gray-700 font-medium mb-2">{label}</label>
      <p className="text-sm text-gray-600 mb-3">{description}</p>
      <div className="flex space-x-2">
        {[1, 2, 3, 4, 5].map((num) => (
          <button
            key={num}
            type="button"
            onClick={() => onChange({ target: { name, value: num.toString() } } as any)}
            className={`w-12 h-12 rounded-lg font-semibold transition ${
              value === num
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            {num}
          </button>
        ))}
      </div>
    </div>
  );
}

function SurveyHistory() {
  const { surveys, loading, error } = useMysurveys();

  if (loading) {
    return (
      <div className="card text-center py-8">
        <p className="text-gray-600">Loading your surveys...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (surveys.length === 0) {
    return (
      <div className="card bg-blue-50 border border-blue-200">
        <p className="text-blue-800">
          You haven't submitted any surveys yet. Click on "Submit Survey" to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {surveys.map((survey, idx) => (
        <div key={idx} className="card">
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-semibold text-gray-800">
              Survey {surveys.length - idx}
            </h3>
            <span className="text-sm text-gray-500">
              {new Date(survey.response_date).toLocaleDateString()}
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
            <SurveyResponseRow
              label="Income Stress"
              value={survey.income_stress_level}
            />
            <SurveyResponseRow
              label="Schedule Satisfaction"
              value={survey.schedule_satisfaction}
            />
            <SurveyResponseRow label="App Usefulness" value={survey.app_usefulness} />
            <SurveyResponseRow
              label="Decision Making"
              value={survey.decision_making_improvement}
            />
            <SurveyResponseRow
              label="Shift Planning"
              value={survey.shift_planning_ease}
            />
            <SurveyResponseRow label="Earnings Stability" value={survey.earnings_stability} />
          </div>
          {survey.feedback && (
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <p className="text-sm font-medium text-gray-700 mb-1">Your feedback:</p>
              <p className="text-sm text-gray-600">{survey.feedback}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function SurveyResponseRow({ label, value }: { label: string; value: number }) {
  const getColor = (val: number) => {
    if (val <= 2) return 'text-red-600';
    if (val <= 3) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="flex justify-between items-center">
      <span className="text-gray-600">{label}:</span>
      <span className={`font-semibold ${getColor(value)}`}>{value}/5</span>
    </div>
  );
}
