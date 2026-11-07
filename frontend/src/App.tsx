import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity, ChevronDown, Flag, FlipHorizontal, Loader2, RotateCcw, Settings2,
  Shield, Sparkles, Swords, TimerReset, Trophy, X,
} from 'lucide-react';
import { ChessBoard } from './components/ChessBoard';
import { AuthPanel } from './components/AuthPanel';
import { checkBackendHealth, clearAccessToken, createGame, getAccessToken, getCurrentUser, makeMove, resignGame } from './services/api';
import { CreateGamePayload, GameResponse, GameSettings, MoveRecord, OpponentType, User } from './types/chess';

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
const formatClock = (seconds: number) => `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;

const defaultSettings: GameSettings = {
  playerColor: 'white',
  opponentType: 'random',
  botSkillLevel: 10,
  timeControlSeconds: 600,
};

function toMoves(game: GameResponse): MoveRecord[] {
  return game.moves.map((move, index) => ({
    ...move,
    fen_before: index === 0 ? START_FEN : game.moves[index - 1].fen_after,
    move_number: index + 1,
  }));
}

export const App: React.FC = () => {
  const [settings, setSettings] = useState(defaultSettings);
  const [game, setGame] = useState<GameResponse | null>(null);
  const [moves, setMoves] = useState<MoveRecord[]>([]);
  const [clocks, setClocks] = useState({ white: 600, black: 600 });
  const [orientation, setOrientation] = useState<'white' | 'black'>('white');
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  const playerColor = settings.playerColor === 'random' ? 'white' : settings.playerColor;
  const isHumanTurn = game && game.turn === playerColor;
  const lastMove = moves[moves.length - 1];
  const gameOver = game?.status !== 'in_progress';

  useEffect(() => {
    checkBackendHealth().then(() => setBackendStatus('online')).catch(() => setBackendStatus('offline'));
    if (!getAccessToken()) {
      setAuthLoading(false);
      return;
    }
    getCurrentUser()
      .then(setUser)
      .catch(() => clearAccessToken())
      .finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => {
    if (!game || gameOver || !settings.timeControlSeconds) return;
    const interval = window.setInterval(() => {
      setClocks((current) => ({ ...current, [game.turn]: Math.max(0, current[game.turn] - 1) }));
    }, 1000);
    return () => window.clearInterval(interval);
  }, [game, gameOver, settings.timeControlSeconds]);

  const startGame = useCallback(async (nextSettings = settings) => {
    if (!user) return;
    setBusy(true);
    setError(null);
    const selectedColor = nextSettings.playerColor === 'random'
      ? (Math.random() > 0.5 ? 'white' : 'black')
      : nextSettings.playerColor;
    const payload: CreateGamePayload = {
      white_player_id: selectedColor === 'white' ? user.id : 'bot',
      black_player_id: selectedColor === 'black' ? user.id : 'bot',
      opponent_type: nextSettings.opponentType,
      bot_skill_level: nextSettings.botSkillLevel,
      time_control_seconds: nextSettings.timeControlSeconds,
    };
    try {
      const created = await createGame(payload);
      setSettings({ ...nextSettings, playerColor: selectedColor });
      setGame(created);
      setMoves(toMoves(created));
      setClocks({ white: nextSettings.timeControlSeconds ?? 600, black: nextSettings.timeControlSeconds ?? 600 });
      setOrientation(selectedColor);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to start game');
    } finally {
      setBusy(false);
    }
  }, [settings, user]);

  useEffect(() => { if (user) void startGame(); }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleMove = async (uci: string) => {
    if (!user || !game || busy || gameOver || !isHumanTurn) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await makeMove(game.game_id, {
        move: uci,
        player_id: user.id,
        expected_version: game.version,
      });
      setGame(updated);
      setMoves(toMoves(updated));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Move rejected');
    } finally {
      setBusy(false);
    }
  };

  const handleResign = async () => {
    if (!user || !game || gameOver || busy) return;
    setBusy(true);
    try {
      const updated = await resignGame(game.game_id, user.id);
      setGame(updated);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to resign');
    } finally {
      setBusy(false);
    }
  };

  const statusLabel = gameOver ? (game?.winner === 'draw' ? 'Draw' : `${game?.winner === playerColor ? 'Victory' : 'Game over'}`) : (isHumanTurn ? 'Your turn' : 'Opponent thinking');
  const movePairs = useMemo(() => Array.from({ length: Math.ceil(moves.length / 2) }, (_, index) => ({
    number: index + 1,
    white: moves[index * 2],
    black: moves[index * 2 + 1],
  })), [moves]);

  if (authLoading) {
    return <main className="auth-page"><Loader2 className="spin" size={22} /></main>;
  }
  if (!user) {
    return <AuthPanel onAuthenticated={setUser} />;
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><Swords size={19} /></div><div><strong>Endgame</strong><span>Chess studio</span></div></div>
        <div className="topbar-status"><span className={`status-dot ${backendStatus}`} /> Backend {backendStatus}<span className="topbar-divider" /> <span className="live-label"><Activity size={13} /> {user?.username}<button className="logout-button" onClick={() => { clearAccessToken(); setUser(null); setGame(null); }}>Sign out</button></span></div>
      </header>

      <main className="game-layout">
        <section className="game-column">
          <div className="page-heading"><div><p className="eyebrow">PLAY ARENA</p><h1>Make your move.</h1><p className="subheading">A focused board for thoughtful games.</p></div><button className="icon-button" title="Game settings"><Settings2 size={18} /></button></div>
          <div className="player-strip"><div className="player"><span className="avatar avatar-dark">♟</span><div><strong>Endgame AI</strong><span>{settings.opponentType === 'random' ? 'Casual opponent' : `${settings.opponentType} · level ${settings.botSkillLevel}`}</span></div></div><span className="turn-status">{statusLabel}</span></div>
          <div className="board-wrap">
            <div className="clock-row"><div className={`clock ${game?.turn === 'black' ? 'clock-active' : ''}`}><span>BLACK</span><strong>{formatClock(clocks.black)}</strong></div><span className="round-label">GAME {game ? game.version + 1 : '—'}</span></div>
            {game ? <ChessBoard fen={game.fen} orientation={orientation} disabled={busy || gameOver || !isHumanTurn} lastMove={lastMove?.uci} onMove={handleMove} /> : <div className="board-loading"><Loader2 className="spin" /> Preparing board</div>}
            <div className="clock-row clock-row-bottom"><div className={`clock ${game?.turn === 'white' ? 'clock-active' : ''}`}><span>YOU · {playerColor.toUpperCase()}</span><strong>{formatClock(clocks.white)}</strong></div><span className="connection-note"><Shield size={13} /> moves sync automatically</span></div>
          </div>
          <div className="board-controls"><button onClick={() => setOrientation((value) => value === 'white' ? 'black' : 'white')}><FlipHorizontal size={16} /> Flip board</button><button onClick={handleResign} disabled={!game || gameOver || busy}><Flag size={16} /> Resign</button><button onClick={() => void startGame()} disabled={busy}><RotateCcw size={16} /> New game</button></div>
        </section>

        <aside className="side-column">
          <div className="panel game-setup"><div className="panel-title"><span><Sparkles size={16} /> GAME SETUP</span><span className={`mini-status ${backendStatus}`} /></div><label>Opponent<select value={settings.opponentType} onChange={(event) => setSettings({ ...settings, opponentType: event.target.value as OpponentType })}><option value="random">Random bot</option><option value="stockfish">Stockfish engine</option><option value="human">Local human</option></select><ChevronDown className="select-chevron" size={15} /></label><label>Play as<select value={settings.playerColor} onChange={(event) => setSettings({ ...settings, playerColor: event.target.value as GameSettings['playerColor'] })}><option value="white">White</option><option value="black">Black</option><option value="random">Random side</option></select><ChevronDown className="select-chevron" size={15} /></label><label>Time control<select value={settings.timeControlSeconds ?? 0} onChange={(event) => setSettings({ ...settings, timeControlSeconds: Number(event.target.value) || null })}><option value={600}>10 min</option><option value={300}>5 min</option><option value={60}>1 min</option><option value={0}>Unlimited</option></select><ChevronDown className="select-chevron" size={15} /></label><button className="primary-button" onClick={() => void startGame()} disabled={busy}><Trophy size={16} /> Start new game</button></div>
          <div className="panel history-panel"><div className="panel-title"><span><TimerReset size={16} /> MOVE HISTORY</span><span className="move-count">{moves.length} moves</span></div><div className="history-list">{movePairs.length === 0 && <div className="empty-history">Your game moves will appear here.</div>}{movePairs.map((pair) => <div className="history-row" key={pair.number}><span className="move-number">{pair.number}.</span><span className={pair.white?.color === playerColor ? 'your-move' : ''}>{pair.white?.san ?? '—'}</span><span className={pair.black?.color === playerColor ? 'your-move' : ''}>{pair.black?.san ?? '—'}</span></div>)}</div></div>
          <div className="panel note-panel"><div className="note-icon"><Sparkles size={16} /></div><div><strong>Play the position</strong><p>Choose a piece, then choose its destination. Legal moves are checked by the backend.</p></div></div>
        </aside>
      </main>
      {error && <div className="error-toast"><X size={16} /><span>{error}</span><button onClick={() => setError(null)}>Dismiss</button></div>}
    </div>
  );
};
