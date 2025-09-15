import React from "react";
import AIForm from "@/components/AIForm";

const ClauseClassification = () => {
  return (
    <AIForm
      title="Clause Classification"
      description="Automatically analyze and categorize legal clauses to understand their purpose and implications."
      placeholder="Paste your legal document or contract clauses here for classification..."
      taskType="clause-classification"
    />
  );
};

export default ClauseClassification;