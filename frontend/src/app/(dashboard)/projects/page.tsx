"use client";

import dynamic from "next/dynamic";
import { ProjectsList } from "@/components/projects/projects-list";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const CreateProjectDialog = dynamic(
  () => import("@/components/projects/create-project-dialog").then((mod) => mod.CreateProjectDialog),
  { ssr: false }
);

export default function ProjectsPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage your molecular dynamics projects
          </p>
        </div>
        <CreateProjectDialog />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Projects</CardTitle>
          <CardDescription>
            Projects you own or have been invited to
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ProjectsList />
        </CardContent>
      </Card>
    </div>
  );
}
