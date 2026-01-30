function TournamentInfo({ tournament }) {
  if (!tournament) {
    return (
      <div className="bg-white shadow p-4">
        <div className="animate-pulse flex items-center gap-4">
          <div className="h-5 bg-gray-200 w-48"></div>
          <div className="h-4 bg-gray-200 w-32"></div>
        </div>
      </div>
    );
  }

  const formatPurse = (purse) => {
    if (!purse) return 'TBD';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(purse);
  };

  return (
    <div className="bg-white shadow p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-bold text-gray-900">{tournament.name}</h2>
          {tournament.major && (
            <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs font-medium">
              MAJOR
            </span>
          )}
        </div>
        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
          <span>{tournament.start_date}</span>
          <span className="hidden sm:inline">|</span>
          <span><span className="text-gray-400">Purse:</span> <span className="font-medium text-gray-800">{formatPurse(tournament.purse)}</span></span>
          <span className="hidden sm:inline">|</span>
          <span><span className="text-gray-400">Field:</span> <span className="font-medium text-gray-800">{tournament.field_size}</span></span>
          {tournament.field_strength && (
            <>
              <span className="hidden sm:inline">|</span>
              <span><span className="text-gray-400">Strength:</span> <span className="font-medium text-gray-800">{tournament.field_strength}/100</span></span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default TournamentInfo;
