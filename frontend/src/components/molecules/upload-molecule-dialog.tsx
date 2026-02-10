"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { uploadMolecule } from "@/lib/api";

interface UploadMoleculeDialogProps {
  projectId: string;
  onUploadComplete: () => void;
}

export function UploadMoleculeDialog({
  projectId,
  onUploadComplete,
}: UploadMoleculeDialogProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [moleculeType, setMoleculeType] = useState<
    "atomistic" | "coarse_grained" | "backmapped"
  >("atomistic");
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      if (!name) {
        const fileName = acceptedFiles[0].name;
        setName(fileName.substring(0, fileName.lastIndexOf(".")) || fileName);
      }
    }
  }, [name]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "chemical/x-pdb": [".pdb"],
      "application/octet-stream": [".gro", ".xtc", ".dcd", ".mol2", ".xyz"],
    },
    multiple: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await uploadMolecule(projectId, file, {
        name: name.trim() || undefined,
        description: description.trim() || undefined,
        moleculeType,
      });
      setOpen(false);
      resetForm();
      onUploadComplete();
    } catch (err) {
      setError("Failed to upload molecule. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setName("");
    setDescription("");
    setMoleculeType("atomistic");
    setError("");
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(value) => {
        setOpen(value);
        if (!value) resetForm();
      }}
    >
      <DialogTrigger asChild>
        <Button>
          <Upload className="mr-2 h-4 w-4" />
          Upload Molecule
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>Upload Molecule</DialogTitle>
            <DialogDescription>
              Upload a molecular structure file (PDB, GRO, XTC, DCD, MOL2, XYZ)
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div
              {...getRootProps()}
              className={`cursor-pointer rounded-lg border-2 border-dashed p-6 text-center transition-colors ${
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-foreground/25 hover:border-primary/50"
              }`}
            >
              <input {...getInputProps()} />
              {file ? (
                <div className="flex items-center justify-center gap-2">
                  <FileText className="h-8 w-8 text-muted-foreground" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                    }}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div>
                  <Upload className="mx-auto h-8 w-8 text-muted-foreground" />
                  <p className="mt-2 text-sm">
                    {isDragActive
                      ? "Drop the file here"
                      : "Drag and drop or click to select"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Supported: PDB, GRO, XTC, DCD, MOL2, XYZ
                  </p>
                </div>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="name">Name (optional)</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Molecule name"
                disabled={loading}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="type">Molecule Type</Label>
              <Select
                value={moleculeType}
                onValueChange={(value: typeof moleculeType) =>
                  setMoleculeType(value)
                }
                disabled={loading}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="atomistic">Atomistic</SelectItem>
                  <SelectItem value="coarse_grained">Coarse-Grained</SelectItem>
                  <SelectItem value="backmapped">Backmapped</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe this molecule..."
                disabled={loading}
              />
            </div>

            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !file}>
              {loading ? "Uploading..." : "Upload"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
