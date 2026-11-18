import type { ReactNode } from "react";

const widths = {
  catalog: "max-w-[1600px]",
  standard: "max-w-6xl",
  narrow: "max-w-5xl",
};

/** Shared spacing for primary pages; the site navigation belongs to the root layout. */
export default function PageLayout({ children, width = "standard" }: {
  children: ReactNode;
  width?: keyof typeof widths;
}) {
  return <main className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
    <div className={`mx-auto ${widths[width]}`}>{children}</div>
  </main>;
}

export function PageHeader({ eyebrow, title, description, actions }: {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  actions?: ReactNode;
}) {
  return <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <div className="min-w-0">
      <p className="text-sm font-semibold uppercase tracking-wider text-blue-700">{eyebrow}</p>
      <h1 className="mt-1 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">{title}</h1>
      {description && <div className="mt-2 text-sm text-slate-600">{description}</div>}
    </div>
    {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
  </header>;
}
