"use client";

import { useState } from "react";
import { Eye, EyeOff, Info } from "lucide-react";
import { b64ToSrc } from "@/lib/utils";
import { Card, CardHeader, CardBody } from "./ui/Card";
import { Button } from "./ui/Button";
import type { GradCAMResult } from "@/lib/types";

interface GradCAMViewerProps {
  result: GradCAMResult;
}

type ViewMode = "original" | "overlay" | "heatmap";

export function GradCAMViewer({ result }: GradCAMViewerProps) {
  const [mode, setMode] = useState<ViewMode>("overlay");
  const [opacity, setOpacity] = useState(60);

  const src =
    mode === "original"
      ? b64ToSrc(result.original_b64)
      : mode === "heatmap"
      ? b64ToSrc(result.gradcam_b64)
      : null; // overlay is composited below

  const buttons: { id: ViewMode; label: string }[] = [
    { id: "original", label: "Original" },
    { id: "overlay",  label: "Overlay" },
    { id: "heatmap",  label: "Heatmap" },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Eye className="h-4 w-4 text-emerald-400" />
            <p className="text-sm font-medium text-slate-200">
              Grad-CAM Explanation
            </p>
          </div>
          <div className="flex items-center gap-1 rounded-lg bg-slate-900/60 p-1">
            {buttons.map(({ id, label }) => (
              <button
                key={id}
                onClick={() => setMode(id)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                  mode === id
                    ? "bg-emerald-500 text-white shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>

      <CardBody>
        {/* Image view */}
        <div className="relative overflow-hidden rounded-lg bg-slate-900">
          {mode === "overlay" ? (
            <div className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={b64ToSrc(result.original_b64)}
                alt="Original satellite image"
                className="h-64 w-full object-contain"
                style={{ imageRendering: "pixelated" }}
              />
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={b64ToSrc(result.overlay_b64)}
                alt="Grad-CAM overlay"
                className="absolute inset-0 h-64 w-full object-contain"
                style={{
                  imageRendering: "pixelated",
                  opacity: opacity / 100,
                  mixBlendMode: "screen",
                }}
              />
            </div>
          ) : (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={src!}
              alt={mode === "original" ? "Satellite image" : "Grad-CAM heatmap"}
              className="h-64 w-full object-contain"
              style={{ imageRendering: "pixelated" }}
            />
          )}

          {/* Predicted class badge */}
          <div className="absolute bottom-2 left-2 rounded-md bg-slate-900/80 px-2 py-1 text-xs text-slate-200 backdrop-blur-sm">
            Predicted: <span className="font-semibold text-emerald-400">{result.class}</span>
          </div>
        </div>

        {/* Opacity slider — only meaningful in overlay mode */}
        {mode === "overlay" && (
          <div className="mt-4 flex items-center gap-3">
            <EyeOff className="h-3.5 w-3.5 shrink-0 text-slate-500" />
            <input
              type="range"
              min={0}
              max={100}
              value={opacity}
              onChange={(e) => setOpacity(Number(e.target.value))}
              className="h-1 flex-1 cursor-pointer appearance-none rounded-full bg-slate-700 accent-emerald-400"
              aria-label="Overlay opacity"
            />
            <Eye className="h-3.5 w-3.5 shrink-0 text-slate-500" />
            <span className="w-9 text-right text-xs tabular-nums text-slate-400">
              {opacity}%
            </span>
          </div>
        )}

        {/* Legend */}
        {mode !== "original" && (
          <div className="mt-4 flex items-start gap-2 rounded-lg bg-slate-900/50 px-3 py-2.5">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-500" />
            <div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span>Low attention</span>
                <div className="flex gap-0.5">
                  {["#00008b", "#0000ff", "#00ffff", "#ffff00", "#ff6600", "#ff0000"].map(
                    (c) => (
                      <div
                        key={c}
                        className="h-3 w-4 rounded-sm"
                        style={{ background: c }}
                      />
                    )
                  )}
                </div>
                <span>High attention</span>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                Red regions had the strongest influence on the prediction.
              </p>
            </div>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
