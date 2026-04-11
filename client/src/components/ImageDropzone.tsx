"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, ImageIcon, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ImageDropzoneProps {
  label: string;
  value: File | null;
  onChange: (file: File | null) => void;
  disabled?: boolean;
}

const ACCEPTED_TYPES = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png":  [".png"],
  "image/tiff": [".tif", ".tiff"],
  "image/webp": [".webp"],
};

export function ImageDropzone({
  label,
  value,
  onChange,
  disabled = false,
}: ImageDropzoneProps) {
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback(
    (accepted: File[]) => {
      const file = accepted[0];
      if (!file) return;
      onChange(file);
      setPreview(URL.createObjectURL(file));
    },
    [onChange]
  );

  const clear = useCallback(() => {
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
    onChange(null);
  }, [preview, onChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    disabled,
  });

  if (preview && value) {
    return (
      <div className="group relative overflow-hidden rounded-xl border border-slate-700 bg-slate-800">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={preview}
          alt={label}
          className="h-52 w-full object-cover"
        />
        <div className="absolute inset-0 flex flex-col justify-between bg-gradient-to-t from-slate-900/80 via-transparent to-transparent p-3">
          <div className="flex justify-end">
            <button
              onClick={clear}
              disabled={disabled}
              className="rounded-full bg-slate-900/70 p-1.5 text-slate-300 backdrop-blur-sm transition-colors hover:bg-slate-800 hover:text-white disabled:cursor-not-allowed"
              aria-label="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <ImageIcon className="h-3.5 w-3.5 text-slate-400" />
            <p className="truncate text-xs text-slate-300">{value.name}</p>
          </div>
        </div>
        <div className="absolute top-3 left-3">
          <span className="rounded-md bg-slate-900/80 px-2 py-1 text-xs font-medium text-slate-200 backdrop-blur-sm">
            {label}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "flex h-52 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed transition-all",
        isDragActive
          ? "border-emerald-400 bg-emerald-400/5"
          : "border-slate-600 bg-slate-800/50 hover:border-slate-500 hover:bg-slate-800",
        disabled && "cursor-not-allowed opacity-50"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3 text-center">
        <div
          className={cn(
            "rounded-full p-3 transition-colors",
            isDragActive ? "bg-emerald-400/10" : "bg-slate-700/60"
          )}
        >
          <Upload
            className={cn(
              "h-6 w-6 transition-colors",
              isDragActive ? "text-emerald-400" : "text-slate-400"
            )}
          />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-200">{label}</p>
          <p className="mt-0.5 text-xs text-slate-500">
            {isDragActive
              ? "Drop to upload"
              : "Drag & drop or click to browse"}
          </p>
          <p className="mt-1 text-xs text-slate-600">JPG, PNG, TIFF, WebP</p>
        </div>
      </div>
    </div>
  );
}
