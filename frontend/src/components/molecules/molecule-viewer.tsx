"use client";

import { useEffect, useRef, useState } from "react";

import { cn } from "@/lib/utils/cn";

interface MoleculeViewerProps {
  structureUrl?: string;
  structureData?: string;
  format?: "pdb" | "gro" | "mol2";
  className?: string;
}

export function MoleculeViewer({
  structureUrl,
  structureData,
  format = "pdb",
  className,
}: MoleculeViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!structureUrl && !structureData) {
      setIsLoading(false);
      return;
    }

    let mounted = true;

    async function initViewer() {
      try {
        const { PluginContext } = await import("molstar/lib/mol-plugin/context");
        const { DefaultPluginSpec } = await import("molstar/lib/mol-plugin/spec");

        if (!mounted || !containerRef.current) return;

        const plugin = new PluginContext(DefaultPluginSpec());
        await plugin.init();

        if (!mounted) {
          plugin.dispose();
          return;
        }

        const canvas = containerRef.current.querySelector("canvas");
        if (canvas) {
          canvas.remove();
        }

        plugin.initViewer(containerRef.current, {
          layoutIsExpanded: false,
          layoutShowControls: false,
          layoutShowRemoteState: false,
          layoutShowSequence: false,
          layoutShowLog: false,
          layoutShowLeftPanel: false,
        });

        if (structureUrl) {
          const data = await plugin.builders.data.download(
            { url: structureUrl },
            { state: { isGhost: true } },
          );
          const trajectory = await plugin.builders.structure.parseTrajectory(
            data,
            format,
          );
          await plugin.builders.structure.hierarchy.applyPreset(
            trajectory,
            "default",
          );
        } else if (structureData) {
          const data = await plugin.builders.data.rawData({
            data: structureData,
            label: "structure",
          });
          const trajectory = await plugin.builders.structure.parseTrajectory(
            data,
            format,
          );
          await plugin.builders.structure.hierarchy.applyPreset(
            trajectory,
            "default",
          );
        }

        setIsLoading(false);

        return () => {
          plugin.dispose();
        };
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : "Failed to load viewer");
          setIsLoading(false);
        }
      }
    }

    initViewer();

    return () => {
      mounted = false;
    };
  }, [structureUrl, structureData, format]);

  if (error) {
    return (
      <div
        className={cn(
          "flex items-center justify-center bg-muted text-muted-foreground",
          className,
        )}
      >
        Error: {error}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      data-testid="molecule-viewer"
      className={cn("relative h-full w-full min-h-[400px]", className)}
    >
      {isLoading && (
        <div
          data-testid="loading-spinner"
          className="absolute inset-0 flex items-center justify-center bg-muted"
        >
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      )}
    </div>
  );
}
