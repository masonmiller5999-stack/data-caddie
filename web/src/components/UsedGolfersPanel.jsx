import { useState, useEffect, useRef } from 'react';
import { searchGolfers, addUsedGolfer, removeUsedGolfer } from '../api';

function UsedGolfersPanel({ isOpen, onClose, usedGolfers, onChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const panelRef = useRef(null);

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

  // Close on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  const handleAddGolfer = async (golferName) => {
    try {
      await addUsedGolfer(golferName);
      onChange([...usedGolfers, golferName]);
      setSearchQuery('');
      setSearchResults([]);
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

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Panel */}
      <div
        ref={panelRef}
        className="fixed top-0 right-0 h-full w-full max-w-md bg-white shadow-xl z-50 transform transition-transform"
      >
        {/* Header */}
        <div className="bg-green-700 text-white px-4 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Used Golfers</h2>
            <p className="text-green-200 text-xs">
              {usedGolfers.length} golfer{usedGolfers.length !== 1 ? 's' : ''} marked as used
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-green-200 transition p-1"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Search Input */}
        <div className="p-4 border-b">
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search to add golfer..."
              className="w-full px-4 py-2 border border-gray-300 focus:ring-2 focus:ring-green-500 focus:border-green-500"
              autoFocus
            />
            {loading && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div className="mt-2 border border-gray-200 max-h-48 overflow-auto">
              {searchResults.map((golfer) => (
                <button
                  key={golfer.name}
                  onClick={() => handleAddGolfer(golfer.name)}
                  className="w-full px-4 py-2 text-left hover:bg-green-50 flex justify-between items-center border-b border-gray-100 last:border-0"
                >
                  <span className="font-medium">{golfer.name}</span>
                  <span className="text-xs text-gray-500">
                    {golfer.rank && `#${golfer.rank}`}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Used Golfers List */}
        <div className="flex-1 overflow-auto p-4">
          {usedGolfers.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <p className="text-sm">No golfers marked as used yet</p>
              <p className="text-xs text-gray-400 mt-1">Search above to add golfers you've already picked</p>
            </div>
          ) : (
            <div className="space-y-2">
              {usedGolfers.map((golfer) => (
                <div
                  key={golfer}
                  className="flex justify-between items-center px-3 py-2 bg-gray-50 hover:bg-gray-100 transition"
                >
                  <span className="text-gray-800">{golfer}</span>
                  <button
                    onClick={() => handleRemoveGolfer(golfer)}
                    className="text-red-500 hover:text-red-700 p-1 hover:bg-red-50 transition"
                    title="Remove"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t p-4 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full bg-green-600 text-white py-2 font-medium hover:bg-green-700 transition"
          >
            Done
          </button>
        </div>
      </div>
    </>
  );
}

export default UsedGolfersPanel;
