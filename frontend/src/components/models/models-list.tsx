"use client";

import { useEffect, useState } from "react";
import { Brain, Loader2, Trash2, Play, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getModels, deleteModel } from "@/lib/api";
import type { GlimpsModel } from "@/types/api";

interface ModelsListProps {
  projectId: string;
  onTrain?: (model: GlimpsModel) => void;
  onInference?: (model: GlimpsModel) => void;
  refreshTrigger?: number;
}

export function ModelsList({
  projectId,
  onTrain,
  onInference,
  refreshTrigger,
}: ModelsListProps) {
  const [models, setModels] = useState<GlimpsModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    loadModels();
  }, [projectId, refreshTrigger]);

  const loadModels = async () => {
    try {
      setLoading(true);
      const data = await getModels(projectId);
      setModels(data.models);
    } catch (err) {
      setError("Failed to load models");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (modelId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this model?")) return;

    setDeletingId(modelId);
    try {
      await deleteModel(modelId);
      setModels((prev) => prev.filter((m) => m.id !== modelId));
    } catch (err) {
      alert("Failed to delete model");
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

  if (models.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-muted-foreground">
        No models yet. Create and train a model.
      </div>
    );
  }

  return (
    <div className="divide-y">
      {models.map((model) => (
        <div
          key={model.id}
          className="flex items-center justify-between p-4"
        >
          <div className="flex items-center gap-3">
            <Brain className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="font-medium">{model.name}</p>
              {model.description && (
                <p className="text-sm text-muted-foreground line-clamp-1">
                  {model.description}
                </p>
              )}
              <p className="text-xs text-muted-foreground">
                Created {new Date(model.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={model.is_trained ? "success" : "secondary"}>
              {model.is_trained ? "Trained" : "Untrained"}
            </Badge>
            {!model.is_trained && onTrain && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onTrain(model)}
              >
                <Play className="mr-1 h-3 w-3" />
                Train
              </Button>
            )}
            {model.is_trained && onInference && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onInference(model)}
              >
                <Zap className="mr-1 h-3 w-3" />
                Inference
              </Button>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => handleDelete(model.id, e)}
              disabled={deletingId === model.id}
            >
              {deletingId === model.id ? (
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
