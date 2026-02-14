// @ts-nocheck
/// <reference types="react" />
/** @jsxImportSource react */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { marked } from "marked";
import html2pdf from "html2pdf.js";
import { Document, Packer, Paragraph } from "docx";
import { saveAs } from "file-saver";

interface GeneratedReportProps {
  value: string;
  title?: string;
}

const GeneratedReport: React.FC<GeneratedReportProps> = ({ value, title = "Generated Report" }) => {
  const [mode, setMode] = useState<"preview" | "edit">("preview");
  const [draft, setDraft] = useState(value);
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setDraft(value);
  }, [value]);

  const html = useMemo(() => marked.parse(draft), [draft]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(draft);
    toast.success("Content copied to clipboard");
  };

  const handleReset = () => {
    setDraft(value);
    toast.success("Reverted to original output");
  };

  const handleDownloadPdf = async () => {
    if (!previewRef.current) return;
    const opt = {
      margin: 0.5,
      filename: "legal-report.pdf",
      html2canvas: { scale: 2 },
      jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
    };
    await (html2pdf() as any).set(opt).from(previewRef.current).save();
  };

  const handleDownloadDocx = () => {
    const htmlContent = `<!doctype html><html><head><meta charset="utf-8"></head><body>${html}</body></html>`;
    const blob = htmlDocx.asBlob(htmlContent);
    saveAs(blob, "legal-report.docx");
  };

  return (
    <Card className="overflow-hidden animate-scale-in">
      <CardContent className="p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground">Preview, edit, or export the AI-generated output.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={mode === "preview" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("preview")}
            >
              Preview
            </Button>
            <Button
              variant={mode === "edit" ? "default" : "outline"}
              size="sm"
              onClick={() => setMode("edit")}
            >
              Edit Markdown
            </Button>
          </div>
        </div>

        <Separator />

        {mode === "preview" ? (
          <div
            ref={previewRef}
            className="prose prose-slate dark:prose-invert max-h-[500px] overflow-auto rounded-lg border bg-background/60 p-4"
            dangerouslySetInnerHTML={{ __html: html }}
          />
        ) : (
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            className="min-h-[400px] font-mono"
          />
        )}

        <div className="flex flex-wrap gap-3">
          <Button variant="ghost" size="sm" onClick={handleCopy}>
            Copy
          </Button>
          <Button variant="ghost" size="sm" onClick={handleReset}>
            Reset
          </Button>
          <div className="flex-1" />
          <Button variant="outline" size="sm" onClick={handleDownloadDocx}>
            Download DOCX
          </Button>
          <Button size="sm" onClick={handleDownloadPdf}>
            Download PDF
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default GeneratedReport;
