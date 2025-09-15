import React from "react";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, File, Check, PenSquare, ArrowRight, Users, Shield, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import LegalTask from "@/components/LegalTask";

const Index: React.FC = () => {
  return (
    <div>
      <Hero />
      <Features />
    </div>
  );
};

export default Index;
