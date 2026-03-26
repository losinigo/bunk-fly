import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://flynsttdbritbkzbwpwq.supabase.co'
const supabaseKey = 'sb_publishable_YbBlNMq98e6nFPQn2Bo3xA_WSebIPJh'

export const supabase = createClient(supabaseUrl, supabaseKey)
