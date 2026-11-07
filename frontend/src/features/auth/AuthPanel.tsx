import React, { FormEvent, useState } from 'react';
import { Loader2, LogIn, UserPlus } from 'lucide-react';
import { getCurrentUser, login, register, saveAccessToken } from '../../services/api';
import { User } from '../../types/chess';

interface AuthPanelProps {
  onAuthenticated: (user: User) => void;
}

export const AuthPanel: React.FC<AuthPanelProps> = ({ onAuthenticated }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === 'register') await register(email, username, password);
      const token = await login(email, password);
      saveAccessToken(token.access_token);
      onAuthenticated(await getCurrentUser());
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Authentication failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="auth-page">
      <form className="auth-panel" onSubmit={submit}>
        <div className="brand auth-brand"><div className="brand-mark">♟</div><div><strong>Endgame</strong><span>Chess studio</span></div></div>
        <p className="eyebrow">{mode === 'login' ? 'WELCOME BACK' : 'JOIN THE STUDIO'}</p>
        <h1>{mode === 'login' ? 'Sign in to play.' : 'Create your account.'}</h1>
        <p className="subheading">Your games and player profile stay connected to your account.</p>
        {mode === 'register' && <label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} minLength={3} maxLength={50} pattern="[A-Za-z0-9_]+" required /></label>}
        <label>Email<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required /></label>
        {error && <p className="auth-error">{error}</p>}
        <button className="primary-button" type="submit" disabled={busy}>{busy ? <Loader2 className="spin" size={16} /> : mode === 'login' ? <LogIn size={16} /> : <UserPlus size={16} />}{mode === 'login' ? 'Sign in' : 'Create account'}</button>
        <button className="auth-switch" type="button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(null); }}>{mode === 'login' ? 'Need an account? Create one' : 'Already have an account? Sign in'}</button>
      </form>
    </main>
  );
};
