import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import SignalConfluence from "./pages/SignalConfluence";
import TimeAnalysis from "./pages/TimeAnalysis";
import ExitStrategy from "./pages/ExitStrategy";
import TierSignals from "./pages/TierSignals";
import Metrics from "./pages/Metrics";
import Trades from "./pages/Trades";
import WalletTracker from "./pages/WalletTracker";
import MirrorTrades from "./pages/MirrorTrades";
import Analytics from "./pages/Analytics";
import Logs from "./pages/Logs";
import NotFound from "./pages/NotFound";
import ActivePositions from "./pages/ActivePositions";
import PnlDashboard from "./pages/PnlDashboard";
import WalletDetail from "./pages/WalletDetail";
import Twitter from "./pages/Twitter";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/confluence" element={<SignalConfluence />} />
            <Route path="/time-analysis" element={<TimeAnalysis />} />
            <Route path="/exit-strategy" element={<ExitStrategy />} />
            <Route path="/tiers" element={<TierSignals />} />
            <Route path="/metrics" element={<Metrics />} />
            <Route path="/trades" element={<Trades />} />
            <Route path="/wallets" element={<WalletTracker />} />
            <Route path="/wallets/:id" element={<WalletDetail />} />
            <Route path="/mirror" element={<MirrorTrades />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/positions" element={<ActivePositions />} />
            <Route path="/pnl" element={<PnlDashboard />} />
            <Route path="/twitter" element={<Twitter />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
