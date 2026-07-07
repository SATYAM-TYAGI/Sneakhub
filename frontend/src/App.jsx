import { useState, useEffect } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// Pre-seeded standard options for dropdown selectors
const BRANDS = ["Nike", "Adidas", "New Balance", "Reebok", "Puma", "Vans", "Converse", "Asics", "Skechers", "Fila"];
const CATEGORIES = ["Running", "Casual", "Basketball", "Skate", "Training", "Walking"];
const GENDERS = [
  { value: "men", label: "Men" },
  { value: "women", label: "Women" },
  { value: "unisex", label: "Unisex" },
];
const COLORS = ["Black", "White", "Red", "Blue", "Grey", "Pink", "Navy", "Green", "Yellow"];
const MATERIALS = ["Leather", "Primeknit", "Canvas", "Mesh", "Suede", "Synthetic"];

const FALLBACK_IMAGES = [
  "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop", // Red Nike
  "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop", // Multicolor
  "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&auto=format&fit=crop", // Orange/Black
  "https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=600&auto=format&fit=crop", // Lime Green
  "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=600&auto=format&fit=crop", // White Adidas
];

export default function App() {
  // Form states
  const [brand, setBrand] = useState(BRANDS[0]);
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [gender, setGender] = useState(GENDERS[0].value);
  const [color, setColor] = useState(COLORS[0]);
  const [material, setMaterial] = useState(MATERIALS[0]);
  const [budget, setBudget] = useState(120);

  // Status and result states
  const [apiConnected, setApiConnected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [searched, setSearched] = useState(false);

  // Check API health on mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => {
        if (res.ok) setApiConnected(true);
        else setApiConnected(false);
      })
      .catch(() => setApiConnected(false));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSearched(true);

    const payload = {
      brand,
      category,
      gender,
      color,
      material,
      budget: Number(budget),
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setRecommendations(data);
    } catch (err) {
      console.error("API error:", err);
      setError(err.message || "Failed to fetch sneaker recommendations. Please check your backend.");
    } finally {
      setLoading(false);
    }
  };

  const getFallbackImage = (name) => {
    const hash = name.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return FALLBACK_IMAGES[hash % FALLBACK_IMAGES.length];
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-rose-500 selection:text-white">
      {/* Header Banner */}
      <header className="relative overflow-hidden border-b border-slate-800 bg-slate-900/50 py-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(244,63,94,0.15),transparent_40%)]" />
        <div className="container mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-xs">
            <span className={`h-2 w-2 rounded-full ${apiConnected === true ? "bg-emerald-500 animate-pulse" : apiConnected === false ? "bg-rose-500" : "bg-amber-500"}`} />
            <span className="text-slate-400 font-medium">
              {apiConnected === true ? "API Connected" : apiConnected === false ? "API Offline" : "Connecting..."}
            </span>
          </div>
          <h1 className="mt-4 text-4xl font-extrabold tracking-tight sm:text-5xl bg-gradient-to-r from-rose-400 via-rose-500 to-amber-500 bg-clip-text text-transparent">
            Sneakhub
          </h1>
          <p className="mx-auto mt-3 max-w-xl text-slate-400 text-sm sm:text-base">
            Find the perfect pair. Enter your preferences below and let our Random Forest model predict compatibility scores to recommend your next sneakers.
          </p>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="container mx-auto max-w-6xl px-4 py-12">
        <div className="grid gap-12 lg:grid-cols-12">
          {/* Form Selector Card */}
          <section className="lg:col-span-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-xl shadow-xl">
              <h2 className="text-xl font-semibold text-slate-200">Sneaker Preferences</h2>
              <p className="text-xs text-slate-500 mt-1">Refine options to generate predictions.</p>

              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                <div>
                  <label htmlFor="brand-select" className="text-xs font-semibold text-slate-400">Brand</label>
                  <select
                    id="brand-select"
                    value={brand}
                    onChange={(e) => setBrand(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                  >
                    {BRANDS.map((b) => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="category-select" className="text-xs font-semibold text-slate-400">Category</label>
                  <select
                    id="category-select"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                  >
                    {CATEGORIES.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="gender-select" className="text-xs font-semibold text-slate-400">Gender</label>
                  <select
                    id="gender-select"
                    value={gender}
                    onChange={(e) => setGender(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                  >
                    {GENDERS.map((g) => (
                      <option key={g.value} value={g.value}>{g.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="color-select" className="text-xs font-semibold text-slate-400">Color</label>
                  <select
                    id="color-select"
                    value={color}
                    onChange={(e) => setColor(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                  >
                    {COLORS.map((col) => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="material-select" className="text-xs font-semibold text-slate-400">Material</label>
                  <select
                    id="material-select"
                    value={material}
                    onChange={(e) => setMaterial(e.target.value)}
                    className="mt-1 block w-full rounded-lg border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                  >
                    {MATERIALS.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label htmlFor="budget-input" className="text-xs font-semibold text-slate-400">Budget (USD)</label>
                  <div className="relative mt-1 rounded-lg shadow-sm">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                      <span className="text-slate-500 text-sm">$</span>
                    </div>
                    <input
                      id="budget-input"
                      type="number"
                      min="1"
                      max="1000"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      className="block w-full rounded-lg border border-slate-800 bg-slate-950 py-2 pl-7 pr-3 text-sm text-slate-300 focus:border-rose-500 focus:outline-none"
                      required
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="mt-2 w-full rounded-xl bg-gradient-to-r from-rose-500 to-rose-600 py-3 text-sm font-semibold text-white transition-all hover:from-rose-600 hover:to-rose-700 focus:outline-none disabled:opacity-50"
                >
                  {loading ? "Matching Features..." : "Match Sneakers"}
                </button>
              </form>
            </div>
          </section>

          {/* Results Grid List */}
          <section className="lg:col-span-8">
            <h2 className="text-2xl font-bold tracking-tight text-slate-200">Recommended Matches</h2>

            {/* Empty State before search */}
            {!searched && !loading && (
              <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 py-16 text-center">
                <span className="text-4xl">👟</span>
                <h3 className="mt-4 text-base font-semibold text-slate-400">Ready to Match</h3>
                <p className="mt-1 text-xs text-slate-500 max-w-xs">
                  Fill in your preferences on the left and submit to see prediction results.
                </p>
              </div>
            )}

            {/* Loading Indicator */}
            {loading && (
              <div className="mt-6 flex flex-col items-center justify-center py-20">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-rose-500 border-t-transparent" />
                <span className="mt-4 text-sm font-medium text-slate-400 animate-pulse">Running ML predictions...</span>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mt-6 rounded-xl border border-rose-900 bg-rose-950/20 p-4 text-sm text-rose-400">
                <p className="font-semibold">Query Failed</p>
                <p className="mt-1 text-xs opacity-80">{error}</p>
              </div>
            )}

            {/* Success Listing */}
            {searched && !loading && !error && (
              <div className="mt-6 space-y-6">
                {recommendations.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800 py-16 text-center">
                    <span className="text-4xl">🤷‍♂️</span>
                    <h3 className="mt-4 text-base font-semibold text-slate-400">No Sneakers Found</h3>
                    <p className="mt-1 text-xs text-slate-500">Try broadening your target selections.</p>
                  </div>
                ) : (
                  recommendations.map((item, index) => (
                    <article
                      key={item.id}
                      className="group relative flex flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/40 transition-all hover:border-slate-700 hover:bg-slate-900/60 sm:flex-row shadow-lg"
                    >
                      {/* Image Container */}
                      <div className="relative h-48 w-full shrink-0 bg-slate-950 sm:h-auto sm:w-48 overflow-hidden border-b border-slate-800 sm:border-b-0 sm:border-r">
                        <img
                          src={item.image_url || getFallbackImage(item.display_name)}
                          alt={item.display_name}
                          onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = getFallbackImage(item.display_name);
                          }}
                          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />
                        <div className="absolute top-3 left-3 rounded-md bg-slate-900/80 px-2 py-1 text-xs font-semibold text-slate-300">
                          #{index + 1}
                        </div>
                      </div>

                      {/* Content details */}
                      <div className="flex flex-col justify-between p-6 w-full">
                        <div>
                          <div className="flex flex-wrap items-center justify-between gap-2">
                            <div>
                              <span className="text-xs font-semibold uppercase tracking-wider text-rose-500">{item.brand}</span>
                              <span className="mx-1.5 text-slate-600">•</span>
                              <span className="text-xs text-slate-400">{item.category}</span>
                            </div>
                            {/* Score Badge */}
                            <div className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-2.5 py-0.5 text-xs font-semibold text-rose-400">
                              <span>★★★★★</span>
                              <span>{item.predicted_score}% Match</span>
                            </div>
                          </div>

                          <h3 className="mt-2 text-lg font-bold text-slate-200 group-hover:text-slate-100">
                            {item.display_name}
                          </h3>
                          <p className="mt-1 text-sm font-semibold text-amber-500">${item.price.toFixed(2)}</p>

                          <p className="mt-3 text-xs text-slate-400 leading-relaxed line-clamp-2">
                            {item.description || "High performance sports sneaker engineered for durability and style matching your selections."}
                          </p>
                        </div>

                        {/* Explanations checklists */}
                        <div className="mt-4 flex flex-wrap gap-2">
                          {item.explanations.map((exp) => (
                            <span
                              key={exp}
                              className="inline-flex items-center gap-1 rounded bg-slate-950 px-2 py-0.5 text-[10px] font-medium text-emerald-400"
                            >
                              ✓ {exp}
                            </span>
                          ))}
                        </div>

                        {/* Footer Action */}
                        <div className="mt-5 flex justify-end">
                          <button
                            onClick={() => {
                              const url = item.product_url || `https://duckduckgo.com/?q=${encodeURIComponent(item.display_name)}+shoes`;
                              window.open(url, "_blank", "noopener,noreferrer");
                            }}
                            className="inline-flex items-center rounded-lg bg-slate-950 border border-slate-800 px-4 py-2 text-xs font-semibold text-slate-300 hover:border-slate-700 hover:bg-slate-900 transition-colors"
                          >
                            View Product
                          </button>
                        </div>
                      </div>
                    </article>
                  ))
                )}
              </div>
            )}
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-8 text-center text-xs text-slate-600">
        <p>© 2026 Sneakhub Recommendation Engine. All rights reserved.</p>
      </footer>
    </div>
  );
}
