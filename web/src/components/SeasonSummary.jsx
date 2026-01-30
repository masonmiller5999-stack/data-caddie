function SeasonSummary({ summary, onClose }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="bg-green-700 text-white px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">Season Summary</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(summary.total_earnings)}
              </div>
              <div className="text-sm text-gray-600">Total Earnings</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-800">
                {summary.picks_made}
              </div>
              <div className="text-sm text-gray-600">Picks Made</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-800">
                {summary.completed}
              </div>
              <div className="text-sm text-gray-600">Results Recorded</div>
            </div>
          </div>

          {/* Pick History */}
          <h3 className="font-semibold text-gray-900 mb-3">Pick History</h3>
          <div className="max-h-60 overflow-auto">
            {summary.picks.length === 0 ? (
              <p className="text-gray-500 text-sm">No picks recorded yet</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left">Golfer</th>
                    <th className="px-3 py-2 text-left">Tournament</th>
                    <th className="px-3 py-2 text-right">Earnings</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.picks.map((pick, idx) => (
                    <tr key={idx} className="border-t">
                      <td className="px-3 py-2 font-medium">{pick.name}</td>
                      <td className="px-3 py-2 text-gray-600">
                        {pick.tournament || '—'}
                      </td>
                      <td className="px-3 py-2 text-right">
                        {pick.earnings !== null
                          ? formatCurrency(pick.earnings)
                          : <span className="text-gray-400">Pending</span>
                        }
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="border-t px-6 py-4">
          <button
            onClick={onClose}
            className="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 rounded-lg transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default SeasonSummary;
