-- AgriVision Supabase Migration: 001_initial_schema.sql
-- Run this in the Supabase SQL editor to set up the database.

-- Prediction logs table
CREATE TABLE IF NOT EXISTS prediction_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module      TEXT NOT NULL CHECK (module IN ('disease', 'yield', 'market')),
    input_data  JSONB,
    result      JSONB,
    confidence  FLOAT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE prediction_logs ENABLE ROW LEVEL SECURITY;

-- Policy: allow all reads (adjust for auth later)
CREATE POLICY "allow_read" ON prediction_logs FOR SELECT USING (true);
CREATE POLICY "allow_insert" ON prediction_logs FOR INSERT WITH CHECK (true);
