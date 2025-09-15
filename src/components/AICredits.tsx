import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { getUserCredits, CreditInfo } from "@/services/usage";
import { useAuth } from "@/contexts/AuthContext";

export function AICredits() {
  const [credits, setCredits] = useState<CreditInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    async function loadCredits() {
      if (!user) return;
      
      try {
        const creditInfo = await getUserCredits(user.id);
        setCredits(creditInfo);
      } catch (error) {
        console.error('Failed to load credits:', error);
      } finally {
        setLoading(false);
      }
    }

    loadCredits();
  }, [user]);

  if (!credits || loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-medium">AI Credits</h2>
              <span className="text-sm text-muted-foreground">Loading...</span>
            </div>
            <Progress value={0} className="h-2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const usedPercentage = (credits.used / credits.total) * 100;

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-medium">AI Credits</h2>
            <span className="text-sm text-muted-foreground">{credits.remaining} remaining</span>
          </div>
          <Progress value={usedPercentage} className="h-2" />
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>{credits.used} used</span>
            <span>{credits.total} total</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}