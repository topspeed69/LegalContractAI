import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Mail, MapPin, Phone } from "lucide-react";
import { toast } from "sonner";

const Contact = () => {
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement form submission
    toast.success("Message sent successfully!");
  };

  return (
    <div className="container-tight py-16 animate-fade-in">
      <div className="max-w-3xl mx-auto mb-12 text-center">
        <h1 className="heading-2 mb-4">Contact Us</h1>
        <p className="text-lg text-muted-foreground">
          Get in touch with our team for inquiries, support, or partnerships
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        <Card>
          <CardContent className="p-6">
            <div className="mb-8">
              <h2 className="text-xl font-semibold mb-4">Reach Out</h2>
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Phone className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">+91 1800-200-3000</p>
                    <p className="text-sm text-muted-foreground">Mon-Fri, 9:30 AM - 6:30 PM IST</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-primary" />
                  <div>
                    <p className="font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">support@legalassist.in</p>
                    <p className="text-sm text-muted-foreground">partnerships@legalassist.in</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-primary mt-1" />
                  <div>
                    <p className="font-medium">Offices</p>
                    <div className="text-sm text-muted-foreground space-y-2">
                      <p>Mumbai: Level 8, Vibgyor Towers, G Block BKC, Mumbai 400098</p>
                      <p>Bangalore: WeWork Galaxy, 43 Residency Road, Bangalore 560025</p>
                      <p>Delhi: Blue One Square, Udyog Vihar Phase 4, Gurugram 122016</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" placeholder="Your name" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" placeholder="Your email" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" placeholder="How can we help?" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="message">Message</Label>
                <Textarea 
                  id="message" 
                  placeholder="Tell us more about your inquiry..."
                  className="min-h-[150px]"
                />
              </div>

              <Button type="submit" className="w-full">
                Send Message
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <div className="aspect-[2/1] w-full overflow-hidden rounded-lg">
        <iframe
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3771.1239350076547!2d72.86498841524664!3d19.062324087093946!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be7c8d82f834aa3%3A0x8fbd06f11d58dd91!2sVibgyor%20Towers%2C%20G%20Block%20BKC%2C%20Bandra%20Kurla%20Complex%2C%20Bandra%20East%2C%20Mumbai%2C%20Maharashtra%20400098!5e0!3m2!1sen!2sin!4v1650123456789!5m2!1sen!2sin"
          width="100%"
          height="100%"
          style={{ border: 0 }}
          allowFullScreen
          loading="lazy"
          referrerPolicy="no-referrer-when-downgrade"
          title="Our location"
        />
      </div>
    </div>
  );
};

export default Contact;
