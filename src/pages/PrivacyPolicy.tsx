
import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent } from "@/components/ui/card";

const PrivacyPolicy = () => {
  return (
    <Layout>
      <div className="container-tight py-16 animate-fade-in">
        <div className="max-w-3xl mx-auto mb-12 text-center">
          <h1 className="heading-2 mb-4">Privacy Policy</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: June 1, 2023
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="p-6 space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-3">Introduction</h2>
              <p className="text-muted-foreground">
                This Privacy Policy describes how LegalAssist ("we", "our", or "us") collects, uses, and discloses your personal information when you use our website, mobile application, or other online services (collectively, the "Services").
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Information We Collect</h2>
              <p className="text-muted-foreground mb-3">
                We collect information that you provide directly to us, information we collect automatically when you use the Services, and information from third-party sources.
              </p>
              <h3 className="text-lg font-medium mb-2">Information You Provide</h3>
              <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                <li>Account information, such as your name, email address, and password</li>
                <li>Profile information, such as your job title, company, and profile picture</li>
                <li>Content you upload, such as legal documents, case details, and other information</li>
                <li>Communications you send to us, such as customer support inquiries</li>
                <li>Payment information, such as credit card details (processed by our payment processor)</li>
              </ul>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">How We Use Your Information</h2>
              <p className="text-muted-foreground mb-3">
                We use the information we collect to:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                <li>Provide, maintain, and improve the Services</li>
                <li>Process transactions and send related information</li>
                <li>Send technical notices, updates, security alerts, and support messages</li>
                <li>Respond to your comments, questions, and customer service requests</li>
                <li>Develop new products and services</li>
                <li>Monitor and analyze trends, usage, and activities in connection with the Services</li>
                <li>Detect, investigate, and prevent fraudulent transactions and other illegal activities</li>
                <li>Personalize the Services and provide advertisements, content, or features that match your preferences</li>
              </ul>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Data Retention</h2>
              <p className="text-muted-foreground">
                We retain your personal information for as long as necessary to fulfill the purposes for which we collected it, including for the purposes of satisfying any legal, accounting, or reporting requirements. To determine the appropriate retention period, we consider the amount, nature, and sensitivity of the data, the potential risk of harm from unauthorized use or disclosure, the purposes for which we process the data, and applicable legal requirements.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Your Rights</h2>
              <p className="text-muted-foreground mb-3">
                Depending on your location, you may have certain rights regarding your personal information, including:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-muted-foreground">
                <li>The right to access personal information we hold about you</li>
                <li>The right to request correction or deletion of your personal information</li>
                <li>The right to restrict or object to our processing of your personal information</li>
                <li>The right to data portability</li>
                <li>The right to withdraw consent at any time for processing based on consent</li>
              </ul>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Contact Us</h2>
              <p className="text-muted-foreground">
                If you have any questions about this Privacy Policy, please contact us at privacy@legalassist.com.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default PrivacyPolicy;
