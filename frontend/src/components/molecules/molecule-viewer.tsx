"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import Script from "next/script";

import { cn } from "@/lib/utils/cn";

interface MoleculeViewerProps {
  structureUrl?: string;
  structureData?: string;
  format?: "pdb" | "gro" | "mol2";
  moleculeType?: "atomistic" | "coarse_grained" | "backmapped";
  className?: string;
}

function MoleculeViewerInner({
  structureUrl,
  structureData,
  format = "pdb",
  moleculeType = "atomistic",
  className,
}: MoleculeViewerProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const viewerInstanceRef = useRef<any>(null);
  const viewerDivRef = useRef<HTMLDivElement | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scriptsLoaded, setScriptsLoaded] = useState(
    typeof window !== "undefined" && !!(window as any).$3Dmol
  );

  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).$3Dmol) {
      setScriptsLoaded(true);
    }
  }, []);

  useEffect(() => {
    if (!scriptsLoaded || !wrapperRef.current) return;
    if (!structureUrl && !structureData) {
      setIsLoading(false);
      return;
    }

    const initViewer = async () => {
      try {
        const $3Dmol = (window as any).$3Dmol;
        if (!$3Dmol) {
          throw new Error("3Dmol library not loaded");
        }

        if (viewerInstanceRef.current) {
          try {
            viewerInstanceRef.current.clear();
          } catch (e) {}
          viewerInstanceRef.current = null;
        }

        if (viewerDivRef.current && wrapperRef.current?.contains(viewerDivRef.current)) {
          wrapperRef.current.removeChild(viewerDivRef.current);
        }

        const viewerDiv = document.createElement("div");
        viewerDiv.style.width = "100%";
        viewerDiv.style.height = "100%";
        viewerDiv.style.position = "relative";
        viewerDivRef.current = viewerDiv;
        wrapperRef.current?.appendChild(viewerDiv);

        const viewer = $3Dmol.createViewer(viewerDiv, {
          backgroundColor: "white",
          antialias: true,
        });

        if (!viewer) {
          throw new Error("Could not create viewer");
        }

        viewerInstanceRef.current = viewer;

        let modelData = structureData;
        if (structureUrl && !modelData) {
          const response = await fetch(structureUrl);
          if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.statusText}`);
          }
          modelData = await response.text();
        }

        if (modelData) {
          viewer.addModel(modelData, format);

          if (moleculeType === "coarse_grained") {
            // CG style: larger spheres with sticks connecting them
            viewer.setStyle({}, {
              sphere: { scale: 1.0, colorscheme: "chainHetatm" },
              stick: { radius: 0.4, colorscheme: "chainHetatm" }
            });
          } else {
            // Atomistic and backmapped: cartoon for proteins, sticks for others
            viewer.setStyle({}, { cartoon: { color: "spectrum" } });
            viewer.addStyle({}, { stick: { radius: 0.1, colorscheme: "default" } });
          }

          viewer.zoomTo();
          viewer.render();
        }

        setIsLoading(false);
      } catch (err) {
        console.error("3Dmol error:", err);
        setError(err instanceof Error ? err.message : "Failed to load viewer");
        setIsLoading(false);
      }
    };

    initViewer();

    return () => {
      if (viewerInstanceRef.current) {
        try {
          viewerInstanceRef.current.clear();
        } catch (e) {}
        viewerInstanceRef.current = null;
      }
    };
  }, [scriptsLoaded, structureUrl, structureData, format, moleculeType]);

  if (error) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-4 bg-muted text-muted-foreground p-8",
          className,
        )}
      >
        <div className="text-center">
          <p className="font-medium text-destructive">3D Viewer Unavailable</p>
          <p className="text-sm mt-2">{error}</p>
          <p className="text-xs mt-4 text-muted-foreground">
            You can still download the structure file using the Download button
            above.
          </p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Script
        src="https://3dmol.org/build/3Dmol-min.js"
        strategy="afterInteractive"
        onLoad={() => setScriptsLoaded(true)}
        onError={() => setError("Failed to load 3Dmol library")}
      />
      <div
        className={cn("relative h-full w-full min-h-[400px]", className)}
      >
        {isLoading && (
          <div
            data-testid="loading-spinner"
            className="absolute inset-0 flex items-center justify-center bg-muted z-10"
          >
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        )}
        <div
          ref={wrapperRef}
          data-testid="molecule-viewer"
          className="absolute inset-0"
        />
      </div>
    </>
  );
}

export const MoleculeViewer = dynamic(
  () => Promise.resolve(MoleculeViewerInner),
  { ssr: false },
);
