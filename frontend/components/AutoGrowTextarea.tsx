"use client";

// Lote 4 (DS-50, pedido de Pablo 2026-11-09): campo de texto que crece con el contenido hasta
// un alto máximo y luego muestra scroll; nunca queda como un bloque pequeño fijo. Ocupa todo el
// ancho disponible (responsivo), corta las palabras largas y muestra un contador de caracteres.
// Se ajusta con JavaScript porque `field-sizing: content` aún no funciona en todos los
// navegadores.

import { useLayoutEffect, useRef, type TextareaHTMLAttributes } from "react";

type Props = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, "value" | "onChange"> & {
  value: string;
  onValueChange: (value: string) => void;
  maxLength: number;
  invalid?: boolean;
};

export default function AutoGrowTextarea({
  value,
  onValueChange,
  maxLength,
  invalid = false,
  className = "",
  rows = 3,
  ...rest
}: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight}px`; // max-h-64 limita y activa el scroll
  }, [value]);

  return (
    <div className="mt-1">
      <textarea
        ref={ref}
        rows={rows}
        value={value}
        maxLength={maxLength}
        aria-invalid={invalid}
        onChange={(event) => onValueChange(event.target.value)}
        className={`block max-h-64 min-h-[5rem] w-full resize-y overflow-y-auto whitespace-pre-wrap break-words rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-900 focus:border-blue-600 focus:outline-none ${className}`}
        {...rest}
      />
      <p className="mt-1 text-right text-xs text-slate-500" aria-live="polite">
        {value.length}/{maxLength}
      </p>
    </div>
  );
}
