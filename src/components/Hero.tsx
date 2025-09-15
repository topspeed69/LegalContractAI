
import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

const Hero: React.FC = () => {
  return (
    <div className="relative py-20 md:py-32 overflow-hidden">
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-background to-background/50"></div>
        <div className="absolute opacity-5">
          <div className="absolute -top-40 -left-40 h-[40rem] w-[40rem] rounded-full bg-highlight blur-3xl"></div>
          <div className="absolute -bottom-40 -right-40 h-[40rem] w-[40rem] rounded-full bg-highlight blur-3xl"></div>
        </div>
      </div>

      <div className="container-tight relative">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary text-foreground text-sm font-medium mb-6 animate-fade-in">
              <span className="flex h-2 w-2 rounded-full bg-[hsl(var(--highlight))] animate-pulse-soft"></span>
              AI-Powered Legal Assistant
            </div>
            
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-6 animate-fade-in [animation-delay:200ms]">
              <span className="block">Your Legal Work,</span>
              <span className="highlight-text">Automated.</span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground mb-10 animate-fade-in [animation-delay:400ms] max-w-2xl mx-auto">
              Generate case summaries, draft contracts, and ensure compliance with precision and efficiency. 
              <span className="highlight-text font-medium"> Save 10+ hours per week.</span>
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in [animation-delay:600ms]">
              <Link 
                to="/case-summary" 
                className="btn-highlight px-8 py-3 text-base sm:text-lg font-medium flex items-center justify-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="h-5 w-5" />
              </Link>
              <Link 
                to="#features" 
                className="px-8 py-3 text-base sm:text-lg font-medium border border-border rounded-md hover:bg-secondary transition-colors"
              >
                See How It Works
              </Link>
            </div>
          </div>
          
          <div className="mt-16 relative mx-auto max-w-4xl animate-fade-in [animation-delay:800ms]">
            <div className="rounded-xl overflow-hidden shadow-2xl border border-border/40">
              <img 
                src="https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80" 
                alt="LegalAssist Dashboard" 
                className="w-full"
              />
            </div>
            <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 bg-card border border-border/60 shadow-lg rounded-lg px-6 py-4 w-4/5 mx-auto text-center">
              <p className="font-medium">Trusted by <span className="highlight-text">2,500+</span> legal professionals worldwide</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;
