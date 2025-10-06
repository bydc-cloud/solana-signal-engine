import { Alert, AlertDescription } from "@/components/ui/alert";
import { ExternalLink } from "lucide-react";

export default function ApiUrlBanner() {
  // Banner no longer needed since we're using ngrok
  return null;

  return (
    <Alert variant="destructive" className="mb-6">
      <AlertDescription className="flex items-center justify-between">
        <span>
          ⚠️ Dashboard is trying to connect to <code className="font-mono bg-destructive/20 px-2 py-1 rounded">localhost:8000</code> - 
          this won't work from Lovable's cloud. Use ngrok or deploy your backend.
        </span>
        <a
          href="https://ngrok.com/download"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-sm underline whitespace-nowrap ml-4"
        >
          Get ngrok <ExternalLink className="w-3 h-3" />
        </a>
      </AlertDescription>
    </Alert>
  );
}
