import { TerraLensApp } from "@/components/TerraLensApp";

// Server Component shell — renders the static scaffold instantly.
// All interactivity (file uploads, API calls, state) lives inside
// TerraLensApp which is a Client Component.
export default function Page() {
  return <TerraLensApp />;
}
