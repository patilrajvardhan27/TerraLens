"use client";

import { CLASS_META, type ClassifyResult, type EuroSATClass } from "@/lib/types";
import { formatConfidence, sortedProbabilities } from "@/lib/utils";
import { Card, CardBody, CardHeader } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { cn } from "@/lib/utils";

interface ResultPanelProps {
  result: ClassifyResult;
  label?: string;
}

export function ResultPanel({ result, label }: ResultPanelProps) {
  const meta = CLASS_META[result.class as EuroSATClass];
  const sorted = sortedProbabilities(result.probabilities);
  const confidencePct = result.confidence * 100;

  const confidenceBadgeVariant =
    confidencePct >= 80 ? "success" : confidencePct >= 50 ? "warning" : "danger";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <p className="text-xs font-medium uppercase tracking-widest text-slate-500">
            {label ?? "Classification Result"}
          </p>
          <Badge variant={confidenceBadgeVariant}>
            {formatConfidence(result.confidence)} confident
          </Badge>
        </div>
        <div className="mt-3 flex items-center gap-3">
          <span
            className={cn(
              "flex h-11 w-11 items-center justify-center rounded-xl text-2xl",
              meta?.bg ?? "bg-slate-700"
            )}
          >
            {meta?.icon ?? "🛰️"}
          </span>
          <div>
            <h2 className={cn("text-xl font-semibold", meta?.color ?? "text-slate-100")}>
              {result.class}
            </h2>
            <p className="text-xs capitalize text-slate-500">{meta?.category ?? "unknown"}</p>
          </div>
        </div>

        {/* Confidence bar */}
        <div className="mt-4">
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-700">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-700"
              style={{ width: `${confidencePct}%` }}
            />
          </div>
        </div>
      </CardHeader>

      <CardBody className="pt-3">
        <p className="mb-2 text-xs font-medium uppercase tracking-widest text-slate-500">
          All Classes
        </p>
        <div className="space-y-2">
          {sorted.map(([cls, prob]) => {
            const clsMeta = CLASS_META[cls as EuroSATClass];
            const pct = prob * 100;
            const isTop = cls === result.class;

            return (
              <div key={cls} className="flex items-center gap-2.5">
                <span className="w-4 text-center text-sm leading-none">
                  {clsMeta?.icon}
                </span>
                <span
                  className={cn(
                    "w-40 truncate text-xs",
                    isTop ? "font-medium text-slate-100" : "text-slate-400"
                  )}
                >
                  {cls}
                </span>
                <div className="relative flex-1">
                  <div className="h-1.5 w-full rounded-full bg-slate-700">
                    <div
                      className={cn(
                        "h-full rounded-full transition-all duration-500",
                        isTop
                          ? (clsMeta?.color?.replace("text-", "bg-") ?? "bg-emerald-400")
                          : "bg-slate-600"
                      )}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
                <span
                  className={cn(
                    "w-12 text-right text-xs tabular-nums",
                    isTop ? "text-slate-200" : "text-slate-500"
                  )}
                >
                  {pct.toFixed(1)}%
                </span>
              </div>
            );
          })}
        </div>
      </CardBody>
    </Card>
  );
}
