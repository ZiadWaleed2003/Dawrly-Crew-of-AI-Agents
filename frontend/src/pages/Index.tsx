import Header from "@/components/Header";
import JobSearchForm from "@/components/JobSearchForm";
import HelpButton from "@/components/HelpButton";
import ThemeToggle from "@/components/ThemeToggle";

const Index = () => {
  return (
    <div className="min-h-screen bg-background py-4 sm:py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-end mb-4 sm:mb-6">
          <ThemeToggle />
        </div>
        <Header />
        <JobSearchForm />
        <HelpButton />
      </div>
    </div>
  );
};

export default Index;
