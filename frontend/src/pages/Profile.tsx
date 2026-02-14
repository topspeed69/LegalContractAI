import React, { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { supabase } from "@/lib/supabase";

const Profile = () => {
  const { user, refreshUser } = useAuth();

  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.user_metadata?.full_name || "");
  const [loading, setLoading] = useState(false);

  // AI Credits
  const [credits, setCredits] = useState<number | null>(null);
  const [creditsLoading, setCreditsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setFullName(user.user_metadata?.full_name || "");
      fetchCredits();
    }
  }, [user]);

  const fetchCredits = async () => {
    if (!user) return;

    setCreditsLoading(true);

    const { data, error } = await supabase
      .from("user_credits")
      .select("credits_remaining")
      .eq("user_id", user.id)
      .single();

    if (error) {
      console.error("Credits fetch error:", error);
      toast.error("Failed to load AI credits");
    } else {
      setCredits(data?.credits_remaining ?? 0);
    }

    setCreditsLoading(false);
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const { error } = await supabase.auth.updateUser({
        data: { full_name: fullName },
      });

      if (error) throw error;

      await refreshUser();
      toast.success("Profile updated successfully");
      setIsEditing(false);
    } catch (error) {
      console.error(error);
      toast.error("Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-tight py-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="heading-2 mb-6">Profile Settings</h1>

        {/* AI Credits Widget */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>AI Usage</CardTitle>
          </CardHeader>

          <CardContent className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Remaining Credits</p>
              <p className="text-3xl font-bold">
                {creditsLoading ? "..." : credits}
              </p>
            </div>

            <Button variant="outline" size="sm" onClick={fetchCredits}>
              Refresh
            </Button>
          </CardContent>
        </Card>

        {/* Profile Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Profile Information</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              <Avatar className="h-20 w-20">
                <AvatarImage src={user?.user_metadata?.avatar_url} />
                <AvatarFallback className="text-lg">
                  {(user?.user_metadata?.full_name || user?.email || "U")[0].toUpperCase()}
                </AvatarFallback>
              </Avatar>

              <div>
                <h2 className="text-xl font-semibold">
                  {user?.user_metadata?.full_name || "Not set"}
                </h2>
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

        {/* Account Info */}
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <div>
              <Label>Email Address</Label>
              <p className="text-muted-foreground">{user?.email}</p>
            </div>

            <div>
              <Label>Account Created</Label>
              <p className="text-muted-foreground">
                {user?.created_at
                  ? new Date(user.created_at).toLocaleDateString()
                  : "N/A"}
              </p>
            </div>

            <div>
              <Label>Last Sign In</Label>
              <p className="text-muted-foreground">
                {user?.last_sign_in_at
                  ? new Date(user.last_sign_in_at).toLocaleDateString()
                  : "N/A"}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
