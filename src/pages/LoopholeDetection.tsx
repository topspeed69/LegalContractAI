import React from "react";
import AIForm from "@/components/AIForm";

const LoopholeDetection = () => {
  return (
    <AIForm
      title="Loophole Detection"
      description="Identify potential legal vulnerabilities and risks in your documents using advanced AI analysis."
      placeholder="Paste your legal document here for loophole detection..."
      taskType="loophole-detection"
    />
  );
};

export default LoopholeDetection;