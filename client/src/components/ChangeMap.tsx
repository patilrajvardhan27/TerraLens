"use client";

import { CHANGE_META, type CompareResult } from "@/lib/types";
import { b64ToSrc } from "@/lib/utils";
import { Card, CardHeader, CardBody } from "./ui/Card";
import { Badge } from "./ui/Badge";
import { AlertTriangle, CheckCircle2, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChangeMapProps {
  result: CompareResult;
}

export function ChangeMap({ result }: ChangeMapProps) {
  const totalChangedPatches = Object.values(result.summary).reduce(
    (s, v) => s + v,
    0
  );
  const hasChange = result.changed && totalChangedPatches > 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {hasChange ? (
              <AlertTriangle className="h-4 w-4 text-yellow-400" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            )}
            <p className="text-sm font-medium text-slate-200">
              Temporal Change Detection
            </p>
          </div>
          <Badge variant={hasChange ? "warning" : "success"}>
            {hasChange ? `${totalChangedPatches} patch${totalChangedPatches !== 1 ? "es" : ""} changed` : "No significant change"}
          </Badge>
        </div>
      </CardHeader>

      <CardBody className="space-y-5">
        {/* Classification transition */}
        <div className="flex items-center justify-center gap-3 rounded-lg bg-slate-900/50 px-4 py-3">
          <div className="text-center">
            <p className="text-xs text-slate-500">T1 — Before</p>
            <p className="mt-1 font-semibold text-slate-100">{result.t1.class}</p>
            <p className="text-xs text-slate-500">
              {(result.t1.confidence * 100).toFixed(1)}%
            </p>
          </div>
          <ArrowRight className="h-5 w-5 shrink-0 text-slate-600" />
          <div className="text-center">
            <p className="text-xs text-slate-500">T2 — After</p>
            <p
              className={cn(
                "mt-1 font-semibold",
                result.t1.class !== result.t2.class
                  ? "text-yellow-300"
                  : "text-slate-100"
              )}
            >
              {result.t2.class}
            </p>
            <p className="text-xs text-slate-500">
              {(result.t2.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Change map */}
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-slate-500">
            Change Map
          </p>
          <div className="overflow-hidden rounded-lg bg-slate-900">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={b64ToSrc(result.change_map_b64)}
              alt="Change detection map"
              className="h-48 w-full object-contain"
              style={{ imageRendering: "pixelated" }}
            />
          </div>
        </div>

        {/* Legend */}
        <div>
          <p className="mb-2 text-xs font-medium uppercase tracking-widest text-slate-500">
            Change Categories
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(CHANGE_META).map(([key, meta]) => {
              const count = result.summary[key] ?? 0;
              return (
                <div
                  key={key}
                  className={cn(
                    "flex items-center gap-2 rounded-lg border px-3 py-2 transition-colors",
                    count > 0
                      ? "border-slate-600 bg-slate-800"
                      : "border-slate-700/40 bg-slate-800/30 opacity-50"
                  )}
                >
                  <div className={cn("h-2.5 w-2.5 shrink-0 rounded-full", meta.bg)} />
                  <div className="min-w-0">
                    <p className="truncate text-xs font-medium text-slate-200">
                      {meta.label}
                    </p>
                    {count > 0 && (
                      <p className="text-xs text-slate-500">{count} patch{count !== 1 ? "es" : ""}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* No change state */}
        {!hasChange && (
          <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
            <CheckCircle2 className="h-4 w-4 shrink-0" />
            <span>
              No significant land cover transition detected between the two images.
            </span>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
