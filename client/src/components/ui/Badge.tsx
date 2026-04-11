"use client";

import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "success" | "warning" | "danger" | "info";
}

const variantStyles = {
  default: "bg-slate-700 text-slate-200",
  success: "bg-emerald-500/20 text-emerald-300 ring-1 ring-emerald-500/30",
  warning: "bg-yellow-500/20 text-yellow-300 ring-1 ring-yellow-500/30",
  danger:  "bg-red-500/20 text-red-300 ring-1 ring-red-500/30",
  info:    "bg-blue-500/20 text-blue-300 ring-1 ring-blue-500/30",
};

export function Badge({ children, className, variant = "default" }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
