import { GPTChat } from "@/components/GPTChat";
import { NansenInsights } from "@/components/NansenInsights";

export default function GPTAssistant() {
  return (
    <div className="container mx-auto p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient-primary mb-2">AI Trading Assistant</h1>
        <p className="text-muted-foreground">Get AI-powered insights with smart money intelligence from Nansen</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-[calc(100vh-200px)]">
          <GPTChat />
        </div>
        <div className="lg:col-span-1">
          <NansenInsights />
        </div>
      </div>
    </div>
  );
}
