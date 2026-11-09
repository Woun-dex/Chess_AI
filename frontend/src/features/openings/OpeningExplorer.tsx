import React, { useEffect, useMemo, useState } from 'react';
import { BookOpen, ChevronRight, Search, Target } from 'lucide-react';

interface Opening {
  eco: string;
  name: string;
  line: string;
}

const DATA_FILES = ['a', 'b', 'c', 'd', 'e'];

async function loadOpenings(): Promise<Opening[]> {
  const files = await Promise.all(DATA_FILES.map((letter) => fetch(`/openings/${letter}.tsv`)));
  if (files.some((response) => !response.ok)) throw new Error('Opening database is unavailable');
  const rows = await Promise.all(files.map((response) => response.text()));
  return rows.flatMap((content) =>
    content.split(/\r?\n/).slice(1).flatMap((row) => {
      const [eco, name, line] = row.split('\t');
      return eco && name && line ? [{ eco, name, line }] : [];
    }),
  );
}

interface OpeningExplorerProps {
  fullPage?: boolean;
}

export const OpeningExplorer: React.FC<OpeningExplorerProps> = ({ fullPage = false }) => {
  const [openings, setOpenings] = useState<Opening[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadOpenings().then(setOpenings).catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : 'Unable to load openings');
    }).finally(() => setLoading(false));
  }, []);

  const filteredOpenings = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return openings.slice(0, fullPage ? 30 : 4);
    return openings.filter((opening) =>
      `${opening.eco} ${opening.name} ${opening.line}`.toLowerCase().includes(normalized),
    ).slice(0, 40);
  }, [fullPage, openings, query]);

  return (
    <div className={`panel opening-panel ${fullPage ? 'opening-page-panel' : ''}`}>
      <div className="panel-title"><span><BookOpen size={16} /> OPENING EXPLORER</span><span className="move-count">{openings.length || '—'} lines</span></div>
      <p className="opening-intro">Search the Lichess ECO database by name, code, or move sequence.</p>
      <label className="opening-search"><Search size={14} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search Sicilian, C60, 1. e4..." /></label>
      {loading && <div className="empty-history">Loading opening tree…</div>}
      {error && <div className="empty-history">{error}</div>}
      {!loading && !error && <div className="opening-list">
        {filteredOpenings.map((opening) => (
          <button className="opening-row" type="button" key={`${opening.eco}-${opening.name}-${opening.line}`}>
            <span className="opening-eco">{opening.eco}</span>
            <span><strong>{opening.name}</strong><small>{opening.line}</small></span>
            <ChevronRight size={15} />
          </button>
        ))}
        {!filteredOpenings.length && <div className="empty-history">No matching opening lines.</div>}
      </div>}
      <button className="opening-practice" type="button"><Target size={14} /> Practice a repertoire line</button>
      <small className="opening-attribution">Opening data from lichess-org/chess-openings.</small>
    </div>
  );
};
