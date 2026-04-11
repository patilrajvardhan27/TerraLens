"use client";

import { useState } from "react";
import { Satellite, Scan, GitCompareArrows } from "lucide-react";
import { cn } from "@/lib/utils";
import { ClassifyTab } from "./ClassifyTab";
import { CompareTab } from "./CompareTab";
import type { TabId } from "@/lib/types";

const TABS: { id: TabId; label: string; icon: React.ReactNode; description: string }[] = [
  {
    id: "classify",
    label: "Classify",
    icon: <Scan className="h-4 w-4" />,
    description: "Single image classification + Grad-CAM",
  },
  {
    id: "compare",
    label: "Compare",
    icon: <GitCompareArrows className="h-4 w-4" />,
    description: "Temporal change detection between two images",
  },
];

export function TerraLensApp() {
  const [activeTab, setActiveTab] = useState<TabId>("classify");

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* ─── Header ────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/30">
              <Satellite className="h-4 w-4 text-emerald-400" />
            </div>
            <div>
              <h1 className="text-sm font-semibold tracking-tight text-slate-100">
                TerraLens
              </h1>
              <p className="hidden text-xs text-slate-500 sm:block">
                Satellite Land Intelligence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-slate-500">
            <span className="hidden sm:inline">CNN_LeakyReLU_Skip · EuroSAT · 93.16%</span>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-400 ring-1 ring-emerald-500/20">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Model Ready
            </span>
          </div>
        </div>
      </header>

      {/* ─── Hero ──────────────────────────────────────────────────── */}
      <section className="border-b border-slate-800/60 bg-gradient-to-b from-slate-900 to-slate-950 px-4 py-10 sm:px-6 sm:py-14">
        <div className="mx-auto max-w-6xl">
          <div className="max-w-2xl">
            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/5 px-3 py-1 text-xs text-emerald-400">
              <Satellite className="h-3 w-3" />
              Explainable AI · Temporal Analysis · 10 Land Classes
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-50 sm:text-4xl">
              AI-Powered Land Use{" "}
              <span className="text-emerald-400">Intelligence</span>
            </h2>
            <p className="mt-3 text-base text-slate-400">
              Upload satellite imagery and get instant land cover classification,
              Grad-CAM visual explanations, and temporal change detection — all
              powered by a CNN trained on EuroSAT Sentinel-2 imagery.
            </p>
          </div>

          {/* Stats row */}
          <div className="mt-8 flex flex-wrap gap-6">
            {[
              { value: "93.16%", label: "Test accuracy" },
              { value: "10",     label: "Land classes" },
              { value: "64×64",  label: "Input size" },
              { value: "~20 ms", label: "Inference" },
            ].map(({ value, label }) => (
              <div key={label}>
                <p className="text-xl font-semibold text-slate-100">{value}</p>
                <p className="text-xs text-slate-500">{label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Main Content ──────────────────────────────────────────── */}
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        {/* Tab navigation */}
        <div className="mb-6 flex items-center gap-1 rounded-xl border border-slate-700/60 bg-slate-800/50 p-1">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex flex-1 items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all sm:justify-start",
                activeTab === tab.id
                  ? "bg-slate-700 text-slate-100 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              )}
            >
              {tab.icon}
              <span>{tab.label}</span>
              <span className="hidden text-xs text-slate-500 sm:inline">
                — {tab.description}
              </span>
            </button>
          ))}
        </div>

        {/* Tab panels */}
        <div>
          {activeTab === "classify" && <ClassifyTab />}
          {activeTab === "compare"  && <CompareTab />}
        </div>
      </main>

      {/* ─── Footer ────────────────────────────────────────────────── */}
      <footer className="mt-12 border-t border-slate-800 px-4 py-6 sm:px-6">
        <div className="mx-auto flex max-w-6xl items-center justify-between text-xs text-slate-600">
          <span>
            TerraLens · CSCI 5922 · University of Colorado Boulder
          </span>
          <span>Rajvardhan Patil · Adwait Desai</span>
        </div>
      </footer>
    </div>
  );
}
