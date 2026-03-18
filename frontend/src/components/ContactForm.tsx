import { useState, type FormEvent } from 'react';
import type { ReportData } from '../types/assessment';

// Mirror of server-side validation
const BLOCKED_DOMAINS = new Set([
  'mailinator.com', 'guerrillamail.com', 'temp-mail.org', 'throwaway.email',
  'yopmail.com', 'sharklasers.com', 'guerrillamailblock.com', 'grr.la',
  'guerrillamail.info', 'guerrillamail.biz', 'guerrillamail.de',
  'guerrillamail.net', 'guerrillamail.org', 'spam4.me', 'trashmail.com',
  'trashmail.me', 'trashmail.net', 'dispostable.com', 'fakeinbox.com',
  'mailnull.com', 'spamgourmet.com', 'maildrop.cc', 'discard.email',
]);

const SUSPICIOUS_LOCAL_PARTS = ['test', 'asdf', 'qwerty', 'aaa', 'abc', '123', 'fake', 'noemail'];

function validateEmail(email: string): string | null {
  const emailRegex = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) return 'Please enter a valid email address.';
  const [local, domain] = email.toLowerCase().split('@');
  if (BLOCKED_DOMAINS.has(domain)) return 'Please use a business or personal email address.';
  if (SUSPICIOUS_LOCAL_PARTS.includes(local)) return 'Please enter a real email address.';
  return null;
}

interface Props {
  report: ReportData;
  onSuccess: () => void;
}

export function ContactForm({ report, onSuccess }: Props) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function getCsrf(): string {
    return (document.querySelector('meta[name="csrf-token"]') as HTMLMetaElement)?.content ?? '';
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Please enter your name.');
      return;
    }
    const emailErr = validateEmail(email.trim());
    if (emailErr) {
      setError(emailErr);
      return;
    }

    setSubmitting(true);
    try {
      const resp = await fetch('/framework/api/save-lead/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrf(),
        },
        body: JSON.stringify({
          name: name.trim(),
          email: email.trim(),
          readiness_level: report.readiness_level,
          answers: {},
        }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        setError(data.error ?? 'Something went wrong. Please try again.');
        setSubmitting(false);
        return;
      }
      onSuccess();
    } catch {
      setError('Network error. Please check your connection and try again.');
      setSubmitting(false);
    }
  }

  return (
    <div className="contact-capture max-w-md mx-auto text-center">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Your report is ready</h3>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Enter your details to unlock your personalised AI readiness report.</p>
      <form onSubmit={handleSubmit} className="space-y-4 text-left">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="lead-name">
            Full name
          </label>
          <input
            id="lead-name"
            type="text"
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Jane Smith"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="lead-email">
            Business email
          </label>
          <input
            id="lead-email"
            type="email"
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="jane@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-indigo-600 text-white font-semibold py-3 rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-60"
        >
          {submitting ? 'Saving…' : 'Unlock My Report'}
        </button>
      </form>
      <p className="text-xs text-gray-400 dark:text-gray-500 mt-4">No spam. Used only to send your report and occasional insights.</p>
    </div>
  );
}
