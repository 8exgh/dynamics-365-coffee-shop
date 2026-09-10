export type Product = {
  id: string;
  name: string;
  category: string;
  price: number;
  color: string;
  recipe: Record<string, number>;
};
export type Customer = {
  id: string;
  name: string;
  email: string;
  points: number;
  visits: number;
};
export type Ingredient = {
  id: string;
  name: string;
  unit: string;
  stock: number;
  reorder: number;
  cost: number;
};
export type Order = {
  id: string;
  number: string;
  customer_id: string;
  kind: string;
  status: string;
  subtotal: number;
  tax: number;
  total: number;
  created_at: string;
  payment: string;
  lines: {
    product_id: string;
    name: string;
    quantity: number;
    price: number;
  }[];
};
export type Purchase = {
  id: string;
  number: string;
  vendor_id: string;
  ingredient_id: string;
  quantity: number;
  total: number;
  status: string;
};
export type Case = {
  id: string;
  customer_id: string;
  subject: string;
  priority: string;
  status: string;
  resolution: string;
};
export type Account = {
  account: string;
  name: string;
  debit: number;
  credit: number;
  balance: number;
};
export type Workspace = {
  products: Product[];
  customers: Customer[];
  ingredients: Ingredient[];
  orders: Order[];
  purchases: Purchase[];
  cases: Case[];
  vendors: { id: string; name: string; lead_days: number }[];
  metrics: {
    revenue: number;
    gross_profit: number;
    cash: number;
    receivable: number;
    payable: number;
    inventory_value: number;
    journal_balance: number;
    orders: number;
    low_stock: number;
    closed: boolean;
  };
  accounts: Account[];
  journals: {
    id: string;
    reference: string;
    description: string;
    created_at: string;
    amount: number;
  }[];
  audit: {
    id: number;
    actor: string;
    action: string;
    reference: string;
    detail: string;
    created_at: string;
  }[];
  closes: {
    id: string;
    business_date: string;
    counted: number;
    expected: number;
    variance: number;
  }[];
  connection: {
    configured: boolean;
    write_enabled: boolean;
    environment: string;
    web_url: string;
    company_id: string | null;
  };
};
export type Session = { username: string; role: string; csrf: string };
