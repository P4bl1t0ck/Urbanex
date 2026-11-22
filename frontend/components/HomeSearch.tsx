// Native GET form: shareable catalog URLs, usable before JavaScript loads.
export default function HomeSearch() {
  return <form action="/properties" method="get" className="mx-auto mt-8 w-full max-w-4xl rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-lg shadow-slate-200/50 sm:p-6">
    <fieldset>
      <legend className="mb-3 text-sm font-medium text-slate-700">Comprar o alquilar <span className="font-normal text-slate-500">(opcional)</span></legend>
      <div className="inline-flex gap-1 rounded-xl bg-slate-100 p-1">
        {[["venta", "Comprar"], ["arriendo", "Alquilar"]].map(([value, label]) => <label key={value} className="cursor-pointer">
          <input type="radio" name="operation_type" value={value} className="peer sr-only" />
          <span className="flex min-h-11 items-center justify-center rounded-lg px-6 py-2 text-sm font-semibold text-slate-600 peer-checked:bg-blue-700 peer-checked:text-white peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-blue-700">{label}</span>
        </label>)}
      </div>
    </fieldset>
    <div className="mt-5 grid gap-4 sm:grid-cols-[minmax(0,1fr)_minmax(0,1.5fr)_auto] sm:items-end">
      <label className="block text-sm font-medium text-slate-700">Tipo de inmueble <span className="font-normal text-slate-500">(opcional)</span>
        <select name="property_type" defaultValue="" className="mt-2 min-h-12 w-full min-w-0 rounded-lg border border-slate-300 bg-white px-3 py-2 text-base text-slate-900 focus:outline-2 focus:outline-blue-700">
          <option value="">Tipo de inmueble</option>
          <option value="casa">Casa</option>
          <option value="departamento">Departamento</option>
          <option value="terreno">Terreno</option>
          <option value="local">Local comercial</option>
        </select>
      </label>
      <label className="block text-sm font-medium text-slate-700">¿Dónde buscas?
        <input type="search" name="location" maxLength={500} placeholder="Ciudad, barrio o sector" className="mt-2 min-h-12 w-full min-w-0 rounded-lg border border-slate-300 px-3 py-2 text-base text-slate-900 focus:outline-2 focus:outline-blue-700" />
      </label>
      <button type="submit" className="min-h-12 rounded-lg bg-blue-700 px-7 py-3 text-base font-semibold text-white hover:bg-blue-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700">Buscar</button>
    </div>
    <button type="reset" className="mt-4 min-h-11 rounded-lg px-2 text-sm font-semibold text-slate-600 underline hover:text-slate-900 focus-visible:outline-2 focus-visible:outline-blue-700">Limpiar búsqueda</button>
  </form>;
}
