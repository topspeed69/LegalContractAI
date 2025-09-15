import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate, useLocation, Outlet } from "react-router-dom";
import { ThemeProvider } from "@/components/ThemeProvider";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import Layout from "@/components/Layout";
import Dashboard from "@/pages/Dashboard";
import Index from "@/pages/Index";
import CaseSummary from "@/pages/CaseSummary";
import LawTemplate from "@/pages/LawTemplate";
import ComplianceCheck from "@/pages/ComplianceCheck";
import ContractDrafting from "@/pages/ContractDrafting";
import LoopholeDetection from "@/pages/LoopholeDetection";
import ClauseClassification from "@/pages/ClauseClassification";
import NotFound from "@/pages/NotFound";
import About from "@/pages/About";
import Pricing from "@/pages/Pricing";
import Contact from "@/pages/Contact";
import Careers from "@/pages/Careers";
import Api from "@/pages/Api";
import Login from "@/pages/Login";
import Signup from "@/pages/Signup";
import PrivacyPolicy from "@/pages/PrivacyPolicy";
import TermsOfService from "@/pages/TermsOfService";
import Profile from "@/pages/Profile";
import Settings from "@/pages/Settings";
import ActivityHistory from "@/pages/ActivityHistory";
import ErrorBoundary from "@/components/ErrorBoundary";

const queryClient = new QueryClient();

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>; // Show a loading state while authentication is being checked
  }

  if (!user) {
    return <Navigate to="/login" replace />; // Redirect to login if not authenticated
  }

  return <>{children}</>; // Render children if authenticated
};

const PublicRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user } = useAuth();

  if (user) {
    return <Navigate to="/dashboard" replace />; // Redirect to dashboard if already logged in
  }

  return <>{children}</>; // Render children if not authenticated
};

const App = () => (
  <ErrorBoundary>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <BrowserRouter>
            <AuthProvider>
              <Routes>
                <Route element={<Layout><Outlet /></Layout>}>
                  {/* Public routes */}
                  <Route path="/" element={<Index />} />
                  <Route path="/about" element={<About />} />
                  <Route path="/pricing" element={<Pricing />} />
                  <Route path="/contact" element={<Contact />} />
                  <Route path="/careers" element={<Careers />} />
                  <Route path="/api" element={<Api />} />
                  <Route path="/privacy" element={<PrivacyPolicy />} />
                  <Route path="/terms" element={<TermsOfService />} />
                  
                  {/* Auth routes */}
                  <Route 
                    path="/login" 
                    element={
                      <PublicRoute>
                        <Login />
                      </PublicRoute>
                    } 
                  />
                  <Route 
                    path="/signup" 
                    element={
                      <PublicRoute>
                        <Signup />
                      </PublicRoute>
                    } 
                  />

                  {/* Protected routes */}
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <Profile />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/settings"
                    element={
                      <ProtectedRoute>
                        <Settings />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/case-summary"
                    element={
                      <ProtectedRoute>
                        <CaseSummary />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/law-template"
                    element={
                      <ProtectedRoute>
                        <LawTemplate />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/compliance-check"
                    element={
                      <ProtectedRoute>
                        <ComplianceCheck />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/contract-drafting"
                    element={
                      <ProtectedRoute>
                        <ContractDrafting />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/loophole-detection"
                    element={
                      <ProtectedRoute>
                        <LoopholeDetection />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/clause-classification"
                    element={
                      <ProtectedRoute>
                        <ClauseClassification />
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/activity-history"
                    element={
                      <ProtectedRoute>
                        <ActivityHistory />
                      </ProtectedRoute>
                    }
                  />

                  {/* Fallback route */}
                  <Route path="*" element={<NotFound />} />
                </Route>
              </Routes>
              <Toaster />
              <Sonner />
            </AuthProvider>
          </BrowserRouter>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </ErrorBoundary>
);

export default App;
