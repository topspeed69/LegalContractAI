import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { GavelIcon } from "lucide-react";

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background dark:bg-black">
      <div className="text-center space-y-6">
        <div className="flex justify-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center text-white dark:bg-[hsl(var(--highlight))]">
            <GavelIcon className="h-8 w-8" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mb-2">404 - Page Not Found</h1>
        <p className="text-muted-foreground mb-8 max-w-md">
          Sorry, the page you are looking for doesn't exist or has been moved.
        </p>
        <Button asChild>
          <Link to="/">Return Home</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
