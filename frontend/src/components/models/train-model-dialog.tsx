"use client";

import { useState, useEffect } from "react";
import { Loader2, Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { getMolecules, trainModel, DEFAULT_GLIMPS_OPTIONS } from "@/lib/api";
import type { GlimpsOptions } from "@/lib/api/models";
import type { GlimpsModel, Molecule } from "@/types/api";

interface TrainModelDialogProps {
  projectId: string;
  model: GlimpsModel | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTrainStarted: () => void;
}

export function TrainModelDialog({
  projectId,
  model,
  open,
  onOpenChange,
  onTrainStarted,
}: TrainModelDialogProps) {
  const [loading, setLoading] = useState(false);
  const [molecules, setMolecules] = useState<Molecule[]>([]);
  const [cgMoleculeId, setCgMoleculeId] = useState("");
  const [atomisticMoleculeId, setAtomisticMoleculeId] = useState("");
  const [glimpsOptions, setGlimpsOptions] = useState<GlimpsOptions>(DEFAULT_GLIMPS_OPTIONS);
  const [error, setError] = useState("");
  const [loadingMolecules, setLoadingMolecules] = useState(false);

  useEffect(() => {
    if (open) {
      loadMolecules();
    }
  }, [open, projectId]);

  const loadMolecules = async () => {
    setLoadingMolecules(true);
    try {
      const data = await getMolecules(projectId);
      setMolecules(data.molecules);
    } catch (err) {
      setError("Failed to load molecules");
    } finally {
      setLoadingMolecules(false);
    }
  };

  const cgMolecules = molecules.filter(
    (m) => m.molecule_type === "coarse_grained"
  );
  const atomisticMolecules = molecules.filter(
    (m) => m.molecule_type === "atomistic"
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!model) return;
    if (!cgMoleculeId) {
      setError("Please select a coarse-grained molecule");
      return;
    }
    if (!atomisticMoleculeId) {
      setError("Please select an atomistic molecule");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await trainModel(model.id, cgMoleculeId, atomisticMoleculeId, glimpsOptions);
      onOpenChange(false);
      setCgMoleculeId("");
      setAtomisticMoleculeId("");
      setGlimpsOptions(DEFAULT_GLIMPS_OPTIONS);
      onTrainStarted();
    } catch (err) {
      setError("Failed to start training. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Train Model: {model?.name}</DialogTitle>
            <DialogDescription>
              Select the coarse-grained and atomistic molecules to train the
              GLIMPS model.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {loadingMolecules ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <>
                <div className="grid gap-2">
                  <Label>Coarse-Grained Molecule</Label>
                  {cgMolecules.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No coarse-grained molecules. Upload one first.
                    </p>
                  ) : (
                    <Select
                      value={cgMoleculeId}
                      onValueChange={setCgMoleculeId}
                      disabled={loading}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select CG molecule" />
                      </SelectTrigger>
                      <SelectContent>
                        {cgMolecules.map((m) => (
                          <SelectItem key={m.id} value={m.id}>
                            {m.name} ({m.n_atoms} atoms)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>

                <div className="grid gap-2">
                  <Label>Atomistic Molecule</Label>
                  {atomisticMolecules.length === 0 ? (
                    <p className="text-sm text-muted-foreground">
                      No atomistic molecules. Upload one first.
                    </p>
                  ) : (
                    <Select
                      value={atomisticMoleculeId}
                      onValueChange={setAtomisticMoleculeId}
                      disabled={loading}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select atomistic molecule" />
                      </SelectTrigger>
                      <SelectContent>
                        {atomisticMolecules.map((m) => (
                          <SelectItem key={m.id} value={m.id}>
                            {m.name} ({m.n_atoms} atoms)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>

                <div className="border-t pt-4 mt-2">
                  <Label className="text-base font-semibold">GLIMPS Options</Label>
                  <p className="text-sm text-muted-foreground mb-3">
                    Configure the GLIMPS resolution transformation pipeline
                  </p>
                  <TooltipProvider>
                    <div className="space-y-3">
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="pca"
                          checked={glimpsOptions.pca}
                          onCheckedChange={(checked) =>
                            setGlimpsOptions((prev) => ({ ...prev, pca: !!checked }))
                          }
                          disabled={loading || glimpsOptions.triangulate}
                        />
                        <Label htmlFor="pca" className="flex items-center gap-1 cursor-pointer">
                          PCA
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="h-3 w-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p className="max-w-xs">Use PCA transform step for dimensionality reduction before regression</p>
                            </TooltipContent>
                          </Tooltip>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="refine"
                          checked={glimpsOptions.refine}
                          onCheckedChange={(checked) =>
                            setGlimpsOptions((prev) => ({ ...prev, refine: !!checked }))
                          }
                          disabled={loading}
                        />
                        <Label htmlFor="refine" className="flex items-center gap-1 cursor-pointer">
                          Refine
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="h-3 w-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p className="max-w-xs">Use elastic network minimizer (ENM) to improve output geometry</p>
                            </TooltipContent>
                          </Tooltip>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="shave"
                          checked={glimpsOptions.shave}
                          onCheckedChange={(checked) =>
                            setGlimpsOptions((prev) => ({ ...prev, shave: !!checked }))
                          }
                          disabled={loading || glimpsOptions.triangulate}
                        />
                        <Label htmlFor="shave" className="flex items-center gap-1 cursor-pointer">
                          Shave
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="h-3 w-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p className="max-w-xs">Calculate terminal atom positions using Z-matrix (shave/sprout algorithm)</p>
                            </TooltipContent>
                          </Tooltip>
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="triangulate"
                          checked={glimpsOptions.triangulate}
                          onCheckedChange={(checked) => {
                            const newTriangulate = !!checked;
                            setGlimpsOptions((prev) => ({
                              ...prev,
                              triangulate: newTriangulate,
                              shave: newTriangulate ? false : prev.shave,
                              pca: newTriangulate ? false : prev.pca,
                            }));
                          }}
                          disabled={loading}
                        />
                        <Label htmlFor="triangulate" className="flex items-center gap-1 cursor-pointer">
                          Triangulate
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Info className="h-3 w-3 text-muted-foreground" />
                            </TooltipTrigger>
                            <TooltipContent>
                              <p className="max-w-xs">Replace core MLR step with triangulation method (disables PCA and Shave)</p>
                            </TooltipContent>
                          </Tooltip>
                        </Label>
                      </div>
                    </div>
                  </TooltipProvider>
                </div>
              </>
            )}

            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={
                loading ||
                !cgMoleculeId ||
                !atomisticMoleculeId ||
                loadingMolecules
              }
            >
              {loading ? "Starting Training..." : "Start Training"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
