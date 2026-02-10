"use client";

import { JobsList } from "@/components/jobs/jobs-list";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function JobsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Jobs</h1>
        <p className="text-muted-foreground">
          Monitor your training and inference jobs
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Jobs</CardTitle>
          <CardDescription>
            Recent training and inference jobs across all projects
          </CardDescription>
        </CardHeader>
        <CardContent>
          <JobsList />
        </CardContent>
      </Card>
    </div>
  );
}
