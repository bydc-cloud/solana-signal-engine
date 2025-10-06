import { Home, Layers, Activity, TrendingUp, BarChart3, FileText, Wallet, Copy, DollarSign, Target, Twitter, Zap, Clock, LogOut } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Confluence", href: "/confluence", icon: Zap },
  { name: "Time Analysis", href: "/time-analysis", icon: Clock },
  { name: "Exit Strategy", href: "/exit-strategy", icon: LogOut },
  { name: "Tier Signals", href: "/tiers", icon: Layers },
  { name: "Active Positions", href: "/positions", icon: Target },
  { name: "PnL Dashboard", href: "/pnl", icon: DollarSign },
  { name: "Metrics", href: "/metrics", icon: Activity },
  { name: "Trades", href: "/trades", icon: TrendingUp },
  { name: "Smart Wallets", href: "/wallets", icon: Wallet },
  { name: "Twitter Signals", href: "/twitter", icon: Twitter },
  { name: "Mirror Trades", href: "/mirror", icon: Copy },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Logs", href: "/logs", icon: FileText },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex flex-col w-full bg-background">
      {/* Top Navigation - Modern Terminal Style */}
      <header className="border-b border-border sticky top-0 z-50 bg-background/95 backdrop-blur-sm">
        {/* Top Bar with Logo */}
        <div className="px-8 py-3 flex items-center justify-center relative bg-background/50 border-b border-border/50">
          
          <div className="absolute left-8 text-[9px] text-muted-foreground/60 font-mono uppercase tracking-wider font-bold">
            [v2.0.1]
          </div>
          
          <div className="text-center relative z-10">
            <h1 className="text-xl font-black text-primary tracking-widest font-mono uppercase leading-none mb-1">
              &gt; MATRIX_
            </h1>
            <p className="text-[8px] text-muted-foreground/80 tracking-[0.4em] font-mono font-bold leading-none">
              multi-asset trading & risk intelligence exchange
            </p>
          </div>

          <div className="absolute right-8 flex items-center gap-2 px-2 py-1 bg-success/10 border border-success/40">
            <div className="relative">
              <div className="w-1.5 h-1.5 bg-success"></div>
              <div className="absolute inset-0 w-1.5 h-1.5 bg-success animate-ping opacity-75"></div>
            </div>
            <span className="text-[9px] text-success font-mono font-extrabold tracking-wider">[ONLINE]</span>
          </div>
        </div>
        
        {/* Navigation Tabs - Modern Terminal Style */}
        <nav className="px-6 py-2 bg-background/80 border-b border-border/30">
          <div className="flex items-center justify-center gap-1 flex-wrap max-w-7xl mx-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`group relative flex items-center gap-2 px-3 py-1 transition-all text-[10px] font-bold font-mono uppercase tracking-wider border ${
                    isActive
                      ? "text-background bg-primary border-primary shadow-sm shadow-primary/20"
                      : "text-muted-foreground bg-transparent border-border hover:text-primary hover:bg-primary/10 hover:border-primary/50"
                  }`}
                >
                  {isActive && <span className="mr-1">&gt;</span>}
                  <Icon className="w-3 h-3" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
