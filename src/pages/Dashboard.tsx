import React from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent } from "@/components/ui/card";
import { FileText, Search, CheckCircle, PenSquare, Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { RecentActivity } from "@/components/RecentActivity";
import { AICredits } from "@/components/AICredits";

const Dashboard = () => {
  const { user } = useAuth();
  
  const features = [
    {
      id: "case-summary",
      title: "Case Summarization",
      description: "Generate concise summaries",
      icon: FileText,
      path: "/case-summary",
      color: "bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
    },
    {
      id: "loophole-detection",
      title: "Loophole Detection",
      description: "Identify legal risks",
      icon: Search,
      path: "/loophole-detection",
      color: "bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300"
    },
    {
      id: "clause-classification",
      title: "Clause Classification",
      description: "Analyze clauses",
      icon: CheckCircle,
      path: "/clause-classification",
      color: "bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300"
    },
    {
      id: "contract-drafting",
      title: "Contract Drafting",
      description: "Create contracts with AI",
      icon: PenSquare,
      path: "/contract-drafting",
      color: "bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300"
    },
    {
      id: "compliance-check",
      title: "Compliance Check",
      description: "Verify regulatory compliance",
      icon: Shield,
      path: "/compliance-check",
      color: "bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"
    }
  ];

  return (
    <div className="container-tight py-8">
      <div className="mb-8">
        <h1 className="heading-2 mb-2">Welcome back, {user?.user_metadata.full_name || 'User'}</h1>
        <p className="text-muted-foreground">Access our AI-powered legal tools</p>
      </div>
      
      <div className="space-y-8">
        <div className="grid gap-4 md:grid-cols-2">
          {features.map((feature) => (
            <Link key={feature.id} to={feature.path}>
              <Card className="h-full transition-colors hover:bg-muted/50">
                <CardContent className="p-6">
                  <div className={`w-12 h-12 rounded-lg mb-4 flex items-center justify-center ${feature.color}`}>
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        <div className="grid gap-6">
          <Card>
            <CardContent className="p-6">
              <RecentActivity />
            </CardContent>
          </Card>

          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardContent className="p-6">
                <h2 className="text-lg font-medium mb-4">Analytics</h2>
                <div className="text-muted-foreground text-center py-8">
                  Analytics dashboard coming soon
                </div>
              </CardContent>
            </Card>
            <AICredits />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;