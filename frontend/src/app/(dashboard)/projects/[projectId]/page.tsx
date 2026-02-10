"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Settings, Trash2 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { UploadMoleculeDialog } from "@/components/molecules/upload-molecule-dialog";
import { MoleculesList } from "@/components/molecules/molecules-list";
import { CreateModelDialog } from "@/components/models/create-model-dialog";
import { ModelsList } from "@/components/models/models-list";
import { TrainModelDialog } from "@/components/models/train-model-dialog";
import { InferenceDialog } from "@/components/models/inference-dialog";
import { JobsList } from "@/components/jobs/jobs-list";
import { getProject, updateProject, deleteProject } from "@/lib/api";
import type { ProjectDetail, GlimpsModel } from "@/types/api";

interface ProjectPageProps {
  params: { projectId: string };
}

export default function ProjectPage({ params }: ProjectPageProps) {
  const router = useRouter();
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [moleculesRefresh, setMoleculesRefresh] = useState(0);
  const [modelsRefresh, setModelsRefresh] = useState(0);
  const [jobsRefresh, setJobsRefresh] = useState(0);

  const [trainModel, setTrainModel] = useState<GlimpsModel | null>(null);
  const [inferenceModel, setInferenceModel] = useState<GlimpsModel | null>(null);

  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadProject();
  }, [params.projectId]);

  const loadProject = async () => {
    try {
      const data = await getProject(params.projectId);
      setProject(data);
      setEditName(data.name);
      setEditDescription(data.description || "");
    } catch (err) {
      setError("Failed to load project");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    if (!project) return;
    setSaving(true);
    try {
      await updateProject(project.id, {
        name: editName,
        description: editDescription || undefined,
      });
      loadProject();
    } catch (err) {
      alert("Failed to save project settings");
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProject = async () => {
    if (!project) return;
    if (!confirm("Are you sure you want to delete this project? This cannot be undone.")) return;

    setDeleting(true);
    try {
      await deleteProject(project.id);
      router.push("/projects");
    } catch (err) {
      alert("Failed to delete project");
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="flex h-64 items-center justify-center text-destructive">
        {error || "Project not found"}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{project.name}</h1>
        {project.description && (
          <p className="text-muted-foreground">{project.description}</p>
        )}
      </div>

      <Tabs defaultValue="molecules" className="space-y-4">
        <TabsList>
          <TabsTrigger value="molecules">Molecules</TabsTrigger>
          <TabsTrigger value="models">Models</TabsTrigger>
          <TabsTrigger value="jobs">Jobs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="molecules">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Molecules</CardTitle>
                <CardDescription>
                  Molecular structures in this project
                </CardDescription>
              </div>
              <UploadMoleculeDialog
                projectId={project.id}
                onUploadComplete={() => setMoleculesRefresh((n) => n + 1)}
              />
            </CardHeader>
            <CardContent>
              <MoleculesList
                projectId={project.id}
                refreshTrigger={moleculesRefresh}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="models">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>GLIMPS Models</CardTitle>
                <CardDescription>Trained backmapping models</CardDescription>
              </div>
              <CreateModelDialog
                projectId={project.id}
                onCreateComplete={() => setModelsRefresh((n) => n + 1)}
              />
            </CardHeader>
            <CardContent>
              <ModelsList
                projectId={project.id}
                refreshTrigger={modelsRefresh}
                onTrain={(model) => setTrainModel(model)}
                onInference={(model) => setInferenceModel(model)}
              />
            </CardContent>
          </Card>

          <TrainModelDialog
            projectId={project.id}
            model={trainModel}
            open={!!trainModel}
            onOpenChange={(open) => !open && setTrainModel(null)}
            onTrainStarted={() => {
              setJobsRefresh((n) => n + 1);
              setModelsRefresh((n) => n + 1);
            }}
          />

          <InferenceDialog
            projectId={project.id}
            model={inferenceModel}
            open={!!inferenceModel}
            onOpenChange={(open) => !open && setInferenceModel(null)}
            onInferenceStarted={() => setJobsRefresh((n) => n + 1)}
          />
        </TabsContent>

        <TabsContent value="jobs">
          <Card>
            <CardHeader>
              <CardTitle>Jobs</CardTitle>
              <CardDescription>
                Training and inference jobs for this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <JobsList
                projectId={project.id}
                refreshTrigger={jobsRefresh}
                onMoleculeCreated={() => setMoleculesRefresh((n) => n + 1)}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Project Settings</CardTitle>
              <CardDescription>
                Manage project settings
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 max-w-md">
                <div className="grid gap-2">
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    disabled={saving}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={editDescription}
                    onChange={(e) => setEditDescription(e.target.value)}
                    disabled={saving}
                  />
                </div>
                <Button
                  onClick={handleSaveSettings}
                  disabled={saving}
                  className="w-fit"
                >
                  {saving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Settings className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>

              <div className="border-t pt-6">
                <h3 className="text-lg font-medium text-destructive">Danger Zone</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Deleting a project will permanently remove all associated molecules, models, and jobs.
                </p>
                <Button
                  variant="destructive"
                  onClick={handleDeleteProject}
                  disabled={deleting}
                >
                  {deleting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Project
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
