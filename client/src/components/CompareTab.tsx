"use client";

import { useCallback, useState } from "react";
import { GitCompareArrows, ArrowRight } from "lucide-react";
import { compareImages } from "@/lib/api";
import type { AsyncState, CompareResult } from "@/lib/types";
import { ImageDropzone } from "./ImageDropzone";
import { ResultPanel } from "./ResultPanel";
import { ChangeMap } from "./ChangeMap";
import { Button } from "./ui/Button";
import { FullPageSpinner } from "./ui/Spinner";
import { ErrorAlert } from "./ui/ErrorAlert";

export function CompareTab() {
  const [fileT1, setFileT1] = useState<File | null>(null);
  const [fileT2, setFileT2] = useState<File | null>(null);
  const [state, setState] = useState<AsyncState<CompareResult>>({ status: "idle" });

  const analyze = useCallback(async () => {
    if (!fileT1 || !fileT2) return;
    setState({ status: "loading" });
    try {
      const data = await compareImages(fileT1, fileT2);
      setState({ status: "success", data });
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Comparison failed",
      });
    }
  }, [fileT1, fileT2]);

  const reset = useCallback(() => {
    setFileT1(null);
    setFileT2(null);
    setState({ status: "idle" });
  }, []);

  const isLoading = state.status === "loading";
  const canAnalyze = !!fileT1 && !!fileT2 && !isLoading;

  return (
    <div className="space-y-6">
      {/* Upload pair */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-[1fr_auto_1fr]">
        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            T1 — Before
          </p>
          <ImageDropzone
            label="Before Image"
            value={fileT1}
            onChange={(f) => {
              setFileT1(f);
              setState({ status: "idle" });
            }}
            disabled={isLoading}
          />
        </div>

        <div className="flex items-center justify-center">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-700">
            <ArrowRight className="h-4 w-4 text-slate-400" />
          </div>
        </div>

        <div className="space-y-3">
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
            T2 — After
          </p>
          <ImageDropzone
            label="After Image"
            value={fileT2}
            onChange={(f) => {
              setFileT2(f);
              setState({ status: "idle" });
            }}
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Action bar */}
      <div className="flex gap-2">
        <Button
          onClick={analyze}
          disabled={!canAnalyze}
          loading={isLoading}
          size="lg"
          className="flex-1 sm:flex-none"
        >
          <GitCompareArrows className="h-5 w-5" />
          {isLoading ? "Comparing…" : "Detect Changes"}
        </Button>
        {state.status !== "idle" && (
          <Button variant="secondary" size="lg" onClick={reset}>
            Reset
          </Button>
        )}
      </div>

      {/* Loading */}
      {isLoading && <FullPageSpinner label="Running change detection…" />}

      {/* Error */}
      {state.status === "error" && (
        <ErrorAlert
          message={state.message}
          onDismiss={() => setState({ status: "idle" })}
        />
      )}

      {/* Results */}
      {state.status === "success" && (
        <div className="animate-in fade-in slide-in-from-bottom-4 space-y-6 duration-500">
          {/* Side-by-side classifications */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ResultPanel result={state.data.t1} label="Before — Classification" />
            <ResultPanel result={state.data.t2} label="After — Classification" />
          </div>

          {/* Change map */}
          <ChangeMap result={state.data} />
        </div>
      )}

      {/* Empty state instructions */}
      {state.status === "idle" && !fileT1 && !fileT2 && (
        <div className="rounded-xl border border-dashed border-slate-700 bg-slate-800/30 px-6 py-10 text-center">
          <GitCompareArrows className="mx-auto h-8 w-8 text-slate-600" />
          <p className="mt-3 text-sm font-medium text-slate-400">
            Upload two images of the same area at different times
          </p>
          <p className="mt-1 text-xs text-slate-600">
            TerraLens will classify each image, detect land cover transitions, and
            generate a color-coded change map highlighting urbanization,
            reforestation, flooding, and drought.
          </p>
        </div>
      )}
    </div>
  );
}
