import { useState, useEffect, useRef } from 'react';
import { searchGolfers, addUsedGolfer, removeUsedGolfer } from '../api';

function UsedGolfers({ usedGolfers, onChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  // Search golfers
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await searchGolfers(searchQuery);
        // Filter out already used golfers
        const filtered = res.data.filter(
          (g) => !usedGolfers.some((u) => u.toLowerCase() === g.name.toLowerCase())
        );
        setSearchResults(filtered);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, usedGolfers]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddGolfer = async (golferName) => {
    try {
      await addUsedGolfer(golferName);
      onChange([...usedGolfers, golferName]);
      setSearchQuery('');
      setShowDropdown(false);
    } catch (err) {
      console.error('Failed to add golfer:', err);
    }
  };

  const handleRemoveGolfer = async (golferName) => {
    try {
      await removeUsedGolfer(golferName);
      onChange(usedGolfers.filter((g) => g !== golferName));
    } catch (err) {
      console.error('Failed to remove golfer:', err);
    }
  };

  return (
    <div className="bg-white shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Used Golfers ({usedGolfers.length})
      </h3>

      {/* Search Input */}
      <div className="relative mb-4" ref={dropdownRef}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setShowDropdown(true);
          }}
          onFocus={() => setShowDropdown(true)}
          placeholder="Add golfer..."
          className="w-full px-3 py-2 border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500"
        />

        {/* Dropdown */}
        {showDropdown && (searchResults.length > 0 || loading) && (
          <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 shadow-lg max-h-60 overflow-auto">
            {loading ? (
              <div className="px-3 py-2 text-gray-500">Searching...</div>
            ) : (
              searchResults.map((golfer) => (
                <button
                  key={golfer.name}
                  onClick={() => handleAddGolfer(golfer.name)}
                  className="w-full px-3 py-2 text-left hover:bg-gray-100 flex justify-between items-center"
                >
                  <span>{golfer.name}</span>
                  <span className="text-xs text-gray-500">
                    {golfer.rank && `#${golfer.rank}`}
                    {golfer.skill_score && ` • ${golfer.skill_score.toFixed(1)} skill`}
                  </span>
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {/* Used Golfers List */}
      <div className="space-y-2 max-h-48 overflow-auto">
        {usedGolfers.length === 0 ? (
          <p className="text-gray-500 text-sm">No golfers used yet</p>
        ) : (
          usedGolfers.map((golfer) => (
            <div
              key={golfer}
              className="flex justify-between items-center px-3 py-2 bg-gray-50"
            >
              <span className="text-gray-800">{golfer}</span>
              <button
                onClick={() => handleRemoveGolfer(golfer)}
                className="text-red-500 hover:text-red-700 font-bold text-lg leading-none"
                title="Remove"
              >
                &times;
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default UsedGolfers;
