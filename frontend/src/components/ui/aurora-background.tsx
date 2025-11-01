"use client";
import { cn } from "@/utils";
import React, { ReactNode } from "react";

interface AuroraBackgroundProps extends React.HTMLProps<HTMLDivElement> {
  children: ReactNode;
  showRadialGradient?: boolean;
}

export const AuroraBackground = ({
  className,
  children,
  showRadialGradient = true,
  ...props
}: AuroraBackgroundProps) => {
  return (
    <main>
      <div
        className={cn(
          "relative flex flex-col min-h-screen text-foreground transition-bg",
          className
        )}
        {...props}
      >
        <div className="fixed inset-0 overflow-hidden pointer-events-none -z-10">
          <div
            //   I'm sorry but this is what peak developer performance looks like // trigger warning
            className={cn(
              `
            [--aurora:repeating-linear-gradient(100deg,var(--blue-500)_10%,var(--purple-500)_15%,var(--violet-500)_20%,var(--pink-500)_25%,var(--cyan-500)_30%)]
            [background-image:var(--aurora)]
            [background-size:300%,_200%]
            [background-position:50%_50%]
            filter blur-[50px]
            after:content-[""] after:absolute after:inset-0 after:[background-image:var(--aurora)] 
            after:[background-size:200%,_100%] 
            after:animate-aurora after:[background-attachment:fixed]
            pointer-events-none
            absolute -inset-[10px] opacity-50 will-change-transform`,

              showRadialGradient &&
                `[mask-image:radial-gradient(ellipse_at_100%_0%,black_10%,var(--transparent)_70%)]` 
            )}
          ></div>
        </div>
        <div className="relative z-10 flex-1">
          {children}
        </div>
      </div>
    </main>
  );
};
