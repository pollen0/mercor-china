import Link from 'next/link'

export default function NotFound() {
  return (
    <main className="min-h-screen bg-white flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <div className="mb-8">
          <h1 className="text-8xl font-semibold text-stone-200">404</h1>
        </div>
        <h2 className="text-2xl font-semibold text-stone-900 mb-4">
          Page not found
        </h2>
        <p className="text-stone-500 mb-8">
          Sorry, we couldn&apos;t find the page you&apos;re looking for. It might have been
          moved or doesn&apos;t exist.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 bg-stone-900 text-white rounded-full hover:bg-stone-800 transition-colors"
          >
            Go home
          </Link>
          <Link
            href="/candidate/login"
            className="inline-flex items-center justify-center px-6 py-3 border border-stone-200 text-stone-700 rounded-full hover:bg-stone-50 transition-colors"
          >
            Sign in
          </Link>
        </div>
      </div>
    </main>
  )
}
