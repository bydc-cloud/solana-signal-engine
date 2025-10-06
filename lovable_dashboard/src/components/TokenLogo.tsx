import { useState } from "react";

interface TokenLogoProps {
  address: string;
  symbol?: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function TokenLogo({ address, symbol, size = "md", className = "" }: TokenLogoProps) {
  const [imageError, setImageError] = useState(false);
  
  const sizeClasses = {
    sm: "w-6 h-6 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-12 h-12 text-base"
  };

  // Extract size from className if provided directly
  const customSize = className.match(/w-\d+/)?.[0];
  const displaySize = customSize ? className : `${sizeClasses[size]} ${className}`;

  const jupiterImageUrl = `https://img.jup.ag/strict/${address}`;
  
  if (imageError || !address) {
    return (
      <div 
        className={`${displaySize} rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-bold`}
        title={symbol}
      >
        {symbol?.charAt(0) || "?"}
      </div>
    );
  }

  return (
    <img
      src={jupiterImageUrl}
      alt={symbol || "Token"}
      className={`${displaySize} rounded-full bg-background border border-border`}
      onError={() => setImageError(true)}
      loading="lazy"
    />
  );
}
