import React from "react";
import AIForm from "@/components/AIForm";
import { useInView } from "react-intersection-observer";
import { cn } from "@/lib/utils";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";

const ContractDrafting = () => {
  const { ref, inView } = useInView({
    triggerOnce: true,
    threshold: 0.1,
  });
  
  const additionalFields = (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="contract-type">Contract Type</Label>
          <Select defaultValue="service">
            <SelectTrigger>
              <SelectValue placeholder="Select contract type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="service">Service Agreement</SelectItem>
              <SelectItem value="employment">Employment Contract</SelectItem>
              <SelectItem value="nda">Non-Disclosure Agreement</SelectItem>
              <SelectItem value="purchase">Purchase Agreement</SelectItem>
              <SelectItem value="lease">Lease Agreement</SelectItem>
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
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="party-a">Party A (Your Client)</Label>
          <Input id="party-a" placeholder="Full legal name" />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="party-b">Party B (Counter-party)</Label>
          <Input id="party-b" placeholder="Full legal name" />
        </div>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="key-terms">Key Contract Terms</Label>
        <Textarea 
          id="key-terms" 
          placeholder="List key terms, deliverables, payment information, term length, etc."
          className="min-h-[100px]"
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
          title="Contract Drafting"
          description="Create professional contracts with AI assistance, ensuring comprehensive coverage of terms and conditions."
          placeholder="Describe the contract you need..."
          taskType="contract-drafting"
          additionalFields={additionalFields}
        />
      </div>
    </div>
  );
};

export default ContractDrafting;
