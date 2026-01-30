function ModelTabs({ activeTab, onTabChange }) {
  const tabs = [
    { id: 'basic', label: 'Basic', description: '5 weighted factors' },
    { id: 'advanced', label: 'Advanced', description: '14 granular metrics' },
  ];

  return (
    <div className="bg-white shadow p-3">
      <p className="text-xs text-gray-500 mb-2 font-medium uppercase tracking-wide">Model</p>
      <div className="flex lg:flex-col gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex-1 lg:flex-none py-2 px-3 text-left text-sm font-medium transition ${
              activeTab === tab.id
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            <div className="font-semibold">{tab.label}</div>
            <div className={`text-xs ${activeTab === tab.id ? 'text-green-100' : 'text-gray-400'}`}>
              {tab.description}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

export default ModelTabs;
