import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  getCurrentTournament,
  calculateRecommendations,
  calculateAdvancedRecommendations,
  getUsedGolfers,
  getDefaultWeights,
  getAdvancedDefaultWeights,
} from './api';
import TournamentInfo from './components/TournamentInfo';
import ModelTabs from './components/ModelTabs';
import WeightSliders from './components/WeightSliders';
import AdvancedWeightSliders from './components/AdvancedWeightSliders';
import UsedGolfersPanel from './components/UsedGolfersPanel';
import RecommendationsTable from './components/RecommendationsTable';
import CookieConsent from './components/CookieConsent';

function App() {
  const [tournament, setTournament] = useState(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [showUsedGolfers, setShowUsedGolfers] = useState(false);

  // Basic model weights
  const [weights, setWeights] = useState({
    skill: 0.35,
    form: 0.10,
    course: 0.15,
    field: 0.10,
    odds: 0.30,
  });
  const [defaultWeights, setDefaultWeights] = useState(null);

  // Advanced model weights
  const [advancedWeights, setAdvancedWeights] = useState({
    sg_ott: 0.10,
    sg_app: 0.12,
    sg_arg: 0.08,
    sg_putt: 0.10,
    driving_dist: 0.05,
    fairways_pct: 0.07,
    gir_pct: 0.08,
    scrambling_pct: 0.10,
    putting_avg: 0.05,
    birdie_pct: 0.04,
    par5_scoring: 0.03,
    bogey_avoid_pct: 0.03,
    course_fit: 0.08,
    odds: 0.07,
  });
  const [defaultAdvancedWeights, setDefaultAdvancedWeights] = useState(null);

  const [usedGolfers, setUsedGolfers] = useState([]);
  const [recommendations, setRecommendations] = useState(null);
  const [seasonRec, setSeasonRec] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultsRef = useRef(null);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [tournamentRes, usedRes, weightsRes, advancedWeightsRes] = await Promise.all([
          getCurrentTournament(),
          getUsedGolfers(),
          getDefaultWeights(),
          getAdvancedDefaultWeights(),
        ]);
        setTournament(tournamentRes.data);
        setUsedGolfers(usedRes.data.map((g) => g.name));
        setWeights(weightsRes.data);
        setDefaultWeights(weightsRes.data);
        setAdvancedWeights(advancedWeightsRes.data);
        setDefaultAdvancedWeights(advancedWeightsRes.data);
      } catch (err) {
        setError('Failed to load initial data: ' + err.message);
      }
    };
    loadInitialData();
  }, []);

  // Run model
  const runModel = async () => {
    setLoading(true);
    setError(null);
    try {
      let res;
      if (activeTab === 'advanced') {
        res = await calculateAdvancedRecommendations(advancedWeights, usedGolfers);
      } else {
        res = await calculateRecommendations(weights, usedGolfers);
      }
      setRecommendations(res.data.golfers);
      setSeasonRec(res.data.season_recommendation);
      setTournament((prev) => ({
        ...prev,
        name: res.data.tournament_name,
        start_date: res.data.tournament_date,
        purse: res.data.purse,
        field_size: res.data.field_size,
        field_strength: res.data.field_strength,
      }));
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError('Failed to run model: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const resetWeights = () => {
    if (defaultWeights) setWeights({ ...defaultWeights });
  };

  const resetAdvancedWeights = () => {
    if (defaultAdvancedWeights) setAdvancedWeights({ ...defaultAdvancedWeights });
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-800 via-green-700 to-green-600 text-white py-3 px-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-90 transition">
            <svg viewBox="0 0 50 50" className="w-9 h-9">
              <circle cx="25" cy="25" r="20" fill="white" stroke="#166534" strokeWidth="2" />
              <circle cx="20" cy="20" r="1.5" fill="#9CA3AF" />
              <circle cx="28" cy="18" r="1.5" fill="#9CA3AF" />
              <circle cx="24" cy="26" r="1.5" fill="#9CA3AF" />
              <circle cx="32" cy="24" r="1.5" fill="#9CA3AF" />
              <circle cx="18" cy="28" r="1.5" fill="#9CA3AF" />
              <rect x="17" y="32" width="4" height="8" fill="#10B981" />
              <rect x="23" y="28" width="4" height="12" fill="#059669" />
              <rect x="29" y="30" width="4" height="10" fill="#047857" />
            </svg>
            <div>
              <h1 className="text-xl font-bold tracking-tight leading-tight">Data Caddie</h1>
              <p className="text-green-200 text-xs leading-tight">Golf Pick 'Em</p>
            </div>
          </Link>

          <div className="flex items-center gap-4">
            {/* Used Golfers Button */}
            <button
              onClick={() => setShowUsedGolfers(true)}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-500 px-3 py-1.5 text-sm font-medium transition"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              Used Golfers
              {usedGolfers.length > 0 && (
                <span className="bg-white text-green-700 text-xs font-bold px-1.5 py-0.5 rounded-full">
                  {usedGolfers.length}
                </span>
              )}
            </button>

            <Link
              to="/"
              className="text-sm text-green-200 hover:text-white transition flex items-center gap-1"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto px-4 py-4 w-full">
        {/* Error display */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 mb-3 text-sm">
            {error}
            <button onClick={() => setError(null)} className="float-right font-bold">&times;</button>
          </div>
        )}

        {/* Tournament Info - Compact */}
        <TournamentInfo tournament={tournament} />

        {/* Model Selection + Weights + Run Button in compact layout */}
        <div className="mt-4 grid grid-cols-1 lg:grid-cols-4 gap-4">
          {/* Model Tabs - Vertical on large screens */}
          <div className="lg:col-span-1">
            <ModelTabs activeTab={activeTab} onTabChange={setActiveTab} />
          </div>

          {/* Weights + Run Button */}
          <div className="lg:col-span-3">
            {activeTab === 'basic' ? (
              <WeightSliders weights={weights} onChange={setWeights} onReset={resetWeights} />
            ) : (
              <AdvancedWeightSliders weights={advancedWeights} onChange={setAdvancedWeights} onReset={resetAdvancedWeights} />
            )}

            {/* Run Model Button - Inline */}
            <div className="mt-4">
              <button
                onClick={runModel}
                disabled={loading || !tournament}
                className={`w-full py-3 text-lg font-semibold transition ${
                  loading || !tournament
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white shadow-lg'
                }`}
              >
                {loading ? 'Running Model...' : 'Run Model'}
              </button>
              {/* Disclaimer */}
              <p className="text-xs text-gray-400 text-center mt-2">
                For informational and entertainment purposes only. Not gambling advice.
              </p>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div ref={resultsRef}>
          {recommendations && (
            <RecommendationsTable
              recommendations={recommendations}
              seasonRec={seasonRec}
              isAdvancedModel={activeTab === 'advanced'}
            />
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-4 px-4 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-2">
          <p className="text-sm">© 2025 Data Caddie. All rights reserved.</p>
          <div className="flex gap-6 text-sm">
            <Link to="/privacy" className="hover:text-white transition">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition">Terms of Service</Link>
          </div>
        </div>
      </footer>

      {/* Used Golfers Panel */}
      <UsedGolfersPanel
        isOpen={showUsedGolfers}
        onClose={() => setShowUsedGolfers(false)}
        usedGolfers={usedGolfers}
        onChange={setUsedGolfers}
      />

      {/* Cookie Consent Banner */}
      <CookieConsent />
    </div>
  );
}

export default App;
