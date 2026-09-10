import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowDownLeft,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ClipboardList,
  Coffee,
  CreditCard,
  Download,
  ExternalLink,
  FileText,
  Headphones,
  LayoutDashboard,
  Leaf,
  LogOut,
  Menu,
  Minus,
  Package,
  Plus,
  RefreshCw,
  Search,
  Settings2,
  ShieldCheck,
  ShoppingBag,
  ShoppingCart,
  Sprout,
  Truck,
  Users,
  Wallet,
  X,
} from "lucide-react";
import type { Product, Session, Workspace } from "./types";
import "./styles.css";

const money = (value: number) =>
  new Intl.NumberFormat("en-CA", { style: "currency", currency: "CAD" }).format(
    value / 100,
  );
const count = (value: number) => new Intl.NumberFormat("en-CA").format(value);
const dateLabel = (value: string) =>
  new Date(value).toLocaleString("en-CA", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
const tabs = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "counter", label: "Counter sales", icon: Coffee },
  { id: "orders", label: "Sales & catering", icon: ShoppingBag },
  { id: "inventory", label: "Inventory & recipes", icon: Package },
  { id: "purchasing", label: "Purchasing", icon: Truck },
  { id: "customers", label: "Customers & loyalty", icon: Users },
  { id: "service", label: "Customer care", icon: Headphones },
  { id: "finance", label: "Finance & close", icon: Wallet },
  { id: "dynamics", label: "Business Central", icon: Settings2 },
  { id: "guide", label: "Workflow guide", icon: CircleHelp },
];
const titles: Record<string, [string, string]> = {
  overview: [
    "A good day starts here.",
    "Your coffee shop, from first pour to final count.",
  ],
  counter: [
    "Make someone’s morning.",
    "Create a sale, update stock, and reward your regulars.",
  ],
  orders: [
    "Every order, taken care of.",
    "Follow counter sales and catering from quote to payment.",
  ],
  inventory: [
    "Keep the good stuff flowing.",
    "Ingredient stock, recipe quantities, and waste in one place.",
  ],
  purchasing: [
    "Ready for the next rush.",
    "Order supplies, approve spend, receive stock, and pay suppliers.",
  ],
  customers: [
    "A little more familiar.",
    "Get to know your regulars and grow their loyalty.",
  ],
  service: [
    "Good coffee. Thoughtful care.",
    "Track the details that keep customers coming back.",
  ],
  finance: [
    "Everything adds up.",
    "Review the ledger, reconcile your till, and close the day.",
  ],
  dynamics: [
    "Connected to your business.",
    "Work with your actual Dynamics 365 Business Central environment.",
  ],
  guide: [
    "One shop. The whole workflow.",
    "Explore the common operations behind a coffee business.",
  ],
};

async function api(path: string, options: RequestInit = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  const data = await response.json();
  if (response.status === 401 && path !== "/login")
    window.dispatchEvent(new Event("coffee-session-expired"));
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Please check the entered values.",
    );
  return data;
}

function Badge({
  children,
  tone = "",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return (
    <span className={`badge ${tone || String(children)}`}>
      {String(children).replaceAll("_", " ")}
    </span>
  );
}
function Empty({ children }: { children: React.ReactNode }) {
  return (
    <div className="empty">
      <Sprout size={28} />
      <p>{children}</p>
    </div>
  );
}
function FormField({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  const id = React.useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {React.isValidElement(children)
        ? React.cloneElement(children as React.ReactElement<{ id: string }>, {
            id,
          })
        : children}
    </div>
  );
}
function ProductArt({
  product,
  small = false,
}: {
  product: Product;
  small?: boolean;
}) {
  return (
    <div
      className={`product-art ${product.color} ${small ? "small" : ""}`}
      aria-hidden="true"
    >
      {product.category === "Coffee" ? (
        <div className="cup">
          <div className="coffee-surface">
            <div className="latte-leaf" />
          </div>
          <div className="handle" />
        </div>
      ) : product.id === "croissant" ? (
        <div className="croissant-shape">◜</div>
      ) : product.id === "cookie" ? (
        <div className="cookie-shape">
          <i />
          <i />
          <i />
          <i />
          <i />
        </div>
      ) : (
        <div className="coffee-bag">
          <Leaf size={24} />
          <span>
            HOUSE
            <br />
            BLEND
          </span>
        </div>
      )}
    </div>
  );
}

function Login({ onLogin }: { onLogin: (session: Session) => void }) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <div className="login-page">
      <div className="login-story">
        <div className="wordmark">
          <Coffee /> EIGHT EXAMPLES
        </div>
        <div>
          <span className="eyebrow">THE COFFEE SHOP WORKSPACE</span>
          <h1>
            A better day,
            <br />
            beautifully brewed.
          </h1>
          <p>Thoughtful tools for the people behind every cup.</p>
          <div className="login-cup">
            <Coffee size={140} strokeWidth={0.7} />
          </div>
        </div>
        <span>Operations · Business Central companion</span>
      </div>
      <main className="login-main">
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy(true);
            setError("");
            const form = new FormData(e.currentTarget);
            try {
              onLogin(
                await api("/login", {
                  method: "POST",
                  body: JSON.stringify(Object.fromEntries(form)),
                }),
              );
            } catch (err) {
              setError((err as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          <span className="eyebrow">WELCOME BACK</span>
          <h2>Let’s open up.</h2>
          <p>Sign in to your coffee shop workspace.</p>
          <FormField label="Username">
            <input
              name="username"
              autoComplete="username"
              required
              defaultValue="manager"
            />
          </FormField>
          <FormField label="Password">
            <input
              name="password"
              type="password"
              autoComplete="current-password"
              required
            />
          </FormField>
          {error && (
            <p className="error" role="alert">
              {error}
            </p>
          )}
          <button className="primary wide" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
            <ArrowRight size={17} />
          </button>
          <p className="login-note">
            Use the credentials generated in your server’s .env file.
          </p>
        </form>
      </main>
    </div>
  );
}

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [data, setData] = useState<Workspace | null>(null);
  const [tab, setTab] = useState("overview");
  const [filter, setFilter] = useState("");
  const [category, setCategory] = useState("All");
  const [cart, setCart] = useState<Record<string, number>>({});
  const [customer, setCustomer] = useState("walk-in");
  const [payment, setPayment] = useState("card");
  const [quote, setQuote] = useState(false);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<{
    message: string;
    error: boolean;
  } | null>(null);
  const [modal, setModal] = useState<{ kind: string; id?: string } | null>(
    null,
  );
  const [mobileNav, setMobileNav] = useState(false);
  const [liveResource, setLiveResource] = useState("customers");
  const [liveRows, setLiveRows] = useState<Record<string, unknown>[] | null>(
    null,
  );
  const [liveError, setLiveError] = useState("");
  const [liveBusy, setLiveBusy] = useState(false);
  const [liveCatalog, setLiveCatalog] = useState<{
    customers: Record<string, string>[];
    items: Record<string, string>[];
  } | null>(null);
  const requestKeys = useRef(new Map<string, string>());
  const dialogRef = useRef<HTMLDialogElement>(null);
  const isManager = session?.role === "manager";
  useEffect(() => {
    api("/session")
      .then(setSession)
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);
  useEffect(() => {
    if (session) refresh();
  }, [session]);
  useEffect(() => {
    const expired = () => {
      setSession(null);
      setData(null);
      requestKeys.current.clear();
    };
    window.addEventListener("coffee-session-expired", expired);
    return () => window.removeEventListener("coffee-session-expired", expired);
  }, []);
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 7000);
      return () => clearTimeout(timer);
    }
  }, [toast]);
  useEffect(() => {
    if (modal) dialogRef.current?.showModal();
    else dialogRef.current?.close();
  }, [modal]);
  function go(id: string) {
    setTab(id);
    setFilter("");
    setMobileNav(false);
  }
  async function refresh() {
    try {
      setData(await api("/workspace"));
    } catch (err) {
      setToast({ message: (err as Error).message, error: true });
    }
  }
  async function mutate(path: string, payload: unknown, message: string) {
    if (busy || !session) return false;
    setBusy(true);
    const fingerprint = path + JSON.stringify(payload);
    const key = requestKeys.current.get(fingerprint) || crypto.randomUUID();
    requestKeys.current.set(fingerprint, key);
    try {
      await api(path, {
        method: "POST",
        headers: { "X-CSRF-Token": session.csrf, "Idempotency-Key": key },
        body: JSON.stringify(payload),
      });
      requestKeys.current.delete(fingerprint);
      await refresh();
      setToast({ message, error: false });
      setModal(null);
      return true;
    } catch (err) {
      setToast({ message: (err as Error).message, error: true });
      return false;
    } finally {
      setBusy(false);
    }
  }
  async function loadLive(resource = liveResource) {
    setLiveBusy(true);
    setLiveError("");
    setLiveRows(null);
    try {
      const result = await api(`/dynamics/${resource}`);
      setLiveRows(result.value || []);
    } catch (err) {
      setLiveError((err as Error).message);
    } finally {
      setLiveBusy(false);
    }
  }
  if (!loaded)
    return (
      <div className="loading">
        <Coffee />
        <p>Opening the coffee shop…</p>
      </div>
    );
  if (!session) return <Login onLogin={setSession} />;
  if (!data)
    return (
      <div className="loading">
        <Coffee />
        <p>{toast?.message || "Loading your workspace…"}</p>
        <button onClick={refresh}>Try again</button>
      </div>
    );
  const { metrics } = data;
  const customerName = (id: string) =>
    data.customers.find((c) => c.id === id)?.name || "Counter guest";
  const filtered = <T,>(rows: T[]) =>
    rows.filter((row) =>
      JSON.stringify(row).toLowerCase().includes(filter.toLowerCase()),
    );
  const total = Object.entries(cart).reduce(
    (sum, [id, quantity]) =>
      sum + data.products.find((p) => p.id === id)!.price * quantity,
    0,
  );
  const cartQuantity = Object.values(cart).reduce((a, b) => a + b, 0);
  const lowStock = data.ingredients.filter((i) => i.stock <= i.reorder);
  const topProducts = data.products
    .map((product) => ({
      ...product,
      sold: data.orders
        .filter((o) => o.status === "paid")
        .reduce(
          (sum, order) =>
            sum +
            order.lines
              .filter((l) => l.product_id === product.id)
              .reduce((s, l) => s + l.quantity, 0),
          0,
        ),
    }))
    .sort((a, b) => b.sold - a.sold)
    .slice(0, 4);
  const stockOptions = data.ingredients.map((i) => (
    <option key={i.id} value={i.id}>
      {i.name} ({i.unit})
    </option>
  ));
  const customerOptions = data.customers.map((c) => (
    <option key={c.id} value={c.id}>
      {c.name}
    </option>
  ));
  const button = (label: string, action: () => void, primary = false) => (
    <button
      disabled={busy}
      className={primary ? "primary" : "secondary"}
      onClick={action}
    >
      {label}
    </button>
  );

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? "open" : ""}`}>
        <a
          href="#"
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            go("overview");
          }}
        >
          <span className="brand-icon">
            <Coffee size={26} />
          </span>
          <span>
            eight examples<small>COFFEE & COMPANY</small>
          </span>
        </a>
        <div className="location">
          <span className="location-icon">
            <ShoppingBag size={17} />
          </span>
          <div>
            Old Strathcona<small>Edmonton · Main shop</small>
          </div>
          <ChevronDown size={15} />
        </div>
        <span className="nav-caption">WORKSPACE</span>
        <nav>
          {tabs.slice(0, 8).map((item) => (
            <button
              key={item.id}
              className={tab === item.id ? "active" : ""}
              onClick={() => go(item.id)}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {item.id === "inventory" && lowStock.length > 0 && (
                <b>{lowStock.length}</b>
              )}
            </button>
          ))}
        </nav>
        <div className="nav-bottom">
          <span className="nav-caption">TOOLS & CONNECTIONS</span>
          <nav>
            {tabs.slice(8).map((item) => (
              <button
                key={item.id}
                className={tab === item.id ? "active" : ""}
                onClick={() => go(item.id)}
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
          <div className="practice-note">
            <span className="status-dot" />
            <div>
              Practice workspace<small>Sample data · CAD</small>
            </div>
            <CircleHelp size={15} />
          </div>
          <button
            className="profile"
            onClick={async () => {
              await api("/logout", {
                method: "POST",
                headers: { "X-CSRF-Token": session.csrf },
              });
              setSession(null);
              setData(null);
            }}
          >
            <span className="avatar">
              {session.username.slice(0, 2).toUpperCase()}
            </span>
            <span>
              {session.username}
              <small>
                {session.role === "manager" ? "Shop manager" : "Counter team"}
              </small>
            </span>
            <LogOut size={16} />
          </button>
        </div>
      </aside>
      {mobileNav && (
        <button
          className="nav-scrim"
          aria-label="Close navigation"
          onClick={() => setMobileNav(false)}
        />
      )}
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb">
            <button
              className="icon-button mobile-toggle"
              aria-label="Open navigation"
              onClick={() => setMobileNav(true)}
            >
              <Menu size={20} />
            </button>
            <span>Workspace</span>
            <ChevronRight size={14} />
            <strong>{tabs.find((t) => t.id === tab)?.label}</strong>
          </div>
          <div className="topbar-right">
            <span className="date">
              {new Date().toLocaleDateString("en-CA", {
                weekday: "short",
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </span>
            <span className="top-divider" />
            <span className="open-status">
              <span className={`status-dot ${metrics.closed ? "amber" : ""}`} />
              {metrics.closed ? "Day closed" : "Shop open"}
            </span>
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <span className="eyebrow">
                {tab === "overview"
                  ? "YOUR DAILY BLEND"
                  : tabs.find((t) => t.id === tab)?.label.toUpperCase()}
              </span>
              <h1>{titles[tab][0]}</h1>
              <p>{titles[tab][1]}</p>
            </div>
            <div className="heading-actions">
              {tab === "overview" && (
                <>
                  <button className="secondary" onClick={() => go("finance")}>
                    <BarChart3 size={16} />
                    View reports
                  </button>
                  <button
                    className="primary"
                    onClick={() => {
                      setQuote(false);
                      go("counter");
                    }}
                  >
                    <Plus size={17} />
                    New sale
                  </button>
                </>
              )}
              {tab === "customers" && (
                <button
                  className="primary"
                  onClick={() => setModal({ kind: "customer" })}
                >
                  <Plus size={17} />
                  Add customer
                </button>
              )}
              {tab === "purchasing" && isManager && (
                <button
                  className="primary"
                  onClick={() => setModal({ kind: "purchase" })}
                >
                  <Plus size={17} />
                  Purchase order
                </button>
              )}
              {tab === "service" && (
                <button
                  className="primary"
                  onClick={() => setModal({ kind: "case" })}
                >
                  <Plus size={17} />
                  New issue
                </button>
              )}
              {tab === "orders" && (
                <button
                  className="primary"
                  onClick={() => {
                    setQuote(true);
                    go("counter");
                  }}
                >
                  <Plus size={17} />
                  Catering quote
                </button>
              )}
            </div>
          </div>

          {tab === "overview" && (
            <>
              <section className="metric-grid">
                <Metric
                  label="Net sales"
                  value={money(metrics.revenue)}
                  note={`${metrics.orders} completed orders`}
                  icon={<ShoppingBag />}
                />
                <Metric
                  label="Gross profit"
                  value={money(metrics.gross_profit)}
                  note={
                    metrics.revenue
                      ? `${Math.round((metrics.gross_profit / metrics.revenue) * 100)}% gross margin`
                      : "Ready for your first sale"
                  }
                  icon={<ArrowUpRight />}
                />
                <Metric
                  label="Average order"
                  value={money(
                    metrics.orders
                      ? Math.round(
                          data.orders
                            .filter((o) => o.status === "paid")
                            .reduce((sum, o) => sum + o.subtotal, 0) /
                            metrics.orders,
                        )
                      : 0,
                  )}
                  note="Before sample tax"
                  icon={<Coffee />}
                />
                <Metric
                  label="Inventory value"
                  value={money(metrics.inventory_value)}
                  note={`${lowStock.length} ingredients need attention`}
                  icon={<Package />}
                />
              </section>
              <div className="dashboard-grid">
                <section className="panel sales-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>A taste of today</h2>
                      <p>Your most-loved menu items</p>
                    </div>
                    <Badge tone="neutral">All recorded sales</Badge>
                  </div>
                  <div className="sales-visual">
                    <div>
                      <span className="eyebrow">SOLD WITH A SMILE</span>
                      <strong>
                        {metrics.orders}
                        <span>orders</span>
                      </strong>
                      <p>
                        Good coffee brings
                        <br />
                        people together.
                      </p>
                      <button
                        className="text-button"
                        onClick={() => go("orders")}
                      >
                        Explore your sales
                        <ArrowRight size={15} />
                      </button>
                    </div>
                    <div className="bar-chart">
                      {topProducts.map((p, i) => (
                        <div className="bar-column" key={p.id}>
                          <span>{p.sold}</span>
                          <div
                            className={`bar bar-${i}`}
                            style={{
                              height: `${30 + (110 * p.sold) / Math.max(1, topProducts[0].sold)}px`,
                            }}
                          />
                          <small>{p.name.replace(" · 250 g", "")}</small>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="sales-footer">
                    <span>
                      <span className="status-dot" />
                      Live from your practice ledger
                    </span>
                    <span>Amounts in CAD</span>
                  </div>
                </section>
                <section className="panel attention-panel">
                  <div className="panel-heading">
                    <div>
                      <h2>A little attention</h2>
                      <p>Small things to keep the day moving</p>
                    </div>
                    <span className="attention-count">
                      {lowStock.length +
                        data.cases.filter((c) => c.status === "open").length}
                    </span>
                  </div>
                  <div className="attention-list">
                    {lowStock.slice(0, 2).map((i) => (
                      <button key={i.id} onClick={() => go("inventory")}>
                        <span className="attention-icon amber-bg">
                          <Package size={19} />
                        </span>
                        <span>
                          <strong>{i.name} is running low</strong>
                          <small>
                            {count(i.stock)} {i.unit} left · Reorder at{" "}
                            {count(i.reorder)}
                          </small>
                        </span>
                        <ChevronRight size={16} />
                      </button>
                    ))}
                    <button onClick={() => go("service")}>
                      <span className="attention-icon blue-bg">
                        <Headphones size={19} />
                      </span>
                      <span>
                        <strong>
                          {data.cases.filter((c) => c.status === "open").length}{" "}
                          customer care issue(s)
                        </strong>
                        <small>A personal touch goes a long way</small>
                      </span>
                      <ChevronRight size={16} />
                    </button>
                  </div>
                  <button
                    className="text-button panel-bottom-link"
                    onClick={() => go("purchasing")}
                  >
                    Manage purchasing
                    <ArrowRight size={15} />
                  </button>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>Recent orders</h2>
                      <p>Fresh from the counter</p>
                    </div>
                    <button
                      className="text-button"
                      onClick={() => go("orders")}
                    >
                      View all
                      <ArrowRight size={15} />
                    </button>
                  </div>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Customer</th>
                          <th>Total</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.orders
                          .slice()
                          .reverse()
                          .slice(0, 5)
                          .map((o) => (
                            <tr key={o.id}>
                              <td>
                                <strong>{o.number}</strong>
                                <small>{dateLabel(o.created_at)}</small>
                              </td>
                              <td>{customerName(o.customer_id)}</td>
                              <td className="numeric">{money(o.total)}</td>
                              <td>
                                <Badge>{o.status}</Badge>
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                </section>
                <section className="panel favourites">
                  <div className="panel-heading">
                    <div>
                      <h2>Counter favourites</h2>
                      <p>A shortcut to your next sale</p>
                    </div>
                    <Coffee size={20} />
                  </div>
                  {data.products.slice(0, 3).map((p) => (
                    <button
                      className="favourite-row"
                      key={p.id}
                      onClick={() => {
                        setCart({ [p.id]: 1 });
                        setQuote(false);
                        go("counter");
                      }}
                    >
                      <ProductArt product={p} small />
                      <span>
                        <strong>{p.name}</strong>
                        <small>{p.category}</small>
                      </span>
                      <b>{money(p.price)}</b>
                      <Plus size={15} />
                    </button>
                  ))}
                </section>
              </div>
              <div className="bottom-banner">
                <div className="banner-icon">
                  <Sprout size={25} />
                </div>
                <div>
                  <strong>From a single cup to the bigger picture.</strong>
                  <span>
                    Explore sales, stock, purchasing, and finance with the
                    workflow guide.
                  </span>
                </div>
                <button className="secondary" onClick={() => go("guide")}>
                  Take a look
                  <ArrowRight size={15} />
                </button>
              </div>
            </>
          )}

          {tab === "counter" && (
            <div className="pos-layout">
              <section>
                <div className="toolbar">
                  <div className="segments">
                    {["All", "Coffee", "Bakery", "Retail"].map((c) => (
                      <button
                        key={c}
                        className={category === c ? "selected" : ""}
                        onClick={() => setCategory(c)}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                  <SearchBox
                    value={filter}
                    onChange={setFilter}
                    label="Find a menu item"
                  />
                </div>
                <div className="product-grid">
                  {filtered(data.products)
                    .filter(
                      (p) => category === "All" || p.category === category,
                    )
                    .map((p) => (
                      <button
                        className="product-card"
                        key={p.id}
                        onClick={() =>
                          setCart({ ...cart, [p.id]: (cart[p.id] || 0) + 1 })
                        }
                      >
                        <ProductArt product={p} />
                        <div>
                          <span className="product-category">{p.category}</span>
                          <h3>{p.name}</h3>
                          <span className="product-price">
                            {money(p.price)}
                            <span>
                              <Plus size={17} />
                            </span>
                          </span>
                        </div>
                      </button>
                    ))}
                </div>
                {filtered(data.products).filter(
                  (p) => category === "All" || p.category === category,
                ).length === 0 && (
                  <Empty>No menu items match your search.</Empty>
                )}
                <p className="subtle">
                  Recipes automatically deduct ingredients when a sale or
                  catering invoice is completed.
                </p>
              </section>
              <section className="panel cart">
                <div className="panel-heading">
                  <h2>{quote ? "Catering quote" : "Current order"}</h2>
                  <Badge tone="neutral">{cartQuantity} items</Badge>
                </div>
                <div className="cart-body">
                  <FormField label="Customer">
                    <select
                      value={customer}
                      onChange={(e) => setCustomer(e.target.value)}
                    >
                      {customerOptions}
                    </select>
                  </FormField>
                  {cartQuantity === 0 ? (
                    <Empty>
                      Your next great cup starts here. Add an item from the
                      menu.
                    </Empty>
                  ) : (
                    <div className="cart-lines">
                      {Object.entries(cart).map(([id, quantity]) => {
                        const p = data.products.find((p) => p.id === id)!;
                        return (
                          <div className="cart-line" key={id}>
                            <div>
                              <strong>{p.name}</strong>
                              <small>{money(p.price)} each</small>
                            </div>
                            <div className="quantity">
                              <button
                                aria-label={`Remove one ${p.name}`}
                                onClick={() => {
                                  const next = { ...cart, [id]: quantity - 1 };
                                  if (!next[id]) delete next[id];
                                  setCart(next);
                                }}
                              >
                                <Minus size={13} />
                              </button>
                              <span>{quantity}</span>
                              <button
                                aria-label={`Add one ${p.name}`}
                                onClick={() =>
                                  setCart({ ...cart, [id]: quantity + 1 })
                                }
                              >
                                <Plus size={13} />
                              </button>
                            </div>
                            <b>{money(p.price * quantity)}</b>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  <div className="cart-totals">
                    <p>
                      <span>Subtotal</span>
                      <span>{money(total)}</span>
                    </p>
                    <p>
                      <span>Sample tax · 5%</span>
                      <span>{money(Math.round(total * 0.05))}</span>
                    </p>
                    <p className="grand-total">
                      <span>Total</span>
                      <span>{money(total + Math.round(total * 0.05))}</span>
                    </p>
                  </div>
                  {!quote && (
                    <div className="payment-options">
                      {["card", "cash"].map((p) => (
                        <button
                          key={p}
                          className={payment === p ? "selected" : ""}
                          onClick={() => setPayment(p)}
                        >
                          {p === "card" ? (
                            <CreditCard size={18} />
                          ) : (
                            <Wallet size={18} />
                          )}
                          {p}
                        </button>
                      ))}
                    </div>
                  )}
                  <button
                    className="primary wide"
                    disabled={
                      busy || !cartQuantity || (!quote && metrics.closed)
                    }
                    onClick={async () => {
                      if (
                        await mutate(
                          "/orders",
                          {
                            customer_id: customer,
                            kind: quote ? "quote" : "counter",
                            payment,
                            lines: Object.entries(cart).map(
                              ([product_id, quantity]) => ({
                                product_id,
                                quantity,
                              }),
                            ),
                          },
                          quote
                            ? "Catering quote created."
                            : "Sale completed. Inventory, loyalty, and ledger updated.",
                        )
                      ) {
                        setCart({});
                        if (quote) go("orders");
                      }
                    }}
                  >
                    {busy
                      ? "Saving…"
                      : quote
                        ? "Create quote"
                        : metrics.closed
                          ? "Day is closed"
                          : "Complete sale"}
                    <ArrowRight size={17} />
                  </button>
                  <button
                    className="text-button wide"
                    onClick={() => setQuote(!quote)}
                  >
                    {quote
                      ? "Switch to counter sale"
                      : "Make this a catering quote"}
                  </button>
                  <p className="cart-note">
                    <ShieldCheck size={14} />
                    Practice transaction · no payment is charged
                  </p>
                </div>
              </section>
            </div>
          )}

          {tab === "orders" && (
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Sales documents</h2>
                  <p>Quote → accepted → invoiced → paid</p>
                </div>
                <SearchBox
                  value={filter}
                  onChange={setFilter}
                  label="Search orders"
                />
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Document</th>
                      <th>Customer / items</th>
                      <th>Total</th>
                      <th>Status</th>
                      <th>Next step</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered(data.orders)
                      .slice()
                      .reverse()
                      .map((o) => (
                        <tr key={o.id}>
                          <td>
                            <strong>{o.number}</strong>
                            <small>{dateLabel(o.created_at)}</small>
                          </td>
                          <td>
                            <strong>{customerName(o.customer_id)}</strong>
                            <small>
                              {o.lines
                                .map((l) => `${l.quantity} × ${l.name}`)
                                .join(", ")}
                            </small>
                          </td>
                          <td className="numeric">{money(o.total)}</td>
                          <td>
                            <Badge>{o.status}</Badge>
                          </td>
                          <td>
                            {isManager &&
                              o.status === "draft" &&
                              button("Accept quote", () =>
                                mutate(
                                  `/orders/${o.id}/accept`,
                                  {},
                                  "Quote accepted.",
                                ),
                              )}
                            {isManager &&
                              o.status === "accepted" &&
                              button("Create invoice", () =>
                                mutate(
                                  `/orders/${o.id}/invoice`,
                                  {},
                                  "Catering invoiced. Inventory and receivables updated.",
                                ),
                              )}
                            {isManager &&
                              o.status === "invoiced" &&
                              button("Record payment", () =>
                                mutate(
                                  `/orders/${o.id}/collect`,
                                  {},
                                  "Payment collected and loyalty points added.",
                                ),
                              )}
                            {isManager &&
                              o.status === "paid" &&
                              button("Refund", () =>
                                setModal({ kind: "refund", id: o.id }),
                              )}
                            {o.status === "refunded" && (
                              <span className="subtle">Refund recorded</span>
                            )}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              {filtered(data.orders).length === 0 && (
                <Empty>No matching sales documents.</Empty>
              )}
            </section>
          )}

          {tab === "inventory" && (
            <>
              <div className="metric-grid three">
                <Metric
                  label="Stock value"
                  value={money(metrics.inventory_value)}
                  note="At standard ingredient cost"
                  icon={<Package />}
                />
                <Metric
                  label="Needs replenishing"
                  value={String(lowStock.length)}
                  note="At or below reorder point"
                  icon={<Truck />}
                />
                <Metric
                  label="Menu recipes"
                  value={String(data.products.length)}
                  note="Ingredient usage per item"
                  icon={<ClipboardList />}
                />
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Ingredient inventory</h2>
                    <p>
                      Quantities use grams, millilitres, or individual units.
                    </p>
                  </div>
                  <SearchBox
                    value={filter}
                    onChange={setFilter}
                    label="Search stock"
                  />
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Ingredient</th>
                        <th>On hand</th>
                        <th>Reorder at</th>
                        <th>Stock health</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered(data.ingredients).map((i) => (
                        <tr key={i.id}>
                          <td>
                            <strong>{i.name}</strong>
                            <small>
                              {money(i.cost)} / {i.unit}
                            </small>
                          </td>
                          <td className="numeric">
                            {count(i.stock)}{" "}
                            <span className="subtle">{i.unit}</span>
                          </td>
                          <td>
                            {count(i.reorder)} {i.unit}
                          </td>
                          <td>
                            <div className="stock-meter">
                              <span
                                style={{
                                  width: `${Math.min(100, (i.stock / (i.reorder * 3)) * 100)}%`,
                                  background:
                                    i.stock <= i.reorder
                                      ? "#c68b42"
                                      : "#688571",
                                }}
                              />
                            </div>
                            <small>
                              {i.stock <= i.reorder
                                ? "Reorder soon"
                                : "Well stocked"}
                            </small>
                          </td>
                          <td>
                            {isManager && (
                              <div className="row-actions">
                                {button("Reorder", () =>
                                  setModal({ kind: "purchase", id: i.id }),
                                )}
                                {button("Log waste", () =>
                                  setModal({ kind: "waste", id: i.id }),
                                )}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              <h2 className="section-title">Behind every cup</h2>
              <div className="recipe-grid">
                {data.products.map((p) => (
                  <section className="panel recipe" key={p.id}>
                    <ProductArt product={p} small />
                    <div>
                      <h3>{p.name}</h3>
                      <p>
                        {Object.entries(p.recipe)
                          .map(([id, quantity]) => {
                            const i = data.ingredients.find(
                              (i) => i.id === id,
                            )!;
                            return `${quantity} ${i.unit} ${i.name.toLowerCase()}`;
                          })
                          .join(" · ")}
                      </p>
                    </div>
                  </section>
                ))}
              </div>
            </>
          )}

          {tab === "purchasing" && (
            <>
              <div className="info-strip">
                <ShieldCheck size={19} />
                <span>
                  Purchases of {money(50000)} or more require manager approval
                  before receiving. Receiving adds stock and creates a supplier
                  balance.
                </span>
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Purchase orders</h2>
                  <SearchBox
                    value={filter}
                    onChange={setFilter}
                    label="Search purchases"
                  />
                </div>
                {data.purchases.length === 0 ? (
                  <Empty>
                    No purchase orders yet. Replenish an ingredient to get
                    started.
                  </Empty>
                ) : (
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Order</th>
                          <th>Supplier / ingredient</th>
                          <th>Quantity</th>
                          <th>Total</th>
                          <th>Status</th>
                          <th>Next step</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filtered(data.purchases)
                          .slice()
                          .reverse()
                          .map((p) => (
                            <tr key={p.id}>
                              <td>
                                <strong>{p.number}</strong>
                              </td>
                              <td>
                                <strong>
                                  {
                                    data.vendors.find(
                                      (v) => v.id === p.vendor_id,
                                    )?.name
                                  }
                                </strong>
                                <small>
                                  {
                                    data.ingredients.find(
                                      (i) => i.id === p.ingredient_id,
                                    )?.name
                                  }
                                </small>
                              </td>
                              <td>{count(p.quantity)}</td>
                              <td>{money(p.total)}</td>
                              <td>
                                <Badge>{p.status}</Badge>
                              </td>
                              <td>
                                {isManager &&
                                  p.status !== "paid" &&
                                  button(
                                    p.status === "pending"
                                      ? "Approve"
                                      : p.status === "approved"
                                        ? "Receive & invoice"
                                        : "Pay supplier",
                                    () =>
                                      mutate(
                                        `/purchases/${p.id}/${p.status === "pending" ? "approve" : p.status === "approved" ? "receive" : "pay"}`,
                                        {},
                                        "Purchase updated.",
                                      ),
                                  )}
                              </td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
              <h2 className="section-title">Our supply partners</h2>
              <div className="supplier-grid">
                {data.vendors.map((v) => (
                  <section className="panel supplier" key={v.id}>
                    <span className="supplier-icon">
                      <Truck size={25} />
                    </span>
                    <h3>{v.name}</h3>
                    <p>{v.lead_days} day lead time</p>
                    <Badge tone="neutral">Active supplier</Badge>
                  </section>
                ))}
              </div>
            </>
          )}

          {tab === "customers" && (
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Our regulars</h2>
                  <p>
                    Earn one point per whole dollar of pre-tax sales. Refunds
                    reverse earned points.
                  </p>
                </div>
                <SearchBox
                  value={filter}
                  onChange={setFilter}
                  label="Search customers"
                />
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Customer</th>
                      <th>Loyalty level</th>
                      <th>Points</th>
                      <th>Visits</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered(data.customers)
                      .filter((c) => c.id !== "walk-in")
                      .map((c) => (
                        <tr key={c.id}>
                          <td>
                            <div className="person-cell">
                              <span className="avatar">
                                {c.name
                                  .split(" ")
                                  .map((n) => n[0])
                                  .slice(0, 2)
                                  .join("")}
                              </span>
                              <div>
                                <strong>{c.name}</strong>
                                <small>{c.email || "No email added"}</small>
                              </div>
                            </div>
                          </td>
                          <td>
                            <Badge
                              tone={
                                c.points >= 200
                                  ? "gold"
                                  : c.points >= 80
                                    ? "paid"
                                    : "neutral"
                              }
                            >
                              {c.points >= 200
                                ? "Gold"
                                : c.points >= 80
                                  ? "Regular"
                                  : "Neighbour"}
                            </Badge>
                          </td>
                          <td className="numeric">{c.points}</td>
                          <td>{c.visits}</td>
                          <td>
                            {button("New order", () => {
                              setCustomer(c.id);
                              setQuote(false);
                              go("counter");
                            })}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {tab === "service" && (
            <div className="case-grid">
              {filtered(data.cases).map((c) => (
                <section className="panel case-card" key={c.id}>
                  <div className="case-top">
                    <Badge>{c.status}</Badge>
                    <Badge tone={c.priority === "high" ? "pending" : "neutral"}>
                      {c.priority}
                    </Badge>
                  </div>
                  <h2>{c.subject}</h2>
                  <p>{customerName(c.customer_id)}</p>
                  {c.resolution && (
                    <div className="resolution">
                      <CheckCircle2 size={17} />
                      {c.resolution}
                    </div>
                  )}
                  {c.status === "open" &&
                    button("Resolve issue", () =>
                      setModal({ kind: "resolve", id: c.id }),
                    )}
                </section>
              ))}
              {data.cases.length === 0 && (
                <Empty>No customer issues. A good day all around.</Empty>
              )}
            </div>
          )}

          {tab === "finance" && (
            <>
              <div className="metric-grid">
                <Metric
                  label="Cash in till"
                  value={money(metrics.cash)}
                  note="Includes $200 opening float"
                  icon={<Wallet />}
                />
                <Metric
                  label="Customer balances"
                  value={money(metrics.receivable)}
                  note="Invoiced, awaiting payment"
                  icon={<ArrowDownLeft />}
                />
                <Metric
                  label="Supplier balances"
                  value={money(metrics.payable)}
                  note="Received, awaiting payment"
                  icon={<ArrowUpRight />}
                />
                <Metric
                  label="Trial balance"
                  value={money(metrics.journal_balance)}
                  note={
                    metrics.journal_balance === 0
                      ? "Debits and credits are balanced"
                      : "Review ledger entries"
                  }
                  icon={<ShieldCheck />}
                />
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <div>
                    <h2>Trial balance</h2>
                    <p>Practice ledger · cumulative amounts in CAD</p>
                  </div>
                  <div className="row-actions">
                    {isManager && (
                      <a
                        className="secondary"
                        href="/api/reports/trial-balance.csv"
                      >
                        <Download size={16} />
                        Export CSV
                      </a>
                    )}
                    {isManager &&
                      !metrics.closed &&
                      button(
                        "Close the day",
                        () => setModal({ kind: "close" }),
                        true,
                      )}
                    {metrics.closed && <Badge>Day closed</Badge>}
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Account</th>
                        <th>Name</th>
                        <th>Debits</th>
                        <th>Credits</th>
                        <th>Balance</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.accounts.map((a) => (
                        <tr key={a.account}>
                          <td>{a.account}</td>
                          <td>
                            <strong>{a.name}</strong>
                          </td>
                          <td className="numeric">{money(a.debit)}</td>
                          <td className="numeric">{money(a.credit)}</td>
                          <td className="numeric">{money(a.balance)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
              <div className="dashboard-grid lower-grid">
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Recent journal entries</h2>
                    <FileText size={19} />
                  </div>
                  <div className="activity-list">
                    {data.journals.slice(0, 10).map((j) => (
                      <div key={j.id}>
                        <span className="activity-icon">
                          <FileText size={16} />
                        </span>
                        <div>
                          <strong>{j.description}</strong>
                          <small>
                            {j.reference} · {dateLabel(j.created_at)}
                          </small>
                        </div>
                        <b>{money(j.amount)}</b>
                      </div>
                    ))}
                  </div>
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Activity trail</h2>
                    <ShieldCheck size={19} />
                  </div>
                  <div className="activity-list">
                    {data.audit.slice(0, 10).map((a) => (
                      <div key={a.id}>
                        <span className="activity-icon">
                          <Check size={16} />
                        </span>
                        <div>
                          <strong>{a.action}</strong>
                          <small>
                            {a.reference} · {a.actor}
                          </small>
                          {a.detail && <small>{a.detail}</small>}
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              </div>
              {data.closes.length > 0 && (
                <section className="panel close-history">
                  <div className="panel-heading">
                    <h2>Cash reconciliations</h2>
                  </div>
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Date</th>
                          <th>Expected</th>
                          <th>Counted</th>
                          <th>Variance</th>
                        </tr>
                      </thead>
                      <tbody>
                        {data.closes.map((c) => (
                          <tr key={c.id}>
                            <td>{c.business_date}</td>
                            <td>{money(c.expected)}</td>
                            <td>{money(c.counted)}</td>
                            <td>{money(c.variance)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              )}
            </>
          )}

          {tab === "dynamics" && (
            <>
              <section className="panel connection-card">
                <div className="connection-logo">
                  <Settings2 size={34} />
                </div>
                <div>
                  <h2>Microsoft Dynamics 365 Business Central</h2>
                  <p>
                    {data.connection.configured
                      ? `${data.connection.environment} · Company ${data.connection.company_id}`
                      : "Connect your Microsoft environment to view real business records."}
                  </p>
                  <Badge tone={data.connection.configured ? "paid" : "neutral"}>
                    {data.connection.configured
                      ? "Credentials configured"
                      : "Not connected"}
                  </Badge>
                </div>
                <a
                  className="secondary"
                  href={data.connection.web_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open Business Central
                  <ExternalLink size={15} />
                </a>
              </section>
              <div className="info-strip">
                <CircleHelp size={20} />
                <span>
                  The other workspace pages use a separate practice ledger. This
                  page reads real Business Central records. The native Coffee
                  Shop extension adds your coffee shop role centre, setup,
                  recipes, loyalty, and workflow actions inside Microsoft’s
                  application.
                </span>
              </div>
              {!data.connection.configured ? (
                <section className="panel setup-panel">
                  <h2>Make the connection</h2>
                  <ol className="setup-steps">
                    <li>
                      <span>1</span>
                      <div>
                        <h3>Start your Business Central sandbox</h3>
                        <p>
                          Use the included Windows Docker setup script or an
                          existing online sandbox. Publish the Coffee Shop
                          extension and run Coffee Demo Setup in the dedicated
                          coffee company.
                        </p>
                      </div>
                    </li>
                    <li>
                      <span>2</span>
                      <div>
                        <h3>Register your Microsoft Entra application</h3>
                        <p>
                          For an online connection, grant API.ReadWrite.All
                          application permission and admin consent. Enable the
                          client in Business Central with the required company
                          permissions.
                        </p>
                      </div>
                    </li>
                    <li>
                      <span>3</span>
                      <div>
                        <h3>Add the server connection settings</h3>
                        <p>
                          Set BC_TENANT_ID, BC_ENVIRONMENT, BC_COMPANY_ID,
                          BC_CLIENT_ID, and BC_CLIENT_SECRET in the server
                          environment, then restart the companion app.
                          Credentials stay on the server.
                        </p>
                      </div>
                    </li>
                  </ol>
                  <p className="subtle">
                    See the repository’s Business Central setup guide for
                    Windows container and online environment instructions.
                  </p>
                </section>
              ) : !isManager ? (
                <Empty>Business Central records require manager access.</Empty>
              ) : (
                <section className="panel">
                  <div className="panel-heading">
                    <div className="row-actions">
                      <select
                        aria-label="Business Central record type"
                        value={liveResource}
                        onChange={(e) => {
                          setLiveResource(e.target.value);
                          setLiveRows(null);
                          setLiveError("");
                        }}
                      >
                        {[
                          "customers",
                          "items",
                          "vendors",
                          "salesOrders",
                          "salesInvoices",
                          "purchaseOrders",
                          "purchaseInvoices",
                          "accounts",
                          "generalLedgerEntries",
                          "customerPayments",
                          "dimensions",
                          "locations",
                        ].map((r) => (
                          <option key={r}>{r}</option>
                        ))}
                      </select>
                      <button
                        className="secondary"
                        disabled={liveBusy}
                        onClick={() => loadLive()}
                      >
                        <RefreshCw size={16} />
                        {liveBusy ? "Loading…" : "Load records"}
                      </button>
                    </div>
                    {data.connection.write_enabled && (
                      <button
                        className="primary"
                        disabled={liveBusy}
                        onClick={async () => {
                          setLiveBusy(true);
                          try {
                            const [customers, items] = await Promise.all([
                              api("/dynamics/customers"),
                              api("/dynamics/items"),
                            ]);
                            setLiveCatalog({
                              customers: customers.value,
                              items: items.value,
                            });
                            setModal({ kind: "draft" });
                          } catch (err) {
                            setLiveError((err as Error).message);
                          } finally {
                            setLiveBusy(false);
                          }
                        }}
                      >
                        New live draft
                      </button>
                    )}
                  </div>
                  {liveError && (
                    <p className="error padded" role="alert">
                      {liveError}
                    </p>
                  )}
                  {liveRows === null ? (
                    <Empty>
                      Load a record type to check the connection and browse its
                      first 100 records.
                    </Empty>
                  ) : liveRows.length === 0 ? (
                    <Empty>No records found in this company.</Empty>
                  ) : (
                    <div className="table-wrap live-table">
                      <table>
                        <thead>
                          <tr>
                            {Object.keys(liveRows[0])
                              .filter((k) => !k.startsWith("@"))
                              .slice(0, 6)
                              .map((k) => (
                                <th key={k}>{k}</th>
                              ))}
                          </tr>
                        </thead>
                        <tbody>
                          {liveRows.map((r, i) => (
                            <tr key={i}>
                              {Object.keys(liveRows[0])
                                .filter((k) => !k.startsWith("@"))
                                .slice(0, 6)
                                .map((k) => (
                                  <td key={k}>
                                    {typeof r[k] === "object"
                                      ? JSON.stringify(r[k])
                                      : String(r[k] ?? "")}
                                  </td>
                                ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  <p className="subtle padded">
                    Showing up to 100 records. Use the native Business Central
                    client for full lists, posting, approvals, and reporting.
                  </p>
                </section>
              )}
            </>
          )}

          {tab === "guide" && (
            <>
              <div className="info-strip">
                <CircleHelp size={19} />
                <span>
                  This workspace is a functional practice companion. The
                  Business Central extension implements native coffee shop setup
                  and operations. The native walkthrough in docs/scenarios.md
                  covers the Microsoft screens and ledger checks.
                </span>
              </div>
              <div className="guide-grid">
                {[
                  [
                    "01",
                    "Counter to ledger",
                    "Sell a flat white and croissant. Watch ingredients decrease, loyalty grow, and balanced sales and cost journals appear.",
                    "counter",
                    "Sales invoices · Item ledger · G/L",
                  ],
                  [
                    "02",
                    "Catering, end to end",
                    "Create a quote for North Studio. Accept, invoice, and collect payment. Replenish ingredients if stock is short.",
                    "orders",
                    "Sales quotes · Sales orders · Receivables",
                  ],
                  [
                    "03",
                    "From supplier to shelf",
                    "Create a purchase over $500. Approve it, receive and invoice, then record the supplier payment.",
                    "purchasing",
                    "Purchasing · Approvals · Payables",
                  ],
                  [
                    "04",
                    "A recipe for control",
                    "Review each menu recipe, track reorder points, and log spoiled ingredients with a waste reason.",
                    "inventory",
                    "Assembly BOM · Item journals · Requisition",
                  ],
                  [
                    "05",
                    "Know your regulars",
                    "Add a customer, complete a sale, and check points and visits. Open and resolve a customer care issue.",
                    "customers",
                    "Customers · Contacts · Custom loyalty",
                  ],
                  [
                    "06",
                    "Close with confidence",
                    "Refund a paid order, inspect the trial balance, export CSV, and reconcile the cash till to end the day.",
                    "finance",
                    "Credit memos · Journals · Bank reconciliation",
                  ],
                ].map(([n, title, description, target, native]) => (
                  <section className="panel guide-card" key={n}>
                    <span className="guide-number">{n}</span>
                    <h2>{title}</h2>
                    <p>{description}</p>
                    <small>{native}</small>
                    <button className="text-button" onClick={() => go(target)}>
                      Explore workflow
                      <ArrowRight size={15} />
                    </button>
                  </section>
                ))}
              </div>
            </>
          )}
          <footer>
            <span>Eight Examples Coffee & Company</span>
            <span>
              Practice workspace · Sample tax and data · Dynamics 365 companion
            </span>
          </footer>
        </main>
      </div>

      <dialog
        ref={dialogRef}
        onCancel={() => setModal(null)}
        onClick={(e) => {
          if (e.target === e.currentTarget && !busy) setModal(null);
        }}
      >
        <div className="modal-heading">
          <h2>
            {
              (
                {
                  customer: "Meet a new regular",
                  purchase: "Create purchase order",
                  waste: "Record ingredient waste",
                  case: "Open a care issue",
                  resolve: "Resolve care issue",
                  close: "Close and reconcile today",
                  refund: "Refund this order",
                  draft: "Create a Business Central draft",
                } as Record<string, string>
              )[modal?.kind || ""]
            }
          </h2>
          <button
            className="icon-button"
            aria-label="Close dialog"
            disabled={busy}
            onClick={() => setModal(null)}
          >
            <X size={21} />
          </button>
        </div>
        {modal && (
          <form
            key={modal.kind + modal.id}
            onSubmit={async (e) => {
              e.preventDefault();
              const f = Object.fromEntries(new FormData(e.currentTarget));
              const id = modal.id;
              switch (modal.kind) {
                case "customer":
                  await mutate("/customers", f, "Customer added.");
                  break;
                case "purchase":
                  await mutate(
                    "/purchases",
                    { ...f, quantity: Number(f.quantity) },
                    "Purchase order created.",
                  );
                  break;
                case "waste":
                  await mutate(
                    "/waste",
                    { ...f, quantity: Number(f.quantity) },
                    "Waste recorded and inventory adjusted.",
                  );
                  break;
                case "case":
                  await mutate("/cases", f, "Customer care issue opened.");
                  break;
                case "resolve":
                  await mutate(
                    `/cases/${id}/resolve`,
                    f,
                    "Customer care issue resolved.",
                  );
                  break;
                case "close":
                  await mutate(
                    "/close",
                    { counted: Math.round(Number(f.counted) * 100) },
                    "Day closed. Cash reconciliation recorded.",
                  );
                  break;
                case "refund":
                  await mutate(
                    `/orders/${id}/refund`,
                    { restock: f.restock === "on" },
                    "Order refunded. Loyalty and ledger updated.",
                  );
                  break;
                case "draft":
                  await mutate(
                    "/dynamics/draft-order",
                    { ...f, quantity: Number(f.quantity) },
                    "Draft created in Business Central. Open the native client to review.",
                  );
                  break;
              }
            }}
          >
            {modal.kind === "customer" && (
              <>
                <FormField label="Full name or company">
                  <input
                    name="name"
                    required
                    minLength={2}
                    maxLength={100}
                    autoFocus
                  />
                </FormField>
                <FormField label="Email">
                  <input name="email" type="email" maxLength={150} />
                </FormField>
              </>
            )}
            {["purchase", "waste"].includes(modal.kind) && (
              <>
                <FormField label="Ingredient">
                  <select name="ingredient_id" defaultValue={modal.id || "oat"}>
                    {stockOptions}
                  </select>
                </FormField>
                <FormField label="Quantity in ingredient units">
                  <input
                    name="quantity"
                    type="number"
                    min={1}
                    max={100000}
                    step={1}
                    required
                    defaultValue={modal.kind === "purchase" ? 1000 : 1}
                  />
                </FormField>
                {modal.kind === "purchase" ? (
                  <>
                    <FormField label="Supplier">
                      <select name="vendor_id">
                        {data.vendors.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.name}
                          </option>
                        ))}
                      </select>
                    </FormField>
                    <p className="subtle">
                      Cost uses the ingredient’s standard unit cost. Orders of
                      $500 or more enter pending approval.
                    </p>
                  </>
                ) : (
                  <FormField label="Reason">
                    <input
                      name="reason"
                      required
                      minLength={3}
                      maxLength={200}
                      placeholder="e.g. Milk past its use-by date"
                    />
                  </FormField>
                )}
              </>
            )}
            {modal.kind === "case" && (
              <>
                <FormField label="Customer">
                  <select name="customer_id">{customerOptions}</select>
                </FormField>
                <FormField label="Subject">
                  <input
                    name="subject"
                    required
                    minLength={3}
                    maxLength={180}
                  />
                </FormField>
                <FormField label="Priority">
                  <select name="priority">
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                  </select>
                </FormField>
              </>
            )}
            {modal.kind === "resolve" && (
              <FormField label="Resolution">
                <textarea
                  name="resolution"
                  minLength={3}
                  maxLength={500}
                  required
                  rows={4}
                  placeholder="How did we take care of it?"
                />
              </FormField>
            )}
            {modal.kind === "close" && (
              <>
                <p>
                  The ledger expects <strong>{money(metrics.cash)}</strong> in
                  the till, including the opening float. Enter the actual count
                  to post any variance. Counter sales and cash refunds will
                  close for today.
                </p>
                <FormField label="Counted cash (CAD)">
                  <input
                    name="counted"
                    type="number"
                    min={0}
                    max={100000}
                    step="0.01"
                    required
                    defaultValue={(metrics.cash / 100).toFixed(2)}
                  />
                </FormField>
              </>
            )}
            {modal.kind === "refund" && (
              <>
                <p>
                  Record a full practice refund of{" "}
                  <strong>
                    {money(data.orders.find((o) => o.id === modal.id)!.total)}
                  </strong>{" "}
                  to the original payment method. Earned loyalty points will be
                  reversed.
                </p>
                {data.orders
                  .find((o) => o.id === modal.id)!
                  .lines.every((l) => l.product_id === "house-blend") ? (
                  <label className="checkbox">
                    <input type="checkbox" name="restock" />
                    Return unopened retail bags to inventory
                  </label>
                ) : (
                  <p className="subtle">
                    Prepared food and drinks remain consumed. This refund does
                    not return ingredients to stock.
                  </p>
                )}
              </>
            )}
            {modal.kind === "draft" && (
              <>
                <div className="info-strip">
                  This creates a real, unposted sales order in{" "}
                  {data.connection.environment}. It does not transfer practice
                  transactions.
                </div>
                <FormField label="Business Central customer">
                  <select name="customer_id" required>
                    {liveCatalog?.customers.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.displayName}
                      </option>
                    ))}
                  </select>
                </FormField>
                <FormField label="Business Central item">
                  <select name="item_id" required>
                    {liveCatalog?.items.map((i) => (
                      <option key={i.id} value={i.id}>
                        {i.displayName}
                      </option>
                    ))}
                  </select>
                </FormField>
                <FormField label="Quantity">
                  <input
                    name="quantity"
                    type="number"
                    min={1}
                    max={500}
                    step={1}
                    required
                    defaultValue={1}
                  />
                </FormField>
              </>
            )}
            <div className="modal-actions">
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => setModal(null)}
              >
                Cancel
              </button>
              <button
                className="primary"
                disabled={
                  busy ||
                  (modal.kind === "draft" &&
                    (!liveCatalog?.customers.length ||
                      !liveCatalog?.items.length))
                }
              >
                {busy
                  ? "Saving…"
                  : modal.kind === "close"
                    ? "Reconcile & close"
                    : modal.kind === "refund"
                      ? "Record refund"
                      : "Save"}
                <Check size={16} />
              </button>
            </div>
          </form>
        )}
      </dialog>
      {toast && (
        <div
          className={`toast ${toast.error ? "toast-error" : ""}`}
          role={toast.error ? "alert" : "status"}
        >
          {toast.error ? <CircleHelp size={20} /> : <CheckCircle2 size={20} />}
          <span>{toast.message}</span>
          <button
            className="icon-button"
            aria-label="Dismiss notification"
            onClick={() => setToast(null)}
          >
            <X size={17} />
          </button>
        </div>
      )}
    </div>
  );
}
function Metric({
  label,
  value,
  note,
  icon,
}: {
  label: string;
  value: string;
  note: string;
  icon: React.ReactNode;
}) {
  return (
    <section className="panel metric">
      <div>
        <span>{label}</span>
        <span className="metric-icon">{icon}</span>
      </div>
      <strong>{value}</strong>
      <small>{note}</small>
    </section>
  );
}
function SearchBox({
  value,
  onChange,
  label,
}: {
  value: string;
  onChange: (value: string) => void;
  label: string;
}) {
  return (
    <label className="search">
      <Search size={16} />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={label}
        aria-label={label}
      />
      {value && (
        <button aria-label="Clear search" onClick={() => onChange("")}>
          <X size={14} />
        </button>
      )}
    </label>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
