DROP POLICY IF EXISTS "allow_read" ON prediction_logs;
DROP POLICY IF EXISTS "allow_insert" ON prediction_logs;

CREATE TABLE IF NOT EXISTS user_prediction_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    module TEXT NOT NULL CHECK (module IN ('disease', 'yield')),
    input_summary TEXT NOT NULL,
    result_summary TEXT NOT NULL,
    result_details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS user_prediction_history_owner_created_idx
    ON user_prediction_history (user_id, created_at DESC);

ALTER TABLE user_prediction_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read their own prediction history"
    ON user_prediction_history FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own prediction history"
    ON user_prediction_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own prediction history"
    ON user_prediction_history FOR DELETE
    USING (auth.uid() = user_id);
