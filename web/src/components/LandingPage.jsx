import { useNavigate, Link } from 'react-router-dom';
import CookieConsent from './CookieConsent';

function LandingPage() {
  const navigate = useNavigate();

  const tools = [
    {
      id: 'pickem',
      title: "Golf Pick 'Em",
      description: 'AI-powered recommendations for your weekly golf picks',
      available: true,
      icon: (
        <svg viewBox="0 0 100 100" className="w-20 h-20">
          {/* Golf flag/pin icon */}
          <rect x="48" y="20" width="4" height="60" fill="#374151" />
          <polygon points="52,20 52,45 80,32.5" fill="#10B981" />
          <ellipse cx="50" cy="85" rx="20" ry="6" fill="#22C55E" />
          <circle cx="50" cy="82" r="4" fill="white" stroke="#374151" strokeWidth="1" />
        </svg>
      ),
    },
    {
      id: 'fantasy',
      title: 'Fantasy Golf',
      description: 'Optimize your fantasy golf lineup with data-driven insights',
      available: false,
      icon: (
        <svg viewBox="0 0 100 100" className="w-20 h-20">
          {/* Golf bag icon */}
          <path d="M30 85 L35 35 L65 35 L70 85 Z" fill="#6B7280" stroke="#374151" strokeWidth="2" />
          <rect x="38" y="20" width="4" height="25" fill="#374151" />
          <rect x="48" y="15" width="4" height="30" fill="#374151" />
          <rect x="58" y="22" width="4" height="23" fill="#374151" />
          <ellipse cx="50" cy="35" rx="18" ry="4" fill="#4B5563" />
          <rect x="42" y="55" width="16" height="3" fill="#9CA3AF" />
        </svg>
      ),
    },
    {
      id: 'betting',
      title: 'Betting Odds Analysis',
      description: 'Compare odds and find value across sportsbooks',
      available: false,
      icon: (
        <svg viewBox="0 0 100 100" className="w-20 h-20">
          {/* Chart/analytics with golf ball */}
          <rect x="15" y="70" width="15" height="20" fill="#10B981" />
          <rect x="35" y="50" width="15" height="40" fill="#059669" />
          <rect x="55" y="35" width="15" height="55" fill="#047857" />
          <polyline points="20,65 42,45 62,30 85,20" stroke="#374151" strokeWidth="3" fill="none" />
          <circle cx="85" cy="20" r="8" fill="white" stroke="#374151" strokeWidth="2" />
          <circle cx="83" cy="18" r="1" fill="#9CA3AF" />
          <circle cx="87" cy="22" r="1" fill="#9CA3AF" />
        </svg>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-800 via-green-700 to-green-600 text-white py-6 px-6 shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center gap-4">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <svg viewBox="0 0 50 50" className="w-12 h-12">
              {/* Golf ball with data bars */}
              <circle cx="25" cy="25" r="20" fill="white" stroke="#166534" strokeWidth="2" />
              <circle cx="20" cy="20" r="1.5" fill="#9CA3AF" />
              <circle cx="28" cy="18" r="1.5" fill="#9CA3AF" />
              <circle cx="24" cy="26" r="1.5" fill="#9CA3AF" />
              <circle cx="32" cy="24" r="1.5" fill="#9CA3AF" />
              <circle cx="18" cy="28" r="1.5" fill="#9CA3AF" />
              {/* Data bars inside ball */}
              <rect x="17" y="32" width="4" height="8" fill="#10B981" />
              <rect x="23" y="28" width="4" height="12" fill="#059669" />
              <rect x="29" y="30" width="4" height="10" fill="#047857" />
            </svg>
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Data Caddie</h1>
              <p className="text-green-200 text-sm">Your AI-powered golf analytics companion</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="max-w-5xl w-full">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-800 mb-3">Choose Your Tool</h2>
            <p className="text-gray-600">Data-driven insights to improve your golf game decisions</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tools.map((tool) => (
              <div
                key={tool.id}
                onClick={() => tool.available && navigate('/pickem')}
                className={`
                  relative bg-white border-2 p-8 text-center transition-all
                  ${tool.available
                    ? 'border-green-500 hover:border-green-600 hover:shadow-xl cursor-pointer hover:-translate-y-1'
                    : 'border-gray-200 opacity-75'
                  }
                `}
              >
                {!tool.available && (
                  <div className="absolute top-3 right-3 bg-amber-500 text-white text-xs font-bold px-2 py-1">
                    COMING SOON
                  </div>
                )}

                <div className="flex justify-center mb-4 opacity-90">
                  {tool.icon}
                </div>

                <h3 className={`text-xl font-bold mb-2 ${tool.available ? 'text-gray-800' : 'text-gray-500'}`}>
                  {tool.title}
                </h3>

                <p className={`text-sm ${tool.available ? 'text-gray-600' : 'text-gray-400'}`}>
                  {tool.description}
                </p>

                {tool.available && (
                  <div className="mt-6">
                    <span className="inline-block bg-green-600 text-white font-semibold px-6 py-2 hover:bg-green-700 transition">
                      Launch Tool →
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Disclaimer */}
          <div className="mt-12 text-center">
            <p className="text-xs text-gray-500 max-w-2xl mx-auto">
              Data Caddie is for informational and entertainment purposes only. We do not provide
              gambling or betting advice. Past performance does not guarantee future results.
              Please gamble responsibly and only where legal.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-6 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm">© 2025 Data Caddie. All rights reserved.</p>
          <div className="flex gap-6 text-sm">
            <Link to="/privacy" className="hover:text-white transition">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition">Terms of Service</Link>
          </div>
        </div>
      </footer>

      {/* Cookie Consent Banner */}
      <CookieConsent />
    </div>
  );
}

export default LandingPage;
