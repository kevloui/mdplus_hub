"use client";

import { useEffect, useState } from "react";
import { Loader2, XCircle, Clock, CheckCircle, Play, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { getJobs, cancelJob } from "@/lib/api";
import type { Job } from "@/types/api";

interface JobsListProps {
  projectId?: string;
  refreshTrigger?: number;
}

const statusConfig: Record<
  Job["status"],
  { icon: React.ElementType; variant: "default" | "secondary" | "success" | "destructive" | "warning" }
> = {
  pending: { icon: Clock, variant: "secondary" },
  queued: { icon: Clock, variant: "secondary" },
  running: { icon: Play, variant: "default" },
  completed: { icon: CheckCircle, variant: "success" },
  failed: { icon: AlertCircle, variant: "destructive" },
  cancelled: { icon: XCircle, variant: "secondary" },
};

const jobTypeLabels: Record<Job["job_type"], string> = {
  training: "Training",
  inference: "Inference",
  file_processing: "File Processing",
};

export function JobsList({ projectId, refreshTrigger }: JobsListProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  useEffect(() => {
    loadJobs();
    const interval = setInterval(loadJobs, 5000);
    return () => clearInterval(interval);
  }, [projectId, refreshTrigger]);

  const loadJobs = async () => {
    try {
      const data = await getJobs({ projectId });
      setJobs(data.jobs);
      if (loading) setLoading(false);
    } catch (err) {
      if (loading) {
        setError("Failed to load jobs");
        setLoading(false);
      }
    }
  };

  const handleCancel = async (jobId: string) => {
    if (!confirm("Are you sure you want to cancel this job?")) return;

    setCancellingId(jobId);
    try {
      await cancelJob(jobId);
      loadJobs();
    } catch (err) {
      alert("Failed to cancel job");
    } finally {
      setCancellingId(null);
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

  if (jobs.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-muted-foreground">
        No jobs yet.
      </div>
    );
  }

  return (
    <div className="divide-y">
      {jobs.map((job) => {
        const config = statusConfig[job.status];
        const StatusIcon = config.icon;
        const canCancel = ["pending", "queued", "running"].includes(job.status);

        return (
          <div key={job.id} className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <StatusIcon
                  className={`h-5 w-5 ${
                    job.status === "running" ? "animate-pulse text-primary" : "text-muted-foreground"
                  }`}
                />
                <div>
                  <p className="font-medium">
                    {jobTypeLabels[job.job_type]}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Started {job.started_at ? new Date(job.started_at).toLocaleString() : "pending"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={config.variant}>{job.status}</Badge>
                {canCancel && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCancel(job.id)}
                    disabled={cancellingId === job.id}
                  >
                    {cancellingId === job.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <XCircle className="h-4 w-4" />
                    )}
                  </Button>
                )}
              </div>
            </div>
            {job.status === "running" && (
              <div className="mt-3">
                <Progress value={job.progress_percent} />
                {job.progress_message && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    {job.progress_message}
                  </p>
                )}
              </div>
            )}
            {job.status === "failed" && job.error_message && (
              <p className="mt-2 text-sm text-destructive">
                {job.error_message}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
