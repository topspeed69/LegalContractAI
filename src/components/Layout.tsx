import React from "react";
import { Link, Outlet } from "react-router-dom";
import { GavelIcon } from "lucide-react";
import Header from "@/components/Header";

const Layout: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen legal-pattern-bg">
      <Header />
      
      <main className="flex-1 relative overflow-hidden">
        {children || <Outlet />}
      </main>
      
      <footer className="border-t border-border/40 py-8 relative overflow-hidden mt-auto">
        <div className="absolute inset-0 legal-bg-overlay bg-legal-pattern opacity-5"></div>
        <div className="container-tight relative z-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <Link to="/" className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white dark:bg-[hsl(var(--highlight))] dark:animate-pulse-soft">
                  <GavelIcon className="h-4 w-4" />
                </div>
                <div className="font-medium">
                  <span className="font-semibold dark:text-[hsl(var(--highlight))] dark:text-shadow-sm">Legal</span>Assist
                </div>
              </Link>
              <p className="text-sm text-muted-foreground">
                AI-powered legal assistant to help with your legal tasks.
              </p>
            </div>
            
            <div>
              <h3 className="font-medium mb-4 dark:text-[hsl(var(--highlight))] dark:text-shadow-sm">Services</h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/case-summary" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Case Summarization
                  </Link>
                </li>
                <li>
                  <Link to="/law-template" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Law Templates
                  </Link>
                </li>
                <li>
                  <Link to="/compliance-check" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Compliance Check
                  </Link>
                </li>
                <li>
                  <Link to="/contract-drafting" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Contract Drafting
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-4 dark:text-[hsl(var(--highlight))] dark:text-shadow-sm">Company</h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/about" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link to="/careers" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Careers
                  </Link>
                </li>
                <li>
                  <Link to="/contact" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Contact
                  </Link>
                </li>
                <li>
                  <Link to="/pricing" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Pricing
                  </Link>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-medium mb-4 dark:text-[hsl(var(--highlight))] dark:text-shadow-sm">Legal</h3>
              <ul className="space-y-3">
                <li>
                  <Link to="/privacy" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Privacy Policy
                  </Link>
                </li>
                <li>
                  <Link to="/terms" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    Terms of Service
                  </Link>
                </li>
                <li>
                  <Link to="/api" className="text-sm text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                    API
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-border/40 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} LegalAssist. All rights reserved.
            </p>
            <div className="flex gap-4">
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                Twitter
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                LinkedIn
              </a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors dark:hover:text-[hsl(var(--highlight))] dark:hover:text-shadow-sm">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
