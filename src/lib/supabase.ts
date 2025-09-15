import { createClient, type SupabaseClient } from '@supabase/supabase-js';

// Read env vars but don't crash the app in dev; components should handle missing client gracefully.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

if (!supabaseUrl || !supabaseKey) {
  // In some environments (tests, storybook) these may be missing. Create a noop-like client would be complex,
  // so we still create the client when values exist and otherwise export a wrapper that throws when used.
  console.warn('Supabase environment variables are missing. Supabase client will not be initialized.');
}

export const supabase: SupabaseClient | null = (supabaseUrl && supabaseKey)
  ? createClient(supabaseUrl, supabaseKey)
  : null;
