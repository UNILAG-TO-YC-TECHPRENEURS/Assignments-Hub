import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import TokenGenerationPage from "./TokenGenerationPage";
import GenerateAssignmentPage from "./GenerateAssignmentPage";

function Navigation() {
  return (
    <nav className="fixed bottom-4 left-1/2 z-50 flex -translate-x-1/2 gap-4 rounded-full bg-background-dark/80 px-6 py-3 backdrop-blur-md border border-primary/20">
      <Link
        to="/muslim"
        className="text-sm font-medium text-slate-400 transition-colors hover:text-primary"
      >
        Token Generator
      </Link>
      <span className="text-slate-600">|</span>
      <Link
        to="/assignment"
        className="text-sm font-medium text-slate-400 transition-colors hover:text-primary"
      >
        Assignment Generator
      </Link>
    </nav>
  );
}

export default function App() {
  return (
    <Router>
      {/* <Navigation /> */}
      <Routes>
        <Route path="/muslim" element={<TokenGenerationPage />} />
        <Route path="/assignment" element={<GenerateAssignmentPage />} />
        {/* Redirect root to assignment page by default */}
        <Route path="/" element={<GenerateAssignmentPage />} />
      </Routes>
    </Router>
  );
}