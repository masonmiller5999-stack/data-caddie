import { Link } from 'react-router-dom';

function TermsOfService() {
  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-green-800 via-green-700 to-green-600 text-white py-4 px-6 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 hover:opacity-90 transition">
            <svg viewBox="0 0 50 50" className="w-10 h-10">
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
            <h1 className="text-2xl font-bold tracking-tight">Data Caddie</h1>
          </Link>
          <Link to="/" className="text-sm text-green-200 hover:text-white transition">
            ← Back to Home
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white shadow p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
          <p className="text-gray-500 mb-8">Last updated: January 29, 2025</p>

          <div className="prose prose-gray max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
              <p className="text-gray-700">
                By accessing or using Data Caddie ("the Service"), you agree to be bound by these Terms
                of Service. If you do not agree to these terms, please do not use our Service.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Description of Service</h2>
              <p className="text-gray-700">
                Data Caddie provides golf analytics tools including pick recommendations, statistical
                analysis, and fantasy golf optimization. The Service is provided for informational
                and entertainment purposes only.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">3. No Gambling Advice</h2>
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4">
                <p className="text-yellow-800 font-medium">Important Disclaimer</p>
              </div>
              <p className="text-gray-700 mb-2">
                <strong>Data Caddie does not provide gambling, betting, or wagering advice.</strong>
              </p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Our tools are for informational and entertainment purposes only</li>
                <li>We do not guarantee any outcomes or results</li>
                <li>Past performance does not indicate future results</li>
                <li>You should not rely on our tools for financial decisions</li>
                <li>If you choose to gamble, please do so responsibly and within legal jurisdictions</li>
                <li>We are not responsible for any losses incurred from gambling activities</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">4. User Responsibilities</h2>
              <p className="text-gray-700 mb-2">By using our Service, you agree to:</p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Use the Service only for lawful purposes</li>
                <li>Not attempt to disrupt or interfere with the Service</li>
                <li>Not use automated systems to access the Service without permission</li>
                <li>Comply with all applicable laws and regulations in your jurisdiction</li>
                <li>Be at least 18 years of age</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Intellectual Property</h2>
              <p className="text-gray-700">
                All content, features, and functionality of the Service, including but not limited to
                text, graphics, logos, algorithms, and software, are owned by Data Caddie and are
                protected by intellectual property laws. You may not reproduce, distribute, or create
                derivative works without our express permission.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Data Accuracy</h2>
              <p className="text-gray-700">
                While we strive to provide accurate and up-to-date information, we make no guarantees
                about the accuracy, completeness, or reliability of any data or analysis provided through
                our Service. Golf statistics and odds can change frequently, and our data may not reflect
                the most current information.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Limitation of Liability</h2>
              <p className="text-gray-700 mb-2">
                To the fullest extent permitted by law:
              </p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>The Service is provided "as is" without warranties of any kind</li>
                <li>We disclaim all warranties, express or implied, including merchantability and fitness for a particular purpose</li>
                <li>We shall not be liable for any indirect, incidental, special, consequential, or punitive damages</li>
                <li>Our total liability shall not exceed the amount you paid for the Service (if any)</li>
                <li>We are not liable for any losses resulting from decisions made based on our tools</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Indemnification</h2>
              <p className="text-gray-700">
                You agree to indemnify and hold harmless Data Caddie, its officers, directors, employees,
                and agents from any claims, damages, losses, or expenses arising from your use of the
                Service or violation of these Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Modifications to Service</h2>
              <p className="text-gray-700">
                We reserve the right to modify, suspend, or discontinue the Service at any time without
                notice. We may also update these Terms from time to time. Continued use of the Service
                after changes constitutes acceptance of the modified Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Termination</h2>
              <p className="text-gray-700">
                We may terminate or suspend your access to the Service immediately, without prior notice,
                for any reason, including breach of these Terms.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Governing Law</h2>
              <p className="text-gray-700">
                These Terms shall be governed by and construed in accordance with the laws of the
                United States, without regard to conflict of law provisions.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">12. Severability</h2>
              <p className="text-gray-700">
                If any provision of these Terms is found to be unenforceable, the remaining provisions
                will continue in full force and effect.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">13. Contact Us</h2>
              <p className="text-gray-700">
                If you have questions about these Terms of Service, please contact us at:
              </p>
              <p className="text-gray-700 mt-2">
                <strong>Email:</strong> legal@datacaddie.app
              </p>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-400 py-6 px-6">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm">© 2025 Data Caddie. All rights reserved.</p>
          <div className="flex gap-6 text-sm">
            <Link to="/privacy" className="hover:text-white transition">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition">Terms of Service</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default TermsOfService;
