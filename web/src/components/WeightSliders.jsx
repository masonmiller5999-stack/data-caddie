import { useState } from 'react';

const WEIGHT_CONFIG = [
  { key: 'skill', label: 'Skill', color: 'green' },
  { key: 'form', label: 'Form', color: 'blue' },
  { key: 'course', label: 'Course', color: 'amber' },
  { key: 'field', label: 'Field', color: 'purple' },
  { key: 'odds', label: 'Odds', color: 'orange' },
];

const colorClasses = {
  green: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700', slider: 'accent-green-600' },
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', slider: 'accent-blue-600' },
  amber: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-700', slider: 'accent-amber-600' },
  purple: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-700', slider: 'accent-purple-600' },
  orange: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', slider: 'accent-orange-600' },
};

function WeightSliders({ weights, onChange, onReset }) {
  const [activeSlider, setActiveSlider] = useState(null);

  const handleSliderChange = (key, newValue) => {
    const newValueFloat = parseFloat(newValue);
    const oldValue = weights[key];
    const diff = newValueFloat - oldValue;

    if (Math.abs(diff) < 0.001) return;

    const otherKeys = Object.keys(weights).filter((k) => k !== key);
    const otherSum = otherKeys.reduce((sum, k) => sum + weights[k], 0);

    const newWeights = { ...weights, [key]: newValueFloat };

    if (otherSum > 0) {
      otherKeys.forEach((k) => {
        const proportion = weights[k] / otherSum;
        newWeights[k] = Math.max(0, weights[k] - diff * proportion);
      });
    }

    const total = Object.values(newWeights).reduce((sum, v) => sum + v, 0);
    if (total > 0) {
      Object.keys(newWeights).forEach((k) => {
        newWeights[k] = newWeights[k] / total;
      });
    }

    onChange(newWeights);
  };

  return (
    <div className="bg-white shadow p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-gray-900">Model Weights</h3>
        <button onClick={onReset} className="text-xs text-green-600 hover:text-green-700 font-medium">
          Reset
        </button>
      </div>

      {/* Weight Boxes */}
      <div className="grid grid-cols-5 gap-2 mb-3">
        {WEIGHT_CONFIG.map((config) => {
          const colors = colorClasses[config.color];
          const value = weights[config.key] || 0;
          const isActive = activeSlider === config.key;

          return (
            <button
              key={config.key}
              onClick={() => setActiveSlider(isActive ? null : config.key)}
              className={`p-2 text-center border transition ${colors.border} ${colors.bg} ${isActive ? 'ring-2 ring-offset-1 ring-green-500' : ''}`}
            >
              <div className={`text-xs font-medium ${colors.text}`}>{config.label}</div>
              <div className="text-lg font-bold text-gray-800">{Math.round(value * 100)}%</div>
            </button>
          );
        })}
      </div>

      {/* Active Slider */}
      {activeSlider && (
        <div className="border border-gray-200 p-3 mb-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-500">
              Adjust {WEIGHT_CONFIG.find(c => c.key === activeSlider)?.label} Weight
            </span>
            <span className="text-sm font-bold text-gray-800">
              {Math.round((weights[activeSlider] || 0) * 100)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={weights[activeSlider] || 0}
            onChange={(e) => handleSliderChange(activeSlider, e.target.value)}
            className="w-full h-3 bg-gray-300 appearance-none cursor-pointer accent-green-600 rounded"
            style={{ background: `linear-gradient(to right, #16a34a ${(weights[activeSlider] || 0) * 100}%, #d1d5db ${(weights[activeSlider] || 0) * 100}%)` }}
          />
        </div>
      )}

      {!activeSlider && (
        <p className="text-xs text-gray-400 text-center mb-2">Click a weight above to adjust</p>
      )}

      <div className="text-center border-t pt-2">
        <span className="text-xs font-medium text-green-600">
          Total: {Math.round(Object.values(weights).reduce((sum, v) => sum + v, 0) * 100)}%
        </span>
      </div>
    </div>
  );
}

export default WeightSliders;
