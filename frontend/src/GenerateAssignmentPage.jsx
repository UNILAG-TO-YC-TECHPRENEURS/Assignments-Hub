import React, { useState } from 'react';
import { assignmentAPI } from './api';

const GenerateAssignmentPage = () => {
  const [course, setCourse]   = useState('cos201');
  const [token, setToken]     = useState('');
  const [name, setName]       = useState('');
  const [matric, setMatric]   = useState('');
  const [email, setEmail]     = useState('');
  const [isLoading, setIsLoading]               = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [error, setError]     = useState('');
  const [department, setDepartment] = useState('cs');
  const [fileLinks, setFileLinks] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setFileLinks(null);
    setIsLoading(true);

    try {
      // Both courses: single awaited call, blocks until backend task.get() resolves
      const response = course === 'cos201'
      ? await assignmentAPI.generateAssignment({ token, name, matric, email, department })
      : await assignmentAPI.generateAssignment205({ token, name, matric, email });

      setFileLinks(response.file_links);
      setShowSuccessModal(true);
    } catch (err) {
      setError(err.message || 'Failed to generate assignment. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle download of the complete ZIP archive
  const handleDownloadZip = () => {
    if (!fileLinks) return;
    const zipKey = course === 'cos201' ? 'COS201_Assignment.zip' : 'COS205_Assignment.zip';
    const zipUrl = fileLinks[zipKey];
    if (zipUrl) window.open(zipUrl, '_blank', 'noopener,noreferrer');
  };

  const closeModal = () => setShowSuccessModal(false);

  const switchCourse = (c) => {
    if (isLoading) return; // don't switch mid-generation
    setCourse(c);
    setError('');
    setFileLinks(null);
  };

  return (
    <div className="relative flex min-h-screen w-full flex-col overflow-x-hidden bg-gradient-mesh">

      {/* ── Success Modal ── */}
      {showSuccessModal && (
        <>
          <div className="fixed inset-0 z-[60] bg-slate-950/60 backdrop-blur-sm" onClick={closeModal} />
          <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
            <div className="w-full max-w-md animate-in zoom-in fade-in rounded-2xl border border-emerald-500/30 bg-slate-900/80 p-8 shadow-2xl shadow-emerald-500/10 backdrop-blur-xl flex flex-col items-center gap-6 text-center">

              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400">
                <span className="material-symbols-outlined text-5xl">check_circle</span>
              </div>

              <div className="flex flex-col gap-2">
                <h2 className="text-3xl font-bold tracking-tight text-white">Done!</h2>
                <p className="text-lg leading-relaxed text-slate-300">
                  Sent to <span className="font-semibold text-white">{email}</span>.
                  Check your inbox and spam folder.
                </p>
              </div>

              <div className="mt-2 flex w-full flex-col gap-3">
                {/* Main download button – now downloads the ZIP archive */}
                <button
                  onClick={handleDownloadZip}
                  disabled={!fileLinks}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-6 py-4 text-lg font-bold text-slate-950 transition-all hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="material-symbols-outlined">folder_zip</span>
                  Download ZIP
                </button>

                {/* List of all individual files (still available) */}
                {fileLinks && Object.keys(fileLinks).length > 1 && (
                  <div className="w-full rounded-xl border border-slate-700 bg-slate-800/50 p-4 text-left">
                    <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">All files</p>
                    <ul className="space-y-2">
                      {Object.entries(fileLinks).map(([filename, url]) => (
                        <li key={filename}>
                          <a
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-slate-300 transition-colors hover:text-emerald-400"
                          >
                            <span className="material-symbols-outlined text-base">
                              {filename.endsWith('.pdf')   ? 'picture_as_pdf' :
                               filename.endsWith('.ipynb') ? 'code'           :
                               filename.endsWith('.csv')   ? 'table_chart'    : 'image'}
                            </span>
                            {filename}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={closeModal}
                  className="mt-1 text-sm font-medium text-slate-500 transition-colors hover:text-slate-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* ── Navbar ── */}
      <header className="sticky top-0 z-50 w-full border-b border-primary/10 bg-background-dark/50 px-6 py-4 backdrop-blur-md lg:px-20">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight text-slate-100">Assignment Hub</h2>
          <div className="flex items-center gap-6">
            <nav className="hidden items-center gap-8 md:flex">
              {['cos201', 'cos205'].map(c => (
                <button
                  key={c}
                  onClick={() => switchCourse(c)}
                  className={`border-b-2 pb-1 text-sm font-semibold transition-colors ${
                    course === c
                      ? 'border-primary text-primary'
                      : 'border-transparent text-slate-400 hover:text-slate-100'
                  }`}
                >
                  {c === 'cos201' ? 'COS201' : 'CSC205'}
                </button>
              ))}
            </nav>
            <button className="flex h-10 w-10 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary transition-all hover:bg-primary/20">
              <span className="material-symbols-outlined text-xl">account_circle</span>
            </button>
          </div>
        </div>
        {/* Mobile tabs */}
        <div className="mt-4 flex justify-center gap-6 md:hidden">
          {['cos201', 'cos205'].map(c => (
            <button
              key={c}
              onClick={() => switchCourse(c)}
              className={`text-sm font-medium transition-colors ${
                course === c
                  ? 'border-b-2 border-primary pb-1 text-primary'
                  : 'text-slate-400'
              }`}
            >
              {c === 'cos201' ? 'COS201' : 'CSC205'}
            </button>
          ))}
        </div>
      </header>

      {/* ── Main ── */}
      <main className="relative flex flex-1 flex-col items-center justify-center px-4 py-12">
        <div className="pointer-events-none absolute left-1/4 top-1/4 h-64 w-64 rounded-full bg-primary/10 blur-[100px]" />
        <div className="pointer-events-none absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-primary/5 blur-[120px]" />

        <div className="glass-card relative z-10 w-full max-w-[540px] rounded-xl p-8 shadow-2xl lg:p-10">
          <div className="mb-8 text-center">
            <h1 className="mb-2 text-3xl font-bold tracking-tight text-white lg:text-4xl">
              {course === 'cos201' ? 'COS201 Assignment' : 'CSC205 Assignment'}
            </h1>
            <p className="text-sm text-slate-400">
              {course === 'cos201'
                ? 'Multiple linear regression with dataset'
                : 'Fourier analysis of energy demand'}
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">Access Token</label>
              <div className="group relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-xl text-slate-500 transition-colors group-focus-within:text-primary">key</span>
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 py-3.5 pl-12 pr-4 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="Enter your access token..."
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">Student Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 px-4 py-3.5 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., John Doe"
                  disabled={isLoading}
                  required
                />
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">Matric Number</label>
                <input
                  type="text"
                  value={matric}
                  onChange={(e) => setMatric(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 px-4 py-3.5 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., U1234567"
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            {course === 'cos201' && (
              <div className="space-y-2">
                <label className="block text-sm font-medium text-slate-300">Department</label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 px-4 py-3.5 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  disabled={isLoading}
                  required
                >
                  <option value="cs">Computer Science</option>
                  <option value="geo">Geosciences</option>
                  <option value="math">Mathematics</option>
                  <option value="math_edu">Mathematics Education</option>
                  <option value="chem">Chemistry</option>
                  <option value="stats">Statistics</option>
                  <option value="ds">Data Science</option>
                </select>
              </div>
            )}

            <div className="space-y-2">
              <label className="block text-sm font-medium text-slate-300">Email Address</label>
              <div className="group relative">
                <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-xl text-slate-500 transition-colors group-focus-within:text-primary">mail</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-primary/20 bg-background-dark/50 py-3.5 pl-12 pr-4 text-white placeholder:text-slate-500 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="e.g., john@example.com"
                  disabled={isLoading}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="glow-hover group mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-4 font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isLoading ? (
                <>
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                  <span>Solving your assignment...</span>
                </>
              ) : (
                <>
                  <span>Generate Assignment Solution</span>
                  <span className="material-symbols-outlined transition-transform group-hover:translate-x-1">auto_fix_high</span>
                </>
              )}
            </button>
          </form>

          {isLoading && (
            <p className="mt-5 text-center text-sm text-slate-400 animate-pulse">
              This usually takes 30–60 seconds. Please keep this tab open.
            </p>
          )}

          <div className="mt-8 flex items-center justify-between border-t border-primary/10 pt-6 text-xs uppercase tracking-widest text-slate-500">
            <span>Secured Session</span>
            <div className="flex gap-2">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
              <span>System Online</span>
            </div>
          </div>
        </div>

        <div className="mt-12 flex gap-8 text-sm text-slate-500">
          <a href="#" className="transition-colors hover:text-primary">Documentation</a>
          <a href="#" className="transition-colors hover:text-primary">Support</a>
          <a href="#" className="transition-colors hover:text-primary">Privacy</a>
        </div>
      </main>

      <div className="absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
    </div>
  );
};

export default GenerateAssignmentPage;