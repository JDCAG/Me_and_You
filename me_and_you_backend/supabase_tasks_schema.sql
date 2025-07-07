-- ======================================================================
-- Me & You Application - `tasks` Table Schema and RLS
-- ======================================================================
-- This script creates the `tasks` table, sets up an automatic `updated_at`
-- timestamp, adds recommended indexes, and enables Row Level Security
-- with policies to ensure users can only access their own tasks.
--
-- Instructions:
-- 1. Navigate to your Supabase project.
-- 2. Go to the "SQL Editor" section.
-- 3. Click "+ New query".
-- 4. Copy and paste the entire content of this script into the editor.
-- 5. Click "RUN".
--
-- Notes:
-- - It's assumed you are running this as a superuser or a role with
--   sufficient privileges to create tables, functions, and policies.
-- - This script uses the `public` schema by default. If you prefer a
--   custom schema (e.g., `app_schema`), you'll need to create it first
--   and adjust the table/function references accordingly.
-- - `auth.uid()` is a Supabase helper function that returns the UUID
--   of the currently authenticated user.
-- ======================================================================

-- Harden the public schema (Optional but Recommended Security Measure)
-- Revoke default public create an usage on public schema to enforce explicit grants
-- REVOKE CREATE ON SCHEMA public FROM PUBLIC;
-- REVOKE USAGE ON SCHEMA public FROM PUBLIC;
-- Grant back usage for authenticated users, anon, and service_role as needed
-- GRANT USAGE ON SCHEMA public TO authenticated;
-- GRANT USAGE ON SCHEMA public TO anon;
-- GRANT USAGE ON SCHEMA public TO service_role;


-- Section 1: `updated_at` Timestamp Handling
-- ======================================================================

-- Create a function to automatically update the `updated_at` timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.handle_updated_at() IS
'This function updates the `updated_at` column to the current timestamp whenever a row in a table it''s attached to is updated.';


-- Section 2: `tasks` Table Creation
-- ======================================================================

CREATE TABLE IF NOT EXISTS public.tasks (
    -- Columns
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- Will be constrained by FK and RLS
    description TEXT NOT NULL CHECK (char_length(description) > 0),
    classified_type VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'Medium' CHECK (priority IN ('None', 'Low', 'Medium', 'High')),
    due_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'deferred', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Foreign Key Constraint (linking to Supabase auth.users)
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES auth.users(id)
        ON DELETE CASCADE -- If a user is deleted, their tasks are also deleted.
);

COMMENT ON TABLE public.tasks IS
'Stores tasks for users of the Me & You application. Each task is linked to a user and includes details like description, classification, priority, due date, and status.';
COMMENT ON COLUMN public.tasks.id IS 'Unique identifier for the task (UUID).';
COMMENT ON COLUMN public.tasks.user_id IS 'Identifier of the user who owns this task, references auth.users.id.';
COMMENT ON COLUMN public.tasks.description IS 'The textual description of the task (cannot be empty).';
COMMENT ON COLUMN public.tasks.classified_type IS 'AI-generated or user-selected category for the task (e.g., work, personal).';
COMMENT ON COLUMN public.tasks.priority IS 'Priority level of the task (None, Low, Medium, High).';
COMMENT ON COLUMN public.tasks.due_date IS 'Optional due date for the task.';
COMMENT ON COLUMN public.tasks.status IS 'Current status of the task (e.g., pending, completed).';
COMMENT ON COLUMN public.tasks.created_at IS 'Timestamp of when the task was created.';
COMMENT ON COLUMN public.tasks.updated_at IS 'Timestamp of the last update to the task.';


-- Section 3: Trigger for `updated_at` on `tasks` Table
-- ======================================================================

-- Attach the trigger to the `tasks` table
CREATE OR REPLACE TRIGGER on_tasks_update
BEFORE UPDATE ON public.tasks
FOR EACH ROW
EXECUTE FUNCTION public.handle_updated_at();

COMMENT ON TRIGGER on_tasks_update ON public.tasks IS
'Ensures the `updated_at` field is automatically updated whenever a task row is modified.';


-- Section 4: Indexes for Performance
-- ======================================================================

CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON public.tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON public.tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON public.tasks(priority); -- Added priority index

COMMENT ON INDEX public.idx_tasks_user_id IS 'Index on user_id for faster querying of user-specific tasks.';
COMMENT ON INDEX public.idx_tasks_due_date IS 'Index on due_date for efficient filtering and sorting by due date.';
COMMENT ON INDEX public.idx_tasks_status IS 'Index on status for quick filtering by task status.';
COMMENT ON INDEX public.idx_tasks_priority IS 'Index on priority for efficient filtering and sorting by priority.';


-- Section 5: Row Level Security (RLS) for `tasks` Table
-- ======================================================================

-- Enable RLS on the `tasks` table
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
-- Force RLS for table owners as well (good practice)
ALTER TABLE public.tasks FORCE ROW LEVEL SECURITY;


COMMENT ON TABLE public.tasks IS
'RLS enabled: Users can only access and manage their own tasks.'; -- Appending to table comment

-- Policy: Allow users to SELECT (read) their own tasks
CREATE POLICY "Allow authenticated users to select their own tasks"
ON public.tasks
FOR SELECT
TO authenticated -- Grant to the 'authenticated' role
USING (auth.uid() = user_id);

-- Policy: Allow users to INSERT (create) tasks for themselves
CREATE POLICY "Allow authenticated users to insert their own tasks"
ON public.tasks
FOR INSERT
TO authenticated -- Grant to the 'authenticated' role
WITH CHECK (auth.uid() = user_id);

-- Policy: Allow users to UPDATE their own tasks
CREATE POLICY "Allow authenticated users to update their own tasks"
ON public.tasks
FOR UPDATE
TO authenticated -- Grant to the 'authenticated' role
USING (auth.uid() = user_id)     -- Specifies which rows can be targeted for update
WITH CHECK (auth.uid() = user_id); -- Ensures user_id cannot be changed to someone else's

-- Policy: Allow users to DELETE their own tasks
CREATE POLICY "Allow authenticated users to delete their own tasks"
ON public.tasks
FOR DELETE
TO authenticated -- Grant to the 'authenticated' role
USING (auth.uid() = user_id);

-- ======================================================================
-- End of Script
-- =================================M=====================================
-- Note: The "M" at the end seems like a typo, removing it.
-- ======================================================================
-- End of Script
-- ======================================================================
