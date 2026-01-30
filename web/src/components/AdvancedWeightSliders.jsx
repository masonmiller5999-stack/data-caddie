import { useState } from 'react';

const WEIGHT_CATEGORIES = [
  {
    name: 'Strokes Gained',
    color: 'green',
    weights: [
      { key: 'sg_ott', label: 'OTT' },
      { key: 'sg_app', label: 'App' },
      { key: 'sg_arg', label: 'ARG' },
      { key: 'sg_putt', label: 'Putt' },
    ],
  },
  {
    name: 'Ball Striking',
    color: 'blue',
    weights: [
      { key: 'driving_dist', label: 'Distance' },
      { key: 'fairways_pct', label: 'Fairways' },
      { key: 'gir_pct', label: 'GIR' },
    ],
  },
  {
    name: 'Short Game',
    color: 'amber',
    weights: [
      { key: 'scrambling_pct', label: 'Scramble' },
      { key: 'putting_avg', label: 'Putt Avg' },
    ],
  },
  {
    name: 'Scoring',
    color: 'purple',
    weights: [
      { key: 'birdie_pct', label: 'Birdie' },
      { key: 'par5_scoring', label: 'Par 5' },
      { key: 'bogey_avoid_pct', label: 'Bogey Avoid' },
    ],
  },
  {
    name: 'Context',
    color: 'orange',
    weights: [
      { key: 'course_fit', label: 'Course' },
      { key: 'odds', label: 'Odds' },
    ],
  },
];

const PRESETS = [
  {
    id: 'balanced',
    name: 'Balanced',
    description: 'Even distribution',
    weights: {
      sg_ott: 0.10, sg_app: 0.12, sg_arg: 0.08, sg_putt: 0.10,
      driving_dist: 0.05, fairways_pct: 0.07, gir_pct: 0.08,
      scrambling_pct: 0.10, putting_avg: 0.05,
      birdie_pct: 0.04, par5_scoring: 0.03, bogey_avoid_pct: 0.03,
      course_fit: 0.08, odds: 0.07,
    },
  },
  {
    id: 'strokes-gained',
    name: 'SG Focus',
    description: 'Strokes Gained heavy',
    weights: {
      sg_ott: 0.15, sg_app: 0.18, sg_arg: 0.12, sg_putt: 0.15,
      driving_dist: 0.03, fairways_pct: 0.04, gir_pct: 0.05,
      scrambling_pct: 0.05, putting_avg: 0.03,
      birdie_pct: 0.02, par5_scoring: 0.02, bogey_avoid_pct: 0.02,
      course_fit: 0.07, odds: 0.07,
    },
  },
  {
    id: 'ball-striking',
    name: 'Ball Striking',
    description: 'Tee-to-green focus',
    weights: {
      sg_ott: 0.12, sg_app: 0.12, sg_arg: 0.05, sg_putt: 0.05,
      driving_dist: 0.12, fairways_pct: 0.12, gir_pct: 0.14,
      scrambling_pct: 0.04, putting_avg: 0.03,
      birdie_pct: 0.03, par5_scoring: 0.02, bogey_avoid_pct: 0.02,
      course_fit: 0.07, odds: 0.07,
    },
  },
  {
    id: 'short-game',
    name: 'Short Game',
    description: 'Around the green',
    weights: {
      sg_ott: 0.06, sg_app: 0.08, sg_arg: 0.14, sg_putt: 0.14,
      driving_dist: 0.03, fairways_pct: 0.04, gir_pct: 0.05,
      scrambling_pct: 0.16, putting_avg: 0.12,
      birdie_pct: 0.02, par5_scoring: 0.02, bogey_avoid_pct: 0.02,
      course_fit: 0.06, odds: 0.06,
    },
  },
  {
    id: 'scoring',
    name: 'Scoring',
    description: 'Birdies & bogey avoid',
    weights: {
      sg_ott: 0.06, sg_app: 0.08, sg_arg: 0.06, sg_putt: 0.08,
      driving_dist: 0.04, fairways_pct: 0.05, gir_pct: 0.06,
      scrambling_pct: 0.06, putting_avg: 0.05,
      birdie_pct: 0.14, par5_scoring: 0.12, bogey_avoid_pct: 0.12,
      course_fit: 0.04, odds: 0.04,
    },
  },
  {
    id: 'value',
    name: 'Value Play',
    description: 'Odds & course fit',
    weights: {
      sg_ott: 0.06, sg_app: 0.08, sg_arg: 0.05, sg_putt: 0.06,
      driving_dist: 0.04, fairways_pct: 0.05, gir_pct: 0.06,
      scrambling_pct: 0.05, putting_avg: 0.04,
      birdie_pct: 0.03, par5_scoring: 0.03, bogey_avoid_pct: 0.03,
      course_fit: 0.18, odds: 0.24,
    },
  },
];

const colorClasses = {
  green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', slider: 'accent-green-600' },
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', slider: 'accent-blue-600' },
  amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', slider: 'accent-amber-600' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', slider: 'accent-purple-600' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', slider: 'accent-orange-600' },
};

function AdvancedWeightSliders({ weights, onChange, onReset }) {
  const [expandedSection, setExpandedSection] = useState(null);
  const [activePreset, setActivePreset] = useState('balanced');

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);

  const handleSliderChange = (key, newValue) => {
    const currentValue = weights[key];
    const delta = newValue - currentValue;

    if (Math.abs(delta) < 0.001) return;

    const otherKeys = Object.keys(weights).filter((k) => k !== key);
    const otherTotal = otherKeys.reduce((sum, k) => sum + weights[k], 0);

    if (otherTotal === 0) return;

    const newWeights = { ...weights, [key]: newValue };
    const scale = (otherTotal - delta) / otherTotal;

    otherKeys.forEach((k) => {
      newWeights[k] = Math.max(0, weights[k] * scale);
    });

    const newTotal = Object.values(newWeights).reduce((sum, w) => sum + w, 0);
    if (newTotal > 0) {
      Object.keys(newWeights).forEach((k) => {
        newWeights[k] = newWeights[k] / newTotal;
      });
    }

    setActivePreset(null);
    onChange(newWeights);
  };

  const handleInputChange = (key, inputValue) => {
    const parsed = parseInt(inputValue, 10);
    if (isNaN(parsed) || parsed < 0 || parsed > 100) return;
    handleSliderChange(key, parsed / 100);
  };

  const applyPreset = (preset) => {
    setActivePreset(preset.id);
    onChange({ ...preset.weights });
    setExpandedSection(null);
  };

  const getCategoryTotal = (category) => {
    return category.weights.reduce((sum, w) => sum + (weights[w.key] || 0), 0);
  };

  return (
    <div className="bg-white shadow p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-gray-900">Advanced Model Weights</h3>
        <button onClick={onReset} className="text-xs text-green-600 hover:text-green-700 font-medium">
          Reset
        </button>
      </div>

      {/* Presets */}
      <div className="mb-3">
        <p className="text-xs text-gray-500 mb-2">Quick Presets</p>
        <div className="flex flex-wrap gap-1">
          {PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => applyPreset(preset)}
              className={`px-2 py-1 text-xs font-medium transition ${
                activePreset === preset.id
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              title={preset.description}
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>

      {/* Category Summary Row */}
      <div className="grid grid-cols-5 gap-2 mb-3">
        {WEIGHT_CATEGORIES.map((category) => {
          const colors = colorClasses[category.color];
          const total = getCategoryTotal(category);
          const isExpanded = expandedSection === category.name;

          return (
            <button
              key={category.name}
              onClick={() => setExpandedSection(isExpanded ? null : category.name)}
              className={`p-2 text-center border transition ${colors.border} ${colors.bg} ${isExpanded ? 'ring-2 ring-offset-1 ring-green-500' : ''}`}
            >
              <div className={`text-xs font-medium ${colors.text}`}>{category.name.split(' ')[0]}</div>
              <div className="text-lg font-bold text-gray-800">{Math.round(total * 100)}%</div>
            </button>
          );
        })}
      </div>

      {/* Expanded Section */}
      {expandedSection && (
        <div className="border border-gray-200 p-3 mb-3">
          <div className="text-xs font-medium text-gray-500 mb-2">{expandedSection} Weights</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {WEIGHT_CATEGORIES.find((c) => c.name === expandedSection)?.weights.map((weightDef) => {
              const colors = colorClasses[WEIGHT_CATEGORIES.find((c) => c.name === expandedSection).color];
              const value = weights[weightDef.key] || 0;
              return (
                <div key={weightDef.key} className={`${colors.bg} p-2`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-gray-600">{weightDef.label}</span>
                    <span className="text-xs font-bold text-gray-700">{Math.round(value * 100)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="0.3"
                    step="0.01"
                    value={value}
                    onChange={(e) => handleSliderChange(weightDef.key, parseFloat(e.target.value))}
                    className="w-full h-3 bg-gray-300 appearance-none cursor-pointer rounded accent-green-600"
                    style={{ background: `linear-gradient(to right, #16a34a ${(value / 0.3) * 100}%, #d1d5db ${(value / 0.3) * 100}%)` }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!expandedSection && (
        <p className="text-xs text-gray-400 text-center mb-2">Click a category above to adjust individual weights</p>
      )}

      <div className="text-center border-t pt-2">
        <span className={`text-xs font-medium ${Math.abs(totalWeight - 1) < 0.01 ? 'text-green-600' : 'text-red-600'}`}>
          Total: {Math.round(totalWeight * 100)}%
        </span>
      </div>
    </div>
  );
}

export default AdvancedWeightSliders;
