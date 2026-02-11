"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { FolderKanban, Layers, Brain, Loader2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getProjects, getJobs, getTrainedModelsCount } from "@/lib/api";
import type { Project, Job } from "@/types/api";

const CreateProjectDialog = dynamic(
  () => import("@/components/projects/create-project-dialog").then((mod) => mod.CreateProjectDialog),
  { ssr: false }
);

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [trainedModelsCount, setTrainedModelsCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [projectsData, jobsData, modelsData] = await Promise.all([
        getProjects(),
        getJobs({ limit: 5 }),
        getTrainedModelsCount(),
      ]);
      setProjects(projectsData.projects);
      setJobs(jobsData.jobs);
      setTrainedModelsCount(modelsData.trained_models_count);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  const runningJobs = jobs.filter((j) =>
    ["pending", "queued", "running"].includes(j.status)
  );

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to MDplus Hub. Start by creating a project.
          </p>
        </div>
        <CreateProjectDialog />
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <StatCard
          title="Projects"
          value={projects.length.toString()}
          description="Active projects"
          icon={FolderKanban}
        />
        <StatCard
          title="Models"
          value={trainedModelsCount.toString()}
          description="Trained GLIMPS models"
          icon={Brain}
        />
        <StatCard
          title="Jobs"
          value={runningJobs.length.toString()}
          description="Running jobs"
          icon={Layers}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Projects</CardTitle>
            <CardDescription>Your most recently accessed projects</CardDescription>
          </CardHeader>
          <CardContent>
            {projects.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                No projects yet. Create your first project to get started.
              </div>
            ) : (
              <div className="space-y-2">
                {projects.slice(0, 5).map((project) => (
                  <Link
                    key={project.id}
                    href={`/projects/${project.id}`}
                    className="flex items-center justify-between rounded-lg p-3 hover:bg-muted"
                  >
                    <div className="flex items-center gap-2">
                      <FolderKanban className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{project.name}</span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(project.created_at).toLocaleDateString()}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Jobs</CardTitle>
            <CardDescription>Training and inference jobs</CardDescription>
          </CardHeader>
          <CardContent>
            {jobs.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                No jobs yet. Train a model to see jobs here.
              </div>
            ) : (
              <div className="space-y-2">
                {jobs.slice(0, 5).map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between rounded-lg p-3"
                  >
                    <div>
                      <span className="font-medium capitalize">
                        {job.job_type.replace("_", " ")}
                      </span>
                      <p className="text-xs text-muted-foreground">
                        {new Date(job.created_at).toLocaleString()}
                      </p>
                    </div>
                    <span
                      className={`text-xs font-medium ${
                        job.status === "completed"
                          ? "text-green-500"
                          : job.status === "failed"
                            ? "text-red-500"
                            : job.status === "running"
                              ? "text-blue-500"
                              : "text-muted-foreground"
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  description,
  icon: Icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ElementType;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}
