'use client';

import { useState, FormEvent } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await signIn('credentials', {
        username,
        password,
        redirect: false,
      });

      if (result?.error) {
        setError('Invalid username or password');
      } else if (result?.ok) {
        router.push('/admin');
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="w-full max-w-md">
        <div className="bg-zinc-800 rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-white mb-2 text-center">Admin Panel</h1>
          <p className="text-gray-400 text-center mb-8">Enter your credentials</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 bg-zinc-700 border border-zinc-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                placeholder="admin"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 bg-zinc-700 border border-zinc-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                placeholder="••••••••"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-900/20 border border-red-700 rounded-md p-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-600/50 disabled:cursor-not-allowed text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <p className="text-gray-400 text-xs text-center mt-6">
            Demo credentials: username: <span className="text-emerald-400">admin</span>, password:{' '}
            <span className="text-emerald-400">admin123</span>
          </p>
        </div>
      </div>
    </div>
  );
}
