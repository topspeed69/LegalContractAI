import React from "react";
import AIForm from "@/components/AIForm";
import { useInView } from "react-intersection-observer";
import { cn } from "@/lib/utils";

const CaseSummary = () => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });
  
  return (
    <div className="legal-bg py-20 px-4 sm:px-6 lg:px-8" ref={ref}>
      <div className={cn(
        "transition-all duration-500 max-w-4xl mx-auto",
        inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      )}>
        <AIForm 
          title="Case Summary"
          description="Generate concise summaries of legal cases using AI."
          placeholder="Enter the case details you want to summarize..."
          taskType="case-summary"
        />
      </div>
    </div>
  );
};

export default CaseSummary;
