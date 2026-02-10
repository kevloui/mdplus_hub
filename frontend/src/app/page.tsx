import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary" />
            <span className="text-xl font-semibold">MDplus Hub</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Log in</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center px-4">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl">
            Molecular Dynamics
            <br />
            <span className="text-primary">Backmapping Platform</span>
          </h1>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Transform coarse-grained molecular structures to atomistic
            resolution using GLIMPS machine learning. Visualize, train, and
            analyze your molecular data with an intuitive, modern interface.
          </p>
          <div className="mt-10 flex items-center justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="px-8">
                Start Free
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="px-8">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        <div className="mt-20 grid max-w-5xl grid-cols-1 gap-8 md:grid-cols-3">
          <FeatureCard
            title="GLIMPS Backmapping"
            description="Machine learning approach to transform coarse-grained structures to atomistic resolution with high accuracy."
          />
          <FeatureCard
            title="3D Visualization"
            description="Interactive molecular viewer powered by Mol* for exploring structures in split or overlay modes."
          />
          <FeatureCard
            title="Cloud Processing"
            description="Train models and run inference in the cloud with real-time progress tracking."
          />
        </div>
      </main>

      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          MDplus Hub - Built with FastAPI, Next.js, and Mol*
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-xl border bg-card p-6">
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
