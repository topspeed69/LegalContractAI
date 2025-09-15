import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowRight, Check, FileJson, FileText, Lock, Server } from "lucide-react";
import { Link } from "react-router-dom";

const Api = () => {
  return (
    <div className="container-tight py-16 animate-fade-in">
      <div className="max-w-3xl mx-auto mb-12 text-center">
        <h1 className="heading-2 mb-4">LegalAssist API</h1>
        <p className="text-lg text-muted-foreground">
          Integrate our powerful legal AI capabilities into your applications
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-12">
        {[
          {
            icon: FileText,
            title: "Document Analysis",
            description: "Extract key information and insights from legal documents."
          },
          {
            icon: Server,
            title: "Easy Integration",
            description: "Simple REST API with comprehensive documentation."
          },
          {
            icon: Lock,
            title: "Secure & Compliant",
            description: "Enterprise-grade security with SOC 2 and GDPR compliance."
          }
        ].map((feature, index) => (
          <Card key={index}>
            <CardContent className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-medium mb-2">{feature.title}</h3>
              <p className="text-sm text-muted-foreground">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="examples">
        <TabsList className="mb-8 justify-center">
          <TabsTrigger value="examples">API Examples</TabsTrigger>
          <TabsTrigger value="pricing">API Pricing</TabsTrigger>
          <TabsTrigger value="docs">Documentation</TabsTrigger>
        </TabsList>
        
        <TabsContent value="examples">
          <Card>
            <CardHeader>
              <CardTitle>Example: Case Summarization API</CardTitle>
              <CardDescription>
                Generate concise summaries from legal case documents
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-6">
                <h3 className="text-lg font-medium mb-2">Request</h3>
                <pre className="bg-secondary/50 p-4 rounded-lg overflow-x-auto text-sm">
{`POST /api/v1/summarize
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "document": "The text of the legal document to summarize...",
  "max_length": 500,
  "format": "markdown"
}`}
                </pre>
              </div>
              
              <div>
                <h3 className="text-lg font-medium mb-2">Response</h3>
                <pre className="bg-secondary/50 p-4 rounded-lg overflow-x-auto text-sm">
{`{
  "summary": "## Case Summary\\n\\nThis case involves a dispute between...",
  "word_count": 127,
  "key_points": [
    "Intellectual property dispute between Company A and B",
    "Prior art documentation provided by Company A",
    "Court ruled in favor of Company A"
  ]
}`}
                </pre>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="pricing">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "Basic",
                price: 99,
                description: "For developers and small businesses",
                requests: "1,000 requests/month",
                features: [
                  "Case summarization API",
                  "Law template generation API",
                  "Basic rate limiting",
                  "Email support"
                ]
              },
              {
                title: "Professional",
                price: 249,
                description: "For growing companies and legal tech startups",
                requests: "5,000 requests/month",
                features: [
                  "All Basic APIs",
                  "Compliance check API",
                  "Contract drafting API",
                  "Enhanced rate limits",
                  "Priority support"
                ]
              },
              {
                title: "Enterprise",
                price: "Custom",
                description: "For large organizations with custom needs",
                requests: "Unlimited requests",
                features: [
                  "All Professional APIs",
                  "Custom model training",
                  "SLA guarantees",
                  "Dedicated support",
                  "On-premise deployment options"
                ]
              }
            ].map((plan, index) => (
              <Card key={index} className="flex flex-col">
                <CardHeader>
                  <CardTitle>{plan.title}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-1">
                  <div className="mb-6">
                    {typeof plan.price === "number" ? (
                      <div>
                        <span className="text-4xl font-bold">${plan.price}</span>
                        <span className="text-muted-foreground">/month</span>
                      </div>
                    ) : (
                      <div className="text-4xl font-bold">{plan.price}</div>
                    )}
                    <div className="text-sm text-muted-foreground mt-1">{plan.requests}</div>
                  </div>
                  <ul className="space-y-3">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-start gap-2">
                        <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="docs">
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-8 items-center">
                <div className="flex-1">
                  <h3 className="text-2xl font-semibold mb-4">Comprehensive API Documentation</h3>
                  <p className="text-muted-foreground mb-6">
                    Our developer documentation provides everything you need to integrate LegalAssist's powerful AI capabilities into your applications.
                  </p>
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <FileJson className="h-5 w-5 text-primary" />
                      <span>Detailed API reference</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="h-5 w-5 text-primary" />
                      <span>Code examples in multiple languages</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Server className="h-5 w-5 text-primary" />
                      <span>Interactive API explorer</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Lock className="h-5 w-5 text-primary" />
                      <span>Authentication and security guides</span>
                    </div>
                  </div>
                  <div className="mt-8">
                    <Button>
                      <Link to="/api-docs" className="flex items-center gap-2">
                        View Documentation
                        <ArrowRight className="h-4 w-4" />
                      </Link>
                    </Button>
                  </div>
                </div>
                <div className="md:w-1/2">
                  <img 
                    src="https://images.unsplash.com/photo-1610986602538-431d65df4385?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80" 
                    alt="API Documentation" 
                    className="rounded-lg shadow-lg w-full"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Api;
