'use client';

import { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { useSubmitSurvey, useMysurveys } from '@/lib/hooks';
import { SurveySubmission } from '@/lib/api';
import { Toaster } from 'react-hot-toast';
import { FileText, AlertCircle, CheckCircle, Send, Clock, Smile } from 'lucide-react';
import { colors, fonts, spacing } from '@/lib/theme';
import { showToast } from '@/lib/notify';

export default function SurveysPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'submit' | 'history'>('submit');

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
            background: `linear-gradient(135deg, ${colors.success[600]} 0%, ${colors.success[700]} 100%)`,
            boxShadow: '0 10px 30px rgba(34, 197, 94, 0.3)',
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div
              className="w-14 h-14 rounded-lg flex items-center justify-center"
              style={{ background: 'rgba(255, 255, 255, 0.2)' }}
            >
              <FileText size={28} />
            </div>
            <div>
              <h1
                style={{
                  fontSize: fonts.sizes.h3,
                  fontWeight: fonts.weights.bold,
                }}
              >
                Your Feedback Matters
              </h1>
              <p
                style={{
                  fontSize: fonts.sizes.caption,
                  opacity: 0.9,
                  marginTop: spacing.xs,
                }}
              >
                Help us improve by sharing your experience
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div
          className="rounded-xl overflow-hidden border"
          style={{
            background: colors.neutral[0],
            borderColor: colors.neutral[200],
          }}
        >
          <div className="flex">
            {[
              { id: 'submit', label: 'Submit Survey', icon: Send },
              { id: 'history', label: 'My Responses', icon: Clock },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => {
                  setActiveTab(id as 'submit' | 'history');
                  showToast.info(`Viewing ${label}`);
                }}
                className="flex-1 flex items-center justify-center gap-3 px-6 py-4 border-b-2 transition-colors"
                style={{
                  background: activeTab === id ? colors.success[50] : colors.neutral[0],
                  borderColor: activeTab === id ? colors.success[500] : colors.neutral[200],
                  color: activeTab === id ? colors.success[600] : colors.neutral[600],
                  fontWeight: activeTab === id ? fonts.weights.semibold : fonts.weights.regular,
                }}
              >
                <Icon size={20} />
                <span style={{ fontSize: fonts.sizes.body }}>{label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div>
          {activeTab === 'submit' && <SurveyForm />}
          {activeTab === 'history' && <SurveyHistory />}
        </div>
      </div>
    </>
  );
}

function SurveyForm() {
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

    const loadingToast = showToast.loading('Submitting your survey...');
    const success = await submit(formData);

    if (success) {
      showToast.dismiss(loadingToast);
      showToast.success('Survey submitted successfully!');
      setSuccessMessage('✓ Thank you for your feedback!');
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
    } else {
      showToast.dismiss(loadingToast);
      showToast.error(error || 'Failed to submit survey');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
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
              Error Submitting Survey
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

      {successMessage && (
        <div
          className="rounded-xl p-6 flex items-start gap-4"
          style={{
            background: colors.success[50],
            border: `1px solid ${colors.success[200]}`,
          }}
        >
          <CheckCircle size={24} color={colors.success[600]} style={{ marginTop: spacing.xs }} />
          <div>
            <p
              style={{
                color: colors.success[900],
                fontWeight: fonts.weights.semibold,
              }}
            >
              {successMessage}
            </p>
          </div>
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
          emoji="💰"
        />

        <SurveyQuestion
          label="How satisfied are you with your schedule flexibility?"
          description="1 = Very unsatisfied, 5 = Very satisfied"
          name="schedule_satisfaction"
          value={formData.schedule_satisfaction}
          onChange={handleChange}
          emoji="📅"
        />

        <SurveyQuestion
          label="How useful is the app for your shift planning?"
          description="1 = Not useful, 5 = Very useful"
          name="app_usefulness"
          value={formData.app_usefulness}
          onChange={handleChange}
          emoji="📱"
        />

        <SurveyQuestion
          label="Has the system improved your decision-making?"
          description="1 = Not at all, 5 = Greatly improved"
          name="decision_making_improvement"
          value={formData.decision_making_improvement}
          onChange={handleChange}
          emoji="🧠"
        />

        <SurveyQuestion
          label="How easy is it to plan shifts ahead?"
          description="1 = Very difficult, 5 = Very easy"
          name="shift_planning_ease"
          value={formData.shift_planning_ease}
          onChange={handleChange}
          emoji="✅"
        />

        <SurveyQuestion
          label="How stable is your earnings now?"
          description="1 = Highly unpredictable, 5 = Very predictable"
          name="earnings_stability"
          value={formData.earnings_stability}
          onChange={handleChange}
          emoji="📈"
        />

        {/* Open feedback */}
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
              color: colors.neutral[900],
              fontWeight: fonts.weights.semibold,
              marginBottom: spacing.sm,
              fontSize: fonts.sizes.body,
            }}
          >
            Additional Feedback
          </label>
          <p
            style={{
              fontSize: fonts.sizes.caption,
              color: colors.neutral[600],
              marginBottom: spacing.md,
            }}
          >
            Please share any other thoughts about your experience (optional)
          </p>
          <textarea
            name="feedback"
            value={formData.feedback}
            onChange={handleChange}
            placeholder="What's on your mind?"
            disabled={loading}
            style={{
              width: '100%',
              minHeight: '120px',
              padding: spacing.md,
              border: `1px solid ${colors.neutral[200]}`,
              borderRadius: '8px',
              fontFamily: fonts.primary,
              fontSize: fonts.sizes.body,
              resize: 'vertical',
              opacity: loading ? 0.5 : 1,
            }}
          />
        </div>
      </div>

      {/* Submit Button */}
      <div
        className="rounded-xl p-6"
        style={{
          background: colors.neutral[0],
          border: `1px solid ${colors.neutral[200]}`,
        }}
      >
        <button
          type="submit"
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-semibold transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{
            background: colors.success[600],
            color: 'white',
            fontSize: fonts.sizes.button,
          }}
        >
          <Send size={20} />
          {loading ? 'Submitting...' : 'Submit Survey'}
        </button>
        <p
          style={{
            fontSize: fonts.sizes.caption,
            color: colors.neutral[500],
            marginTop: spacing.md,
            textAlign: 'center',
          }}
        >
          Your honest feedback helps us improve the system for everyone.
        </p>
      </div>
    </form>
  );
}

interface SurveyQuestionProps {
  label: string;
  description: string;
  name: string;
  value: number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  emoji: string;
}

function SurveyQuestion({
  label,
  description,
  name,
  value,
  onChange,
  emoji,
}: SurveyQuestionProps) {
  return (
    <div
      className="rounded-xl p-6"
      style={{
        background: colors.neutral[0],
        border: `1px solid ${colors.neutral[200]}`,
      }}
    >
      <div className="flex items-start gap-4 mb-4">
        <span style={{ fontSize: '28px' }}>{emoji}</span>
        <div className="flex-1">
          <label
            style={{
              display: 'block',
              color: colors.neutral[900],
              fontWeight: fonts.weights.semibold,
              marginBottom: spacing.xs,
              fontSize: fonts.sizes.body,
            }}
          >
            {label}
          </label>
          <p
            style={{
              fontSize: fonts.sizes.caption,
              color: colors.neutral[600],
            }}
          >
            {description}
          </p>
        </div>
      </div>

      <div className="flex justify-between gap-2">
        {[1, 2, 3, 4, 5].map((num) => {
          let bgColor = colors.neutral[100];
          let textColor = colors.neutral[700];

          if (value === num) {
            if (num <= 2) {
              bgColor = colors.error[500];
              textColor = 'white';
            } else if (num === 3) {
              bgColor = colors.warning[500];
              textColor = 'white';
            } else {
              bgColor = colors.success[500];
              textColor = 'white';
            }
          }

          return (
            <button
              key={num}
              type="button"
              onClick={() => onChange({ target: { name, value: num.toString() } } as any)}
              className="flex-1 py-3 rounded-lg font-semibold transition-all hover:scale-110"
              style={{
                background: bgColor,
                color: textColor,
              }}
            >
              {num}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function SurveyHistory() {
  const { surveys, loading, error } = useMysurveys();

  if (loading) {
    return (
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
              borderTopColor: colors.success[500],
              borderRightColor: colors.success[500],
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
          Loading your surveys...
        </p>
      </div>
    );
  }

  if (error) {
    return (
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
            Error Loading Surveys
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
    );
  }

  if (surveys.length === 0) {
    return (
      <div
        className="rounded-xl p-6 flex items-start gap-4"
        style={{
          background: colors.success[50],
          border: `1px solid ${colors.success[200]}`,
        }}
      >
        <Smile size={24} color={colors.success[600]} style={{ marginTop: spacing.xs }} />
        <div>
          <p
            style={{
              color: colors.success[900],
              fontWeight: fonts.weights.semibold,
            }}
          >
            No Surveys Yet
          </p>
          <p
            style={{
              color: colors.success[700],
              fontSize: fonts.sizes.caption,
              marginTop: spacing.xs,
            }}
          >
            You haven't submitted any surveys yet. Click on "Submit Survey" to get started!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {surveys.map((survey, idx) => (
        <div
          key={idx}
          className="rounded-xl p-6"
          style={{
            background: colors.neutral[0],
            border: `1px solid ${colors.neutral[200]}`,
          }}
        >
          <div className="flex justify-between items-start mb-6 pb-4" style={{ borderBottom: `1px solid ${colors.neutral[200]}` }}>
            <h3
              style={{
                fontWeight: fonts.weights.bold,
                color: colors.neutral[900],
                fontSize: fonts.sizes.body,
              }}
            >
              Survey {surveys.length - idx}
            </h3>
            <span
              style={{
                fontSize: fonts.sizes.caption,
                color: colors.neutral[500],
              }}
            >
              {new Date(survey.response_date).toLocaleDateString()}
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <SurveyResponseRow label="Income Stress" value={survey.income_stress_level} />
            <SurveyResponseRow label="Schedule Satisfaction" value={survey.schedule_satisfaction} />
            <SurveyResponseRow label="App Usefulness" value={survey.app_usefulness} />
            <SurveyResponseRow label="Decision Making" value={survey.decision_making_improvement} />
            <SurveyResponseRow label="Shift Planning" value={survey.shift_planning_ease} />
            <SurveyResponseRow label="Earnings Stability" value={survey.earnings_stability} />
          </div>

          {survey.feedback && (
            <div
              className="mt-4 p-4 rounded-lg"
              style={{
                background: colors.neutral[50],
                border: `1px solid ${colors.neutral[200]}`,
              }}
            >
              <p
                style={{
                  fontSize: fonts.sizes.caption,
                  fontWeight: fonts.weights.semibold,
                  color: colors.neutral[700],
                  marginBottom: spacing.xs,
                }}
              >
                Your feedback:
              </p>
              <p
                style={{
                  fontSize: fonts.sizes.body,
                  color: colors.neutral[600],
                  lineHeight: 1.6,
                }}
              >
                {survey.feedback}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

interface SurveyResponseRowProps {
  label: string;
  value: number;
}

function SurveyResponseRow({ label, value }: SurveyResponseRowProps) {
  let color = colors.error[600];
  if (value > 2 && value <= 3) {
    color = colors.warning[600];
  } else if (value > 3) {
    color = colors.success[600];
  }

  return (
    <div
      className="p-3 rounded-lg"
      style={{
        background: `${color}10`,
        border: `1px solid ${color}30`,
      }}
    >
      <p
        style={{
          fontSize: fonts.sizes.caption,
          color: colors.neutral[600],
          marginBottom: spacing.xs,
        }}
      >
        {label}
      </p>
      <p
        style={{
          fontWeight: fonts.weights.semibold,
          color: color,
          fontSize: fonts.sizes.body,
        }}
      >
        {value}/5
      </p>
    </div>
  );
}

