import React, { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { supabase } from "@/lib/supabase";
import { Progress } from "@/components/ui/progress";
import { getUserCredits } from "@/services/usage";
import { Cpu, Zap, Check, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

// Define CreditInfo type based on the new state structure
interface CreditInfo {
  used: number;
  total: number;
  remaining: number;
}

const Profile = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.user_metadata?.full_name || "");
  const [loading, setLoading] = useState(false);
  const [credits, setCredits] = useState<CreditInfo>({
    used: 0,
    total: 5,
    remaining: 5
  });
  const [provider, setProvider] = useState(user?.user_metadata?.llm_provider || "nvidia");

  useEffect(() => {
    const fetchCredits = async () => {
      if (user) {
        const data = await getUserCredits(user.id);
        setCredits(data);
      }
    };
    fetchCredits();
  }, [user]);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { error } = await supabase.auth.updateUser({
        data: { full_name: fullName }
      });

      if (error) throw error;

      await refreshUser();
      toast.success("Profile updated successfully");
      setIsEditing(false);
    } catch (error) {
      toast.error("Failed to update profile");
      console.error("Update error:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateLLMProvider = async (newProvider: 'nvidia') => {
    try {
      setProvider(newProvider);
      const { error } = await supabase.auth.updateUser({
        data: { llm_provider: newProvider }
      });
      if (error) throw error;
      await refreshUser();
      toast.success("Default AI set to Nvidia NIM (Kimi)");
    } catch (error) {
      toast.error("Failed to update AI preference");
      console.error("Provider update error:", error);
    }
  };

  const creditPercentage = Math.min(100, Math.round((credits.used / credits.total) * 100));

  return (
    <div className="container-tight py-8 space-y-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="heading-2 mb-2">Account Settings</h1>
          <p className="text-muted-foreground">Manage your profile, subscription, and AI preferences.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Main Info */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your personal details</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4 mb-6">
                <Avatar className="h-20 w-20 border-2 border-primary/10">
                  <AvatarImage src={user?.user_metadata?.avatar_url} />
                  <AvatarFallback className="text-lg bg-primary/5 text-primary">
                    {(user?.user_metadata?.full_name || user?.email || "U")[0].toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h2 className="text-xl font-semibold">{user?.user_metadata?.full_name || "Not set"}</h2>
                  <p className="text-sm text-muted-foreground">{user?.email}</p>
                </div>
              </div>

              {isEditing ? (
                <form onSubmit={handleUpdateProfile} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div className="flex space-x-2">
                    <Button type="submit" disabled={loading}>
                      {loading ? "Saving..." : "Save Changes"}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setIsEditing(false);
                        setFullName(user?.user_metadata?.full_name || "");
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              ) : (
                <Button variant="outline" onClick={() => setIsEditing(true)}>
                  Edit Profile
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Credits Box */}
          <Card className="relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
              <Zap className="h-12 w-12 text-primary" />
            </div>
            <CardHeader>
              <CardTitle className="text-lg">AI Credits</CardTitle>
              <CardDescription>Monthly usage limit</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-3xl font-bold">{credits.total - credits.used}</span>
                <span className="text-sm text-muted-foreground mb-1">/{credits.total} left</span>
              </div>
              <Progress value={creditPercentage} className="h-2" />
              <p className="text-xs text-muted-foreground">
                Current usage is {creditPercentage}%. Credits reset on the 1st of every month.
              </p>
              <Link to="/pricing">
                <Button variant="link" className="p-0 h-auto text-primary text-xs">Upgrade Plan</Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* LLM Provider Selection */}
        <Card>
          <CardHeader>
            <CardTitle>AI Intelligence Model</CardTitle>
            <CardDescription>Choose the default LLM provider for your contract drafting and analysis.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-4">
              <div
                onClick={() => updateLLMProvider('nvidia')}
                className={cn(
                  "relative flex flex-col p-4 rounded-xl border-2 cursor-pointer transition-all hover:border-primary/50",
                  provider === 'nvidia' ? "border-primary bg-primary/5 shadow-md" : "border-border bg-transparent opacity-80"
                )}
              >
                {provider === 'nvidia' && <Check className="absolute top-3 right-3 h-4 w-4 text-primary" />}
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600">
                    <Zap className="h-6 w-6" />
                  </div>
                  <span className="font-bold">Nvidia NIM (Kimi) Intelligence Engine</span>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  State-of-the-art legal reasoning powered by Moonshot AI Kimi-K2. Optimized for contract drafting, compliance, and legal research with massive context support.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Security / Other */}
        <Card>
          <CardHeader>
            <CardTitle>Security & Privacy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4 text-sm">
              <ShieldCheck className="h-5 w-5 text-emerald-600" />
              <div>
                <p className="font-medium">Confidential Processing</p>
                <p className="text-muted-foreground">Your data is never used for model training. Documents stay secure.</p>
              </div>
            </div>
            <div className="pt-4 border-t flex justify-end">
              <Button variant="ghost" className="text-destructive hover:bg-destructive/5 hover:text-destructive text-xs">Delete Account</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
