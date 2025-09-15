import React from "react";
import AIForm from "@/components/AIForm";
import { useInView } from "react-intersection-observer";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

const LawTemplate = () => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });
  
  const additionalFields = (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="template-type">Template Type</Label>
          <Select defaultValue="employment">
            <SelectTrigger>
              <SelectValue placeholder="Select template type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="employment">Employment Contract</SelectItem>
              <SelectItem value="nda">Non-Disclosure Agreement</SelectItem>
              <SelectItem value="lease">Lease Agreement</SelectItem>
              <SelectItem value="partnership">Partnership Agreement</SelectItem>
              <SelectItem value="services">Service Agreement</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="jurisdiction">Jurisdiction</Label>
          <Select defaultValue="us">
            <SelectTrigger>
              <SelectValue placeholder="Select jurisdiction" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="us">United States</SelectItem>
              <SelectItem value="eu">European Union</SelectItem>
              <SelectItem value="uk">United Kingdom</SelectItem>
              <SelectItem value="ca">Canada</SelectItem>
              <SelectItem value="au">Australia</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="specific-requirements">Specific Requirements (Optional)</Label>
        <Input 
          id="specific-requirements" 
          placeholder="Enter any specific clauses or requirements for your template"
        />
      </div>
    </div>
  );
  
  return (
    <div className="container-tight py-16" ref={ref}>
      <div className={cn(
        "transition-all duration-500",
        inView ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      )}>
        <AIForm 
          title="Law Template Generation"
          description="Generate customized legal templates tailored to your specific needs and jurisdiction requirements."
          placeholder="Describe what kind of legal template you need..."
          taskType="law-template"
          additionalFields={additionalFields}
        />
      </div>
    </div>
  );
};

export default LawTemplate;
