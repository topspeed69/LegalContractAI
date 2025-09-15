
import React from "react";
import { Link } from "react-router-dom";
import { useInView } from "react-intersection-observer";
import { cn } from "@/lib/utils";
import { FileText, FileCheck, Search, PenSquare, ArrowRight, Shield } from "lucide-react";

const Features: React.FC = () => {
  const features = [
    {
      id: "case-summary",
      title: "Case Summarization",
      description: "Upload legal documents to get concise, accurate summaries capturing key case details.",
      icon: FileText,
      path: "/case-summary",
      color: "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
    },
    {
      id: "clause-classification",
      title: "Clause Classification",
      description: "Automatically categorize and analyze legal clauses with precision and clarity.",
      icon: FileCheck,
      path: "/clause-classification",
      color: "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300"
    },
    {
      id: "loophole-detection",
      title: "Loophole Detection",
      description: "Identify potential legal risks and vulnerabilities in your documents.",
      icon: Search,
      path: "/loophole-detection",
      color: "bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300"
    },
    {
      id: "contract-drafting",
      title: "Contract Drafting",
      description: "Create professional, comprehensive contracts with AI-powered assistance.",
      icon: PenSquare,
      path: "/contract-drafting",
      color: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300"
    },
    {
      id: "compliance-check",
      title: "Compliance Check",
      description: "Verify regulatory compliance and get detailed reports with risk assessments.",
      icon: Shield,
      path: "/compliance-check",
      color: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"
    }
  ];
  
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });
  
  return (
    <div id="features" className="py-24 relative" ref={ref}>
      <div className="absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[40rem] w-[40rem] rounded-full bg-highlight blur-3xl" />
        </div>
      </div>

      <div className="container-tight">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="label-sm animate-fade-in">Features</div>
          <h2 className="heading-2 mb-6 animate-fade-in [animation-delay:100ms]">
            Comprehensive Legal AI Solutions
          </h2>
          <p className="text-lg text-muted-foreground animate-fade-in [animation-delay:200ms]">
            Advanced AI tools to enhance legal document analysis, drafting, and risk assessment.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <div 
              key={feature.id} 
              className={cn(
                "rounded-xl p-6 transition-all duration-500 bg-card border border-border/50 card-shadow card-hover",
                inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8",
              )}
              style={{ 
                transitionDelay: `${(index + 1) * 100}ms`,
              }}
            >
              <div className={cn("w-12 h-12 rounded-md flex items-center justify-center mb-4", feature.color)}>
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground mb-4">{feature.description}</p>
              <Link 
                to={feature.path} 
                className="inline-flex items-center text-sm font-medium text-[hsl(var(--highlight))] hover:underline group"
              >
                Try Now
                <ArrowRight className="ml-1 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Features;
