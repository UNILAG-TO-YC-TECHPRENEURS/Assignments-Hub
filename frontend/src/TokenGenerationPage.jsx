import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faMagic,
  faAdd,
  faCopy,
  faCheck,
  faUserCircle,
  faKey,
  faBolt,
  faHistory,
  faShield,
  faCircle,
  faSpinner,
  faWarning,
} from '@fortawesome/free-solid-svg-icons';
import { tokenAPI } from './api';

const TokenGenerationPage = () => {
  const [latestToken, setLatestToken] = useState(null);
  const [copied, setCopied] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  const [activeNav, setActiveNav] = useState('cos201');
  const [tokens, setTokens] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  // Add dark class to html element when component mounts
  useEffect(() => {
    document.documentElement.classList.add('dark');
    return () => {
      document.documentElement.classList.remove('dark');
    };
  }, []);

  // Load token history on mount
  useEffect(() => {
    loadTokenHistory();
  }, []);

  const loadTokenHistory = async () => {
    try {
      const data = await tokenAPI.getAllTokens();
      setTokens(data);
    } catch (error) {
      console.error('Failed to load token history:', error);
    }
  };

  const generateToken = async () => {
    setError('');
    setIsGenerating(true);
    
    try {
      // Call the actual API to generate token
      const response = await tokenAPI.generateToken();
      
      // Format token with # prefix if not already present
      const tokenValue = response.token.startsWith('#') 
        ? response.token 
        : `#${response.token}`;
      
      setLatestToken(tokenValue);
      setCopied(false);
      
      // Refresh token history
      await loadTokenHistory();
      
    } catch (error) {
      setError(error.message || 'Failed to generate token. Please try again.');
      console.error('Token generation error:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = () => {
    if (!latestToken) return;
    
    // Remove # prefix for actual copying if needed
    const tokenToCopy = latestToken.startsWith('#') 
      ? latestToken.substring(1) 
      : latestToken;
      
    navigator.clipboard.writeText(tokenToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-background-light font-display text-slate-900 dark:bg-background-dark dark:text-slate-100">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/5 px-6 py-4 backdrop-blur-md dark:border-primary/10 dark:bg-background-dark/50 lg:px-40">
        <div className="mx-auto flex max-w-[1200px] items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-bold tracking-tight">Assignment Hub</h2>
          </div>

          <div className="flex items-center gap-8">
            <nav className="hidden items-center gap-8 md:flex">
              <button
                onClick={() => setActiveNav('cos201')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeNav === 'cos201' ? 'text-primary' : 'text-slate-400'
                }`}
              >
                COS201
              </button>
              <button
                onClick={() => setActiveNav('csc205')}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  activeNav === 'csc205' ? 'text-primary' : 'text-slate-400'
                }`}
              >
                CSC205
              </button>
            </nav>

            <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full border border-primary/30 bg-primary/20">
              <FontAwesomeIcon icon={faUserCircle} className="h-6 w-6 text-primary" />
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="mt-4 flex justify-center gap-6 md:hidden">
          <button
            onClick={() => setActiveNav('cos201')}
            className={`text-sm font-medium transition-colors ${
              activeNav === 'cos201' ? 'text-primary' : 'text-slate-400'
            }`}
          >
            COS201
          </button>
          <button
            onClick={() => setActiveNav('csc205')}
            className={`text-sm font-medium transition-colors ${
              activeNav === 'csc205' ? 'text-primary' : 'text-slate-400'
            }`}
          >
            CSC205
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-[1200px] px-6 py-8 lg:px-40 lg:py-12">
        {/* Hero / Action Section */}
        <div className="mb-12 flex flex-col items-center text-center md:mb-16">
          <div className="mb-4 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-xs font-bold uppercase tracking-widest text-primary">
            Admin Control Panel
          </div>

          <h1 className="mb-3 text-3xl font-black tracking-tight text-white md:text-4xl lg:mb-4 lg:text-5xl">
            Token Management
          </h1>

          <p className="mb-8 max-w-lg text-base text-slate-400 md:mb-10 md:text-lg">
            Generate secure access tokens for student assignments. Each token is unique and
            trackable.
          </p>

          {/* Error Message */}
          {error && (
            <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-500">
              <FontAwesomeIcon icon={faWarning} />
              <span>{error}</span>
            </div>
          )}

          <button
            onClick={generateToken}
            disabled={isGenerating}
            className="group relative flex items-center gap-3 rounded-xl bg-primary px-6 py-3 text-base font-bold text-white shadow-lg shadow-primary/20 transition-all hover:bg-primary/90 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 md:px-8 md:py-4 md:text-lg"
          >
            {isGenerating ? (
              <FontAwesomeIcon icon={faSpinner} spin className="text-lg" />
            ) : (
              <FontAwesomeIcon
                icon={faAdd}
                className="transition-transform group-hover:rotate-90"
              />
            )}
            {isGenerating ? 'Generating...' : 'Generate New Token'}
          </button>
        </div>

        {/* Generated Token Display */}
        {latestToken && (
          <div className="glass relative overflow-hidden rounded-2xl p-6 md:p-8">
            <div className="absolute right-0 top-0 p-4">
              <span className="relative flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex h-3 w-3 rounded-full bg-primary"></span>
              </span>
            </div>

            <div className="flex flex-col items-center gap-4 md:gap-6">
              <p className="text-center text-xs font-medium uppercase tracking-[0.2em] text-slate-400 md:text-sm">
                Latest Generated Token
              </p>

              <div className="group relative flex w-full max-w-md items-center justify-between gap-2 rounded-2xl border border-primary/20 bg-background-dark/40 p-4 backdrop-blur-sm md:p-4">
                <span className="token-glow font-mono text-l font-black tracking-widest text-primary md:text-2l lg:text-3l">
                  {latestToken}
                </span>

                <button
                  onClick={copyToClipboard}
                  className="relative rounded-lg p-2 text-slate-400 transition-colors hover:bg-primary/10 hover:text-primary"
                  title="Copy to clipboard"
                >
                  <FontAwesomeIcon icon={copied ? faCheck : faCopy} className="text-lg md:text-xl" />

                  {/* Toast notification */}
                  <div
                    className={`absolute -top-12 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-lg bg-slate-800 px-3 py-2 text-xs text-white transition-opacity ${
                      copied ? 'opacity-100' : 'opacity-0'
                    }`}
                  >
                    Copied!
                  </div>
                </button>
              </div>

              {/* Token Stats */}
              <div className="mt-2 flex gap-6 text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon icon={faKey} className="text-primary" />
                  <span>8-character secure token</span>
                </div>
                <div className="flex items-center gap-2">
                  <FontAwesomeIcon icon={faBolt} className="text-primary" />
                  <span>One-time use</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 rounded-lg border border-primary/20 bg-background-dark/30 px-4 py-2 text-xs text-slate-400 transition-all hover:border-primary/40 hover:text-primary"
          >
            <FontAwesomeIcon icon={faHistory} />
            <span>{showHistory ? 'Hide' : 'View'} Token History</span>
          </button>
          <button className="flex items-center gap-2 rounded-lg border border-primary/20 bg-background-dark/30 px-4 py-2 text-xs text-slate-400 transition-all hover:border-primary/40 hover:text-primary">
            <FontAwesomeIcon icon={faShield} />
            <span>Security Settings</span>
          </button>
        </div>

        {/* Token History Section */}
        {showHistory && tokens.length > 0 && (
          <div className="mt-8">
            <h3 className="mb-4 text-lg font-bold text-white">Recent Tokens</h3>
            <div className="space-y-2">
              {tokens.slice(0, 5).map((token, index) => (
                <div
                  key={token.id || index}
                  className="flex items-center justify-between rounded-lg border border-primary/10 bg-background-dark/20 p-3 backdrop-blur-sm"
                >
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm text-primary">
                      {token.token.startsWith('#') ? token.token : `#${token.token}`}
                    </span>
                    <button
                      onClick={() => {
                        const tokenToCopy = token.token.startsWith('#') 
                          ? token.token.substring(1) 
                          : token.token;
                        navigator.clipboard.writeText(tokenToCopy);
                        // Optional: Show temporary copied state for history items
                      }}
                      className="text-slate-500 hover:text-primary transition-colors"
                      title="Copy token"
                    >
                      <FontAwesomeIcon icon={faCopy} className="text-xs" />
                    </button>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    token.used 
                      ? 'bg-amber-500/10 text-amber-500' 
                      : 'bg-emerald-500/10 text-emerald-500'
                  }`}>
                    {token.used ? 'Used' : 'Available'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer Decoration */}
      <div className="fixed bottom-0 left-0 h-1 w-full bg-gradient-to-r from-transparent via-primary/50 to-transparent"></div>
    </div>
  );
};

export default TokenGenerationPage;