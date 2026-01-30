import Link from 'next/link'

export const metadata = {
  title: 'Privacy Policy | ZhiMian',
  description: 'Privacy policy for ZhiMian AI-powered interview platform',
}

export default function PrivacyPolicyPage() {
  return (
    <main className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b bg-white/95 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold">智</span>
            </div>
            <span className="text-xl font-semibold">ZhiMian 智面</span>
          </Link>
        </div>
      </header>

      {/* Content */}
      <div className="container mx-auto px-4 py-12 max-w-4xl">
        <h1 className="text-3xl font-bold mb-2">Privacy Policy</h1>
        <h2 className="text-2xl text-gray-600 mb-8">隐私政策</h2>

        <p className="text-sm text-gray-500 mb-8">
          Last Updated / 最后更新: January 2025
        </p>

        <div className="prose prose-emerald max-w-none">
          {/* Introduction */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">1. Introduction / 简介</h3>
            <p className="mb-4 text-gray-700">
              Welcome to ZhiMian (&quot;智面&quot;, &quot;we&quot;, &quot;our&quot;, or &quot;us&quot;). We are committed to protecting your privacy and personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered video interview platform.
            </p>
            <p className="text-gray-600">
              欢迎使用智面（以下简称"我们"）。我们致力于保护您的隐私和个人信息。本隐私政策说明了当您使用我们的AI视频面试平台时，我们如何收集、使用、披露和保护您的信息。
            </p>
          </section>

          {/* Information We Collect */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">2. Information We Collect / 我们收集的信息</h3>

            <h4 className="font-medium mb-2">Personal Information / 个人信息</h4>
            <ul className="list-disc pl-6 mb-4 text-gray-700">
              <li>Name, email address, and phone number / 姓名、邮箱地址和电话号码</li>
              <li>Resume and professional background / 简历和职业背景</li>
              <li>Video recordings of interview responses / 面试回答的视频录制</li>
              <li>WeChat account information (if using WeChat login) / 微信账户信息（如果使用微信登录）</li>
            </ul>

            <h4 className="font-medium mb-2">Automatically Collected Information / 自动收集的信息</h4>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Device information and browser type / 设备信息和浏览器类型</li>
              <li>IP address and location data / IP地址和位置数据</li>
              <li>Usage data and interaction patterns / 使用数据和交互模式</li>
            </ul>
          </section>

          {/* How We Use Information */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">3. How We Use Your Information / 我们如何使用您的信息</h3>
            <p className="mb-4 text-gray-700">We use the collected information to:</p>
            <p className="mb-4 text-gray-600">我们使用收集的信息用于：</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Provide and maintain our interview services / 提供和维护我们的面试服务</li>
              <li>Process and analyze video interviews using AI technology / 使用AI技术处理和分析视频面试</li>
              <li>Match candidates with potential employers / 为候选人匹配潜在雇主</li>
              <li>Improve our platform and user experience / 改进我们的平台和用户体验</li>
              <li>Communicate with you about our services / 就我们的服务与您沟通</li>
              <li>Comply with legal obligations / 遵守法律义务</li>
            </ul>
          </section>

          {/* AI Processing */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">4. AI Processing / AI处理</h3>
            <p className="mb-4 text-gray-700">
              Our platform uses AI technology to analyze interview responses. This includes:
            </p>
            <p className="mb-4 text-gray-600">
              我们的平台使用AI技术分析面试回答，包括：
            </p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Speech-to-text transcription of video responses / 视频回答的语音转文字</li>
              <li>Assessment of communication skills, problem-solving ability, and domain knowledge / 评估沟通能力、解决问题能力和专业知识</li>
              <li>Resume parsing and analysis / 简历解析和分析</li>
            </ul>
            <p className="mt-4 text-gray-700">
              AI assessments are provided to assist employers in their hiring decisions but are not the sole determining factor.
            </p>
            <p className="text-gray-600">
              AI评估仅作为协助雇主进行招聘决策的参考，而非唯一决定因素。
            </p>
          </section>

          {/* Data Sharing */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">5. Information Sharing / 信息共享</h3>
            <p className="mb-4 text-gray-700">We may share your information with:</p>
            <p className="mb-4 text-gray-600">我们可能与以下方共享您的信息：</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li><strong>Employers</strong>: Interview results and profile information for job matching / <strong>雇主</strong>：用于职位匹配的面试结果和个人资料</li>
              <li><strong>Service Providers</strong>: Cloud storage, AI processing, and analytics services / <strong>服务提供商</strong>：云存储、AI处理和分析服务</li>
              <li><strong>Legal Requirements</strong>: When required by law or to protect our rights / <strong>法律要求</strong>：当法律要求或为保护我们的权利时</li>
            </ul>
            <p className="mt-4 text-gray-700">
              We do not sell your personal information to third parties.
            </p>
            <p className="text-gray-600">
              我们不会将您的个人信息出售给第三方。
            </p>
          </section>

          {/* Data Security */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">6. Data Security / 数据安全</h3>
            <p className="mb-4 text-gray-700">
              We implement appropriate technical and organizational security measures to protect your personal information, including:
            </p>
            <p className="mb-4 text-gray-600">
              我们采取适当的技术和组织安全措施来保护您的个人信息，包括：
            </p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Encryption of data in transit and at rest / 传输中和存储中的数据加密</li>
              <li>Secure cloud storage infrastructure / 安全的云存储基础设施</li>
              <li>Access controls and authentication / 访问控制和身份验证</li>
              <li>Regular security assessments / 定期安全评估</li>
            </ul>
          </section>

          {/* Data Retention */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">7. Data Retention / 数据保留</h3>
            <p className="mb-4 text-gray-700">
              We retain your personal information for as long as necessary to provide our services and fulfill the purposes described in this policy. Interview recordings are typically retained for 12 months unless you request earlier deletion.
            </p>
            <p className="text-gray-600">
              我们在提供服务和实现本政策所述目的所需的时间内保留您的个人信息。面试录像通常保留12个月，除非您要求提前删除。
            </p>
          </section>

          {/* Your Rights */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">8. Your Rights / 您的权利</h3>
            <p className="mb-4 text-gray-700">You have the right to:</p>
            <p className="mb-4 text-gray-600">您有权：</p>
            <ul className="list-disc pl-6 text-gray-700">
              <li>Access your personal information / 访问您的个人信息</li>
              <li>Correct inaccurate information / 更正不准确的信息</li>
              <li>Request deletion of your data / 请求删除您的数据</li>
              <li>Withdraw consent for data processing / 撤回数据处理同意</li>
              <li>Export your data in a portable format / 以可移植格式导出您的数据</li>
            </ul>
            <p className="mt-4 text-gray-700">
              To exercise these rights, please contact us at the email address below.
            </p>
            <p className="text-gray-600">
              如需行使这些权利，请通过以下邮箱联系我们。
            </p>
          </section>

          {/* WeChat Integration */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">9. WeChat Integration / 微信集成</h3>
            <p className="mb-4 text-gray-700">
              If you choose to log in using WeChat, we receive your WeChat OpenID and basic profile information (nickname, profile picture). We use this information solely for account authentication and do not access your WeChat contacts, messages, or other private data.
            </p>
            <p className="text-gray-600">
              如果您选择使用微信登录，我们会收到您的微信OpenID和基本资料信息（昵称、头像）。我们仅将此信息用于账户验证，不会访问您的微信联系人、消息或其他私人数据。
            </p>
          </section>

          {/* Updates to Policy */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">10. Changes to This Policy / 政策变更</h3>
            <p className="mb-4 text-gray-700">
              We may update this Privacy Policy from time to time. We will notify you of any material changes by posting the new policy on this page and updating the &quot;Last Updated&quot; date.
            </p>
            <p className="text-gray-600">
              我们可能会不时更新本隐私政策。如有重大变更，我们将在此页面发布新政策并更新"最后更新"日期。
            </p>
          </section>

          {/* Contact */}
          <section className="mb-10">
            <h3 className="text-xl font-semibold mb-4">11. Contact Us / 联系我们</h3>
            <p className="mb-4 text-gray-700">
              If you have questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <p className="mb-4 text-gray-600">
              如果您对本隐私政策或我们的数据处理有疑问，请联系我们：
            </p>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-gray-700"><strong>Email / 邮箱:</strong> privacy@zhimian.ai</p>
              <p className="text-gray-700"><strong>Platform / 平台:</strong> ZhiMian 智面</p>
            </div>
          </section>
        </div>

        {/* Back to Home */}
        <div className="mt-12 pt-8 border-t">
          <Link
            href="/"
            className="inline-flex items-center text-emerald-600 hover:text-emerald-700"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home / 返回首页
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t py-8 mt-12">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} ZhiMian 智面. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}
