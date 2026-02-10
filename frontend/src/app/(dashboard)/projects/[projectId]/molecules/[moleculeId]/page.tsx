"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Download, Loader2, Trash2, Atom, Layers } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { MoleculeViewer } from "@/components/molecules/molecule-viewer";
import { getMolecule, getMoleculeStructure, deleteMolecule } from "@/lib/api";
import type { Molecule } from "@/types/api";

interface MoleculePageProps {
  params: { projectId: string; moleculeId: string };
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

export default function MoleculePage({ params }: MoleculePageProps) {
  const router = useRouter();
  const [molecule, setMolecule] = useState<Molecule | null>(null);
  const [structureData, setStructureData] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadMolecule();
  }, [params.moleculeId]);

  const loadMolecule = async () => {
    try {
      const [moleculeData, structure] = await Promise.all([
        getMolecule(params.moleculeId),
        getMoleculeStructure(params.moleculeId),
      ]);
      setMolecule(moleculeData);
      setStructureData(structure.content);
    } catch (err) {
      setError("Failed to load molecule");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!molecule) return;
    if (!confirm("Are you sure you want to delete this molecule?")) return;

    setDeleting(true);
    try {
      await deleteMolecule(molecule.id);
      router.push(`/projects/${params.projectId}`);
    } catch (err) {
      alert("Failed to delete molecule");
      setDeleting(false);
    }
  };

  const handleDownload = () => {
    if (!molecule || !structureData) return;
    const blob = new Blob([structureData], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${molecule.name}.${molecule.file_format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !molecule) {
    return (
      <div className="flex h-64 items-center justify-center text-destructive">
        {error || "Molecule not found"}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href={`/projects/${params.projectId}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{molecule.name}</h1>
              <Badge variant={typeVariants[molecule.molecule_type]}>
                {typeLabels[molecule.molecule_type]}
              </Badge>
            </div>
            <p className="text-muted-foreground">
              {molecule.n_atoms.toLocaleString()} atoms &bull; {molecule.n_frames} frame(s) &bull; {molecule.file_format.toUpperCase()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleDownload}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="mr-2 h-4 w-4" />
            )}
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        <div className="lg:col-span-3">
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <div className="h-[600px] bg-slate-900">
                {structureData && (
                  <MoleculeViewer
                    structureData={structureData}
                    format={molecule.file_format as "pdb" | "gro" | "mol2"}
                    moleculeType={molecule.molecule_type}
                    className="h-full w-full"
                  />
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Structure Info</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-2">
                <Atom className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Atoms:</span>
                <span className="font-medium">{molecule.n_atoms.toLocaleString()}</span>
              </div>
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Frames:</span>
                <span className="font-medium">{molecule.n_frames}</span>
              </div>
              <div className="border-t pt-3">
                <p className="text-xs text-muted-foreground">
                  Created {new Date(molecule.created_at).toLocaleDateString()}
                </p>
              </div>
            </CardContent>
          </Card>

          {molecule.description && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{molecule.description}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
