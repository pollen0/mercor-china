import Link from 'next/link'

export const metadata = {
  title: 'Privacy Policy | Pathway',
  description: 'Privacy policy for Pathway AI-powered interview platform',
}

export default function PrivacyPolicyPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-teal-600 to-teal-500 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="text-xl font-semibold">Pathway</span>
          </Link>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>

        <p className="text-sm text-gray-500 mb-8">
          Last Updated: January 2025
        </p>

        <div className="prose prose-teal max-w-none">
          {/* Introduction */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">1. Introduction</h3>
            <p className="mb-4 text-gray-700">
              Welcome to Pathway (&quot;Pathway&quot;, &quot;we&quot;, &quot;our&quot;, or &quot;us&quot;). We are committed to protecting your privacy and personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered video interview platform designed for college students and early-career professionals.
            </p>
          </section>

          {/* Information We Collect */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">2. Information We Collect</h3>

            <h4 className="font-medium mb-2">Personal Information</h4>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Name, email address, and phone number</li>
              <li>Educational background (university, major, graduation year)</li>
              <li>Resume and professional background</li>
              <li>Video recordings of interview responses</li>
              <li>GitHub account information (if connected)</li>
            </ul>

            <h4 className="font-medium mb-2">Automatically Collected Information</h4>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Device information and browser type</li>
              <li>IP address and location data</li>
              <li>Usage data and interaction patterns</li>
            </ul>
          </section>

          {/* How We Use Information */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">3. How We Use Your Information</h3>
            <p className="mb-4 text-gray-700">We use the collected information to:</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Provide and maintain our interview services</li>
              <li>Process and analyze video interviews using AI technology</li>
              <li>Track your progress and growth over time</li>
              <li>Match candidates with potential employers</li>
              <li>Improve our platform and user experience</li>
              <li>Communicate with you about our services</li>
              <li>Comply with legal obligations</li>
            </ul>
          </section>

          {/* AI Processing */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">4. AI Processing</h3>
            <p className="mb-4 text-gray-700">
              Our platform uses AI technology to analyze interview responses. This includes:
            </p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Speech-to-text transcription of video responses</li>
              <li>Assessment of communication skills, problem-solving ability, and domain knowledge</li>
              <li>Resume parsing and analysis</li>
              <li>Progress tracking across multiple interviews</li>
            </ul>
            <p className="mt-4 text-gray-700">
              AI assessments are provided to assist employers in their hiring decisions but are not the sole determining factor. We believe in showing your growth trajectory, not just a single snapshot.
            </p>
          </section>

          {/* Data Sharing */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">5. Information Sharing</h3>
            <p className="mb-4 text-gray-700">We may share your information with:</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li><strong>Employers</strong>: Interview results, profile information, and progress history for job matching</li>
              <li><strong>Service Providers</strong>: Cloud storage, AI processing, and analytics services</li>
              <li><strong>Legal Requirements</strong>: When required by law or to protect our rights</li>
            </ul>
            <p className="mt-4 text-gray-700">
              We do not sell your personal information to third parties.
            </p>
          </section>

          {/* GitHub Integration */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">6. GitHub Integration</h3>
            <p className="mb-4 text-gray-700">
              If you choose to connect your GitHub account, we access your public profile information, public repositories, and contribution statistics. We use this information to showcase your coding activity and projects to potential employers. You can disconnect your GitHub account at any time from your profile settings.
            </p>
          </section>

          {/* Data Security */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">7. Data Security</h3>
            <p className="mb-4 text-gray-700">
              We implement appropriate technical and organizational security measures to protect your personal information, including:
            </p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Encryption of data in transit and at rest</li>
              <li>Secure cloud storage infrastructure</li>
              <li>Access controls and authentication</li>
              <li>Regular security assessments</li>
            </ul>
          </section>

          {/* Data Retention */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">8. Data Retention</h3>
            <p className="mb-4 text-gray-700">
              We retain your personal information for as long as necessary to provide our services and fulfill the purposes described in this policy. Interview recordings are typically retained for 24 months to track your progress over time, unless you request earlier deletion.
            </p>
          </section>

          {/* Your Rights */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">9. Your Rights</h3>
            <p className="mb-4 text-gray-700">You have the right to:</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Access your personal information</li>
              <li>Correct inaccurate information</li>
              <li>Request deletion of your data</li>
              <li>Withdraw consent for data processing</li>
              <li>Export your data in a portable format</li>
              <li>Disconnect third-party integrations (like GitHub)</li>
            </ul>
            <p className="mt-4 text-gray-700">
              To exercise these rights, please contact us at the email address below.
            </p>
          </section>

          {/* Updates to Policy */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">10. Changes to This Policy</h3>
            <p className="mb-4 text-gray-700">
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the &quot;Last Updated&quot; date.
            </p>
          </section>

          {/* Contact */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">11. Contact Us</h3>
            <p className="mb-4 text-gray-700">
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700"><strong>Email:</strong> privacy@pathway.careers</p>
              <p className="text-gray-700"><strong>Platform:</strong> Pathway</p>
            </div>
          </section>
        </div>

        {/* Back to Home */}
        <div className="mt-12 pt-8 border-t">
          <Link
            href="/"
            className="inline-flex items-center text-teal-600 hover:text-teal-700"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} Pathway. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}
