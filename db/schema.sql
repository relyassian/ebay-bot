-- Supabase / Postgres schema (M1). Money in USD numeric(10,2).
create table if not exists products (
  id bigserial primary key,
  brand text not null,
  model text not null,
  colorway text,
  style_code text unique,          -- identity key; never match by name alone
  category text not null,          -- sneaker | loafer | dress_shoe | accessory
  size_system text,                -- US | UK | IT | EU
  retail_price numeric(10,2),
  discontinued_verified boolean default false,
  created_at timestamptz default now()
);

create table if not exists size_map (
  brand text not null,
  native_system text not null,
  native_size text not null,
  us_size text not null,
  width text not null default '',  -- D, EE, EEE for dress shoes; '' when not applicable
  primary key (brand, native_system, native_size, width)
);

create table if not exists sources (
  key text primary key,            -- matches sources.yaml
  reliable boolean default false,
  enabled boolean default true,
  consecutive_failures int default 0,
  authenticator_fails_90d int default 0
);

create table if not exists source_prices (
  id bigserial primary key,
  product_id bigint references products(id),
  source_key text references sources(key),
  native_size text not null,
  us_size text,
  price numeric(10,2) not null,
  shipping numeric(10,2),
  tax_estimate numeric(10,2),
  duties_estimate numeric(10,2),
  in_stock boolean not null,
  condition text not null default 'new_with_box',
  url text,
  seen_at timestamptz default now()
);
create index if not exists source_prices_lookup on source_prices(product_id, us_size, seen_at desc);

create table if not exists promos (
  id bigserial primary key,
  source_key text references sources(key),
  code text, percent_off numeric(5,2), amount_off numeric(10,2),
  min_spend numeric(10,2), conditions text, expires_at timestamptz,
  found_at timestamptz default now()
);

create table if not exists listings (
  ebay_item_id text primary key,
  product_id bigint references products(id),
  title text,
  adopted_legacy boolean default false,
  created_at timestamptz default now()
);

create table if not exists listing_sizes (
  ebay_item_id text references listings(ebay_item_id),
  us_size text not null,
  price numeric(10,2),
  available_qty int,
  quantity_sold int,
  last_changed timestamptz default now(),
  primary key (ebay_item_id, us_size)
);

create table if not exists orders (
  ebay_order_id text primary key,
  ebay_item_id text, us_size text,
  sale_price numeric(10,2), ebay_fees numeric(10,2),
  source_key text, source_cost numeric(10,2), tax numeric(10,2), shipping numeric(10,2),
  promo_code text, net_profit numeric(10,2),
  evtn text, status text, authenticator_result text,
  cancelled boolean default false, cancel_reason text,
  created_at timestamptz default now()
);

create table if not exists evidence (
  id bigserial primary key,
  product_id bigint references products(id),
  kind text,                       -- discontinued | price | stock
  url text, note text, captured_at timestamptz default now()
);

create table if not exists runs (
  id bigserial primary key,
  started_at timestamptz default now(),
  kind text,                       -- scan | sync | apply
  dry_run boolean,
  decision_log jsonb               -- why listed / skipped / repriced
);
