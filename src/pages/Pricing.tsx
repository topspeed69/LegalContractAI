import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Check } from "lucide-react";

const Pricing = () => {
  const plans = [
    {
      name: "Basic",
      description: "Essential legal AI tools for individuals",
      price: 400,
      features: [
        "Case summarization (100/month)",
        "Basic law templates",
        "Single user access",
        "Email support"
      ],
      popular: false,
      buttonText: "Start Basic Plan"
    },
    {
      name: "Professional",
      description: "Advanced features for legal professionals",
      price: 779,
      features: [
        "Unlimited case summarization",
        "All law templates",
        "Compliance checking",
        "Contract drafting",
        "3 team members",
        "Priority support"
      ],
      popular: true,
      buttonText: "Start Professional Plan"
    },
    {
      name: "Enterprise",
      description: "Custom solutions for law firms",
      price: 2000,
      features: [
        "All Professional features",
        "Unlimited team members",
        "Custom templates",
        "API access",
        "Dedicated account manager",
        "Custom integrations"
      ],
      popular: false,
      buttonText: "Contact Sales"
    }
  ];

  return (
    <div className="container py-24 animate-fade-in">
      <div className="max-w-3xl mx-auto mb-12 text-center">
        <h1 className="heading-2 mb-4">Simple, Transparent Pricing</h1>
        <p className="text-lg text-muted-foreground">
          Choose the plan that best fits your needs
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <Card key={plan.name} className={`relative ${plan.popular ? "border-primary shadow-lg" : ""}`}>
            {plan.popular && (
              <div className="absolute -top-3 left-0 right-0 mx-auto w-fit">
                <span className="bg-primary text-white text-sm font-medium px-3 py-1 rounded-full">
                  Most Popular
                </span>
              </div>
            )}
            
            <CardHeader>
              <CardTitle>{plan.name}</CardTitle>
              <CardDescription>{plan.description}</CardDescription>
            </CardHeader>
            
            <CardContent>
              <div className="text-3xl font-bold mb-6">
                ₹{plan.price}<span className="text-lg font-normal text-muted-foreground">/mo</span>
              </div>
              
              <ul className="space-y-3">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
            
            <CardFooter>
              <Button className="w-full">{plan.buttonText}</Button>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Pricing;
