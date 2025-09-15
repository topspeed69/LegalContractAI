
import React from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { LucideIcon, ArrowRight } from "lucide-react";

interface LegalTaskProps {
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  color: string;
  index: number;
}

const LegalTask: React.FC<LegalTaskProps> = ({
  title,
  description,
  icon: Icon,
  path,
  color,
  index,
}) => {
  return (
    <Card 
      className={cn(
        "overflow-hidden transition-all duration-500 hover:shadow-lg hover:-translate-y-1 border-0 card-shadow animate-slide-in bg-card group dark:border dark:border-[hsl(var(--highlight))/0.1] dark:neon-card",
      )}
      style={{ animationDelay: `${index * 100}ms` }}
    >
      <div className="p-6 flex flex-col h-full">
        <div className={cn("w-12 h-12 rounded-md flex items-center justify-center mb-5", color, "dark:animate-pulse-soft dark:shadow-md")}>
          <Icon className="h-6 w-6" />
        </div>
        
        <h3 className="text-xl font-semibold mb-3 dark:group-hover:neon-glow-text dark:group-hover:text-[hsl(var(--highlight))] transition-all duration-300">{title}</h3>
        <p className="text-muted-foreground text-sm mb-6 flex-grow">{description}</p>
        
        <Link to={path} className="mt-auto">
          <Button 
            variant="ghost" 
            className="px-0 hover:bg-transparent hover:text-[hsl(var(--highlight))] p-0 h-auto font-medium dark:neon-button group/btn"
          >
            <span>Get Started</span>
            <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Button>
        </Link>
      </div>
    </Card>
  );
};

export default LegalTask;
