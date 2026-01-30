import { Link } from 'react-router-dom';

function PrivacyPolicy() {
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
          <p className="text-gray-500 mb-8">Last updated: January 29, 2025</p>

          <div className="prose prose-gray max-w-none space-y-6">
            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Introduction</h2>
              <p className="text-gray-700">
                Data Caddie ("we," "our," or "us") operates the datacaddie.app website. This Privacy Policy
                explains how we collect, use, disclose, and safeguard your information when you visit our
                website and use our golf analytics services.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Information We Collect</h2>
              <h3 className="text-lg font-medium text-gray-800 mb-2">Information You Provide</h3>
              <ul className="list-disc list-inside text-gray-700 space-y-1 mb-4">
                <li>Golfer selections and preferences you input into our tools</li>
                <li>Weight configurations and model settings</li>
                <li>Any feedback or correspondence you send to us</li>
              </ul>

              <h3 className="text-lg font-medium text-gray-800 mb-2">Automatically Collected Information</h3>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Browser type and version</li>
                <li>Operating system</li>
                <li>Pages visited and time spent on pages</li>
                <li>Referring website addresses</li>
                <li>IP address (anonymized)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">3. How We Use Your Information</h2>
              <p className="text-gray-700 mb-2">We use the information we collect to:</p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Provide and maintain our golf analytics services</li>
                <li>Improve and optimize our website and tools</li>
                <li>Understand how users interact with our services</li>
                <li>Respond to your inquiries and support requests</li>
                <li>Detect and prevent technical issues or abuse</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Cookies and Tracking Technologies</h2>
              <p className="text-gray-700 mb-2">
                We use cookies and similar tracking technologies to track activity on our website.
                Cookies are small data files stored on your device. We use:
              </p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li><strong>Essential Cookies:</strong> Required for the website to function properly</li>
                <li><strong>Analytics Cookies:</strong> Help us understand how visitors use our site</li>
                <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
              </ul>
              <p className="text-gray-700 mt-2">
                You can instruct your browser to refuse all cookies or indicate when a cookie is being sent.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Data Storage and Security</h2>
              <p className="text-gray-700">
                Your data is stored locally in your browser and on our secure servers. We implement
                appropriate technical and organizational measures to protect your personal information
                against unauthorized access, alteration, disclosure, or destruction.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Third-Party Services</h2>
              <p className="text-gray-700">
                We may use third-party services for analytics and hosting. These services have their
                own privacy policies governing the use of your information. We do not sell your
                personal information to third parties.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Your Rights</h2>
              <p className="text-gray-700 mb-2">Depending on your location, you may have the right to:</p>
              <ul className="list-disc list-inside text-gray-700 space-y-1">
                <li>Access the personal data we hold about you</li>
                <li>Request correction of inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Object to processing of your data</li>
                <li>Request data portability</li>
              </ul>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Children's Privacy</h2>
              <p className="text-gray-700">
                Our services are not intended for individuals under the age of 18. We do not knowingly
                collect personal information from children. If you are a parent or guardian and believe
                your child has provided us with personal information, please contact us.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Changes to This Policy</h2>
              <p className="text-gray-700">
                We may update this Privacy Policy from time to time. We will notify you of any changes
                by posting the new Privacy Policy on this page and updating the "Last updated" date.
              </p>
            </section>

            <section>
              <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Contact Us</h2>
              <p className="text-gray-700">
                If you have questions about this Privacy Policy, please contact us at:
              </p>
              <p className="text-gray-700 mt-2">
                <strong>Email:</strong> privacy@datacaddie.app
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

export default PrivacyPolicy;
