"use client";

import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
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
import { getMolecules, runInference } from "@/lib/api";
import type { GlimpsModel, Molecule } from "@/types/api";

interface InferenceDialogProps {
  projectId: string;
  model: GlimpsModel | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onInferenceStarted: () => void;
}

export function InferenceDialog({
  projectId,
  model,
  open,
  onOpenChange,
  onInferenceStarted,
}: InferenceDialogProps) {
  const [loading, setLoading] = useState(false);
  const [molecules, setMolecules] = useState<Molecule[]>([]);
  const [inputMoleculeId, setInputMoleculeId] = useState("");
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!model) return;
    if (!inputMoleculeId) {
      setError("Please select an input molecule");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await runInference(model.id, inputMoleculeId);
      onOpenChange(false);
      setInputMoleculeId("");
      onInferenceStarted();
    } catch (err) {
      setError("Failed to start inference. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Run Inference: {model?.name}</DialogTitle>
            <DialogDescription>
              Select a coarse-grained molecule to backmap using this trained
              model.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            {loadingMolecules ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : (
              <div className="grid gap-2">
                <Label>Input Molecule (Coarse-Grained)</Label>
                {cgMolecules.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    No coarse-grained molecules. Upload one first.
                  </p>
                ) : (
                  <Select
                    value={inputMoleculeId}
                    onValueChange={setInputMoleculeId}
                    disabled={loading}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select input molecule" />
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
              disabled={loading || !inputMoleculeId || loadingMolecules}
            >
              {loading ? "Starting Inference..." : "Run Inference"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
