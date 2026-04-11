"use client";

import { useCallback, useState } from "react";
import { Scan, Sparkles } from "lucide-react";
import { getGradCAM } from "@/lib/api";
import type { AsyncState, GradCAMResult } from "@/lib/types";
import { ImageDropzone } from "./ImageDropzone";
import { ResultPanel } from "./ResultPanel";
import { GradCAMViewer } from "./GradCAMViewer";
import { Button } from "./ui/Button";
import { FullPageSpinner } from "./ui/Spinner";
import { ErrorAlert } from "./ui/ErrorAlert";

export function ClassifyTab() {
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<AsyncState<GradCAMResult>>({ status: "idle" });

  const analyze = useCallback(async () => {
    if (!file) return;
    setState({ status: "loading" });
    try {
      const data = await getGradCAM(file);
      setState({ status: "success", data });
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Analysis failed",
      });
    }
  }, [file]);

  const reset = useCallback(() => {
    setFile(null);
    setState({ status: "idle" });
  }, []);

  return (
    <div className="space-y-6">
      {/* Upload area */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="space-y-3">
          <ImageDropzone
            label="Satellite Image"
            value={file}
            onChange={(f) => {
              setFile(f);
              setState({ status: "idle" });
            }}
            disabled={state.status === "loading"}
          />
          <div className="flex gap-2">
            <Button
              onClick={analyze}
              disabled={!file || state.status === "loading"}
              loading={state.status === "loading"}
              className="flex-1"
            >
              <Scan className="h-4 w-4" />
              {state.status === "loading" ? "Analyzing…" : "Analyze Image"}
            </Button>
            {state.status !== "idle" && (
              <Button variant="secondary" onClick={reset}>
                Reset
              </Button>
            )}
          </div>
        </div>

        {/* Right — instructions or result summary */}
        <div className="flex items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-800/30 p-6">
          {state.status === "idle" && (
            <div className="text-center">
              <Sparkles className="mx-auto h-8 w-8 text-slate-600" />
              <p className="mt-3 text-sm font-medium text-slate-400">
                Upload any satellite image
              </p>
              <p className="mt-1 text-xs text-slate-600">
                The model will classify land cover and generate a visual explanation
                showing which regions influenced the prediction.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-1.5 text-xs text-slate-600">
                {["Forest", "Urban", "Crops", "Water", "Highway"].map((c) => (
                  <span
                    key={c}
                    className="rounded-full border border-slate-700 px-2 py-0.5"
                  >
                    {c}
                  </span>
                ))}
                <span className="rounded-full border border-slate-700 px-2 py-0.5">
                  +5 more
                </span>
              </div>
            </div>
          )}
          {state.status === "loading" && (
            <FullPageSpinner label="Running inference…" />
          )}
          {state.status === "success" && (
            <div className="w-full">
              <ResultPanel result={state.data} />
            </div>
          )}
          {state.status === "error" && (
            <div className="w-full">
              <ErrorAlert
                message={state.message}
                onDismiss={() => setState({ status: "idle" })}
              />
            </div>
          )}
        </div>
      </div>

      {/* Grad-CAM section */}
      {state.status === "success" && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          <GradCAMViewer result={state.data} />
        </div>
      )}
    </div>
  );
}
