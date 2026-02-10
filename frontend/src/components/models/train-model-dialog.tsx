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
import { getMolecules, trainModel } from "@/lib/api";
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
      await trainModel(model.id, cgMoleculeId, atomisticMoleculeId);
      onOpenChange(false);
      setCgMoleculeId("");
      setAtomisticMoleculeId("");
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
