import { useState } from 'react';

function RecommendationsTable({ recommendations, seasonRec, isAdvancedModel = false }) {
  const [sortField, setSortField] = useState('rank');
  const [sortDir, setSortDir] = useState('asc');
  const [showAll, setShowAll] = useState(false);
  const [showHelpModal, setShowHelpModal] = useState(false);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir(field === 'ev' || field === 'skill_score' || field === 'composite_score' ? 'desc' : 'asc');
    }
  };

  const sortedRecs = [...recommendations].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    // Handle nulls
    if (aVal === null || aVal === undefined) aVal = sortDir === 'asc' ? Infinity : -Infinity;
    if (bVal === null || bVal === undefined) bVal = sortDir === 'asc' ? Infinity : -Infinity;

    if (sortDir === 'asc') {
      return aVal > bVal ? 1 : -1;
    }
    return aVal < bVal ? 1 : -1;
  });

  const displayRecs = showAll ? sortedRecs : sortedRecs.slice(0, 20);

  // Calculate category averages for advanced model
  const getCategoryScore = (rec, category) => {
    if (!isAdvancedModel) return null;

    switch (category) {
      case 'sg': {
        const scores = [rec.sg_ott_score, rec.sg_app_score, rec.sg_arg_score, rec.sg_putt_score].filter(s => s != null);
        return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      }
      case 'ballStriking': {
        const scores = [rec.driving_dist_score, rec.fairways_pct_score, rec.gir_pct_score].filter(s => s != null);
        return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      }
      case 'shortGame': {
        const scores = [rec.scrambling_pct_score, rec.putting_avg_score].filter(s => s != null);
        return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      }
      case 'scoring': {
        const scores = [rec.birdie_pct_score, rec.par5_scoring_score, rec.bogey_avoid_pct_score].filter(s => s != null);
        return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      }
      case 'context': {
        const scores = [rec.course_fit_score, rec.odds_score].filter(s => s != null);
        return scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null;
      }
      default:
        return null;
    }
  };

  const getScoreColor = (score) => {
    if (score === null || score === undefined) return 'text-gray-400';
    if (score >= 75) return 'text-green-600 font-semibold';
    if (score >= 60) return 'text-green-500';
    if (score >= 45) return 'text-gray-600';
    if (score >= 30) return 'text-orange-500';
    return 'text-red-500';
  };

  const exportCsv = () => {
    let headers, rows;

    if (isAdvancedModel) {
      headers = [
        'Rank', 'Golfer', 'EV ($)', 'Composite',
        'SG', 'Ball Striking', 'Short Game', 'Scoring', 'Context',
        'Odds', 'Win %', 'Cut %', 'Action', 'Pick Rank',
      ];
      rows = recommendations.map((r) => [
        r.rank,
        r.player_name,
        r.ev,
        r.composite_score?.toFixed(1),
        getCategoryScore(r, 'sg')?.toFixed(1) || '',
        getCategoryScore(r, 'ballStriking')?.toFixed(1) || '',
        getCategoryScore(r, 'shortGame')?.toFixed(1) || '',
        getCategoryScore(r, 'scoring')?.toFixed(1) || '',
        getCategoryScore(r, 'context')?.toFixed(1) || '',
        r.odds || '',
        r.win_prob?.toFixed(2),
        r.make_cut_prob?.toFixed(0),
        r.season_action,
        r.pick_rank || '',
      ]);
    } else {
      headers = [
        'Rank', 'Golfer', 'EV ($)', 'Skill', 'SG Total', 'OWGR',
        'Form', 'Course', 'Odds', 'Win %', 'Cut %', 'Action', 'Pick Rank',
      ];
      rows = recommendations.map((r) => [
        r.rank,
        r.player_name,
        r.ev,
        r.skill_score?.toFixed(1),
        r.sg_total?.toFixed(3) || '',
        r.owgr_rank || '',
        r.form_label,
        r.course_label,
        r.odds || '',
        r.win_prob?.toFixed(2),
        r.make_cut_prob?.toFixed(0),
        r.season_action,
        r.pick_rank || '',
      ]);
    }

    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'golf_recommendations.csv';
    a.click();
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <span className="text-gray-300 ml-1">↕</span>;
    return <span className="ml-1">{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  const getFormColor = (form) => {
    switch (form) {
      case 'Hot':
        return 'text-green-600 font-semibold';
      case 'Good':
        return 'text-green-500';
      case 'Average':
        return 'text-gray-600';
      case 'Cold':
        return 'text-orange-500';
      case 'Poor':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };

  const getCourseColor = (course) => {
    switch (course) {
      case 'Strong':
        return 'text-green-600 font-semibold';
      case 'Good':
        return 'text-green-500';
      case 'Average':
        return 'text-gray-600';
      case 'Weak':
        return 'text-orange-500';
      case 'Poor':
        return 'text-red-500';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="mt-8">
      {/* Help Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white shadow-xl max-w-lg mx-4 p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900">SAVE/USE Strategy Explained</h3>
              <button
                onClick={() => setShowHelpModal(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >
                &times;
              </button>
            </div>
            <div className="text-sm text-gray-700 space-y-3">
              <p>
                The SAVE/USE system helps you optimize golfer picks across the entire season by
                reserving elite players for premium tournaments.
              </p>
              <div className="bg-gray-50 p-3">
                <p className="font-semibold mb-2">Tournament Tiers:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  <li><span className="font-medium">Tier 1 (Majors):</span> Masters, PGA, US Open, The Open</li>
                  <li><span className="font-medium">Tier 2:</span> The Players Championship</li>
                  <li><span className="font-medium">Tier 3:</span> Signature Events ($15M+ purse)</li>
                  <li><span className="font-medium">Tier 4:</span> Regular events</li>
                </ul>
              </div>
              <div className="bg-green-50 p-3">
                <p className="font-semibold mb-2">How it works:</p>
                <ul className="list-disc list-inside space-y-1 text-gray-600">
                  <li>Top OWGR players are reserved for the biggest tournaments</li>
                  <li>#1-3 ranked golfers → Reserved for Majors</li>
                  <li>#4 ranked → Reserved for The Players</li>
                  <li>#5-13 ranked → Reserved for Signature Events</li>
                  <li>Players not in current field are still counted globally</li>
                </ul>
              </div>
              <div className="bg-yellow-50 p-3">
                <p className="font-semibold mb-1">SAVE</p>
                <p className="text-gray-600">Don't use this golfer now—they're reserved for a bigger tournament later.</p>
              </div>
              <div className="bg-green-50 p-3">
                <p className="font-semibold mb-1">USE</p>
                <p className="text-gray-600">This golfer is available to pick this week without sacrificing future value.</p>
              </div>
            </div>
            <button
              onClick={() => setShowHelpModal(false)}
              className="mt-4 w-full bg-green-600 text-white py-2 hover:bg-green-700"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* Recommended Pick Banner */}
      {seasonRec && (
        <div className="bg-green-100 p-4 mb-6 flex items-center justify-between">
          <div>
            <span className="text-green-800 font-medium">Recommended Pick:</span>
            <span className="text-green-900 font-bold text-lg ml-2">
              {seasonRec.recommended_pick}
            </span>
            <span className="text-green-700 ml-2">
              (EV: {formatCurrency(seasonRec.recommended_ev)})
            </span>
          </div>
          <button
            onClick={() => setShowHelpModal(true)}
            className="bg-white text-green-700 px-3 py-1.5 text-sm font-medium hover:bg-green-50 border border-green-300"
          >
            How does SAVE/USE work?
          </button>
        </div>
      )}

      {/* Table Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          {isAdvancedModel ? 'Advanced Model Results' : 'Recommendations'}
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowAll(!showAll)}
            className="text-sm text-green-600 hover:text-green-700 font-medium"
          >
            {showAll ? 'Show Top 20' : `Show All (${recommendations.length})`}
          </button>
          <button
            onClick={exportCsv}
            className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1 font-medium"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white shadow overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th
                className="px-3 py-3 text-left cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('rank')}
              >
                #<SortIcon field="rank" />
              </th>
              <th className="px-3 py-3 text-left">Golfer</th>
              <th
                className="px-3 py-3 text-right cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('ev')}
              >
                EV ($)<SortIcon field="ev" />
              </th>

              {isAdvancedModel ? (
                <>
                  <th
                    className="px-3 py-3 text-center cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('composite_score')}
                    title="Weighted composite score"
                  >
                    Score<SortIcon field="composite_score" />
                  </th>
                  <th className="px-3 py-3 text-center" title="Strokes Gained (OTT, Approach, Around Green, Putting)">
                    SG
                  </th>
                  <th className="px-3 py-3 text-center" title="Ball Striking (Driving, Fairways, GIR)">
                    Ball
                  </th>
                  <th className="px-3 py-3 text-center" title="Short Game (Scrambling, Putting Avg)">
                    Short
                  </th>
                  <th className="px-3 py-3 text-center" title="Scoring (Birdie%, Par 5, Bogey Avoid)">
                    Scoring
                  </th>
                  <th className="px-3 py-3 text-center" title="Context (Course Fit, Odds)">
                    Context
                  </th>
                </>
              ) : (
                <>
                  <th
                    className="px-3 py-3 text-right cursor-pointer hover:bg-gray-100"
                    onClick={() => handleSort('skill_score')}
                  >
                    Skill<SortIcon field="skill_score" />
                  </th>
                  <th className="px-3 py-3 text-center">Form</th>
                  <th className="px-3 py-3 text-center">Course</th>
                </>
              )}

              <th className="px-3 py-3 text-right">Odds</th>
              <th
                className="px-3 py-3 text-right cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('win_prob')}
              >
                Win %<SortIcon field="win_prob" />
              </th>
              <th className="px-3 py-3 text-right">Cut %</th>
              <th className="px-3 py-3 text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            {displayRecs.map((rec) => (
              <tr
                key={rec.player_name}
                className={`border-b hover:bg-gray-50 ${
                  seasonRec?.recommended_pick === rec.player_name
                    ? 'bg-green-50'
                    : ''
                }`}
              >
                <td className="px-3 py-2 text-gray-500">{rec.rank}</td>
                <td className="px-3 py-2 font-medium text-gray-900">
                  {rec.player_name}
                  {rec.pick_rank && (
                    <span className="ml-2 text-xs text-gray-500">
                      (Pick #{rec.pick_rank})
                    </span>
                  )}
                </td>
                <td className="px-3 py-2 text-right font-medium">
                  {formatCurrency(rec.ev)}
                </td>

                {isAdvancedModel ? (
                  <>
                    <td className="px-3 py-2 text-center font-medium">
                      {rec.composite_score?.toFixed(1)}
                    </td>
                    <td className={`px-3 py-2 text-center ${getScoreColor(getCategoryScore(rec, 'sg'))}`}>
                      {getCategoryScore(rec, 'sg')?.toFixed(0) || '—'}
                    </td>
                    <td className={`px-3 py-2 text-center ${getScoreColor(getCategoryScore(rec, 'ballStriking'))}`}>
                      {getCategoryScore(rec, 'ballStriking')?.toFixed(0) || '—'}
                    </td>
                    <td className={`px-3 py-2 text-center ${getScoreColor(getCategoryScore(rec, 'shortGame'))}`}>
                      {getCategoryScore(rec, 'shortGame')?.toFixed(0) || '—'}
                    </td>
                    <td className={`px-3 py-2 text-center ${getScoreColor(getCategoryScore(rec, 'scoring'))}`}>
                      {getCategoryScore(rec, 'scoring')?.toFixed(0) || '—'}
                    </td>
                    <td className={`px-3 py-2 text-center ${getScoreColor(getCategoryScore(rec, 'context'))}`}>
                      {getCategoryScore(rec, 'context')?.toFixed(0) || '—'}
                    </td>
                  </>
                ) : (
                  <>
                    <td className="px-3 py-2 text-right">
                      {rec.skill_score?.toFixed(1)}
                    </td>
                    <td className={`px-3 py-2 text-center ${getFormColor(rec.form_label)}`}>
                      {rec.form_label}
                    </td>
                    <td className={`px-3 py-2 text-center ${getCourseColor(rec.course_label)}`}>
                      {rec.course_label}
                    </td>
                  </>
                )}

                <td className="px-3 py-2 text-right text-gray-600">
                  {rec.odds || '—'}
                </td>
                <td className="px-3 py-2 text-right">{rec.win_prob?.toFixed(1)}%</td>
                <td className="px-3 py-2 text-right">{rec.make_cut_prob?.toFixed(0)}%</td>
                <td className="px-3 py-2 text-center">
                  <span
                    className={`px-2 py-0.5 text-xs font-medium ${
                      rec.season_action === 'USE'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                    title={rec.reason}
                  >
                    {rec.season_action}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default RecommendationsTable;
