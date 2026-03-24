import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Loader2, Check } from "lucide-react";
import { aiClient } from "@/lib/ai-clients";
import PipelineViewer, { DEFAULT_STAGES, COMPLIANCE_STAGES, RESEARCH_STAGES, SUMMARY_STAGES } from "@/components/PipelineViewer";
import { TaskType, AIFormProps } from '@/types/ai';
import { supabase } from '@/lib/supabase';
import { useAuth } from '@/contexts/AuthContext';
import { recordUsage } from '@/services/usage';
import GeneratedReport from "@/components/GeneratedReport";

interface UserCredits {
  id: string;
  user_id: string;
  credits_remaining: number;
  credits_used_today: number;
  last_reset_date: string;
}

interface GeneratedResult {
  markdown: string;
  metadata?: Record<string, any> | null;
}

interface ComplianceSummary {
  total_clauses: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
}

const AIForm: React.FC<AIFormProps> = ({
  title,
  description,
  placeholder = "Enter details here...",
  taskType,
  additionalFields,
  additionalData,
  onReset,
}) => {
  const [inputMethod, setInputMethod] = useState<"text" | "file">("text");
  const [inputText, setInputText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<GeneratedResult | null>(null);
  const [credits, setCredits] = useState<UserCredits | null>(null);
  const { user } = useAuth();

  useEffect(() => {
    async function loadCredits() {
      if (!user || !supabase) return;
      try {
        const { data, error } = await supabase
          .from('user_credits')
          .select('*')
          .eq('user_id', user.id)
          .single();

        if (error && error.code !== 'PGRST116') { // PGRST116 = No rows returned (varying between setups)
          console.warn('Could not load credits:', error.message);
          return;
        }

        const defaultCredits = Number(import.meta.env.VITE_DEFAULT_CREDITS) || 5;

        if (!data) {
          // Create initial credits record for user
          const { data: created, error: createErr } = await supabase
            .from('user_credits')
            .insert({
              user_id: user.id,
              credits_remaining: defaultCredits,
              credits_used_today: 0,
              last_reset_date: new Date().toISOString().slice(0, 10)
            })
            .select()
            .single();

          if (createErr) {
            console.warn('Failed to create credits record:', createErr.message);
            return;
          }

          setCredits(created ?? null);
          return;
        }

        // handle daily reset if last_reset_date is older than today
        const today = new Date().toISOString().slice(0, 10);
        if (data.last_reset_date !== today) {
          const { data: resetData, error: resetError } = await supabase
            .from('user_credits')
            .update({ credits_remaining: defaultCredits, credits_used_today: 0, last_reset_date: today, updated_at: new Date().toISOString() })
            .eq('user_id', user.id)
            .select()
            .single();

          if (resetError) {
            console.warn('Failed to reset credits:', resetError.message);
          } else {
            setCredits(resetData ?? null);
            return;
          }
        }

        setCredits(data ?? null);
      } catch (err) {
        console.error('Error loading credits', err);
      }
    }

    loadCredits();
  }, [user]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (inputMethod === "text" && !inputText.trim()) {
      toast.error("Please enter some text");
      return;
    }

    if (inputMethod === "file" && !file) {
      toast.error("Please upload a file");
      return;
    }

    setIsLoading(true);
    setResponse(null);
    console.log("Submit started. Loading set to true.");

    try {
      let textContent = inputText;

      if (inputMethod === "file" && file) {
        const text = await file.text();
        textContent = text;
      }

      // Check credits before invoking AI
      if (!user) {
        console.log("No user found. Aborting.");
        toast.error('You must be logged in to use this feature');
        setIsLoading(false); // Make sure we stop the spinner
        return;
      }
      console.log("User found:", user.id);

      const defaultCredits = Number(import.meta.env.VITE_DEFAULT_CREDITS) || 5;

      if (!credits) {
        // Try to create a credits row and consume one credit immediately
        const today = new Date().toISOString().slice(0, 10);
        const { data: created, error: createErr } = await supabase
          .from('user_credits')
          .insert({
            user_id: user.id,
            credits_remaining: defaultCredits,
            credits_used_today: 0,
            last_reset_date: today
          })
          .select()
          .single();

        if (createErr) {
          toast.error('Could not initialize credits. Try again later.');
          return;
        }

        setCredits(created ?? null);
      }

      // Re-check credits after possible creation/reset
      const currentCredits = (credits) ? credits : (await (async () => {
        const { data: r } = await supabase.from('user_credits').select('*').eq('user_id', user.id).single();
        return r as UserCredits | null;
      })());

      if (!currentCredits) {
        toast.error('Could not determine your credits. Please try again later.');
        return;
      }

      // ensure daily reset is respected
      const today = new Date().toISOString().slice(0, 10);
      if (currentCredits.last_reset_date !== today) {
        // reset credit counts
        const { data: resetData } = await supabase
          .from('user_credits')
          .update({ credits_remaining: defaultCredits, credits_used_today: 0, last_reset_date: today, updated_at: new Date().toISOString() })
          .eq('user_id', user.id)
          .select()
          .single();

        if (resetData) {
          setCredits(resetData as UserCredits);
        }
      }

      const available = (currentCredits.last_reset_date === today) ? currentCredits.credits_remaining : defaultCredits;
      console.log("Credits available:", available);
      if (available <= 0) {
        toast.error('You have exhausted your daily credits');
        setIsLoading(false); // Make sure we stop the spinner
        return;
      }

      console.log("Calling aiClient.process...");
      const { data, error, metadata } = await aiClient.process(taskType, textContent, additionalData);
      console.log("aiClient.process response:", { data: data ? "Success" : null, error, metadata });
      if (error) throw error;

      // Record the usage with prompt and response
      try {
        await recordUsage(user.id, taskType, textContent.substring(0, 100), data);
      } catch (recordError) {
        console.error('Failed to record usage:', recordError);
        // Don't throw here - we want to continue even if recording fails
      }

      // On success, decrement credits in DB atomically via RPC-like upsert pattern
      const { data: updated, error: updateError } = await supabase
        .from('user_credits')
        .update({
          credits_remaining: Math.max(0, available - 1),
          credits_used_today: (currentCredits.credits_used_today ?? 0) + 1,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', user.id)
        .select()
        .single();

      if (updateError) {
        console.warn('Failed to update credits:', updateError.message);
      } else if (updated) {
        setCredits(updated as UserCredits);
      }

      setResponse({
        markdown: data ?? '',
        metadata: metadata ?? null
      });
      toast.success("Analysis completed successfully");
    } catch (error) {
      console.error("Error:", error);
      const msg = (error instanceof Error) ? error.message : String(error);
      toast.error(msg || "An error occurred while processing your request");
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setInputText("");
    setFile(null);
    setResponse(null);
    // Call parent's reset callback if provided
    if (onReset) {
      onReset();
    }
  };

  const summary = response?.metadata?.summary as ComplianceSummary | undefined;
  const actionItems = response?.metadata?.insights?.action_items as Array<any> | undefined;

  return (
    <div className="animate-fade-in">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="heading-2 mb-3">{title}</h1>
            <p className="text-lg text-muted-foreground">{description}</p>
          </div>
          <div className="text-sm text-muted-foreground">
            <div>Credits remaining: <span className="font-medium">{credits ? credits.credits_remaining : '—'}</span></div>
            <div className="text-xs">Used today: {credits ? credits.credits_used_today : '—'}</div>
          </div>
        </div>

        <Card className="mb-8">
          <CardContent className="p-6">
            <Tabs
              defaultValue="text"
              onValueChange={(value) => setInputMethod(value as "text" | "file")}
              className="w-full"
            >
              <TabsList className="mb-6">
                <TabsTrigger value="text">Text Input</TabsTrigger>
                <TabsTrigger value="file">File Upload</TabsTrigger>
              </TabsList>

              <form onSubmit={handleSubmit}>
                <TabsContent value="text">
                  <div className="space-y-4">
                    <Textarea
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      placeholder={placeholder}
                      className="min-h-[200px] resize-none"
                    />
                  </div>
                </TabsContent>

                <TabsContent value="file">
                  <div className="space-y-4">
                    <Label
                      htmlFor="file-upload"
                      className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-secondary/50 hover:bg-secondary transition-colors"
                    >
                      <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <p className="mb-2 text-sm text-muted-foreground">
                          <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-muted-foreground">
                          PDF, DOCX, or TXT (MAX. 10MB)
                        </p>
                      </div>
                      <Input
                        id="file-upload"
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.txt"
                        onChange={handleFileChange}
                      />
                    </Label>

                    {file && (
                      <div className="flex items-center gap-2 text-sm">
                        <Check className="h-4 w-4 text-green-500" />
                        <span>
                          {file.name} ({Math.round(file.size / 1024)} KB)
                        </span>
                      </div>
                    )}
                  </div>
                </TabsContent>

                {additionalFields && (
                  <div className="mt-6">
                    {additionalFields}
                  </div>
                )}

                <div className="flex flex-wrap gap-3 mt-6">
                  <Button
                    type="submit"
                    disabled={isLoading}
                    className="min-w-[120px]"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : "Generate"}
                  </Button>

                  {(inputText || file) && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={resetForm}
                      disabled={isLoading}
                    >
                      Reset
                    </Button>
                  )}
                </div>
              </form>
            </Tabs>
          </CardContent>
        </Card>

        {/* Agent Pipeline Progress Viewer — only for contract drafting */}
        {/* Agent Pipeline Progress Viewer */}
        {isLoading && taskType === "contract-drafting" && (
          <PipelineViewer stages={DEFAULT_STAGES} isActive={isLoading} />
        )}
        {isLoading && taskType === "compliance-check" && (
          <PipelineViewer stages={COMPLIANCE_STAGES} isActive={isLoading} />
        )}
        {isLoading && taskType === "legal-research" && (
          <PipelineViewer stages={RESEARCH_STAGES} isActive={isLoading} />
        )}
        {isLoading && taskType === "case-summary" && (
          <PipelineViewer stages={SUMMARY_STAGES} isActive={isLoading} />
        )}

        {response && (
          <div className="space-y-6">
            {summary && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[{
                  label: "Total Clauses",
                  value: summary.total_clauses
                }, {
                  label: "High Risk",
                  value: summary.high_risk,
                  tone: summary.high_risk ? "text-red-500" : ""
                }, {
                  label: "Medium Risk",
                  value: summary.medium_risk,
                  tone: summary.medium_risk ? "text-amber-500" : ""
                }, {
                  label: "Low Risk",
                  value: summary.low_risk,
                  tone: "text-emerald-500"
                }].map((item) => (
                  <Card key={item.label}>
                    <CardContent className="py-4">
                      <p className="text-xs uppercase tracking-wide text-muted-foreground">{item.label}</p>
                      <p className={`text-2xl font-semibold ${item.tone ?? ''}`}>{item.value}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {actionItems && actionItems.length > 0 && (
              <Card>
                <CardContent className="py-4 space-y-2">
                  <p className="text-sm font-semibold">Priority Actions</p>
                  <ul className="space-y-1 text-sm text-muted-foreground list-disc list-inside">
                    {actionItems.map((item, idx) => (
                      <li key={`${item.title}-${idx}`}>
                        <span className="font-medium">[{(item.risk_level || '').toUpperCase()}]</span> {item.title}: {item.actions?.[0] || 'Review clause'}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            <GeneratedReport value={response.markdown} />
          </div>
        )}
      </div>
    </div>
  );
};

export default AIForm;
