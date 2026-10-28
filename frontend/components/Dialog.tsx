"use client";

import { useEffect, useId, useRef, type ReactNode } from "react";

// Modal de aviso o confirmación con Tailwind (reemplaza alert/confirm nativos, DS-15).
// Sin onCancel es un aviso de un solo botón. Escape y el fondo cancelan (o cierran el aviso).

type Tone = "primary" | "danger" | "warning";

type DialogProps = {
  open: boolean;
  title: string;
  children: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  tone?: Tone;
  busy?: boolean;
  onConfirm: () => void;
  onCancel?: () => void;
};

const TONE_BUTTON: Record<Tone, string> = {
  primary: "bg-blue-700 hover:bg-blue-800",
  danger: "bg-red-600 hover:bg-red-700",
  warning: "bg-amber-600 hover:bg-amber-700",
};

const TONE_ICON: Record<Tone, string> = {
  primary: "bg-blue-100 text-blue-700",
  danger: "bg-red-100 text-red-700",
  warning: "bg-amber-100 text-amber-700",
};

export default function Dialog({
  open,
  title,
  children,
  confirmLabel = "Aceptar",
  cancelLabel = "Cancelar",
  tone = "primary",
  busy = false,
  onConfirm,
  onCancel,
}: DialogProps) {
  const titleId = useId();
  const confirmRef = useRef<HTMLButtonElement>(null);
  const dismiss = onCancel ?? onConfirm;
  // Refs para que el foco solo se mueva al abrir, no en cada render del padre.
  const dismissRef = useRef(dismiss);
  const busyRef = useRef(busy);
  useEffect(() => {
    dismissRef.current = dismiss;
    busyRef.current = busy;
  });

  useEffect(() => {
    if (!open) return;
    confirmRef.current?.focus();
    function handleKey(event: KeyboardEvent) {
      if (event.key === "Escape" && !busyRef.current) dismissRef.current();
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm"
      onClick={() => !busy && dismiss()}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(event) => event.stopPropagation()}
        className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl"
      >
        <div className="flex items-start gap-3">
          <span className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-lg font-bold ${TONE_ICON[tone]}`} aria-hidden="true">
            {tone === "primary" ? "?" : "!"}
          </span>
          <div className="min-w-0 flex-1">
            <h2 id={titleId} className="text-lg font-bold text-slate-900">{title}</h2>
            <div className="mt-2 text-sm text-slate-600">{children}</div>
          </div>
        </div>
        <div className="mt-6 flex justify-end gap-2">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={busy}
              className="rounded-lg px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-100 disabled:opacity-60"
            >
              {cancelLabel}
            </button>
          )}
          <button
            ref={confirmRef}
            type="button"
            onClick={onConfirm}
            disabled={busy}
            className={`rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:opacity-60 ${TONE_BUTTON[tone]}`}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
