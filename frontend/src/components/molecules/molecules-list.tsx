"use client";

import { useEffect, useState } from "react";
import { FileText, Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getMolecules, deleteMolecule } from "@/lib/api";
import type { Molecule } from "@/types/api";

interface MoleculesListProps {
  projectId: string;
  onSelect?: (molecule: Molecule) => void;
  selectedId?: string;
  refreshTrigger?: number;
}

const typeLabels: Record<string, string> = {
  atomistic: "Atomistic",
  coarse_grained: "Coarse-Grained",
  backmapped: "Backmapped",
};

const typeVariants: Record<string, "default" | "secondary" | "success"> = {
  atomistic: "default",
  coarse_grained: "secondary",
  backmapped: "success",
};

export function MoleculesList({
  projectId,
  onSelect,
  selectedId,
  refreshTrigger,
}: MoleculesListProps) {
  const [molecules, setMolecules] = useState<Molecule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadMolecules();
  }, [projectId, refreshTrigger]);

  const loadMolecules = async () => {
    try {
      setLoading(true);
      const data = await getMolecules(projectId);
      setMolecules(data.molecules);
    } catch (err) {
      setError("Failed to load molecules");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (moleculeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this molecule?")) return;

    setDeletingId(moleculeId);
    try {
      await deleteMolecule(moleculeId);
      setMolecules((prev) => prev.filter((m) => m.id !== moleculeId));
    } catch (err) {
      alert("Failed to delete molecule");
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-32 items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-32 items-center justify-center text-destructive">
        {error}
      </div>
    );
  }

  if (molecules.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-muted-foreground">
        No molecules yet. Upload a structure to get started.
      </div>
    );
  }

  return (
    <div className="divide-y">
      {molecules.map((molecule) => (
        <div
          key={molecule.id}
          onClick={() => onSelect?.(molecule)}
          className={`flex items-center justify-between p-4 transition-colors ${
            onSelect ? "cursor-pointer hover:bg-muted/50" : ""
          } ${selectedId === molecule.id ? "bg-muted" : ""}`}
        >
          <div className="flex items-center gap-3">
            <FileText className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">{molecule.name}</p>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{molecule.n_atoms} atoms</span>
                <span>&bull;</span>
                <span>{molecule.file_format.toUpperCase()}</span>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={typeVariants[molecule.molecule_type]}>
              {typeLabels[molecule.molecule_type]}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => handleDelete(molecule.id, e)}
              disabled={deletingId === molecule.id}
            >
              {deletingId === molecule.id ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive" />
              )}
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
