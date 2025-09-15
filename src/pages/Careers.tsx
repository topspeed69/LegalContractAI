
import React from "react";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight } from "lucide-react";

const Careers = () => {
  const openPositions = [
    {
      title: "Senior Legal AI Engineer",
      department: "Engineering",
      location: "New York, NY (Hybrid)",
      description: "Lead the development of advanced AI models for legal document analysis and generation."
    },
    {
      title: "Legal Content Specialist",
      department: "Content",
      location: "Remote",
      description: "Create and curate high-quality legal content to train our AI models."
    },
    {
      title: "Product Manager",
      department: "Product",
      location: "San Francisco, CA",
      description: "Define and execute the product roadmap for our legal AI platform."
    },
    {
      title: "Legal UX Researcher",
      department: "Design",
      location: "Remote",
      description: "Conduct research to understand how legal professionals interact with our platform."
    }
  ];

  return (
    <Layout>
      <div className="container-tight py-16 animate-fade-in">
        <div className="max-w-3xl mx-auto mb-12 text-center">
          <h1 className="heading-2 mb-4">Join Our Team</h1>
          <p className="text-lg text-muted-foreground">
            Help us reshape the future of legal technology
          </p>
        </div>

        <div className="mb-16">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <img 
                src="https://images.unsplash.com/photo-1552664730-d307ca884978?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80" 
                alt="Team working together" 
                className="rounded-lg shadow-lg object-cover w-full h-[400px]"
              />
            </div>
            <div>
              <h2 className="heading-3 mb-6">Why Work With Us</h2>
              <div className="space-y-6">
                {[
                  {
                    title: "Innovative Technology",
                    description: "Work on cutting-edge AI technology that's transforming the legal industry."
                  },
                  {
                    title: "Growth Opportunities",
                    description: "Develop your skills and advance your career in a rapidly expanding field."
                  },
                  {
                    title: "Inclusive Culture",
                    description: "Join a diverse team that values different perspectives and ideas."
                  },
                  {
                    title: "Competitive Benefits",
                    description: "Enjoy comprehensive healthcare, flexible PTO, remote work options, and more."
                  }
                ].map((benefit, index) => (
                  <div key={index}>
                    <h3 className="text-lg font-medium mb-1">{benefit.title}</h3>
                    <p className="text-muted-foreground">{benefit.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mb-16">
          <h2 className="heading-3 mb-8 text-center">Open Positions</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {openPositions.map((position, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <CardTitle>{position.title}</CardTitle>
                  <CardDescription>
                    {position.department} • {position.location}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{position.description}</p>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" className="w-full">
                    Apply Now
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>

        <div className="bg-secondary rounded-lg p-8 text-center">
          <h2 className="text-2xl font-semibold mb-4">Don't see the right position?</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            We're always looking for talented individuals to join our team. Submit your resume and we'll keep you in mind for future opportunities.
          </p>
          <Button className="inline-flex items-center gap-2">
            <span>Submit Resume</span>
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default Careers;
