import { HelpCircle, Github, Linkedin, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useState } from "react";

const HelpButton = () => {
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          size="icon"
          variant="secondary"
          className="fixed bottom-4 right-4 rounded-full w-12 h-12 shadow-lg bg-primary text-primary-foreground hover:bg-primary/90"
        >
          <HelpCircle className="h-6 w-6" />
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md mx-auto m-4 rounded-2xl">
        <DialogHeader>
          <DialogTitle className="text-center text-lg font-semibold">How Job Search Works</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 p-2">
          <div className="space-y-3 text-sm text-muted-foreground">
            <div>
              <h3 className="font-medium text-foreground mb-1">🎯 Fill Your Preferences</h3>
              <p>Enter your job title, location, and email to get started with personalized job recommendations.</p>
            </div>
            <div>
              <h3 className="font-medium text-foreground mb-1">🔍 Smart Matching</h3>
              <p>Our system finds relevant job opportunities based on your criteria and experience level.</p>
            </div>
            <div>
              <h3 className="font-medium text-foreground mb-1">📧 Get Notified</h3>
              <p>Receive curated job matches directly in your inbox with detailed descriptions and application links.</p>
            </div>
          </div>
          
          <div className="border-t pt-4 mt-6">
            <p className="text-xs text-muted-foreground mb-3 text-center">Created by Ziad Waleed</p>
            <div className="flex justify-center gap-4">
              <a
                href="https://github.com/ZiadWaleed2003"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Github className="h-4 w-4" />
                GitHub
                <ExternalLink className="h-3 w-3" />
              </a>
              <a
                href="https://www.linkedin.com/in/ziadwaleed"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <Linkedin className="h-4 w-4" />
                LinkedIn
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default HelpButton;