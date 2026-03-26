-- Libraries table
create table libraries (
  id serial primary key,
  name text not null unique
);

-- Chapters table
create table chapters (
  id serial primary key,
  library_id integer references libraries(id) on delete cascade,
  chapter_number text not null,
  section text not null
);

-- Figures table
create table figures (
  id serial primary key,
  figure_ref text not null unique,  -- e.g. "Refer to figure 84"
  image_url text not null           -- public URL from Supabase Storage
);

-- Questions table
create table questions (
  id serial primary key,
  chapter_id integer references chapters(id) on delete cascade,
  question_id text not null unique,  -- e.g. "1.1.1"
  question text not null,
  correct_answer text,
  figure_id integer references figures(id) on delete set null
);

-- Answers table
create table answers (
  id serial primary key,
  question_id integer references questions(id) on delete cascade,
  letter text not null,  -- A, B, C
  answer text not null
);

-- Explanations table
create table explanations (
  id serial primary key,
  question_id integer references questions(id) on delete cascade,
  letter text not null,  -- A, B, C
  explanation text not null
);
