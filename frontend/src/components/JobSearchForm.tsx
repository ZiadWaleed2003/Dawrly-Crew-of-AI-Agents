import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";

const JobSearchForm = () => {
  const [formData, setFormData] = useState({
    jobTitle: "",
    skills: "",
    experienceLevel: "",
    yearsOfExperience: "",
    location: "",
    remotePreference: [] as string[],
    jobType: [] as string[],
    email: "",
  });
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCheckboxChange = (field: "remotePreference" | "jobType", value: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: checked 
        ? [...prev[field], value]
        : prev[field].filter(item => item !== value)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.email) {
      toast({
        title: "Email Required",
        description: "Please enter your email address to receive job results.",
        variant: "destructive",
      });
      return;
    }
    
    // Show success modal immediately after validation
    setShowSuccessModal(true);

    const Base_URL = import.meta.env.VITE_API_BASE_URL;
    
    // Check if API URL is configured
    if (!Base_URL) {
      console.error('API Base URL not configured');
      toast({
        title: "Configuration Error",
        description: "API endpoint not configured. Please contact support.",
        variant: "destructive",
      });
      return;
    }
    
    // Make API call in background (fire and forget)
    fetch(`${Base_URL}/jobs/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    }).catch((error) => {
      console.error('API call failed:', error);
      // Silently handle errors - user will get results via email
    });
  };

  return (
    <>
      <Card className="max-w-md mx-auto shadow-lg border-border rounded-2xl">
        <CardContent className="p-6 sm:p-8">
          <div className="text-center mb-6 sm:mb-8">
            <h2 className="text-lg sm:text-xl font-medium text-foreground mb-2">
              Find Your Perfect Job
            </h2>
            <p className="text-muted-foreground text-xs sm:text-sm">
              Tell us your preferences and we'll search for you
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
            <div>
              <Label htmlFor="jobTitle" className="text-sm font-medium text-foreground mb-2 block">
                Job Title
              </Label>
              <Input
                id="jobTitle"
                placeholder="e.g. Software Engineer, Data Scientist, Product Manager"
                value={formData.jobTitle}
                onChange={(e) => handleInputChange("jobTitle", e.target.value)}
                className="w-full bg-muted border-none"
              />
            </div>

            <div>
              <Label htmlFor="skills" className="text-sm font-medium text-foreground mb-2 block">
                Skills
              </Label>
              <Input
                id="skills"
                placeholder="e.g. Python, FastAPI, Machine Learning"
                value={formData.skills}
                onChange={(e) => handleInputChange("skills", e.target.value)}
                className="w-full bg-muted border-none"
              />
            </div>

            <div>
              <Label htmlFor="experienceLevel" className="text-sm font-medium text-foreground mb-2 block">
                Experience Level
              </Label>
              <Select value={formData.experienceLevel} onValueChange={(value) => handleInputChange("experienceLevel", value)}>
                <SelectTrigger className="w-full bg-muted border-none">
                  <SelectValue placeholder="Select experience level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="entry">Entry Level</SelectItem>
                  <SelectItem value="mid">Mid Level</SelectItem>
                  <SelectItem value="senior">Senior Level</SelectItem>
                  <SelectItem value="lead">Lead/Principal</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="years" className="text-sm font-medium text-foreground mb-2 block">
                Years of Experience
              </Label>
              <Input
                id="years"
                type="number"
                placeholder="0"
                value={formData.yearsOfExperience}
                onChange={(e) => handleInputChange("yearsOfExperience", e.target.value)}
                className="w-full bg-muted border-none"
              />
            </div>

            <div>
              <Label htmlFor="location" className="text-sm font-medium text-foreground mb-2 block">
                Location
              </Label>
              <Input
                id="location"
                placeholder="e.g. City ?"
                value={formData.location}
                onChange={(e) => handleInputChange("location", e.target.value)}
                className="w-full bg-muted border-none"
              />
            </div>

            <div>
              <Label className="text-sm font-medium text-foreground mb-3 block">
                Remote Preference
              </Label>
              <div className="flex flex-wrap gap-3 sm:gap-4">
                {["Remote", "Hybrid", "Onsite"].map((option) => (
                  <div key={option} className="flex items-center space-x-2">
                    <Checkbox
                      id={`remote-${option}`}
                      checked={formData.remotePreference.includes(option)}
                      onCheckedChange={(checked) => 
                        handleCheckboxChange("remotePreference", option, !!checked)
                      }
                    />
                    <Label htmlFor={`remote-${option}`} className="text-xs sm:text-sm font-normal">
                      {option}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label className="text-sm font-medium text-foreground mb-3 block">
                Job Type
              </Label>
              <div className="flex flex-wrap gap-3 sm:gap-4">
                {["Full-time", "Part-time", "Internship"].map((option) => (
                  <div key={option} className="flex items-center space-x-2">
                    <Checkbox
                      id={`type-${option}`}
                      checked={formData.jobType.includes(option)}
                      onCheckedChange={(checked) => 
                        handleCheckboxChange("jobType", option, !!checked)
                      }
                    />
                    <Label htmlFor={`type-${option}`} className="text-xs sm:text-sm font-normal">
                      {option}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <Label htmlFor="email" className="text-sm font-medium text-foreground mb-2 block">
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={(e) => handleInputChange("email", e.target.value)}
                className="w-full bg-muted border-none"
                required
              />
            </div>

            <Button 
              type="submit" 
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 font-medium py-3 text-sm sm:text-base"
            >
              Search for Jobs
            </Button>
          </form>

          <p className="text-xs text-muted-foreground text-center mt-3 sm:mt-4 px-2">
            Results will be sent to your email in 5-10 minutes. Please check your spam folder.
          </p>
        </CardContent>
      </Card>

      <Dialog open={showSuccessModal} onOpenChange={setShowSuccessModal}>
        <DialogContent className="max-w-sm mx-auto m-4 rounded-2xl">
          <DialogHeader>
            <DialogTitle className="text-center text-base sm:text-lg">Job Search Submitted</DialogTitle>
            <DialogDescription className="text-center text-xs sm:text-sm text-muted-foreground mt-4 px-2">
              You can expect your results on your email within 5-10 minutes. Please check your spam folder.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-center mt-4 sm:mt-6">
            <Button 
              onClick={() => setShowSuccessModal(false)}
              className="bg-primary text-primary-foreground hover:bg-primary/90 px-6 text-sm"
            >
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>

    </>
  );
};

export default JobSearchForm;
