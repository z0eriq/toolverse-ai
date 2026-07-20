-- ToolVerse: profiles + light usage (Supabase Auth as identity)
-- Apply on project: kxtcxncucwvbepmqkcgf (SQL Editor or CLI)

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  display_name text not null default '',
  avatar_url text,
  locale text not null default 'en',
  theme text not null default 'system',
  public_username text unique,
  is_public boolean not null default false,
  headline text not null default '',
  bio text not null default '',
  role text not null default 'user' check (role in ('user', 'admin')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.usage_monthly (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles (id) on delete cascade,
  period_ym char(7) not null,
  tool_runs int not null default 0,
  unique (user_id, period_ym)
);

create index if not exists profiles_public_username_idx
  on public.profiles (public_username)
  where public_username is not null;

alter table public.profiles enable row level security;
alter table public.usage_monthly enable row level security;

grant select, insert, update on table public.profiles to authenticated;
grant select on table public.profiles to anon;
grant select, insert, update on table public.usage_monthly to authenticated;

-- Own row
create policy "profiles_select_own"
  on public.profiles
  for select
  to authenticated
  using ((select auth.uid()) = id);

-- Public profiles for community pages
create policy "profiles_select_public"
  on public.profiles
  for select
  to anon, authenticated
  using (is_public = true);

create policy "profiles_insert_own"
  on public.profiles
  for insert
  to authenticated
  with check ((select auth.uid()) = id);

create policy "profiles_update_own"
  on public.profiles
  for update
  to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

create policy "usage_select_own"
  on public.usage_monthly
  for select
  to authenticated
  using ((select auth.uid()) = user_id);

create policy "usage_insert_own"
  on public.usage_monthly
  for insert
  to authenticated
  with check ((select auth.uid()) = user_id);

create policy "usage_update_own"
  on public.usage_monthly
  for update
  to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

-- Auto-create profile on signup (role stays in profiles / app_metadata — never user_metadata for authz)
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'name', '')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

revoke all on function public.handle_new_user() from public;
revoke execute on function public.handle_new_user() from anon, authenticated;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function public.handle_new_user();

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
  before update on public.profiles
  for each row
  execute function public.set_updated_at();
