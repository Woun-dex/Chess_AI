import React, { useState } from 'react';
import { Send, Bot, Lightbulb, RefreshCw } from 'lucide-react';
import { TutorMessage } from '../types/chess';

interface TutorCoachProps {
  currentFen: string;
  lastMoveSan?: string;
  centipawns: number | null;
}

export const TutorCoach: React.FC<TutorCoachProps> = ({
  currentFen,
  lastMoveSan,
  centipawns,
}) => {
  const [messages, setMessages] = useState<TutorMessage[]>([
    {
      id: '1',
      sender: 'tutor',
      content:
        "Hello! I am your AI Grandmaster Tutor. I don't calculate raw moves — Stockfish handles the tactical precision. My job is to explain the strategic principles, pawn structures, and pedagogical concepts behind every position. Play a move on the board to begin!",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const userMsg: TutorMessage = {
      id: String(Date.now()),
      sender: 'student',
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    // Pedagogical response demo
    setTimeout(() => {
      const tutorReply: TutorMessage = {
        id: String(Date.now() + 1),
        sender: 'tutor',
        content: `Looking at this position (${lastMoveSan || 'opening'}), Stockfish evaluates it at ${
          centipawns !== null ? (centipawns / 100).toFixed(2) : '0.00'
        }. Current FEN: ${currentFen.slice(0, 24)}... Notice how control of the center (d4/e4/d5/e5) and piece mobility dictate the advantage here. What do you think your primary pawn break should be?`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, tutorReply]);
      setIsTyping(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-[520px] w-96 bg-slate-800 rounded-xl border border-slate-700 shadow-xl overflow-hidden">
      {/* Tutor Header */}
      <div className="bg-slate-850 px-4 py-3 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-md bg-indigo-600/30 text-indigo-400 border border-indigo-500/30">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Socratic Coach</h3>
            <p className="text-[11px] text-slate-400">Pedagogical explanations</p>
          </div>
        </div>
        <button
          title="Explain current position"
          className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-700 rounded transition"
        >
          <Lightbulb className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.sender === 'student' ? 'items-end' : 'items-start'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3.5 py-2.5 text-sm leading-relaxed ${
                msg.sender === 'student'
                  ? 'bg-indigo-600 text-white rounded-br-none'
                  : 'bg-slate-700/80 text-slate-100 border border-slate-600/50 rounded-bl-none shadow-sm'
              }`}
            >
              {msg.content}
            </div>
            <span className="text-[10px] text-slate-500 mt-1 px-1">
              {msg.timestamp}
            </span>
          </div>
        ))}
        {isTyping && (
          <div className="flex items-center space-x-1.5 text-slate-400 text-xs px-2 py-1">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            <span>Tutor is analyzing pedagogical concepts...</span>
          </div>
        )}
      </div>

      {/* Chat Input */}
      <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-700 bg-slate-850">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask why a move was played or what to do..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
};
