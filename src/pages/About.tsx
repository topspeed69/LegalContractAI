import React from "react";
import { Card, CardContent } from "@/components/ui/card";

const About = () => {
  return (
    <div className="container-tight py-16 animate-fade-in">
      <div className="max-w-3xl mx-auto mb-12 text-center">
        <h1 className="heading-2 mb-4">About LegalAssist</h1>
        <p className="text-lg text-muted-foreground">
          Transforming legal work with advanced AI technology
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
        <div>
          <img 
            src="https://images.unsplash.com/photo-1589391886645-d51941baf7fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80" 
            alt="Legal team" 
            className="rounded-lg shadow-lg object-cover w-full h-[400px]"
          />
        </div>
        <div>
          <h2 className="heading-3 mb-4">Our Mission</h2>
          <p className="mb-4 text-muted-foreground">
            At LegalAssist, we're on a mission to streamline legal processes and make high-quality legal assistance accessible to everyone through cutting-edge artificial intelligence.
          </p>
          <p className="mb-4 text-muted-foreground">
            Our platform leverages state-of-the-art AI models to help legal professionals save time, reduce errors, and deliver better results for their clients.
          </p>
          <p className="text-muted-foreground">
            Founded in 2023 by a team of legal experts and AI engineers, LegalAssist has quickly become a trusted tool for law firms, corporate legal departments, and independent practitioners around the world.
          </p>
        </div>
      </div>

      <div className="mb-16">
        <h2 className="heading-3 mb-8 text-center">Our Core Values</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            {
              title: "Accuracy",
              description: "We prioritize delivering accurate and reliable legal information and documentation."
            },
            {
              title: "Innovation",
              description: "We continuously improve our AI models and platform to deliver cutting-edge solutions."
            },
            {
              title: "Accessibility",
              description: "We believe quality legal assistance should be accessible to everyone."
            }
          ].map((value, index) => (
            <Card key={index} className="overflow-hidden">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                <p className="text-muted-foreground">{value.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div className="text-center mb-16">
        <h2 className="heading-3 mb-8">Meet Our Team</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            {
              name: "Sarah Johnson",
              title: "CEO & Co-Founder",
              image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
            },
            {
              name: "David Chen",
              title: "CTO & Co-Founder",
              image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
            },
            {
              name: "Maya Patel",
              title: "Chief Legal Officer",
              image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
            },
            {
              name: "James Wilson",
              title: "AI Research Lead",
              image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80"
            }
          ].map((member, index) => (
            <div key={index} className="text-center">
              <img 
                src={member.image} 
                alt={member.name} 
                className="w-32 h-32 rounded-full mx-auto mb-3 object-cover"
              />
              <h3 className="font-medium">{member.name}</h3>
              <p className="text-sm text-muted-foreground">{member.title}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default About;
