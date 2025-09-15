
import React from "react";
import Layout from "@/components/Layout";
import { Card, CardContent } from "@/components/ui/card";

const TermsOfService = () => {
  return (
    <Layout>
      <div className="container-tight py-16 animate-fade-in">
        <div className="max-w-3xl mx-auto mb-12 text-center">
          <h1 className="heading-2 mb-4">Terms of Service</h1>
          <p className="text-lg text-muted-foreground">
            Last updated: June 1, 2023
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="p-6 space-y-6">
            <div>
              <h2 className="text-xl font-semibold mb-3">Introduction</h2>
              <p className="text-muted-foreground">
                These Terms of Service ("Terms") govern your access to and use of the LegalAssist website, mobile application, and other online services (collectively, the "Services"). By accessing or using the Services, you agree to be bound by these Terms.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Using the Services</h2>
              <p className="text-muted-foreground mb-3">
                You may use the Services only if you agree to these Terms and comply with all applicable laws. You must be at least 18 years old to use the Services.
              </p>
              <p className="text-muted-foreground">
                The Services are intended for use by legal professionals and should not be used as a substitute for professional legal advice. The information provided by the Services is for informational purposes only and should not be construed as legal advice.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Account Registration</h2>
              <p className="text-muted-foreground mb-3">
                To access certain features of the Services, you may need to register for an account. When you register, you agree to provide accurate and complete information and to keep this information up to date.
              </p>
              <p className="text-muted-foreground">
                You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Content and License</h2>
              <p className="text-muted-foreground mb-3">
                The Services may allow you to upload, share, or otherwise make available certain content, such as legal documents, case details, and other information ("User Content"). You retain all rights in your User Content and are responsible for it.
              </p>
              <p className="text-muted-foreground">
                By uploading or sharing User Content, you grant us a non-exclusive, transferable, sublicensable, royalty-free, worldwide license to use, host, store, reproduce, modify, create derivative works, communicate, publish, and distribute such User Content in connection with providing and improving the Services.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Subscription and Billing</h2>
              <p className="text-muted-foreground mb-3">
                Some features of the Services require a subscription. By subscribing, you agree to pay the fees as described during the subscription process.
              </p>
              <p className="text-muted-foreground mb-3">
                Subscriptions automatically renew unless you cancel at least 24 hours before the end of the current billing period. You can cancel your subscription at any time through your account settings.
              </p>
              <p className="text-muted-foreground">
                All fees are exclusive of taxes, which we may collect from you. We may change our fees at any time, but we'll provide notice before any changes take effect.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Limitation of Liability</h2>
              <p className="text-muted-foreground">
                In no event will LegalAssist, its affiliates, officers, employees, agents, suppliers, or licensors be liable for any indirect, incidental, special, consequential, or punitive damages, including lost profits, lost data, personal injury, or property damage arising out of or in connection with your use of the Services, whether based on warranty, contract, tort (including negligence), or any other legal theory, and whether or not LegalAssist has been informed of the possibility of such damage.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Changes to these Terms</h2>
              <p className="text-muted-foreground">
                We may modify these Terms from time to time. If we make material changes, we will provide notice through the Services or by other means. Your continued use of the Services after the changes take effect constitutes your acceptance of the modified Terms.
              </p>
            </div>
            
            <div>
              <h2 className="text-xl font-semibold mb-3">Contact Us</h2>
              <p className="text-muted-foreground">
                If you have any questions about these Terms, please contact us at legal@legalassist.com.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </Layout>
  );
};

export default TermsOfService;
