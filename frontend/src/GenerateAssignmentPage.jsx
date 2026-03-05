import React, { useState } from 'react';

const GenerateAssignmentPage = () => {
  const [token, setToken] = useState('');
  const [name, setName] = useState('');
  const [matric, setMatric] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle form submission
    console.log({ token, name, matric, email });
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-gradient-mesh">
      {/* Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-primary/10 bg-background-dark/50 px-6 py-4 backdrop-blur-md lg:px-20">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold tracking-tight text-slate-100">
              Assignment Hub
            </h2>
          </div>

          <div className="flex items-center gap-6">
            <nav className="hidden items-center gap-8 md:flex">
              <a
                href="#"
                className="border-b-2 border-primary pb-1 text-sm font-semibold text-primary"
              >
                COS201
              </a>
              <a
                href="#"
                className="text-sm font-medium text-slate-400 transition-colors hover:text-slate-100"
              >
                CSC205
              </a>
            </nav>

            <button className="flex h-10 w-10 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary transition-all hover:bg-primary/20">
              <span className="material-symbols-outlined text-xl">
                account_circle
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative flex flex-1 flex-col items-center justify-center px-4 py-12">
        {/* Decorative Elements */}
        <div className="pointer-events-none absolute left-1/4 top-1/4 h-64 w-64 rounded-full bg-primary/10 blur-[100px]"></div>
        <div className="pointer-events-none absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-primary/5 blur-[120px]"></div>

        <div className="glass-card relative z-10 w-full max-w-[540px] rounded-xl p-8 shadow-2xl lg:p-10">
          <div className="mb-8 text-center">
            <h1 className="mb-2 text-3xl font-bold tracking-tight text-white lg:text-4xl">
              Generate Assignment
            </h1>
            <p className="text-sm text-slate-400">
              Fill in your details to auto-generate your course work
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Access Token */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">
                Access Token
              </label>
              <div className="group relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-xl text-slate-500 transition-colors group-focus-within:text-primary">
                  key
                </span>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 py-3.5 pl-12 pr-4 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="Enter your access token..."
                />
              </div>
            </div>

            {/* Name and Matric */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">
                  Student Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 px-4 py-3.5 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., John Doe"
                />
              </div>

              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">
                  Matric Number
                </label>
                <input
                  type="text"
                  value={matric}
                  onChange={(e) => setMatric(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 px-4 py-3.5 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., U1234567"
                />
              </div>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">
                Email Address
              </label>
              <div className="group relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-xl text-slate-500 transition-colors group-focus-within:text-primary">
                  mail
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 py-3.5 pl-12 pr-4 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., john@example.com"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="glow-hover group mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-4 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90"
            >
              <span>Generate Assignment</span>
              <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">
                auto_fix_high
              </span>
            </button>
          </form>

          {/* Footer Status */}
          <div className="mt-8 flex items-center justify-between border-t border-primary/10 pt-6 text-xs uppercase tracking-widest text-slate-500">
            <span>Secured Session</span>
            <div className="flex gap-2">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500"></span>
              <span>System Online</span>
            </div>
          </div>
        </div>

        {/* Bottom Helper Links */}
        <div className="mt-12 flex gap-8 text-sm text-slate-500">
          <a href="#" className="transition-colors hover:text-primary">
            Documentation
          </a>
          <a href="#" className="transition-colors hover:text-primary">
            Support
          </a>
          <a href="#" className="transition-colors hover:text-primary">
            Privacy
          </a>
        </div>
      </main>

      {/* Background Gradient Footer */}
      <div className="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-transparent via-primary/50 to-transparent"></div>
    </div>
  );
};

export default GenerateAssignmentPage;